import { Link } from 'react-router-dom'
import { Mic, ArrowRight, Tractor, GraduationCap, Users, HardHat } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function LandingPage() {
  const { t } = useTranslation()

  const categories = [
    { icon: Tractor, labelKey: 'cat_farmer', color: 'text-green-600', bg: 'bg-green-50' },
    { icon: GraduationCap, labelKey: 'cat_student', color: 'text-blue-600', bg: 'bg-blue-50' },
    { icon: Users, labelKey: 'cat_elder', color: 'text-purple-600', bg: 'bg-purple-50' },
    { icon: HardHat, labelKey: 'cat_worker', color: 'text-orange-600', bg: 'bg-orange-50' },
  ]

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      {/* Headline */}
      <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6 leading-tight">
        {t('headline')}
      </h1>

      {/* Hero Image + CTA Overlay */}
      <div className="relative rounded-2xl overflow-hidden shadow-md">
        <img
          src="/hero.png"
          alt="JanMitra AI Hero"
          className="w-full object-cover h-72 sm:h-96"
        />

        {/* Gradient overlay at bottom */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />

        {/* CTA buttons on image */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col sm:flex-row gap-3 w-full justify-center px-6">
          <Link
            to="/eligibility"
            className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-7 py-3 rounded-xl transition shadow-lg"
          >
            {t('start_eligibility')} <ArrowRight size={18} />
          </Link>
          <Link
            to="/voice-assistant"
            className="flex items-center justify-center gap-2 bg-orange-400 hover:bg-orange-500 text-white font-semibold px-7 py-3 rounded-xl transition shadow-lg"
          >
            <Mic size={18} /> {t('use_voice_assistant')}
          </Link>
        </div>
      </div>

      {/* Category Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mt-10">
        {categories.map((cat) => {
          const Icon = cat.icon
          return (
            <Link
              key={cat.labelKey}
              to="/eligibility"
              className="card-hover flex flex-col items-center justify-center gap-3 py-8 cursor-pointer group"
            >
              <div className={`w-16 h-16 ${cat.bg} ${cat.color} rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform`}>
                <Icon size={32} />
              </div>
              <span className="text-sm font-semibold text-gray-700">{t(cat.labelKey)}</span>
            </Link>
          )
        })}
      </div>

      {/* Info strip */}
      <div className="mt-10 bg-blue-50 border border-blue-100 rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="font-semibold text-blue-800">{t('discover_schemes')}</h3>
          <p className="text-sm text-blue-600 mt-0.5">{t('ai_powered_check')}</p>
        </div>
        <Link
          to="/upload-document"
          className="flex-shrink-0 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition"
        >
          {t('upload_documents')}
        </Link>
      </div>
    </div>
  )
}
