/**
 * Agent API - 调用后端 /api/agents 或 /api/v1/agents
 */
import { api } from '../clients/cyberteam'

export interface Agent {
  id: string
  name: string
  type: string
  department: string
  status: 'active' | 'idle' | 'shutdown'
  currentTask?: string
  lastTask?: string
  capabilities?: string[]
  joinedAt?: string
}

export async function fetchAgents(): Promise<Agent[]> {
  try {
    const data = await api<any[]>('GET', '/agents', { limit: 20 })
    return data.map(normalizeAgent)
  } catch (error) {
    console.warn('[Agents API] 后端不可用:', error)
    return []
  }
}

export async function fetchAgent(id: string): Promise<Agent | null> {
  try {
    const data = await api<any>('GET', `/agents/${id}`)
    return normalizeAgent(data)
  } catch (error) {
    console.error('[Agents API] 获取Agent失败:', error)
    return null
  }
}

export async function sendMessageToAgent(
  agentId: string,
  content: string,
  msgType: string = 'message'
): Promise<boolean> {
  try {
    await api<any>('POST', `/agents/${agentId}/messages`, {
      content,
      type: msgType,
    })
    return true
  } catch (error) {
    console.error('[Agents API] 发送消息失败:', error)
    return false
  }
}

function normalizeAgent(raw: any): Agent {
  return {
    id: raw.id || raw.agent_id || raw.name || 'unknown',
    name: raw.name || raw.agent_name || 'Unknown Agent',
    type: raw.agent_type || raw.type || 'general-purpose',
    department: raw.department || 'unknown',
    status: normalizeAgentStatus(raw.status),
    currentTask: raw.current_task || raw.currentTask,
    lastTask: raw.last_task || raw.lastTask,
    capabilities: raw.capabilities || [],
    joinedAt: raw.joined_at || raw.joinedAt,
  }
}

function normalizeAgentStatus(s?: string): Agent['status'] {
  const map: Record<string, Agent['status']> = {
    active: 'active',
    idle: 'idle',
    shutdown: 'shutdown',
    running: 'active',
    busy: 'active',
    offline: 'shutdown',
  }
  return map[s || ''] || 'idle'
}
