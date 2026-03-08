import { useState } from 'react'
import { MessageSquare, Send, CheckCircle } from 'lucide-react'
import { submitFeedback } from '../services/api'
import { useTranslation } from 'react-i18next'

export default function FeedbackPage() {
    const { t } = useTranslation()
    const [form, setForm] = useState({ name: '', email: '', message: '' })
    const [loading, setLoading] = useState(false)
    const [submitted, setSubmitted] = useState(false)
    const [error, setError] = useState('')

    const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
        setForm(prev => ({ ...prev, [key]: e.target.value }))

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            await submitFeedback(form)
            setSubmitted(true)
        } catch {
            setError(t('feedback_error'))
        } finally {
            setLoading(false)
        }
    }

    if (submitted) {
        return (
            <div className="max-w-lg mx-auto px-6 py-20 text-center">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <CheckCircle size={40} className="text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('feedback_thanks')}</h2>
                <p className="text-gray-500">{t('feedback_success_msg')}</p>
                <button
                    onClick={() => { setSubmitted(false); setForm({ name: '', email: '', message: '' }) }}
                    className="mt-6 btn-primary"
                >
                    {t('feedback_submit_another')}
                </button>
            </div>
        )
    }

    return (
        <div className="max-w-2xl mx-auto px-6 py-10">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <MessageSquare size={24} className="text-blue-600" /> {t('feedback')}
                </h1>
                <p className="text-sm text-gray-500 mt-1">{t('feedback_subtitle')}</p>
            </div>

            <div className="card">
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="field-label">{t('feedback_name')}</label>
                            <input
                                type="text"
                                value={form.name}
                                onChange={set('name')}
                                placeholder={t('feedback_name_placeholder')}
                                className="field-input"
                                required
                            />
                        </div>
                        <div>
                            <label className="field-label">{t('feedback_email')}</label>
                            <input
                                type="email"
                                value={form.email}
                                onChange={set('email')}
                                placeholder="you@example.com"
                                className="field-input"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="field-label">{t('feedback_message_label')}</label>
                        <textarea
                            value={form.message}
                            onChange={set('message')}
                            placeholder={t('feedback_message_placeholder')}
                            className="field-input min-h-[140px] resize-y"
                            required
                            minLength={10}
                        />
                    </div>

                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2"
                    >
                        {loading ? t('submitting') : <><Send size={16} /> {t('feedback_submit')}</>}
                    </button>
                </form>
            </div>
        </div>
    )
}
