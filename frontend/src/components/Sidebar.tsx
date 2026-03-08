import { NavLink } from 'react-router-dom'
import { Home, Sparkles, FileText, List, Mic, LogOut, X } from 'lucide-react'
import { useTranslation } from 'react-i18next'

interface SidebarProps {
    isOpen?: boolean;
    setIsOpen?: (isOpen: boolean) => void;
}

const Sidebar = ({ isOpen, setIsOpen }: SidebarProps) => {
    const { t } = useTranslation()

    const navItems = [
        { name: t('home'), path: '/', icon: Home },
        { name: t('eligibility_check'), path: '/eligibility', icon: Sparkles },
        { name: t('all_schemes'), path: '/results', icon: List },
        { name: t('voice_assistant'), path: '/voice-assistant', icon: Mic },
        { name: t('documents'), path: '/upload-document', icon: FileText },
    ]

    return (
        <>
            {/* Mobile overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity"
                    onClick={() => setIsOpen && setIsOpen(false)}
                />
            )}

            <aside className={`w-64 fixed left-0 top-0 h-screen bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col pt-20 z-50 transition-transform duration-300 transform ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
                {/* Mobile close button */}
                {isOpen && (
                    <button
                        onClick={() => setIsOpen && setIsOpen(false)}
                        className="lg:hidden absolute top-4 right-4 p-2 text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}

                <div className="flex-1 px-4 space-y-2 mt-4 overflow-y-auto">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.name}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 font-semibold ${isActive
                                    ? 'bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 shadow-sm'
                                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-blue-600 dark:hover:text-blue-400'
                                }`
                            }
                        >
                            <item.icon className="w-5 h-5" />
                            <span>{item.name}</span>
                        </NavLink>
                    ))}
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-gray-800">
                    <button className="flex items-center space-x-3 w-full px-4 py-3 rounded-xl transition-all duration-200 font-semibold text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400">
                        <LogOut className="w-5 h-5" />
                        <span>{t('logout')}</span>
                    </button>
                </div>
            </aside>
        </>
    )
}

export default Sidebar
