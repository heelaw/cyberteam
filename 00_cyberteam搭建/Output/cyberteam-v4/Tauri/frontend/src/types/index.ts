export interface Skill {
  id: string
  name: string
  description: string
  icon: string
  enabled: boolean
  category: 'builtin' | 'custom'
  triggerKeywords: string[]
}

export interface Agent {
  id: string
  name: string
  department: string
  layer: 'decision' | 'coordination' | 'execution'
  status: 'idle' | 'running' | 'error'
  skills: string[]
  soulPreview: string
}

export interface Message {
  id: string
  senderType: 'user' | 'agent'
  senderName?: string
  content: string
  timestamp: Date
}

export interface Conversation {
  id: string
  title: string
  createdAt: Date
  updatedAt: Date
  agentCount: number
}
