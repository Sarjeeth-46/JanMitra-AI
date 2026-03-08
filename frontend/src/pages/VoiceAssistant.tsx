import { useState, useRef, useCallback, useEffect } from 'react'
import { Mic, Square, Loader2 } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { apiEndpoints } from '../config/api'

// ── Types ───────────────────────────────────────────────────────────────────
interface Message {
    id: string
    sender: 'user' | 'ai'
    text: string
    time: string
}

// Four mutually-exclusive UI states for the voice pipeline
type VoiceState = 'idle' | 'recording' | 'processing' | 'speaking'

import { generateUUID } from '../utils/uuid'

// Persistent session ID so the backend can cancel stale requests
const SESSION_ID = generateUUID()

// AbortController ref — replaced on every new request so the previous fetch is cancelled
let _abortController: AbortController | null = null

// ── Helpers ────────────────────────────────────────────────────────────────
function formatTime(date: Date) {
    return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false })
}

let _currentAudioSource: AudioBufferSourceNode | null = null

async function playBase64Audio(base64: string): Promise<void> {
    // Stop any currently playing audio before starting new one
    _currentAudioSource?.stop()
    _currentAudioSource = null

    if (!base64) return
    try {
        const binary = atob(base64)
        const bytes = new Uint8Array(binary.length)
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
        const ctx = new AudioContext()
        const buffer = await ctx.decodeAudioData(bytes.buffer)
        const src = ctx.createBufferSource()
        src.buffer = buffer
        src.connect(ctx.destination)
        _currentAudioSource = src
        return new Promise(resolve => {
            src.onended = () => {
                _currentAudioSource = null
                resolve()
            }
            src.start()
        })
    } catch {
        // Playback unavailable — silent fail
    }
}

const LANG_MAP: Record<string, string> = {
    en: 'en-IN', hi: 'hi-IN', ta: 'ta-IN',
    te: 'te-IN', bn: 'bn-IN', mr: 'mr-IN',
    kn: 'kn-IN', ml: 'ml-IN',
}

