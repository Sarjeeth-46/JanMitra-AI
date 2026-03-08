import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
    name: string
    email: string
    phone: string
}

interface AuthContextType {
    isLoggedIn: boolean
    user: User | null
    login: (user: User, token: string) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used within AuthProvider')
    return ctx
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null)

    // Rehydrate from localStorage on mount
    useEffect(() => {
        const stored = localStorage.getItem('jm_user')
        if (stored) {
            try { setUser(JSON.parse(stored)) } catch { /* ignore */ }
        }
    }, [])

    const login = (userData: User, token: string) => {
        localStorage.setItem('access_token', token)
        localStorage.setItem('jm_user', JSON.stringify(userData))
        setUser(userData)
    }

    const logout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('jm_user')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ isLoggedIn: !!user, user, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}
