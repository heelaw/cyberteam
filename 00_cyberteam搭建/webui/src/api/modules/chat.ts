import { api } from '../client'

export interface Conversation {
  id: string
  title: string
  agent_id: string | null
  status: 'active' | 'completed' | 'archived'
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  sender_type: 'user' | 'agent' | 'system'
  sender_id: string
  content: string
  metadata?: Record<string, unknown>
  created_at: string
}

export const chatApi = {
  listConversations: () => api.get('/chat'),

  createConversation: (data: { agent_id?: string; title?: string }) =>
    api.post('/chat', data),

  getConversation: (id: string) => api.get(`/chat/${id}`),

  deleteConversation: (id: string) => api.delete(`/chat/${id}`),

  getMessages: (convId: string) => api.get(`/chat/${convId}/messages`),

  sendMessage: (convId: string, data: { content: string }) =>
    api.post(`/chat/${convId}/messages`, data)
}