// 聊天 API
import { request } from '@/apis/clients/request'
import type { Message, Conversation } from '@/types'

export interface SendMessageRequest {
  message: string
  conversation_id?: string
}

export interface ChatResponse {
  conversation_id: string
  message: Message
}

// 对话相关
export async function fetchConversations(): Promise<Conversation[]> {
  return request.get<Conversation[]>('/api/chat/conversations')
}

export async function createConversation(title: string): Promise<Conversation> {
  return request.post<Conversation>('/api/chat/conversations', { title })
}

export async function deleteConversation(id: string): Promise<void> {
  return request.delete(`/api/chat/conversations/${id}`)
}

// 消息相关
export async function fetchMessages(conversationId: string): Promise<Message[]> {
  return request.get<Message[]>(`/api/chat/conversations/${conversationId}/messages`)
}

export async function sendMessage(
  conversationId: string,
  message: string
): Promise<ChatResponse> {
  return request.post<ChatResponse>(
    `/api/chat/conversations/${conversationId}/messages`,
    { message }
  )
}

// 流式响应
export async function* sendMessageStream(
  conversationId: string,
  message: string
): AsyncGenerator<string> {
  const response = await fetch(
    `${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/api/chat/conversations/${conversationId}/messages/stream`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    }
  )

  if (!response.ok) {
    throw new Error('Failed to send message')
  }

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()

  if (!reader) return

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const text = decoder.decode(value)
      yield text
    }
  } finally {
    reader.releaseLock()
  }
}
