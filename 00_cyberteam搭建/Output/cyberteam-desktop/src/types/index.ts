export type Page = 'chat' | 'settings' | 'skills' | 'agents'

export interface Session {
  id: string
  name: string
  created_at: string
  last_message: string | null
}

export interface Agent {
  id: string
  name: string
  role: string
  description: string
  status: 'idle' | 'running' | 'error'
  last_active: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}
