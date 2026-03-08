import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Phone, ArrowRight } from 'lucide-react'
import { sendOTP } from '../services/api'
import toast from 'react-hot-toast'

export default function LoginPage() {
    const navigate = useNavigate()
    const [mobile, setMobile] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        const cleanMobile = mobile.trim()
        if (cleanMobile.length < 10) {
            setError('Please enter a valid 10-digit mobile number')
            return
        }

        setLoading(true)
        setError('')
        try {
            await sendOTP(cleanMobile)
            toast.success('OTP sent successfully!')
            navigate('/verify-otp', { state: { mobile: cleanMobile } })
        } catch (err: unknown) {
            const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
            setError(msg || 'Failed to send OTP. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8 border border-gray-100">
                <div className="text-center mb-10">
                    <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-blue-100">
                        <Phone size={36} className="text-blue-600" />
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900">Sign In with Mobile</h1>
                    <p className="text-sm text-gray-500 mt-2 italic px-4">
                        We'll send a 6-digit OTP for secure access to JanMitra AI
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-500 text-red-700 text-sm p-4 rounded mb-6">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Mobile Number</label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none group-focus-within:text-blue-600 transition-colors">
                                <span className="text-gray-500 font-medium">+91</span>
                            </div>
                            <input
                                type="tel"
                                maxLength={10}
                                value={mobile}
                                onChange={(e) => setMobile(e.target.value.replace(/\D/g, ''))}
                                placeholder="9876543210"
                                className="block w-full pl-14 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none text-lg tracking-wider"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading || mobile.length < 10}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-4 rounded-xl transition-all shadow-lg hover:shadow-xl active:scale-[0.98] flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Sending OTP...
                            </>
                        ) : (
                            <>
                                Get Verification Code
                                <ArrowRight size={20} />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-8 pt-8 border-t border-gray-100 text-center">
                    <p className="text-sm text-gray-500">
                        Don't have an account?{' '}
                        <Link to="/signup" className="text-blue-600 font-bold hover:text-blue-800 transition">
                            Sign Up Now
                        </Link>
                    </p>
                </div>

                <div className="mt-6 text-center">
                    <p className="text-[10px] text-gray-400 uppercase tracking-widest font-bold">Hackathon Demo Mode</p>
                    <p className="text-[10px] text-gray-400 mt-1">Check backend console logs for OTP</p>
                </div>
            </div>
        </div>
    )
}
