import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogOut, User, Phone, Mail, FileText, CheckSquare, Clock, Edit, ShieldCheck } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getProfile, getUserApplications, type UserApplication } from '../services/api'
import toast from 'react-hot-toast'

export default function ProfilePage() {
    const { user, login, logout } = useAuth()
    const navigate = useNavigate()
    const [applications, setApplications] = useState<UserApplication[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            if (!user) return
            try {
                const [prof, apps] = await Promise.all([
                    getProfile(),
                    getUserApplications()
                ])
                // Refresh context user data if changed
                login(prof, localStorage.getItem('access_token') || '')
                setApplications(apps)
            } catch (err) {
                console.error("Profile fetch error:", err)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [])

    const handleLogout = () => {
        logout()
        toast.success("Logged out successfully")
        navigate('/')
    }

    if (!user) {
        return (
            <div className="max-w-lg mx-auto px-6 py-20 text-center">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <User size={36} className="text-gray-400" />
                </div>
                <h2 className="text-xl font-bold text-gray-800 mb-2">You're not logged in</h2>
                <p className="text-gray-500 text-sm mb-6">Please log in to view your profile and saved applications.</p>
                <Link to="/login" className="btn-primary">Login</Link>
            </div>
        )
    }

    const initials = user.name.startsWith('User ')
        ? user.name.split(' ')[1].slice(-2)
        : user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)

    return (
        <div className="max-w-4xl mx-auto px-6 py-10">
            {/* Header */}
            <div className="card mb-6 flex items-center justify-between flex-wrap gap-4 border-l-4 border-blue-600">
                <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0 shadow-lg">
                        {initials}
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">{user.name}</h1>
                        <p className="text-sm text-gray-500 flex items-center gap-1.5">
                            <ShieldCheck size={14} className="text-green-500" /> Verified Citizen Account
                        </p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <button className="flex items-center gap-2 border border-gray-300 text-gray-700 hover:border-blue-400 hover:text-blue-600 font-medium px-4 py-2 rounded-lg text-sm transition">
                        <Edit size={15} /> Edit Profile
                    </button>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 bg-red-50 text-red-600 hover:bg-red-100 font-medium px-4 py-2 rounded-lg text-sm transition"
                    >
                        <LogOut size={15} /> Logout
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* User Info */}
                <div className="card h-fit">
                    <h2 className="text-sm font-semibold text-gray-700 mb-4 px-1">Account Details</h2>
                    <div className="flex flex-col gap-4">
                        {[
                            { icon: User, label: 'Full Name', value: user.name },
                            { icon: Mail, label: 'Email Address', value: user.email.includes('@janmitra.ai') && user.phone ? 'Not set' : user.email },
                            { icon: Phone, label: 'Phone Number', value: user.phone || 'Not provided' },
                        ].map(({ icon: Icon, label, value }) => (
                            <div key={label} className="bg-gray-50 p-3 rounded-lg">
                                <p className="text-[10px] text-gray-400 uppercase tracking-wider mb-1 flex items-center gap-2">
                                    <Icon size={12} className="text-blue-500" /> {label}
                                </p>
                                <p className="text-sm font-medium text-gray-800 break-words">{value}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Application History */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="card">
                        <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                            <FileText size={15} className="text-blue-500" /> Application History
                        </h2>

                        {loading ? (
                            <div className="py-10 text-center text-gray-400 text-sm">Loading applications...</div>
                        ) : applications.length > 0 ? (
                            <div className="flex flex-col gap-3">
                                {applications.map((app) => (
                                    <div key={app.application_id} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:border-blue-100 hover:bg-blue-50/30 transition group">
                                        <div className="flex items-start gap-3">
                                            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition">
                                                <FileText size={16} />
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">{app.scheme_name}</p>
                                                <p className="text-[10px] text-gray-400">ID: {app.application_id} • {app.submitted_date}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${app.status === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                                                }`}>
                                                {app.status}
                                            </span>
                                            <button
                                                onClick={() => navigate('/track')}
                                                className="text-gray-300 hover:text-blue-600 transition"
                                            >
                                                <Clock size={16} />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-10 text-gray-400">
                                <FileText size={32} className="mx-auto mb-2 opacity-20" />
                                <p className="text-sm">No applications submitted yet.</p>
                                <Link to="/eligibility" className="text-blue-600 text-sm font-medium hover:underline mt-2 block">
                                    Check Eligibility Now →
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Eligibility Stats & Quick Links */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <div className="card bg-gradient-to-br from-blue-600 to-blue-700 text-white border-0">
                            <h2 className="text-sm font-semibold mb-4 flex items-center gap-2 text-blue-100">
                                <CheckSquare size={15} /> Quick Action
                            </h2>
                            <p className="text-xs text-blue-100 mb-4 leading-relaxed">
                                See which new government schemes you qualify for based on your updated profile.
                            </p>
                            <Link to="/eligibility" className="bg-white text-blue-600 text-xs font-bold py-2 px-4 rounded-lg block text-center hover:bg-blue-50 transition shadow-md">
                                Re-verify Eligibility
                            </Link>
                        </div>

                        <div className="card">
                            <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                                <Clock size={15} className="text-blue-500" /> Voice Assistant
                            </h2>
                            <p className="text-xs text-gray-400 mb-4 leading-relaxed">
                                Ask questions about schemes or track your status using voice in your native language.
                            </p>
                            <Link to="/voice-assistant" className="border border-blue-600 text-blue-600 text-xs font-bold py-2 px-4 rounded-lg block text-center hover:bg-blue-50 transition">
                                Open Voice AI
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
