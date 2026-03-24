// Agent Types
export type AgentStatus = 'online' | 'busy' | 'offline' | 'error'

export interface Agent {
  id: string
  name: string
  role: string
  status: AgentStatus
  description: string
  currentTask?: string
  lastActive: Date
  tasksCompleted: number
  avatar?: string
}

// Task Types
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'blocked'

export interface Task {
  id: string
  title: string
  description: string
  status: TaskStatus
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assignee?: Agent
  createdAt: Date
  updatedAt: Date
  dueDate?: Date
  tags: string[]
}

// Message Types
export interface Message {
  id: string
  content: string
  sender: Agent | 'system'
  receiver?: Agent | 'all'
  timestamp: Date
  type: 'task' | 'chat' | 'notification' | 'system'
  read: boolean
  attachments?: string[]
}

// Kanban Column Types
export interface KanbanColumn {
  id: TaskStatus
  title: string
  tasks: Task[]
}

// Dashboard Stats
export interface DashboardStats {
  totalAgents: number
  activeAgents: number
  totalTasks: number
  completedTasks: number
  pendingTasks: number
  blockedTasks: number
  messagesToday: number
}
