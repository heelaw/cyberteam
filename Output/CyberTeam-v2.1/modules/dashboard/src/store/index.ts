import { create } from 'zustand'
import type { Agent, Task, Message, DashboardStats } from '@/types'

interface DashboardState {
  // Agents
  agents: Agent[]
  setAgents: (agents: Agent[]) => void
  updateAgentStatus: (id: string, status: Agent['status']) => void

  // Tasks
  tasks: Task[]
  setTasks: (tasks: Task[]) => void
  addTask: (task: Task) => void
  updateTask: (id: string, updates: Partial<Task>) => void
  moveTask: (id: string, status: Task['status']) => void

  // Messages
  messages: Message[]
  addMessage: (message: Message) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void

  // UI State
  selectedAgentId: string | null
  setSelectedAgentId: (id: string | null) => void
  sidebarCollapsed: boolean
  toggleSidebar: () => void
}

// Mock data
const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'gsd-planner',
    role: '任务规划',
    status: 'online',
    description: '负责创建详细的规格说明书和任务规划',
    lastActive: new Date(),
    tasksCompleted: 45,
  },
  {
    id: '2',
    name: 'gsd-executor',
    role: '任务执行',
    status: 'busy',
    description: '负责执行开发任务和代码实现',
    currentTask: '开发用户认证模块',
    lastActive: new Date(Date.now() - 5 * 60 * 1000),
    tasksCompleted: 38,
  },
  {
    id: '3',
    name: 'gsd-verifier',
    role: '质量验证',
    status: 'online',
    description: '负责验证实现是否符合规格要求',
    lastActive: new Date(Date.now() - 10 * 60 * 1000),
    tasksCompleted: 42,
  },
  {
    id: '4',
    name: 'code-reviewer',
    role: '代码审查',
    status: 'offline',
    description: '负责代码质量审查和安全检查',
    lastActive: new Date(Date.now() - 60 * 60 * 1000),
    tasksCompleted: 67,
  },
  {
    id: '5',
    name: 'security-engineer',
    role: '安全工程',
    status: 'online',
    description: '负责安全审计和漏洞修复',
    lastActive: new Date(Date.now() - 2 * 60 * 1000),
    tasksCompleted: 23,
  },
]

const mockTasks: Task[] = [
  {
    id: '1',
    title: '设计用户认证流程',
    description: '设计并实现完整的用户注册、登录、登出流程',
    status: 'completed',
    priority: 'high',
    assignee: mockAgents[0],
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    tags: ['认证', '安全'],
  },
  {
    id: '2',
    title: '实现 API 接口',
    description: '开发 RESTful API 接口包括用户、任务、消息等模块',
    status: 'in_progress',
    priority: 'high',
    assignee: mockAgents[1],
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(),
    dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    tags: ['API', '后端'],
  },
  {
    id: '3',
    title: '编写单元测试',
    description: '为关键模块编写单元测试和集成测试',
    status: 'pending',
    priority: 'medium',
    assignee: mockAgents[2],
    createdAt: new Date(),
    updatedAt: new Date(),
    dueDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
    tags: ['测试'],
  },
  {
    id: '4',
    title: '修复登录 Bug',
    description: '用户反馈登录后 token 过期时间计算错误',
    status: 'blocked',
    priority: 'urgent',
    assignee: mockAgents[1],
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    tags: ['Bug', '认证'],
  },
  {
    id: '5',
    title: '优化数据库查询',
    description: '分析并优化慢查询，提升系统性能',
    status: 'pending',
    priority: 'medium',
    createdAt: new Date(),
    updatedAt: new Date(),
    tags: ['性能', '数据库'],
  },
  {
    id: '6',
    title: '更新 API 文档',
    description: '根据最新实现更新 OpenAPI 文档',
    status: 'in_progress',
    priority: 'low',
    assignee: mockAgents[0],
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(),
    tags: ['文档'],
  },
]

const mockMessages: Message[] = [
  {
    id: '1',
    content: '任务 "设计用户认证流程" 已完成，请审查',
    sender: mockAgents[0],
    receiver: mockAgents[2],
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    type: 'task',
    read: false,
  },
  {
    id: '2',
    content: 'API 接口开发遇到问题，需要安全团队协助',
    sender: mockAgents[1],
    receiver: mockAgents[4],
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    type: 'chat',
    read: false,
  },
  {
    id: '3',
    content: '系统检测到异常登录尝试，已自动拦截',
    sender: 'system',
    receiver: mockAgents[4],
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    type: 'notification',
    read: true,
  },
  {
    id: '4',
    content: '新的代码审查请求：#42',
    sender: mockAgents[1],
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
    type: 'task',
    read: true,
  },
]

export const useDashboardStore = create<DashboardState>((set) => ({
  // Agents
  agents: mockAgents,
  setAgents: (agents) => set({ agents }),
  updateAgentStatus: (id, status) =>
    set((state) => ({
      agents: state.agents.map((a) =>
        a.id === id ? { ...a, status } : a
      ),
    })),

  // Tasks
  tasks: mockTasks,
  setTasks: (tasks) => set({ tasks }),
  addTask: (task) => set((state) => ({ tasks: [...state.tasks, task] })),
  updateTask: (id, updates) =>
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.id === id ? { ...t, ...updates } : t
      ),
    })),
  moveTask: (id, status) =>
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.id === id ? { ...t, status, updatedAt: new Date() } : t
      ),
    })),

  // Messages
  messages: mockMessages,
  addMessage: (message) =>
    set((state) => ({ messages: [message, ...state.messages] })),
  markAsRead: (id) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, read: true } : m
      ),
    })),
  markAllAsRead: () =>
    set((state) => ({
      messages: state.messages.map((m) => ({ ...m, read: true })),
    })),

  // UI State
  selectedAgentId: null,
  setSelectedAgentId: (id) => set({ selectedAgentId: id }),
  sidebarCollapsed: false,
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}))

// Selector hooks
export const useStats = () => {
  const tasks = useDashboardStore((state) => state.tasks)
  const agents = useDashboardStore((state) => state.agents)
  const messages = useDashboardStore((state) => state.messages)

  const stats: DashboardStats = {
    totalAgents: agents.length,
    activeAgents: agents.filter((a) => a.status === 'online').length,
    totalTasks: tasks.length,
    completedTasks: tasks.filter((t) => t.status === 'completed').length,
    pendingTasks: tasks.filter((t) => t.status === 'pending').length,
    blockedTasks: tasks.filter((t) => t.status === 'blocked').length,
    messagesToday: messages.filter(
      (m) =>
        new Date(m.timestamp).toDateString() === new Date().toDateString()
    ).length,
  }

  return stats
}
