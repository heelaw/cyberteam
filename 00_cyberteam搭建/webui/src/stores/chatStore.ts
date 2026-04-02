/**
 * Chat Store — Zustand store with SSE streaming support
 * 集成本地 Claude Code CLI 作为 AI 引擎
 */
import { create } from 'zustand'
import { api } from '../api/client'

export interface Message {
  id: string
  conversation_id: string
  sender_type: 'user' | 'agent' | 'assistant' | 'system'
  sender_id: string
  content: string
  metadata?: {
    agent_name?: string
    tools_used?: string[]
    tokens_used?: number
    thinking_mode?: string
    model_used?: string
    status?: 'streaming' | 'completed' | 'error'
  }
  created_at: string
}

export interface Conversation {
  id: string
  title: string
  agent_id: string | null
  status: 'active' | 'completed' | 'archived'
  created_at: string
  updated_at: string
}

interface ChatState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]
  isLoading: boolean
  streamingContent: string

  createConversation: (agentId?: string) => Promise<void>
  loadConversations: () => Promise<void>
  loadMessages: (convId: string) => Promise<void>
  sendMessage: (content: string) => Promise<void>
  sendMessageStream: (content: string, agentName?: string) => Promise<void>
  deleteConversation: (id: string) => Promise<void>
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  isLoading: false,
  streamingContent: '',

  createConversation: async (agentName?: string) => {
    set({ isLoading: true })
    try {
      const conversation = await api.createConversation(agentName ? { agent_name: agentName } : {}) as Conversation
      set(state => ({
        conversations: [conversation, ...state.conversations],
        currentConversation: conversation,
        messages: []
      }))
    } finally {
      set({ isLoading: false })
    }
  },

  loadConversations: async () => {
    set({ isLoading: true })
    try {
      const data = await api.getConversations() as Conversation[]
      set({ conversations: data })
    } finally {
      set({ isLoading: false })
    }
  },

  loadMessages: async (convId: string) => {
    set({ isLoading: true })
    try {
      const data = await api.getMessages(convId) as Message[]
      set({ messages: data })
      const conversation = get().conversations.find(c => c.id === convId)
      if (conversation) {
        set({ currentConversation: conversation })
      }
    } finally {
      set({ isLoading: false })
    }
  },

  sendMessage: async (content: string) => {
    const { currentConversation, messages } = get()
    if (!currentConversation) return

    // 1. 添加用户消息到 UI（乐观更新）
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: currentConversation.id,
      sender_type: 'user',
      sender_id: 'current-user',
      content,
      created_at: new Date().toISOString()
    }
    set({ messages: [...messages, userMessage], isLoading: true })

    try {
      // 2. POST 到后端，获取 AI 回复（非流式）
      const response = await api.sendMessage(currentConversation.id, { content }) as {
        id: string
        content: string
        thinking_mode?: string
        tokens_used?: number
        model_used?: string
        created_at: string
      }

      // 3. 添加 AI 回复到 UI
      const aiMessage: Message = {
        id: response.id,
        conversation_id: currentConversation.id,
        sender_type: 'assistant',
        sender_id: 'cyberteam',
        content: response.content,
        metadata: {
          thinking_mode: response.thinking_mode,
          tokens_used: response.tokens_used,
          model_used: response.model_used,
        },
        created_at: response.created_at,
      }
      set(state => ({
        messages: [...state.messages, aiMessage],
        isLoading: false
      }))
    } catch (e) {
      set({ isLoading: false })
      console.error('Send message failed:', e)
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        conversation_id: currentConversation.id,
        sender_type: 'system',
        sender_id: 'system',
        content: '消息发送失败，请稍后重试。',
        metadata: { status: 'error' },
        created_at: new Date().toISOString()
      }
      set(state => ({ messages: [...state.messages, errorMessage] }))
    }
  },

  sendMessageStream: async (content: string, agentName?: string) => {
    const { currentConversation, messages } = get()
    if (!currentConversation) return

    // 如果选了特定 Agent，创建带该 Agent 的新对话
    if (agentName && !currentConversation.agent_id) {
      const conversation = await api.createConversation({ agent_name: agentName, title: content.slice(0, 20) }) as Conversation
      set(state => ({
        conversations: [conversation, ...state.conversations],
        currentConversation: conversation,
      }))
      // 用新conversation重试
      return get().sendMessageStream(content, agentName)
    }

    // 1. 添加用户消息到 UI（乐观更新）
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: currentConversation.id,
      sender_type: 'user',
      sender_id: 'current-user',
      content: agentName ? `[@agent:${agentName}] ${content}` : content,
      metadata: agentName ? { agent_name: agentName } : undefined,
      created_at: new Date().toISOString()
    }

    // 2. 创建一个流式 AI 消息占位符
    const streamingMsgId = `stream-${Date.now()}`
    const streamingMessage: Message = {
      id: streamingMsgId,
      conversation_id: currentConversation.id,
      sender_type: 'assistant',
      sender_id: agentName || 'cyberteam',
      content: '',
      metadata: { status: 'streaming', agent_name: agentName },
      created_at: new Date().toISOString()
    }

    set({
      messages: [...messages, userMessage, streamingMessage],
      isLoading: true,
      streamingContent: ''
    })

    try {
      // 3. 通过 SSE 流式请求，携带 agent_id
      let authToken: string | null = null
      try {
        const persisted = localStorage.getItem('cyberteam-auth')
        if (persisted) {
          const parsed = JSON.parse(persisted)
          authToken = parsed?.state?.token || null
        }
      } catch { /* ignore */ }

      const response = await fetch(`/api/chat/${currentConversation.id}/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
        },
        body: JSON.stringify({ content, agent_name: agentName }),
      })

      if (!response.ok) {
        throw new Error(`Stream request failed: ${response.status}`)
      }

      // 4. 消费 SSE 流
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let accumulated = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const jsonStr = line.slice(6).trim()
          if (!jsonStr) continue

          try {
            const evt = JSON.parse(jsonStr)

            if (evt.type === 'text') {
              // 流式文本增量
              accumulated += evt.data
              set({ streamingContent: accumulated })
              // 更新占位消息的内容
              set(state => ({
                messages: state.messages.map(m =>
                  m.id === streamingMsgId
                    ? { ...m, content: accumulated }
                    : m
                )
              }))
            } else if (evt.type === 'status') {
              // 状态事件（模型信息、会话信息等）
              const model = evt.model
              if (model) {
                set(state => ({
                  messages: state.messages.map(m =>
                    m.id === streamingMsgId
                      ? { ...m, metadata: { ...m.metadata, model_used: model } }
                      : m
                  )
                }))
              }
            } else if (evt.type === 'result') {
              // 最终结果
              const usage = evt.usage
              if (usage) {
                set(state => ({
                  messages: state.messages.map(m =>
                    m.id === streamingMsgId
                      ? {
                          ...m,
                          metadata: {
                            ...m.metadata,
                            status: 'completed' as const,
                            tokens_used: usage.output_tokens,
                          }
                        }
                      : m
                  )
                }))
              }
            } else if (evt.type === 'error') {
              const errorMsg = typeof evt.data === 'string' ? evt.data : (evt.data?.userMessage || '未知错误')
              set(state => ({
                messages: state.messages.map(m =>
                  m.id === streamingMsgId
                    ? { ...m, content: accumulated + `\n\n❌ 错误: ${errorMsg}`, metadata: { status: 'error' as const } }
                    : m
                )
              }))
            } else if (evt.type === 'done') {
              // 流结束
              set(state => ({
                messages: state.messages.map(m =>
                  m.id === streamingMsgId
                    ? { ...m, metadata: { ...m.metadata, status: 'completed' as const } }
                    : m
                ),
                isLoading: false
              }))
            }
          } catch {
            // 忽略解析错误
          }
        }
      }

      // 如果流没有发送 done 事件，确保状态更新
      set(state => ({
        messages: state.messages.map(m =>
          m.id === streamingMsgId
            ? { ...m, metadata: { ...m.metadata, status: 'completed' as const } }
            : m
        ),
        isLoading: false
      }))

    } catch (e) {
      console.error('Stream message failed:', e)
      set(state => ({
        messages: state.messages.map(m =>
          m.id === streamingMsgId
            ? { ...m, content: `消息发送失败: ${e}`, metadata: { status: 'error' as const } }
            : m
        ),
        isLoading: false
      }))
    }
  },

  deleteConversation: async (id: string) => {
    await api.deleteConversation(id)
    set(state => ({
      conversations: state.conversations.filter(c => c.id !== id),
      currentConversation: state.currentConversation?.id === id ? null : state.currentConversation,
      messages: state.currentConversation?.id === id ? [] : state.messages
    }))
  }
}))
