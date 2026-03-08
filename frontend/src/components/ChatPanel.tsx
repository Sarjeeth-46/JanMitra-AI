import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Bot, User } from 'lucide-react'
import { useApp } from '../context/AppContext'
import api from '../services/api'
import toast from 'react-hot-toast'

const ChatPanel = () => {
  const { chatHistory, addChatMessage, updateLastMessage } = useApp()
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      role: 'user' as const,
      content: input.trim(),
      timestamp: new Date(),
    }

    addChatMessage(userMessage)
    setInput('')
    setIsLoading(true)

    // Add empty assistant message that will be populated by the stream
    addChatMessage({
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    })

    try {
      let fullResponse = ''
      await (api as unknown as { streamChatMessage: (msg: string, hist: unknown[], cb: (c: string) => void) => Promise<void> }).streamChatMessage(userMessage.content, chatHistory, (chunk: string) => {
        fullResponse += chunk
        updateLastMessage(fullResponse)
      })
    } catch (error) {
      console.error('Chat error:', error)
      toast.error('Failed to send message. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {chatHistory.length === 0 ? (
          <div className="text-center mt-12 space-y-4">
            <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-saffron-500 rounded-3xl flex items-center justify-center mx-auto shadow-lg">
              <Bot className="w-10 h-10 text-white" />
            </div>
            <div>
              <p className="text-base font-semibold text-gray-700 dark:text-gray-300">Start a conversation</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                Ask about schemes, eligibility, or documents
              </p>
            </div>
          </div>
        ) : (
          chatHistory.map((message, index) => (
            <div
              key={index}
              className={`flex items-start space-x-3 ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
            >
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md ${message.role === 'user'
                  ? 'bg-gradient-to-br from-primary-600 to-primary-700'
                  : 'bg-gradient-to-br from-saffron-500 to-saffron-600'
                  }`}
              >
                {message.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>
              <div className="flex-1 max-w-[75%]">
                <div
                  className={`rounded-2xl px-5 py-3 shadow-md ${message.role === 'user'
                    ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white'
                    : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-600'
                    }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                </div>
                <p className={`text-xs text-gray-500 dark:text-gray-400 mt-2 px-2 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-saffron-500 to-saffron-600 rounded-xl flex items-center justify-center shadow-md">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white dark:bg-gray-700 rounded-2xl px-5 py-3 shadow-md border border-gray-200 dark:border-gray-600">
              <Loader2 className="w-5 h-5 animate-spin text-gray-600 dark:text-gray-400" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200/50 dark:border-gray-700/50 p-6 bg-gradient-to-t from-gray-50/50 to-transparent dark:from-gray-900/50">
        <div className="flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 input-field"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="btn-primary px-5 flex items-center justify-center"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatPanel
