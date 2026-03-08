import { useState } from 'react'
import { HelpCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { useTranslation } from 'react-i18next'

function FAQItem({ q, a }: { q: string; a: string }) {
    const [open, setOpen] = useState(false)
    return (
        <div className="border border-gray-200 rounded-xl overflow-hidden">
            <button
                onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between px-5 py-4 text-left bg-white hover:bg-gray-50 transition"
            >
                <span className="font-medium text-gray-800 text-sm">{q}</span>
                {open ? <ChevronUp size={18} className="text-blue-600 flex-shrink-0" /> : <ChevronDown size={18} className="text-gray-400 flex-shrink-0" />}
            </button>
            {open && (
                <div className="px-5 pb-5 pt-1 bg-white border-t border-gray-100">
                    <p className="text-sm text-gray-600 leading-relaxed">{a}</p>
                </div>
            )}
        </div>
    )
}

export default function FAQPage() {
    const { t } = useTranslation()

    const faqs = [
        { q: t('faq_q1'), a: t('faq_a1') },
        { q: t('faq_q2'), a: t('faq_a2') },
        { q: t('faq_q3'), a: t('faq_a3') },
        { q: t('faq_q4'), a: t('faq_a4') },
    ]

    return (
        <div className="max-w-3xl mx-auto px-6 py-10">
            <div className="mb-8 flex items-start gap-3">
                <HelpCircle size={28} className="text-blue-600 mt-1 flex-shrink-0" />
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">{t('faq_heading')}</h1>
                    <p className="text-sm text-gray-500 mt-1">{t('faq_subtitle')}</p>
                </div>
            </div>

            <div className="flex flex-col gap-3">
                {faqs.map(faq => (
                    <FAQItem key={faq.q} q={faq.q} a={faq.a} />
                ))}
            </div>

            <div className="mt-10 card bg-blue-50 border border-blue-100 text-center">
                <p className="text-sm text-blue-700 font-medium">{t('faq_still_questions')}</p>
                <p className="text-sm text-blue-600 mt-1">
                    {t('faq_helpdesk')} <span className="font-semibold">1800-XXX-XXXX</span> {t('faq_helpdesk_hours')}
                </p>
            </div>
        </div>
    )
}
