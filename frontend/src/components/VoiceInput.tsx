import { useState, useRef, useEffect } from 'react'
import { Mic, Square, Loader2 } from 'lucide-react'
import { voiceQuery } from '../services/api'
import toast from 'react-hot-toast'
import type { UserProfile } from '../types'

interface VoiceInputProps {
  onTranscriptReceived: (transcript: string, extractedData?: Partial<UserProfile>) => void
}

const VoiceInput = ({ onTranscriptReceived }: VoiceInputProps) => {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop()
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        await processAudio(audioBlob)
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      toast.success('Recording started')
    } catch (error) {
      console.error('Error starting recording:', error)
      toast.error('Failed to access microphone')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true)
    try {
      const response = await voiceQuery(audioBlob, 'voice.webm')

      if (response.transcript) {
        toast.success('Audio processed successfully')
        onTranscriptReceived(response.transcript, {})
      } else {
        toast.error('Failed to process audio')
      }
    } catch (error) {
      console.error('Error processing audio:', error)
      toast.error('Failed to process audio')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="flex items-center space-x-4">
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isProcessing}
        className={`relative p-6 rounded-2xl transition-all duration-300 shadow-lg ${isRecording
          ? 'bg-gradient-to-br from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 animate-pulse scale-110'
          : 'bg-gradient-to-br from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 hover:scale-105'
          } text-white disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100`}
      >
        {isProcessing ? (
          <Loader2 className="w-7 h-7 animate-spin" />
        ) : isRecording ? (
          <Square className="w-7 h-7" />
        ) : (
          <Mic className="w-7 h-7" />
        )}
        {isRecording && (
          <span className="absolute -top-1 -right-1 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500"></span>
          </span>
        )}
      </button>
      <div className="flex-1">
        <p className="text-base font-semibold text-gray-900 dark:text-white">
          {isProcessing
            ? 'Processing your voice...'
            : isRecording
              ? 'Recording... Click to stop'
              : 'Click to start recording'}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {isRecording ? 'Speak your details clearly' : 'Voice input will auto-fill the form'}
        </p>
      </div>
    </div>
  )
}

export default VoiceInput
