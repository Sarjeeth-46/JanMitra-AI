import { useLocation, useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle, ArrowLeft, Star } from 'lucide-react'

interface EvaluationResult {
  scheme_name: string
  eligible: boolean
  missing_fields: string[]
  failed_conditions: string[]
}

// Benefit descriptions per scheme (enriched display data)
const SCHEME_META: Record<string, { benefit: string; description: string }> = {
  'PM-KISAN': {
    benefit: '₹6,000/year',
    description: 'Direct income support for small and marginal farmer families.',
  },
  'Ayushman Bharat': {
    benefit: 'Up to ₹5 lakh/year health cover',
    description: 'Health insurance for economically weaker sections under PM-JAY.',
  },
  'PMAY': {
    benefit: 'Subsidy up to ₹2.67 lakh',
    description: 'Housing for All – credit-linked subsidy for home loan interest.',
  },
  'PMJDY': {
    benefit: '₹10,000 overdraft + insurance',
    description: 'Zero-balance bank account with accident & life insurance coverage.',
  },
  'Scholarship SC/ST': {
    benefit: 'Full tuition + maintenance allowance',
    description: 'Post-matric scholarship for SC/ST students to continue education.',
  },
}

function getSchemeExtra(name: string) {
  // Try exact match first, then partial
  if (SCHEME_META[name]) return SCHEME_META[name]
  const key = Object.keys(SCHEME_META).find(k => name.toLowerCase().includes(k.toLowerCase()))
  return key
    ? SCHEME_META[key]
    : { benefit: 'Government assistance', description: 'Welfare scheme for eligible citizens.' }
}

export default function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as { results?: EvaluationResult[]; profile?: { name?: string } } | null

  const results: EvaluationResult[] = state?.results ?? []
  const eligible = results.filter(r => r.eligible)
  const ineligible = results.filter(r => !r.eligible)
  const userName = state?.profile?.name || 'You'

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 flex-wrap">
        <button
          onClick={() => navigate('/eligibility')}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition"
        >
          <ArrowLeft size={16} /> Back
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">Eligible Schemes For You</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Based on the profile of <span className="font-medium text-gray-700">{userName}</span> —{' '}
            <span className="text-blue-600 font-medium">{eligible.length}</span> scheme{eligible.length !== 1 ? 's' : ''} matched
          </p>
        </div>
      </div>

      {/* No results state */}
      {results.length === 0 && (
        <div className="card text-center py-14">
          <XCircle size={48} className="text-gray-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700 mb-1">No Results Available</h2>
          <p className="text-sm text-gray-500 mb-5">
            Could not retrieve eligibility data from the server. Please try again.
          </p>
          <button onClick={() => navigate('/eligibility')} className="btn-primary">
            Retry Eligibility Check
          </button>
        </div>
      )}

      {/* Eligible schemes */}
      {eligible.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Star size={18} className="text-yellow-500" fill="currentColor" />
            <h2 className="text-base font-semibold text-gray-800">Schemes You Qualify For</h2>
            <span className="badge-green ml-1">{eligible.length} eligible</span>
          </div>
          <div className="flex flex-col gap-4">
            {eligible.map((r, i) => {
              const meta = getSchemeExtra(r.scheme_name)
              return (
                <div
                  key={r.scheme_name}
                  className="card border-l-4 border-green-500 flex items-start justify-between gap-4 flex-wrap"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-9 h-9 bg-green-100 text-green-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                      {i + 1}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{r.scheme_name}</h3>
                      <p className="text-sm text-gray-500 mt-0.5">{meta.description}</p>
                      <span className="inline-block mt-2 text-sm font-medium text-green-700 bg-green-50 px-3 py-0.5 rounded-full">
                        Benefit: {meta.benefit}
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-3 flex-shrink-0">
                    <div className="flex items-center gap-1.5">
                      <CheckCircle size={18} className="text-green-500" />
                      <span className="badge-green text-[11px]">Eligible</span>
                    </div>
                    <button
                      onClick={() => navigate('/apply', { state: { scheme: r, profile: state?.profile } })}
                      className="btn-primary py-1.5 px-4 text-xs"
                    >
                      Apply Now
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Ineligible schemes (collapsible hint) */}
      {ineligible.length > 0 && (
        <div>
          <h2 className="text-base font-semibold text-gray-500 mb-3 flex items-center gap-2">
            <XCircle size={16} className="text-red-400" /> Schemes You Don't Currently Qualify For
          </h2>
          <div className="flex flex-col gap-3">
            {ineligible.map(r => (
              <div key={r.scheme_name} className="card border border-gray-200 opacity-70 flex items-start justify-between gap-4 flex-wrap">
                <div>
                  <h3 className="font-medium text-gray-700">{r.scheme_name}</h3>
                  {r.failed_conditions.length > 0 && (
                    <p className="text-xs text-red-500 mt-1">
                      Reason: {r.failed_conditions[0]}
                    </p>
                  )}
                </div>
                <span className="badge-yellow text-[11px]">Not Eligible</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CTA */}
      {results.length > 0 && (
        <div className="mt-8 bg-blue-50 border border-blue-100 rounded-xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-blue-800">Want to apply for a scheme?</p>
            <p className="text-sm text-blue-600 mt-0.5">Upload your documents to speed up the application process.</p>
          </div>
          <button onClick={() => navigate('/upload-document')} className="btn-primary flex-shrink-0">
            Upload Documents
          </button>
        </div>
      )}
    </div>
  )
}
