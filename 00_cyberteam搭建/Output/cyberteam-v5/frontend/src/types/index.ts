// 类型定义
export interface Employee {
  id: string
  name: string
  role: string
  description: string
  skills: string[]
  status: string
}

export interface Task {
  task_id: string
  status: string
  content: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export interface Conversation {
  id: string
  title: string
  created_at: number
  updated_at: number
}
