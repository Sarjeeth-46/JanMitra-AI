import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, ArrowRight } from 'lucide-react'
import { sendOTP } from '../services/api'
import toast from 'react-hot-toast'

export default function SignupPage() {
    const navigate = useNavigate()
    const [form, setForm] = useState({ name: '', mobile: '' })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        const cleanMobile = form.mobile.trim()
        if (cleanMobile.length < 10) {
            setError('Please enter a valid 10-digit mobile number')
            return
        }

        setLoading(true)
        setError('')
        try {
            await sendOTP(cleanMobile)
            toast.success('OTP sent! Verify to complete signup.')
            // Pass name in state so verify-otp can use it if needed (or just demo)
            navigate('/verify-otp', { state: { mobile: cleanMobile, name: form.name } })
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
                    <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-green-100">
                        <UserPlus size={36} className="text-green-600" />
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900">Create Citizen Account</h1>
                    <p className="text-sm text-gray-500 mt-2">Sign up using your mobile number for secure access</p>
                </div>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-500 text-red-700 text-sm p-4 rounded mb-6">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
                        <input
                            type="text"
                            value={form.name}
                            onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))}
                            placeholder="Rajesh Kumar"
                            className="field-input"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Mobile Number</label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                                <span className="font-medium">+91</span>
                            </div>
                            <input
                                type="tel"
                                maxLength={10}
                                value={form.mobile}
                                onChange={(e) => setForm(p => ({ ...p, mobile: e.target.value.replace(/\D/g, '') }))}
                                placeholder="9876543210"
                                className="block w-full pl-14 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-lg tracking-wider"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading || form.mobile.length < 10 || !form.name.trim()}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-4 rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 mt-4"
                    >
                        {loading ? 'Sending OTP...' : (
                            <>
                                Create Account
                                <ArrowRight size={20} />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-8 pt-8 border-t border-gray-100 text-center">
                    <p className="text-sm text-gray-500">
                        Already have an account?{' '}
                        <Link to="/login" className="text-blue-600 font-bold hover:text-blue-800 transition">
                            Login instead
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}
