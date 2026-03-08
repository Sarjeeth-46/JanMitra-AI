import { Link } from 'react-router-dom'
import { CheckSquare, Mic, Upload, Search, Clock } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function ServicesPage() {
    const { t } = useTranslation()

    const services = [
        {
            icon: CheckSquare,
            titleKey: 'svc_eligibility_title',
            descKey: 'svc_eligibility_desc',
            href: '/eligibility',
            color: 'text-blue-600',
            bg: 'bg-blue-50',
            borderHover: 'hover:border-blue-400',
        },
        {
            icon: Mic,
            titleKey: 'svc_voice_title',
            descKey: 'svc_voice_desc',
            href: '/voice-assistant',
            color: 'text-orange-500',
            bg: 'bg-orange-50',
            borderHover: 'hover:border-orange-400',
        },
        {
            icon: Upload,
            titleKey: 'svc_doc_title',
            descKey: 'svc_doc_desc',
            href: '/upload-document',
            color: 'text-green-600',
            bg: 'bg-green-50',
            borderHover: 'hover:border-green-400',
        },
        {
            icon: Search,
            titleKey: 'svc_scheme_title',
            descKey: 'svc_scheme_desc',
            href: '/eligibility',
            color: 'text-purple-600',
            bg: 'bg-purple-50',
            borderHover: 'hover:border-purple-400',
        },
        {
            icon: Clock,
            titleKey: 'svc_track_title',
            descKey: 'svc_track_desc',
            href: '/track',
            color: 'text-rose-500',
            bg: 'bg-rose-50',
            borderHover: 'hover:border-rose-400',
        },
    ]

    const stats = [
        { value: '500+', labelKey: 'stat_schemes' },
        { value: '8', labelKey: 'stat_languages' },
        { value: '60s', labelKey: 'stat_time' },
    ]

    return (
        <div className="max-w-6xl mx-auto px-6 py-10">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">{t('our_services')}</h1>
                <p className="text-gray-500 mt-2 text-sm">{t('our_services_subtitle')}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {services.map((svc) => {
                    const Icon = svc.icon
                    return (
                        <Link
                            key={svc.titleKey}
                            to={svc.href}
                            className={`card-hover flex flex-col gap-4 border border-gray-200 ${svc.borderHover} transition-all duration-200`}
                        >
                            <div className={`w-14 h-14 ${svc.bg} ${svc.color} rounded-xl flex items-center justify-center`}>
                                <Icon size={28} />
                            </div>
                            <div>
                                <h2 className="font-semibold text-gray-900 text-base mb-1">{t(svc.titleKey)}</h2>
                                <p className="text-sm text-gray-500 leading-relaxed">{t(svc.descKey)}</p>
                            </div>
                            <span className={`text-sm font-medium ${svc.color} mt-auto`}>{t('get_started')} →</span>
                        </Link>
                    )
                })}
            </div>

            <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-6">
                {stats.map((stat) => (
                    <div key={stat.labelKey} className="card text-center">
                        <p className="text-3xl font-bold text-blue-600">{stat.value}</p>
                        <p className="text-sm text-gray-500 mt-1">{t(stat.labelKey)}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}
