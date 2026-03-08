import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { evaluateEligibility, type EvaluationRequest } from '../services/api'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Jammu and Kashmir',
]

const OCCUPATIONS = ['Farmer', 'Laborer', 'Business', 'Student', 'Teacher', 'Government Employee', 'Self-Employed', 'Other']
const CATEGORIES = ['General', 'OBC', 'SC', 'ST', 'EWS']

const eligibilitySchema = z.object({
  name: z.string().min(3, "Name must be at least 3 characters").regex(/^[A-Za-z\s]+$/, "Only letters and spaces allowed"),
  dob: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid Date of Birth").refine(val => {
    const d = new Date(val);
    if (isNaN(d.getTime())) return false;
    const age = new Date().getFullYear() - d.getFullYear();
    return age >= 18 && age <= 100;
  }, "Age must be between 18 and 100"),
  income: z.preprocess((val) => Number(String(val).replace(/,/g, '')), z.number({ invalid_type_error: "Must be a valid number" }).min(0, "Income must be at least 0").max(10000000, "Income cannot exceed 1,00,00,000")),
  state: z.string().min(1, "State is required"),
  occupation: z.string().min(1, "Occupation is required"),
  category: z.string().min(1, "Category is required"),
  land_size: z.preprocess((val) => val === '' ? 0 : Number(val), z.number().min(0, "Must be >= 0").default(0)),
})

type EligibilityFormValues = z.infer<typeof eligibilitySchema>

export default function EligibilityFormPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formError, setFormError] = useState('')
  const [autoFilled, setAutoFilled] = useState(false)

  const { register, handleSubmit, formState: { errors }, setValue } = useForm<EligibilityFormValues>({
    resolver: zodResolver(eligibilitySchema),
    defaultValues: {
      name: '',
      dob: '',
      income: undefined,
      state: '',
      occupation: '',
      category: '',
      land_size: 0,
    }
  })

  // Auto-fill from sessionStorage if document was uploaded
  useEffect(() => {
    const stored = sessionStorage.getItem('autofill_form')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        if (parsed.name) setValue('name', parsed.name)
        if (parsed.dob) {
          const parts = parsed.dob.split('/')
          if (parts.length === 3) setValue('dob', `${parts[2]}-${parts[1]}-${parts[0]}`)
          else setValue('dob', parsed.dob)
        }
        if (parsed.income) setValue('income', parsed.income)
        if (parsed.state) setValue('state', parsed.state)
        setAutoFilled(true)
      } catch {
        /* ignore */
      }
    }
  }, [setValue])

  const onSubmit = async (data: EligibilityFormValues) => {
    setLoading(true)
    setFormError('')

    const dobParts = data.dob.split('-')
    const age = new Date().getFullYear() - parseInt(dobParts[0])

    const payload: EvaluationRequest = {
      name: data.name,
      age,
      income: data.income,
      state: data.state,
      occupation: data.occupation.toLowerCase(),
      category: data.category,
      land_size: data.land_size,
    }

    try {
      const results = await evaluateEligibility(payload)
      navigate('/results', { state: { results, profile: payload } })
    } catch (err: unknown) {
      const msg = (err as any)?.response?.data?.detail
      setFormError(msg || 'Could not connect to the eligibility engine. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4 py-10">
      <div className="bg-white rounded-2xl shadow-md w-full max-w-xl p-8">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-xl font-bold text-gray-900">Scheme Eligibility Checker</h1>
          <p className="text-sm text-gray-500 mt-1">
            Fill the form below to determine your eligibility for government<br />
            schemes and services.
          </p>
        </div>

        {autoFilled && (
          <div className="bg-blue-50 border border-blue-200 text-blue-800 text-sm rounded-lg px-4 py-2 mb-4">
            ✅ Form auto-filled from your uploaded document. Please review and update if needed.
          </div>
        )}

        {formError && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2 mb-2">
            {formError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Row 1: Name + DOB */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="field-label">Full Name</label>
              <input
                type="text"
                {...register('name')}
                placeholder="Your full name"
                className={`field-input ${errors.name ? 'border-red-500 focus:ring-red-500' : ''}`}
              />
              {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name.message}</p>}
            </div>
            <div>
              <label className="field-label">Date of Birth</label>
              <input
                type="date"
                {...register('dob')}
                className={`field-input w-full ${errors.dob ? 'border-red-500 focus:ring-red-500' : ''}`}
              />
              {errors.dob && <p className="text-xs text-red-500 mt-1">{errors.dob.message}</p>}
            </div>
          </div>

          {/* Row 2: Income + State */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="field-label">Annual Income (INR)</label>
              <input
                type="number"
                {...register('income')}
                placeholder="e.g. 250000"
                className={`field-input ${errors.income ? 'border-red-500 focus:ring-red-500' : ''}`}
              />
              {errors.income && <p className="text-xs text-red-500 mt-1">{errors.income.message}</p>}
            </div>
            <div>
              <label className="field-label">State/UT</label>
              <select {...register('state')} className={`field-input ${errors.state ? 'border-red-500 focus:ring-red-500' : ''}`}>
                <option value="">Select State</option>
                {STATES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
              {errors.state && <p className="text-xs text-red-500 mt-1">{errors.state.message}</p>}
            </div>
          </div>

          {/* Row 3: Occupation + Category */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="field-label">Occupation</label>
              <select {...register('occupation')} className={`field-input ${errors.occupation ? 'border-red-500 focus:ring-red-500' : ''}`}>
                <option value="">Select Occupation</option>
                {OCCUPATIONS.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
              {errors.occupation && <p className="text-xs text-red-500 mt-1">{errors.occupation.message}</p>}
            </div>
            <div>
              <label className="field-label">Category</label>
              <select {...register('category')} className={`field-input ${errors.category ? 'border-red-500 focus:ring-red-500' : ''}`}>
                <option value="">Select Category</option>
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
              {errors.category && <p className="text-xs text-red-500 mt-1">{errors.category.message}</p>}
            </div>
          </div>

          {/* Row 4: Land Size */}
          <div>
            <label className="field-label">Total Land Size (Acres)</label>
            <input
              type="number"
              {...register('land_size')}
              placeholder="0"
              step="0.1"
              min="0"
              className={`field-input ${errors.land_size ? 'border-red-500 focus:ring-red-500' : ''}`}
            />
            {errors.land_size && <p className="text-xs text-red-500 mt-1">{errors.land_size.message}</p>}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold flex justify-center items-center py-3 rounded-lg transition mt-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Checking Eligibility...
              </>
            ) : 'Check Eligibility'}
          </button>
        </form>
      </div>
    </div>
  )
}
