/**
 * Custom Agents API - 调用后端 /api/v1/agents
 */
import { api } from '../clients/cyberteam'

export interface CustomAgent {
  id: string
  code: string
  name: string
  agent_type: string
  description: string | null
  company_id: string | null
  skills: string[]
  skill_count: number
  status: string
  is_active: boolean
  config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface CreateAgentRequest {
  name: string
  code: string
  agent_type?: string
  description?: string
  company_id?: string
  skills?: string[]
  config?: Record<string, unknown>
}

export interface UpdateAgentRequest {
  name?: string
  description?: string
  skills?: string[]
  config?: Record<string, unknown>
  is_active?: boolean
}

export interface BindSkillRequest {
  skill_id: string
}

export async function fetchAgents(
  companyId?: string,
  skillIds?: string[]
): Promise<CustomAgent[]> {
  try {
    const params: Record<string, string> = {}
    if (companyId) params.company_id = companyId
    if (skillIds && skillIds.length > 0) params.skill_ids = skillIds.join(',')

    const data = await api<CustomAgent[]>('GET', '/v1/agents', Object.keys(params).length > 0 ? params : undefined)
    return data
  } catch (error) {
    console.warn('[CustomAgents API] 获取 Agent 列表失败:', error)
    return []
  }
}

export async function fetchAgent(code: string): Promise<CustomAgent | null> {
  try {
    const data = await api<CustomAgent>('GET', `/v1/agents/${code}`)
    return data
  } catch (error) {
    console.error('[CustomAgents API] 获取 Agent 详情失败:', error)
    return null
  }
}

export async function createAgent(request: CreateAgentRequest): Promise<CustomAgent | null> {
  try {
    const data = await api<CustomAgent>('POST', '/v1/agents', request)
    return data
  } catch (error) {
    console.error('[CustomAgents API] 创建 Agent 失败:', error)
    return null
  }
}

export async function updateAgent(
  code: string,
  request: UpdateAgentRequest
): Promise<CustomAgent | null> {
  try {
    const data = await api<CustomAgent>('PUT', `/v1/agents/${code}`, request)
    return data
  } catch (error) {
    console.error('[CustomAgents API] 更新 Agent 失败:', error)
    return null
  }
}

export async function deleteAgent(code: string): Promise<boolean> {
  try {
    await api<{ status: string; code: string }>('DELETE', `/v1/agents/${code}`)
    return true
  } catch (error) {
    console.error('[CustomAgents API] 删除 Agent 失败:', error)
    return false
  }
}

export async function bindSkillToAgent(
  agentCode: string,
  skillId: string
): Promise<CustomAgent | null> {
  try {
    const data = await api<CustomAgent>('POST', `/v1/agents/${agentCode}/skills`, {
      skill_id: skillId,
    })
    return data
  } catch (error) {
    console.error('[CustomAgents API] 绑定 Skill 失败:', error)
    return null
  }
}

export async function unbindSkillFromAgent(
  agentCode: string,
  skillId: string
): Promise<CustomAgent | null> {
  try {
    const data = await api<CustomAgent>(
      'DELETE',
      `/v1/agents/${agentCode}/skills/${skillId}`
    )
    return data
  } catch (error) {
    console.error('[CustomAgents API] 解绑 Skill 失败:', error)
    return null
  }
}

export interface Skill {
  id: string
  code: string
  name: string
  description: string | null
  category: string
  difficulty: string
  trigger_keywords: string[]
  success_metrics: Record<string, unknown>
  agent_count: number
  config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export async function fetchSkills(
  category?: string,
  difficulty?: string
): Promise<Skill[]> {
  try {
    const params: Record<string, string> = {}
    if (category) params.category = category
    if (difficulty) params.difficulty = difficulty

    const data = await api<Skill[]>('GET', '/v1/skills', Object.keys(params).length > 0 ? params : undefined)
    return data
  } catch (error) {
    console.warn('[CustomAgents API] 获取 Skills 列表失败:', error)
    return []
  }
}

export interface Execution {
  id: string
  agent_code: string
  status: string
  input_text: string | null
  output_text: string | null
  duration_ms: number
  created_at: string
}

export async function fetchAgentExecutions(
  agentCode: string,
  limit = 50,
  offset = 0
): Promise<Execution[]> {
  try {
    const data = await api<Execution[]>('GET', `/v1/agents/${agentCode}/executions`, {
      limit,
      offset,
    })
    return data
  } catch (error) {
    console.error('[CustomAgents API] 获取执行历史失败:', error)
    return []
  }
}
