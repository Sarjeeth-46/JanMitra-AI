import { createContext, useContext, useState, ReactNode } from 'react'
import type { UserProfile, EvaluationResult, ChatMessage } from '../types'

interface AppContextType {
  userProfile: UserProfile | null
  setUserProfile: any
  evaluationResults: EvaluationResult[]
  setEvaluationResults: (results: EvaluationResult[]) => void
  chatHistory: ChatMessage[]
  addChatMessage: (message: ChatMessage) => void
  updateLastMessage: (content: string) => void
  clearChatHistory: () => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export const useApp = () => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider = ({ children }: AppProviderProps) => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResult[]>([])
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])

  const addChatMessage = (message: ChatMessage) => {
    setChatHistory((prev) => [...prev, message])
  }

  const updateLastMessage = (content: string) => {
    setChatHistory((prev) => {
      if (prev.length === 0) return prev;
      const newHistory = [...prev];
      newHistory[newHistory.length - 1].content = content;
      return newHistory;
    });
  }

  const clearChatHistory = () => {
    setChatHistory([])
  }

  return (
    <AppContext.Provider
      value={{
        userProfile,
        setUserProfile,
        evaluationResults,
        setEvaluationResults,
        chatHistory,
        addChatMessage,
        updateLastMessage,
        clearChatHistory,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}
