import { useState } from 'react'
import { Search, Clock, CheckCircle, FileText, AlertCircle } from 'lucide-react'
import { getApplicationStatus } from '../services/api'
import { useTranslation } from 'react-i18next'

interface StatusResult {
    application_id: string
    status: string
    submitted_date: string
    estimated_approval: string
    scheme_name: string
}

const statusConfig: Record<string, { color: string; icon: typeof CheckCircle; badge: string }> = {
    'Approved': { color: 'text-green-600', icon: CheckCircle, badge: 'badge-green' },
    'Under Review': { color: 'text-blue-600', icon: Clock, badge: 'badge-blue' },
    'Processing': { color: 'text-blue-600', icon: Clock, badge: 'badge-blue' },
    'Pending Documents': { color: 'text-yellow-600', icon: AlertCircle, badge: 'badge-yellow' },
}

export default function TrackStatusPage() {
    const { t } = useTranslation()
    const [appId, setAppId] = useState('')
    const [phone, setPhone] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<StatusResult | null>(null)
    const [error, setError] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        setResult(null)
        try {
            const data = await getApplicationStatus(appId.trim(), phone.trim())
            setResult(data)
        } catch {
            setError(t('track_error'))
        } finally {
            setLoading(false)
        }
    }

    const cfg = result ? (statusConfig[result.status] ?? statusConfig['Processing']) : null

    return (
        <div className="max-w-2xl mx-auto px-6 py-10">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">{t('track_heading')}</h1>
                <p className="text-sm text-gray-500 mt-1">{t('track_subtitle')}</p>
            </div>

            <div className="card">
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="field-label">{t('track_app_id')}</label>
                        <input
                            type="text"
                            value={appId}
                            onChange={e => setAppId(e.target.value)}
                            placeholder="e.g. JMAI/20260307/0045"
                            className="field-input"
                            required
                        />
                    </div>
                    <div>
                        <label className="field-label">{t('track_phone')}</label>
                        <input
                            type="tel"
                            value={phone}
                            onChange={e => setPhone(e.target.value)}
                            placeholder={t('track_phone_placeholder')}
                            className="field-input"
                            pattern="[0-9]{10}"
                            required
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
                        {loading ? t('searching') : <><Search size={18} /> {t('track_status')}</>}
                    </button>
                </form>
            </div>

            {result && cfg && (
                <div className="card mt-6 border-l-4 border-blue-500">
                    <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                        <div>
                            <h2 className="text-base font-semibold text-gray-800">{t('track_found')}</h2>
                            <p className="text-xs text-gray-500 mt-0.5">ID: {result.application_id}</p>
                        </div>
                        <span className={cfg.badge}>
                            <cfg.icon size={12} /> {result.status}
                        </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {[
                            { label: t('track_scheme'), value: result.scheme_name, icon: FileText },
                            { label: t('track_submitted'), value: result.submitted_date, icon: Clock },
                            { label: t('track_current_status'), value: result.status, icon: cfg.icon },
                            { label: t('track_est_approval'), value: result.estimated_approval, icon: CheckCircle },
                        ].map(({ label, value, icon: Icon }) => (
                            <div key={label} className="flex items-start gap-3">
                                <Icon size={16} className="text-blue-500 mt-0.5 flex-shrink-0" />
                                <div>
                                    <p className="text-xs text-gray-500">{label}</p>
                                    <p className="text-sm font-medium text-gray-800">{value}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Visual Timeline */}
                    <div className="mt-8 pt-8 border-t border-gray-100">
                        <h3 className="text-sm font-semibold text-gray-700 mb-6 px-1">Application Journey</h3>
                        <div className="relative pl-8 space-y-8 before:content-[''] before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-gray-100">
                            {[
                                { step: 'Application Submitted', date: result.submitted_date, status: 'completed' },
                                { step: 'Initial AI Verification', date: result.submitted_date, status: 'completed' },
                                { step: 'Department Review', date: 'In Progress', status: result.status === 'Processing' || result.status === 'Under Review' ? 'active' : 'pending' },
                                { step: 'Final Approval', date: 'TBD', status: result.status === 'Approved' ? 'completed' : 'pending' },
                            ].map((item, idx) => (
                                <div key={idx} className="relative">
                                    <div className={`absolute -left-[27px] top-1 w-4 h-4 rounded-full border-2 bg-white z-10 ${item.status === 'completed' ? 'border-green-500 bg-green-500' :
                                            item.status === 'active' ? 'border-blue-500 animate-pulse' : 'border-gray-200'
                                        }`}>
                                        {item.status === 'completed' && <CheckCircle size={10} className="text-white mx-auto mt-[1px]" />}
                                    </div>
                                    <div>
                                        <p className={`text-sm font-semibold ${item.status === 'pending' ? 'text-gray-400' : 'text-gray-800'}`}>{item.step}</p>
                                        <p className="text-xs text-gray-500">{item.date}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
