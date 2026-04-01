export interface Department {
  id: string
  name: string
  description: string
  parentId: string | null
  rules?: string
  createdAt: string
  updatedAt: string
}

export interface Agent {
  id: string
  name: string
  role: string
  departmentId: string
  level: string
  description: string
  capabilities: string[]
  knowledge: string[]
  outputStyle: string
  upstreamDeps: string[]
  downstreamDeps: string[]
  skills: string[]
  createdAt: string
  updatedAt: string
}

export interface Team {
  id: string
  name: string
  description: string
  departmentId: string
  members: string[]
  settings: {
    collaborationMode: string
    reportCycle: string
  }
  createdAt: string
  updatedAt: string
}

export interface Template {
  id: string
  name: string
  description: string
  teamConfig: object
  createdAt: string
  updatedAt: string
}

export interface Skill {
  id: string
  name: string
  category: string
  description: string
  trigger: string
  triggerConditions: string
  usageGuide: string
  difficulty: string
  version: string
  author: string
  tags: string[]
  source_path: string
  references?: Array<{ name: string; path: string; type: string }>
  content?: string
}

// Chat types
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
  metadata?: {
    agent_name?: string
    tools_used?: string[]
    tokens_used?: number
    status?: 'streaming' | 'completed' | 'error'
  }
  created_at: string
}

// Agent Profile type
export interface AgentProfile {
  name: string
  description: string
  llm: {
    provider: string
    model: string
    temperature: number
  }
  tools: string[]
  skills: string[]
  departments: string[]
  status: 'idle' | 'running' | 'error'
  avatar?: string
  created_at: string
  updated_at: string
}

// User type
export interface User {
  id: string
  username: string
  email: string
  org_id: string
  role: 'admin' | 'user' | 'guest'
  avatar?: string
  created_at: string
  updated_at: string
}