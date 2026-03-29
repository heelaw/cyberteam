// ====== CyberTeam v4 Type Definitions ======

// --- Agent Types ---
export type AgentLayer = 'decision' | 'coordination' | 'execution'

export interface Agent {
  id: string
  name: string
  department: string
  layer: AgentLayer
  status: 'idle' | 'running' | 'error'
  model: string
  tools: string[]
  skills: string[]
  subordinates: string[]
  rating: number
  avatar?: string
  description: string
}

// --- Chat Types ---
export interface Conversation {
  id: string
  title: string
  status: 'active' | 'archived'
  projectId?: string
  createdAt: string
  updatedAt: string
}

export interface Message {
  id: string
  conversationId: string
  senderType: 'user' | 'agent' | 'system'
  senderId: string
  senderName: string
  department?: string
  content: string
  contentType: 'markdown' | 'text' | 'tool_call' | 'tool_result'
  metadata?: Record<string, unknown>
  parentId?: string
  createdAt: string
}

// --- Project Types ---
export interface Project {
  id: string
  name: string
  description: string
  status: 'planning' | 'executing' | 'reviewing' | 'completed'
  currentStep: number
  steps: ProjectStep[]
  createdAt: string
  updatedAt: string
}

export interface ProjectStep {
  index: number
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  agentName?: string
  startedAt?: string
  completedAt?: string
  output?: string
}

// --- Task Types ---
export interface Task {
  id: string
  title: string
  description: string
  status: 'pending' | 'assigned' | 'running' | 'completed' | 'failed'
  priority: 'low' | 'medium' | 'high'
  assignee?: string
  department?: string
  createdAt: string
  completedAt?: string
}

// --- WebSocket Event Types ---
export type WSEventType =
  | 'agent_start'
  | 'agent_output'
  | 'agent_complete'
  | 'agent_error'
  | 'debate_start'
  | 'debate_message'
  | 'debate_converge'
  | 'state_change'
  | 'heartbeat'
  | 'heartbeat_ack'

export interface WSEvent {
  type: WSEventType
  data: Record<string, unknown>
  timestamp: string
  source?: string
}

// --- API Response Types ---
export interface ApiResponse<T> {
  code: number
  data: T
  message: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}
