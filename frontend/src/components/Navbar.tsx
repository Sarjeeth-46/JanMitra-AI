import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Menu, X, Bell, ChevronDown, LogOut, User } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'

const languages = [
    { label: 'English', code: 'en' },
    { label: 'हिंदी (Hindi)', code: 'hi' },
    { label: 'தமிழ் (Tamil)', code: 'ta' },
    { label: 'తెలుగు (Telugu)', code: 'te' },
    { label: 'বাংলা (Bengali)', code: 'bn' },
    { label: 'मराठी (Marathi)', code: 'mr' },
    { label: 'ಕನ್ನಡ (Kannada)', code: 'kn' },
    { label: 'മലയാളം (Malayalam)', code: 'ml' },
]

export default function Navbar() {
    const { i18n, t } = useTranslation()
    const { isLoggedIn, user, logout } = useAuth()
    const location = useLocation()
    const navigate = useNavigate()
    const [mobileOpen, setMobileOpen] = useState(false)
    const [langOpen, setLangOpen] = useState(false)
    const [userMenuOpen, setUserMenuOpen] = useState(false)
    const [notifOpen, setNotifOpen] = useState(false)
    const [notifRead, setNotifRead] = useState(false)

    const notifications = [
        { id: 1, title: 'Eligibility check complete', body: 'You qualify for 3 government schemes.', time: '2 min ago', read: notifRead },
        { id: 2, title: 'Document uploaded', body: 'Your Aadhaar card was analysed successfully.', time: '1 hr ago', read: notifRead },
        { id: 3, title: 'New scheme available', body: 'PM-KISAN 2025 applications are now open.', time: '3 hrs ago', read: true },
    ]

    const navLinks = [
        { label: t('home'), href: '/' },
        { label: t('services'), href: '/services' },
        { label: t('track_status'), href: '/track' },
        { label: t('feedback'), href: '/feedback' },
        { label: t('faqs'), href: '/faqs' },
    ]

    const currentLang = languages.find(l => l.code === i18n.language) ?? languages[0]

    const changeLanguage = (code: string) => {
        i18n.changeLanguage(code)
        localStorage.setItem('language', code)       // persist for reloads
        localStorage.setItem('preferredLanguage', code) // used by i18n detector
        setLangOpen(false)
    }

    const handleLogout = () => {
        logout()
        setUserMenuOpen(false)
        navigate('/')
    }

    const initials = user?.name
        ? user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
        : '?'

    return (
        <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2">
                    <img src="/Logo.png" className="h-10 w-auto" alt="JanMitra AI Logo" />
                </Link>

                {/* Desktop Nav */}
                <nav className="hidden md:flex items-center gap-6">
                    {navLinks.map(link => (
                        <Link
                            key={link.href}
                            to={link.href}
                            className={`text-sm font-medium transition-colors ${location.pathname === link.href
                                ? 'text-blue-600 border-b-2 border-blue-600 pb-0.5'
                                : 'text-gray-600 hover:text-blue-600'
                                }`}
                        >
                            {link.label}
                        </Link>
                    ))}
                </nav>

                {/* Right side */}
                <div className="hidden md:flex items-center gap-3">
                    {/* Language switcher */}
                    <div className="relative">
                        <button
                            onClick={() => { setLangOpen(!langOpen); setUserMenuOpen(false) }}
                            className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600 font-medium border border-gray-200 rounded-lg px-3 py-1.5 transition"
                        >
                            {currentLang.label.split(' ')[0]} <ChevronDown size={14} />
                        </button>
                        {langOpen && (
                            <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
                                {languages.map(lang => (
                                    <button
                                        key={lang.code}
                                        onClick={() => changeLanguage(lang.code)}
                                        className={`block w-full text-left px-4 py-2 text-sm hover:bg-blue-50 hover:text-blue-600 ${i18n.language === lang.code ? 'text-blue-600 font-medium' : 'text-gray-700'}`}
                                    >
                                        {lang.label}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Notification bell */}
                    <div className="relative">
                        <button
                            onClick={() => { setNotifOpen(!notifOpen); setLangOpen(false); setUserMenuOpen(false) }}
                            className="relative p-2 text-gray-500 hover:text-blue-600 transition"
                        >
                            <Bell size={18} />
                            {!notifRead && (
                                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                            )}
                        </button>

                        {notifOpen && (
                            <div className="absolute right-0 mt-1 w-80 bg-white rounded-xl shadow-xl border border-gray-100 z-50 overflow-hidden">
                                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                                    <span className="text-sm font-semibold text-gray-800">Notifications</span>
                                    <button
                                        onClick={() => setNotifRead(true)}
                                        className="text-xs text-blue-600 hover:underline"
                                    >
                                        Mark all read
                                    </button>
                                </div>
                                <div className="max-h-72 overflow-y-auto divide-y divide-gray-50">
                                    {notifications.map(n => (
                                        <div key={n.id} className={`px-4 py-3 hover:bg-gray-50 transition ${!n.read ? 'bg-blue-50/40' : ''}`}>
                                            <div className="flex items-start justify-between gap-2">
                                                <div>
                                                    <p className={`text-sm font-medium ${!n.read ? 'text-blue-800' : 'text-gray-800'}`}>{n.title}</p>
                                                    <p className="text-xs text-gray-500 mt-0.5">{n.body}</p>
                                                </div>
                                                {!n.read && <span className="w-2 h-2 bg-blue-500 rounded-full mt-1.5 flex-shrink-0" />}
                                            </div>
                                            <p className="text-[11px] text-gray-400 mt-1">{n.time}</p>
                                        </div>
                                    ))}
                                </div>
                                <div className="px-4 py-2 border-t border-gray-100 text-center">
                                    <button onClick={() => setNotifOpen(false)} className="text-xs text-blue-600 hover:underline">Close</button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Auth section */}
                    {isLoggedIn ? (
                        <div className="relative">
                            <button
                                onClick={() => { setUserMenuOpen(!userMenuOpen); setLangOpen(false) }}
                                className="flex items-center gap-2"
                            >
                                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                                    {initials}
                                </div>
                                <ChevronDown size={14} className="text-gray-500" />
                            </button>
                            {userMenuOpen && (
                                <div className="absolute right-0 mt-2 w-44 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
                                    <div className="px-4 py-2 border-b border-gray-100">
                                        <p className="text-sm font-semibold text-gray-800 truncate">{user?.name}</p>
                                        <p className="text-xs text-gray-500 truncate">{user?.phone || user?.email}</p>
                                    </div>
                                    <Link
                                        to="/profile"
                                        onClick={() => setUserMenuOpen(false)}
                                        className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                                    >
                                        <User size={14} /> My Profile
                                    </Link>
                                    <button
                                        onClick={handleLogout}
                                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                    >
                                        <LogOut size={14} /> Logout
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="flex items-center gap-2">
                            <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-blue-600 transition px-3 py-1.5 border border-gray-200 rounded-lg">
                                {t('login')}
                            </Link>
                            <Link to="/signup" className="text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 transition px-3 py-1.5 rounded-lg">
                                {t('signup')}
                            </Link>
                        </div>
                    )}
                </div>

                {/* Mobile menu button */}
                <button
                    className="md:hidden p-2 text-gray-500"
                    onClick={() => setMobileOpen(!mobileOpen)}
                >
                    {mobileOpen ? <X size={20} /> : <Menu size={20} />}
                </button>
            </div>

            {/* Mobile dropdown */}
            {mobileOpen && (
                <div className="md:hidden bg-white border-t border-gray-100 px-6 py-4 flex flex-col gap-3">
                    {navLinks.map(link => (
                        <Link
                            key={link.href}
                            to={link.href}
                            onClick={() => setMobileOpen(false)}
                            className="text-sm font-medium text-gray-700 hover:text-blue-600 transition"
                        >
                            {link.label}
                        </Link>
                    ))}
                    <hr className="border-gray-100" />
                    {isLoggedIn ? (
                        <>
                            <Link to="/profile" onClick={() => setMobileOpen(false)} className="text-sm font-medium text-gray-700 hover:text-blue-600">My Profile</Link>
                            <button onClick={() => { handleLogout(); setMobileOpen(false) }} className="text-sm text-left font-medium text-red-600">Logout</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" onClick={() => setMobileOpen(false)} className="text-sm font-medium text-gray-700 hover:text-blue-600">{t('login')}</Link>
                            <Link to="/signup" onClick={() => setMobileOpen(false)} className="text-sm font-medium text-blue-600">{t('signup')}</Link>
                        </>
                    )}
                </div>
            )}
        </header>
    )
}