// ── Component ───────────────────────────────────────────────────────────────
export default function VoiceAssistant() {
    const { t, i18n } = useTranslation()

    const [voiceState, setVoiceState] = useState<VoiceState>('idle')
    const [messages, setMessages] = useState<Message[]>([
        { id: '0', sender: 'ai', text: t('voice_greeting'), time: '' },
    ])
    const [elapsed, setElapsed] = useState(0)
    const elapsedRef = useRef(0)   // readable inside onstop closure

    const mediaRecorderRef = useRef<MediaRecorder | null>(null)
    const chunksRef = useRef<Blob[]>([])
    const timerRef = useRef<number | null>(null)

    // ── Recording ────────────────────────────────────────────────────────────
    const startRecording = useCallback(async () => {
        if (voiceState !== 'idle') return   // guard: only start from idle
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            const recorder = new MediaRecorder(stream)
            chunksRef.current = []

            recorder.ondataavailable = (e) => {
                if (e.data.size > 0) chunksRef.current.push(e.data)
            }

            recorder.onstop = async () => {
                stream.getTracks().forEach(t => t.stop())
                // Discard recordings that are too short to transcribe reliably
                if (elapsedRef.current < 2) {
                    setVoiceState('idle')
                    return
                }
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
                await sendAudio(blob)
            }

            recorder.start()
            mediaRecorderRef.current = recorder
            setVoiceState('recording')
            setElapsed(0)
            elapsedRef.current = 0
            timerRef.current = window.setInterval(() => {
                const next = elapsedRef.current + 1
                elapsedRef.current = next
                setElapsed(next)
            }, 1000)
        } catch {
            setVoiceState('idle')
        }
    }, [voiceState])

    const stopRecording = useCallback(() => {
        if (voiceState !== 'recording') return
        // If < 2s, just ignore the tap — the inline hint already shows the countdown.
        // The onstop handler will also check elapsed before sending.
        if (elapsedRef.current < 2) return
        if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null }
        mediaRecorderRef.current?.stop()
        // state transitions to 'processing' inside sendAudio
    }, [voiceState])

    // Auto-stop after 15 s
    useEffect(() => {
        if (voiceState === 'recording' && elapsed >= 15) stopRecording()
    }, [voiceState, elapsed, stopRecording])

    // ── Send Audio ───────────────────────────────────────────────────────────
    const sendAudio = async (blob: Blob) => {
        // Cancel any in-flight fetch for this session
        if (_abortController) {
            _abortController.abort()
        }
        _abortController = new AbortController()
        const signal = _abortController.signal

        const userMsg: Message = {
            id: Date.now().toString(),
            sender: 'user',
            text: t('voice_msg_sent'),
            time: formatTime(new Date()),
        }
        setMessages(prev => [...prev, userMsg])
        setVoiceState('processing')

        try {
            // If a UI language is explicitly selected, send it so Transcribe skips auto-detect.
            // 'auto' means IdentifyLanguage=True on the backend.
            const uiLang = i18n.language  // e.g. 'hi', 'ta', 'en'
            const langParam = LANG_MAP[uiLang] ? uiLang : 'auto'  // short code or 'auto'
            const formData = new FormData()
            formData.append('audio', blob, 'voice.webm')

            // ── Token (centralized API configuration) ──
            let token = localStorage.getItem('access_token') || ''
            if (!token) {
                try {
                    const tr = await fetch(apiEndpoints.anonymous_token)
                    if (tr.ok) {
                        const td = await tr.json()
                        token = td.access_token || ''
                        if (token) localStorage.setItem('access_token', token)
                    }
                } catch { /* continue without token */ }
            }

            const res = await fetch(
                `${apiEndpoints.voice_query}?lang=${encodeURIComponent(langParam)}`,
                {
                    method: 'POST',
                    headers: {
                        'X-Session-Id': SESSION_ID,
                        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                    },
                    body: formData,
                    signal,
                }
            )


            // Surface real HTTP errors (401, 500, etc.) into the catch block
            if (!res.ok && res.status !== 204) {
                throw new Error(`Voice API error: ${res.status}`)
            }

            // 204 = this request was cancelled server-side by a newer one
            if (res.status === 204) {
                setVoiceState('idle')
                return
            }

            const data = await res.json()

            // Update user bubble with real transcript
            if (data.transcript) {
                setMessages(prev =>
                    prev.map(m => m.id === userMsg.id ? { ...m, text: data.transcript } : m)
                )
            }

            const aiText = data.response_text || t('voice_fallback_msg')
            setMessages(prev => [...prev, {
                id: Date.now().toString() + '_ai',
                sender: 'ai',
                text: aiText,
                time: formatTime(new Date()),
            }])

            // Play audio and wait for it to finish before returning to idle
            setVoiceState('speaking')
            await playBase64Audio(data.audio_url || '')

        } catch (err: unknown) {
            if ((err as Error)?.name === 'AbortError') {
                // Fetch was aborted because user sent a new query — silently ignore
                setVoiceState('idle')
                return
            }
            setMessages(prev => [...prev, {
                id: Date.now().toString() + '_fallback',
                sender: 'ai',
                text: t('voice_fallback_msg'),
                time: formatTime(new Date()),
            }])
        } finally {
            setVoiceState('idle')
        }
    }

    // ── State labels ─────────────────────────────────────────────────────────
    const stateLabel: Record<VoiceState, string> = {
        idle: t('voice_state_tap_speak'),
        recording: t('voice_state_recording'),
        processing: t('voice_state_processing'),
        speaking: t('voice_state_speaking'),
    }
    const stateSubLabel: Record<VoiceState, string> = {
        idle: t('voice_state_ask'),
        recording: t('voice_state_tap_stop'),
        processing: '⏳ Thinking...',
        speaking: '🔊 Playing response...',
    }

    const toggle = () => {
        if (voiceState === 'idle') startRecording()
        if (voiceState === 'recording') stopRecording()
        // Ignore clicks while processing / speaking
    }

    const formatElapsed = (s: number) =>
        `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

    const isActive = voiceState !== 'idle'
    const isRecording = voiceState === 'recording'
    const isProcessing = voiceState === 'processing'
    const isSpeaking = voiceState === 'speaking'
    const isDisabled = isProcessing || isSpeaking

    // ── Render ───────────────────────────────────────────────────────────────
    return (
        <div className="max-w-2xl mx-auto px-4 py-10">
            <div className="card flex flex-col items-center gap-6">

                {/* Mic / State Button */}
                <div className="flex flex-col items-center gap-3">
                    <div className={`relative ${isActive ? 'animate-pulse' : ''}`}>
                        {isActive && (
                            <div className="absolute inset-0 rounded-full ring-8 ring-blue-200 animate-ping opacity-60" />
                        )}
                        <button
                            onClick={toggle}
                            disabled={isDisabled}
                            aria-label={isRecording ? 'Stop recording' : 'Start recording'}
                            className={`relative w-24 h-24 rounded-full flex items-center justify-center shadow-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed ${isRecording
                                ? 'bg-red-500 hover:bg-red-600 ring-4 ring-red-200'
                                : isProcessing || isSpeaking
                                    ? 'bg-orange-500 ring-4 ring-orange-200'
                                    : 'bg-blue-600 hover:bg-blue-700 ring-4 ring-blue-300'
                                }`}
                        >
                            {isProcessing
                                ? <Loader2 size={32} className="text-white animate-spin" />
                                : isRecording
                                    ? <Square size={32} className="text-white" fill="white" />
                                    : <Mic size={32} className="text-white" />
                            }
                        </button>
                    </div>

                    <div className="text-center">
                        <p className="text-base font-semibold text-gray-800">{stateLabel[voiceState]}</p>
                        <p className="text-sm text-gray-500">{stateSubLabel[voiceState]}</p>
                        {isRecording && elapsed < 2 && (
                            <p className="text-xs text-orange-500 mt-1">Keep speaking… ({2 - elapsed}s min)</p>
                        )}
                    </div>
                </div>

                {/* Waveform */}
                {isActive && (
                    <div className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4">
                        <div className="flex items-center justify-center gap-1 h-12">
                            {Array.from({ length: 20 }).map((_, i) => (
                                <div
                                    key={i}
                                    className={`waveform-bar w-1.5 rounded-full ${isSpeaking ? 'bg-green-400'
                                        : isProcessing ? 'bg-orange-400'
                                            : 'bg-blue-500'
                                        }`}
                                    style={{ height: `${20 + Math.random() * 30}px`, animationDelay: `${i * 0.06}s` }}
                                />
                            ))}
                        </div>
                        <div className="flex justify-between mt-2 text-xs text-gray-400">
                            <span>{formatElapsed(elapsed)}</span>
                            <span>0:15</span>
                        </div>
                    </div>
                )}

                {/* Chat Messages */}
                <div className="w-full flex flex-col gap-3 max-h-96 overflow-y-auto">
                    {messages.map(msg => (
                        <div
                            key={msg.id}
                            className={`flex gap-2 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            {msg.sender === 'ai' && (
                                <div className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold">
                                    JAI
                                </div>
                            )}
                            <div className={`max-w-xs lg:max-w-sm ${msg.sender === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                                <div className={`rounded-2xl p-3 text-sm leading-relaxed whitespace-pre-wrap ${msg.sender === 'user'
                                    ? 'bg-blue-600 text-white rounded-tr-sm'
                                    : 'bg-gray-100 text-gray-800 rounded-tl-sm'
                                    }`}>
                                    {msg.text}
                                </div>
                                {msg.time && (
                                    <span className="text-[10px] text-gray-400 mt-1 px-1">{msg.time}</span>
                                )}
                            </div>
                            {msg.sender === 'user' && (
                                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold">
                                    R
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
