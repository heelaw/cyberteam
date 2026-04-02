import React, { useState, useRef, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Send, Bot, User, Loader2 } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export default function Chat() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [, setSessionKey] = useState<string | null>(null)
  const [claudePath, setClaudePath] = useState<string>('/opt/homebrew/bin/claude')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 初始化 Claude Code 路径
  useEffect(() => {
    const initClaude = async () => {
      try {
        const path = await invoke<string>('get_claude_path')
        setClaudePath(path)
      } catch (e) {
        console.error('Failed to get claude path:', e)
      }
    }
    initClaude()
  }, [])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: Date.now(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // 调用 Tauri 后端启动 Claude Code 会话
      const result = await invoke<{ session_key: string; success: boolean; error?: string }>('spawn_session', {
        task: input.trim(),
        agentId: 'chat-assistant',
        runTimeoutSeconds: 60,
        model: null,
      })

      if (result.success) {
        setSessionKey(result.session_key)

        // 模拟 AI 响应（因为 Claude Code 是 CLI 工具）
        // 实际生产环境中，这里应该读取 Claude Code 的 stdout
        setTimeout(() => {
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `已收到您的消息，正在处理中...\n\nClaude Code 路径: ${claudePath}\n会话ID: ${result.session_key}\n\n这是一个本地运行的 AI 助手，可以调用 Claude Code CLI 进行真实的任务执行。`,
            timestamp: Date.now(),
          }
          setMessages(prev => [...prev, assistantMessage])
          setLoading(false)
        }, 1000)
      } else {
        throw new Error(result.error || 'Failed to start session')
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `错误: ${error instanceof Error ? error.message : String(error)}\n\n请检查 Claude Code 是否已安装，或在「设置」中配置正确的路径。`,
        timestamp: Date.now(),
      }
      setMessages(prev => [...prev, errorMessage])
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={styles.container}>
      {/* 消息列表 */}
      <div style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.empty}>
            <Bot size={48} style={{ color: '#58A6FF', marginBottom: 16, opacity: 0.5 }} />
            <p style={{ color: '#8B949E', fontSize: 14 }}>
              开始新对话，Claude Code 已就绪
            </p>
            <p style={{ color: '#6E7681', fontSize: 12, marginTop: 8 }}>
              路径: {claudePath}
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              ...styles.message,
              ...(msg.role === 'user' ? styles.userMessage : styles.assistantMessage),
            }}
          >
            <div style={styles.messageAvatar}>
              {msg.role === 'user' ? (
                <User size={16} style={{ color: '#58A6FF' }} />
              ) : (
                <Bot size={16} style={{ color: '#7EE787' }} />
              )}
            </div>
            <div style={styles.messageContent}>
              <pre style={styles.messageText}>{msg.content}</pre>
            </div>
          </div>
        ))}

        {loading && (
          <div style={styles.message}>
            <div style={styles.messageAvatar}>
              <Bot size={16} style={{ color: '#7EE787' }} />
            </div>
            <div style={styles.messageContent}>
              <div style={styles.loadingDots}>
                <span style={{ ...styles.dot, animationDelay: '0s' }}>●</span>
                <span style={{ ...styles.dot, animationDelay: '0.2s' }}>●</span>
                <span style={{ ...styles.dot, animationDelay: '0.4s' }}>●</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入区 */}
      <div style={styles.inputArea}>
        <div style={styles.inputContainer}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息，Enter 发送..."
            style={styles.textarea}
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            style={{
              ...styles.sendButton,
              ...(input.trim() && !loading ? styles.sendButtonActive : {}),
            }}
          >
            {loading ? (
              <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
            ) : (
              <Send size={18} />
            )}
          </button>
        </div>
        <p style={styles.hint}>
          Claude Code CLI · {claudePath}
        </p>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes bounce {
          0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    backgroundColor: '#0D1117',
  },
  messages: {
    flex: 1,
    overflow: 'auto',
    padding: '20px',
  },
  empty: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
  },
  message: {
    display: 'flex',
    gap: 12,
    marginBottom: 16,
    maxWidth: '800px',
    margin: '0 auto 16px',
  },
  userMessage: {
    flexDirection: 'row-reverse',
  },
  assistantMessage: {
    flexDirection: 'row',
  },
  messageAvatar: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    backgroundColor: '#161B22',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  messageContent: {
    flex: 1,
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: '10px 14px',
    border: '1px solid #30363D',
  },
  messageText: {
    margin: 0,
    fontSize: 14,
    lineHeight: 1.6,
    color: '#E6EDF3',
    whiteSpace: 'pre-wrap',
    fontFamily: 'inherit',
  },
  loadingDots: {
    display: 'flex',
    gap: 4,
    padding: '4px 0',
  },
  dot: {
    color: '#58A6FF',
    fontSize: 12,
    animation: 'bounce 1s infinite',
  },
  inputArea: {
    padding: '16px 20px',
    borderTop: '1px solid #30363D',
    backgroundColor: '#161B22',
  },
  inputContainer: {
    display: 'flex',
    gap: 12,
    alignItems: 'flex-end',
    maxWidth: '800px',
    margin: '0 auto',
  },
  textarea: {
    flex: 1,
    backgroundColor: '#0D1117',
    border: '1px solid #30363D',
    borderRadius: 12,
    padding: '12px 16px',
    fontSize: 14,
    color: '#E6EDF3',
    resize: 'none',
    outline: 'none',
    fontFamily: 'inherit',
    minHeight: 44,
    maxHeight: 120,
    overflow: 'auto',
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 12,
    border: 'none',
    backgroundColor: '#30363D',
    color: '#8B949E',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'all 0.15s ease',
  },
  sendButtonActive: {
    backgroundColor: '#238636',
    color: '#FFFFFF',
  },
  hint: {
    textAlign: 'center',
    fontSize: 11,
    color: '#6E7681',
    marginTop: 8,
    maxWidth: '800px',
    margin: '8px auto 0',
  },
}
