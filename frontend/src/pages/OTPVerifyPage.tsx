import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ShieldCheck, ArrowRight, RefreshCcw } from 'lucide-react'
import { verifyOTP, sendOTP } from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function OTPVerifyPage() {
    const navigate = useNavigate()
    const location = useLocation()
    const { login } = useAuth()
    const mobile = location.state?.mobile || ''
    const name = location.state?.name || ''

    const [otp, setOtp] = useState('')
    const [loading, setLoading] = useState(false)
    const [timer, setTimer] = useState(30)
    const [error, setError] = useState('')

    useEffect(() => {
        if (!mobile) {
            navigate('/login')
            return
        }
        const interval = setInterval(() => {
            setTimer((prev) => (prev > 0 ? prev - 1 : 0))
        }, 1000)
        return () => clearInterval(interval)
    }, [mobile, navigate])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (otp.length < 6) {
            setError('Please enter the 6-digit OTP')
            return
        }

        setLoading(true)
        setError('')
        try {
            const res = await verifyOTP(mobile, otp, name)
            login(res.user, res.access_token)
            toast.success('Successfully authenticated!')
            navigate('/profile')
        } catch (err: unknown) {
            const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
            setError(msg || 'Invalid verification code. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    const handleResend = async () => {
        if (timer > 0) return
        try {
            await sendOTP(mobile)
            setTimer(30)
            toast.success('OTP resent successfully!')
        } catch (err) {
            toast.error('Failed to resend OTP')
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8 border border-gray-100">
                <div className="text-center mb-8">
                    <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-green-100">
                        <ShieldCheck size={40} className="text-green-600" />
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900">Verification Code</h1>
                    <p className="text-sm text-gray-500 mt-2">
                        Sent to <span className="font-bold text-gray-700">+91 {mobile}</span>
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-500 text-red-700 text-sm p-4 rounded mb-6">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <input
                            type="tel"
                            maxLength={6}
                            value={otp}
                            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                            placeholder="· · · · · ·"
                            className="block w-full text-center py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none text-3xl font-bold tracking-[0.5em] placeholder:text-gray-200"
                            required
                        />
                        <p className="text-[10px] text-center text-blue-500 mt-2 font-semibold uppercase tracking-wider">
                            Demo Mode: Use code 123456 if SMS not received
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={loading || otp.length < 6}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-4 rounded-xl transition-all shadow-lg hover:shadow-xl active:scale-[0.98] flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Verifying...
                            </>
                        ) : (
                            <>
                                Verify & Continue
                                <ArrowRight size={20} />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-8 text-center bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">
                        Didn't receive the code?
                    </p>
                    <button
                        onClick={handleResend}
                        disabled={timer > 0}
                        className={`mt-2 flex items-center justify-center gap-2 mx-auto font-bold text-sm transition ${timer > 0 ? 'text-gray-400 cursor-not-allowed' : 'text-blue-600 hover:text-blue-800'
                            }`}
                    >
                        <RefreshCcw size={16} className={timer > 0 ? '' : 'animate-spin-slow'} />
                        {timer > 0 ? `Resend in ${timer}s` : 'Resend OTP Now'}
                    </button>
                </div>

                <div className="mt-6 text-center">
                    <button
                        onClick={() => navigate('/login')}
                        className="text-xs text-blue-500 hover:underline font-medium"
                    >
                        Change mobile number
                    </button>
                </div>
            </div>
        </div>
    )
}
