/**
 * 项目 API - 调用后端 /api/v1/projects
 */
import { api } from '../clients/cyberteam'

export interface Project {
  id: string
  name: string
  description?: string
  status: 'planning' | 'executing' | 'completed' | 'paused'
  currentStep: number
  totalSteps: number
  createdAt: string
  agentCount: number
  messageCount: number
  metadata?: Record<string, any>
}

export interface CreateProjectRequest {
  name: string
  description?: string
  metadata?: Record<string, any>
}

export async function fetchProjects(): Promise<Project[]> {
  try {
    const data = await api<any[]>('GET', '/v1/projects')
    return data.map(normalizeProject)
  } catch (error) {
    console.warn('[Projects API] 后端不可用:', error)
    return []
  }
}

export async function createProject(req: CreateProjectRequest): Promise<Project | null> {
  try {
    const data = await api<any>('POST', '/v1/projects', req)
    return normalizeProject(data)
  } catch (error) {
    console.error('[Projects API] 创建项目失败:', error)
    return null
  }
}

export async function fetchProject(id: string): Promise<Project | null> {
  try {
    const data = await api<any>('GET', `/v1/projects/${id}`)
    return normalizeProject(data)
  } catch (error) {
    console.error('[Projects API] 获取项目失败:', error)
    return null
  }
}

export async function updateProject(id: string, updates: Partial<Project>): Promise<boolean> {
  try {
    await api<any>('PUT', `/v1/projects/${id}`, updates)
    return true
  } catch (error) {
    console.error('[Projects API] 更新项目失败:', error)
    return false
  }
}

/**
 * Playground 生成 API
 * POST /api/v1/projects/{id}/playground - 生成 Playground HTML
 * GET  /api/v1/projects/{id}/playground/file - 获取 HTML 内容
 */
export interface PlaygroundResponse {
  status: 'ok'
  project_id: string
  playground_path: string
  playground_url: string
  generated_at: string
}

export async function generatePlayground(projectId: string): Promise<PlaygroundResponse> {
  const data = await api<PlaygroundResponse>('POST', `/v1/projects/${projectId}/playground`)
  return data
}

export async function fetchPlaygroundHTML(projectId: string): Promise<string> {
  // 直接 fetch 获取 HTML 内容（用于 iframe srcdoc）
  const baseURL = import.meta.env.VITE_API_BASE_URL || ''
  const response = await fetch(`${baseURL}/api/v1/projects/${projectId}/playground/file`)
  if (!response.ok) {
    throw new Error(`获取 Playground 失败: ${response.status}`)
  }
  return response.text()
}

/**
 * 将后端 Project 模型标准化为前端 Project 接口
 */
function normalizeProject(raw: any): Project {
  return {
    id: raw.id || raw.project_id || raw.name || 'unknown',
    name: raw.name || '未命名项目',
    description: raw.description || '',
    status: normalizeStatus(raw.status),
    currentStep: raw.current_step || raw.currentStep || 1,
    totalSteps: raw.total_steps || raw.totalSteps || 8,
    createdAt: raw.created_at || raw.createdAt || new Date().toISOString().split('T')[0],
    agentCount: raw.agent_count || raw.agentCount || 0,
    messageCount: raw.message_count || raw.messageCount || 0,
    metadata: raw.metadata || {},
  }
}

function normalizeStatus(s?: string): Project['status'] {
  const map: Record<string, Project['status']> = {
    active: 'executing',
    planning: 'planning',
    executing: 'executing',
    completed: 'completed',
    done: 'completed',
    paused: 'paused',
    idle: 'planning',
  }
  return map[s || ''] || 'planning'
}
