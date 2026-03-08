import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Eye, EyeOff } from 'lucide-react'
import { register as apiRegister } from '../services/api'

export default function SignupPage() {
    const navigate = useNavigate()
    const [form, setForm] = useState({ name: '', email: '', phone: '', password: '', confirm: '' })
    const [showPwd, setShowPwd] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
        setForm(prev => ({ ...prev, [key]: e.target.value }))

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (form.password !== form.confirm) {
            setError('Passwords do not match.')
            return
        }
        setLoading(true)
        setError('')
        try {
            await apiRegister({ name: form.name, email: form.email, phone: form.phone, password: form.password })
            navigate('/login', { state: { message: 'Account created! Please log in.' } })
        } catch (err: unknown) {
            const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
            setError(msg || 'Registration failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4 py-10">
            <div className="bg-white rounded-2xl shadow-md w-full max-w-md p-8">
                <div className="text-center mb-7">
                    <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                        <UserPlus size={26} className="text-green-600" />
                    </div>
                    <h1 className="text-xl font-bold text-gray-900">Create an Account</h1>
                    <p className="text-sm text-gray-500 mt-1">Join JanMitra AI to track your applications and schemes</p>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2 mb-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="field-label">Full Name</label>
                        <input type="text" value={form.name} onChange={set('name')} placeholder="Rajesh Kumar" className="field-input" required />
                    </div>
                    <div>
                        <label className="field-label">Email Address</label>
                        <input type="email" value={form.email} onChange={set('email')} placeholder="you@example.com" className="field-input" required />
                    </div>
                    <div>
                        <label className="field-label">Phone Number</label>
                        <input type="tel" value={form.phone} onChange={set('phone')} placeholder="10-digit mobile" className="field-input" pattern="[0-9]{10}" required />
                    </div>
                    <div>
                        <label className="field-label">Password</label>
                        <div className="relative">
                            <input
                                type={showPwd ? 'text' : 'password'}
                                value={form.password}
                                onChange={set('password')}
                                placeholder="Min. 8 characters"
                                className="field-input pr-10"
                                minLength={8}
                                required
                            />
                            <button type="button" onClick={() => setShowPwd(!showPwd)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>
                    <div>
                        <label className="field-label">Confirm Password</label>
                        <input type="password" value={form.confirm} onChange={set('confirm')} placeholder="Re-enter password" className="field-input" required />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-3 rounded-lg transition mt-2"
                    >
                        {loading ? 'Creating Account...' : 'Sign Up'}
                    </button>
                </form>

                <p className="text-center text-sm text-gray-500 mt-5">
                    Already have an account?{' '}
                    <Link to="/login" className="text-blue-600 font-medium hover:underline">Login</Link>
                </p>
            </div>
        </div>
    )
}
