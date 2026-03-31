/**
 * 统计概览 API - 调用后端 /api/stats 或 /api/v1/stats
 * 如果后端无此端点，返回模拟数据（开发阶段降级）
 */
import { api } from '../clients/cyberteam'

export interface DashboardStats {
  activeTasks: number
  agentCount: number
  todayTokens: number
  todayCost: number
}

export interface AgentActivity {
  name: string
  dept: string
  status: 'running' | 'idle' | 'shutdown'
  task: string
}

export interface SystemStats {
  stats: DashboardStats
  agentActivity: AgentActivity[]
  recentTasks: Array<{
    id: string
    subject: string
    status: string
    priority: string
  }>
}

export async function fetchDashboardStats(): Promise<SystemStats> {
  try {
    // 尝试从多个可能的端点获取数据
    const [tasks, agents] = await Promise.allSettled([
      api<any[]>('GET', '/tasks', { limit: 5 }),
      api<{agents?: any[]; agent_id?: string}[]>('GET', '/agents', { limit: 10 }),
    ])

    // 处理 tasks 响应格式
    let taskData: any[] = []
    if (tasks.status === 'fulfilled') {
      const value = tasks.value
      // 兼容 {tasks: [...]} 或直接是数组
      if (Array.isArray(value)) {
        taskData = value
      } else if (value && typeof value === 'object' && 'tasks' in value) {
        taskData = (value as any).tasks || []
      }
    }

    // 处理 agents 响应格式
    let agentData: any[] = []
    if (agents.status === 'fulfilled') {
      const value = agents.value
      // 兼容 {agents: [...]} 或直接是数组
      if (Array.isArray(value)) {
        agentData = value
      } else if (value && typeof value === 'object' && 'agents' in value) {
        agentData = (value as any).agents || []
      }
    }

    // 从真实数据计算统计
    const activeTasks = taskData.filter((t: any) => t.status === 'in_progress').length
    const agentActivity: AgentActivity[] = agentData.slice(0, 6).map((a: any) => ({
      name: a.name || a.agent_id || 'Unknown',
      dept: a.department || a.agent_type || 'unknown',
      status: a.status || 'idle',
      task: a.current_task || a.last_task || '等待任务',
    }))

    // 估算 token 和费用（从 tasks 数据中如有则用真实值）
    const todayTokens = taskData.reduce((sum: number, t: any) => sum + (t.tokens_used || 0), 0) || 0
    const todayCost = todayTokens * 0.000003 // 按 $0.003/1K token 估算

    return {
      stats: {
        activeTasks: activeTasks || taskData.length || 0,
        agentCount: agentData.length || 0,
        todayTokens,
        todayCost: Math.round(todayCost * 100) / 100,
      },
      agentActivity,
      recentTasks: taskData.slice(0, 5).map((t: any) => ({
        id: t.id,
        subject: t.subject,
        status: t.status,
        priority: t.priority,
      })),
    }
  } catch (error) {
    console.warn('[Stats API] 后端不可用，返回降级数据:', error)
    return getFallbackStats()
  }
}

function getFallbackStats(): SystemStats {
  return {
    stats: {
      activeTasks: 0,
      agentCount: 0,
      todayTokens: 0,
      todayCost: 0,
    },
    agentActivity: [
      { name: '系统', dept: 'engine', status: 'idle', task: '等待启动' },
    ],
    recentTasks: [],
  }
}
