/**
 * Skills API - Skill 配置管理
 * 调用后端 /api/v1/skills
 */
import { baseURL } from '../base'

export interface Skill {
  id: string
  code: string
  name: string
  description: string | null
  category: string
  difficulty: string
  trigger_keywords: string[]
  success_metrics: Record<string, any>
  agent_count: number
  config: Record<string, any>
  created_at: string
  updated_at: string
}

export interface SkillCreate {
  name: string
  code: string
  description?: string
  category?: string
  difficulty?: string
  trigger_keywords?: string[]
  success_metrics?: Record<string, any>
  config?: Record<string, any>
}

export interface SkillUpdate {
  name?: string
  description?: string
  category?: string
  difficulty?: string
  trigger_keywords?: string[]
  success_metrics?: Record<string, any>
  config?: Record<string, any>
}

export interface SkillCategory {
  category: string
  count: number
  skills: Skill[]
}

export interface AgentBrief {
  id: string
  code: string
  name: string
  agent_type: string
  is_active: boolean
}

export interface ExecuteSkillRequest {
  input: string
  context?: Record<string, any>
}

export interface ExecuteSkillResponse {
  execution_id: string
  skill_code: string
  status: string
  result: Record<string, any>
}

/**
 * 获取 Skill 列表（支持 category/difficulty 过滤）
 */
export async function fetchSkills(params?: {
  category?: string
  difficulty?: string
}): Promise<Skill[]> {
  const searchParams = new URLSearchParams()
  if (params?.category) searchParams.set('category', params.category)
  if (params?.difficulty) searchParams.set('difficulty', params.difficulty)

  const url = `${baseURL}/v1/skills${searchParams.toString() ? `?${searchParams}` : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`获取 Skill 列表失败: ${res.statusText}`)
  return res.json()
}

/**
 * 获取 Skill 分类列表
 */
export async function fetchSkillCategories(): Promise<SkillCategory[]> {
  const res = await fetch(`${baseURL}/v1/skills/categories`)
  if (!res.ok) throw new Error(`获取 Skill 分类失败: ${res.statusText}`)
  return res.json()
}

/**
 * 获取 Skill 详情
 */
export async function fetchSkill(skillCode: string): Promise<Skill> {
  const res = await fetch(`${baseURL}/v1/skills/${encodeURIComponent(skillCode)}`)
  if (!res.ok) throw new Error(`获取 Skill 详情失败: ${res.statusText}`)
  return res.json()
}

/**
 * 创建自定义 Skill
 */
export async function createSkill(data: SkillCreate): Promise<Skill> {
  const res = await fetch(`${baseURL}/v1/skills`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!res.ok) throw new Error(`创建 Skill 失败: ${res.statusText}`)
  return res.json()
}

/**
 * 更新 Skill
 */
export async function updateSkill(skillCode: string, data: SkillUpdate): Promise<Skill> {
  const res = await fetch(`${baseURL}/v1/skills/${encodeURIComponent(skillCode)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!res.ok) throw new Error(`更新 Skill 失败: ${res.statusText}`)
  return res.json()
}

/**
 * 删除 Skill
 */
export async function deleteSkill(skillCode: string): Promise<void> {
  const res = await fetch(`${baseURL}/v1/skills/${encodeURIComponent(skillCode)}`, {
    method: 'DELETE'
  })
  if (!res.ok) throw new Error(`删除 Skill 失败: ${res.statusText}`)
}

/**
 * 获取使用某 Skill 的 Agent 列表
 */
export async function fetchSkillAgents(skillCode: string): Promise<AgentBrief[]> {
  const res = await fetch(`${baseURL}/v1/skills/${encodeURIComponent(skillCode)}/agents`)
  if (!res.ok) throw new Error(`获取 Skill Agent 列表失败: ${res.statusText}`)
  return res.json()
}

/**
 * 执行 Skill
 */
export async function executeSkill(
  skillCode: string,
  request: ExecuteSkillRequest
): Promise<ExecuteSkillResponse> {
  const res = await fetch(`${baseURL}/v1/skills/${encodeURIComponent(skillCode)}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  if (!res.ok) throw new Error(`执行 Skill 失败: ${res.statusText}`)
  return res.json()
}