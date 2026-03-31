import { useState, useRef, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { listen } from '@tauri-apps/api/event'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

interface ChatProps {
  claudePath: string
  apiKey: string
}

export default function Chat(_props: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'system',
      content: '欢迎使用 CyberTeam Desktop！请在设置页面配置 Claude Code CLI 路径和 API Key。',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessions, setSessions] = useState<{ id: string; name: string }[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadSessions()
    // Listen for Claude output
    const unlisten = listen<string>('claude-output', (event) => {
      const output = event.payload
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: output,
        timestamp: new Date()
      }])
      setIsLoading(false)
    })
    return () => {
      unlisten.then(fn => fn())
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadSessions = async () => {
    try {
      const result = await invoke<{ id: string; name: string }[]>('list_sessions')
      setSessions(result)
    } catch (e) {
      console.error('Failed to load sessions:', e)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const result = await invoke<string>('send_message', {
        message: userMessage.content,
        sessionId: currentSessionId
      })
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result,
        timestamp: new Date()
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `错误: ${String(e)}`,
        timestamp: new Date()
      }])
    }
    setIsLoading(false)
  }

  const createNewSession = async () => {
    try {
      const sessionId = await invoke<string>('create_session', { name: '新会话' })
      setCurrentSessionId(sessionId)
      setMessages([{
        id: '1',
        role: 'system',
        content: '新会话已创建，开始对话吧！',
        timestamp: new Date()
      }])
      loadSessions()
    } catch (e) {
      console.error('Failed to create session:', e)
    }
  }

  return (
    <div className="h-full flex">
      {/* Session sidebar */}
      <div className="w-48 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-3 border-b border-slate-700">
          <button
            onClick={createNewSession}
            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
          >
            + 新会话
          </button>
        </div>
        <div className="flex-1 overflow-auto p-2">
          {sessions.map(session => (
            <button
              key={session.id}
              onClick={() => setCurrentSessionId(session.id)}
              className={`w-full text-left px-3 py-2 rounded text-sm mb-1 transition-colors ${
                currentSessionId === session.id
                  ? 'bg-slate-700 text-white'
                  : 'text-slate-400 hover:bg-slate-700'
              }`}
            >
              {session.name}
            </button>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-auto p-6">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map(message => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.role === 'system'
                      ? 'bg-slate-700 text-slate-300 italic'
                      : 'bg-slate-800 text-white border border-slate-700'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <p className="text-xs opacity-60 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-800 text-white rounded-lg px-4 py-3 border border-slate-700">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                    <span>Claude 正在思考...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="p-4 border-t border-slate-700 bg-slate-800">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="输入消息..."
                className="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                发送
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
