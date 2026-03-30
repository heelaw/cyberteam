/**
 * Departments API - 调用后端 /api/v1/departments
 */
import { api } from '../clients/cyberteam'

export interface DepartmentSkill {
  name: string
  description: string
  level: string
}

export interface DepartmentLeader {
  role: string
  skills: string[]
}

export interface DepartmentExecutor {
  role: string
  skills: string[]
}

export interface Department {
  department_id: string
  name: string
  description: string
  responsibility: string
  skills: DepartmentSkill[]
  routing_rules: Record<string, unknown>[]
  leader: DepartmentLeader
  executor: DepartmentExecutor
  parent_id: string | null
  price_tier: string
  tags: string[]
  is_builtin: boolean
}

export interface RegisterDepartmentRequest {
  department_id: string
  name: string
  description: string
  responsibility: string
  skills?: DepartmentSkill[]
  routing_rules?: Record<string, unknown>[]
  leader_role?: string
  leader_skills?: string[]
  executor_role?: string
  executor_skills?: string[]
  parent_id?: string
  price_tier?: string
  tags?: string[]
}

export interface UpdateDepartmentRequest {
  name?: string
  description?: string
  responsibility?: string
  skills?: DepartmentSkill[]
  routing_rules?: Record<string, unknown>[]
  leader_role?: string
  leader_skills?: string[]
  executor_role?: string
  executor_skills?: string[]
  parent_id?: string
  price_tier?: string
  tags?: string[]
}

export async function fetchDepartments(
  includeBuiltin = true,
  includeCustom = true
): Promise<Department[]> {
  try {
    const data = await api<Department[]>('GET', '/v1/departments', {
      include_builtin: includeBuiltin,
      include_custom: includeCustom,
    })
    return data
  } catch (error) {
    console.warn('[Departments API] 获取部门列表失败:', error)
    return []
  }
}

export async function fetchDepartment(departmentId: string): Promise<Department | null> {
  try {
    const data = await api<Department>('GET', `/v1/departments/${departmentId}`)
    return data
  } catch (error) {
    console.error('[Departments API] 获取部门详情失败:', error)
    return null
  }
}

export async function registerDepartment(request: RegisterDepartmentRequest): Promise<Department | null> {
  try {
    const data = await api<Department>('POST', '/v1/departments', request)
    return data
  } catch (error) {
    console.error('[Departments API] 创建部门失败:', error)
    return null
  }
}

export async function updateDepartment(
  departmentId: string,
  request: UpdateDepartmentRequest
): Promise<Department | null> {
  try {
    const data = await api<Department>('PUT', `/v1/departments/${departmentId}`, request)
    return data
  } catch (error) {
    console.error('[Departments API] 更新部门失败:', error)
    return null
  }
}

export async function deleteDepartment(departmentId: string): Promise<boolean> {
  try {
    await api<{ status: string; department_id: string }>('DELETE', `/v1/departments/${departmentId}`)
    return true
  } catch (error) {
    console.error('[Departments API] 删除部门失败:', error)
    return false
  }
}

export interface DepartmentStatistics {
  total_count: number
  builtin_count: number
  custom_count: number
  builtin_departments: string[]
  custom_departments: string[]
}

export async function fetchDepartmentStatistics(): Promise<DepartmentStatistics | null> {
  try {
    const data = await api<DepartmentStatistics>('GET', '/v1/departments/statistics')
    return data
  } catch (error) {
    console.error('[Departments API] 获取统计信息失败:', error)
    return null
  }
}

// 部门绑定 Agent 相关
export interface BindAgentRequest {
  agent_code: string
}

export async function bindAgentToDepartment(
  departmentId: string,
  agentCode: string
): Promise<boolean> {
  try {
    await api<{ status: string }>('POST', `/v1/departments/${departmentId}/agents`, {
      agent_code: agentCode,
    })
    return true
  } catch (error) {
    console.error('[Departments API] 绑定 Agent 失败:', error)
    return false
  }
}

export async function unbindAgentFromDepartment(
  departmentId: string,
  agentCode: string
): Promise<boolean> {
  try {
    await api<{ status: string }>(
      'DELETE',
      `/v1/departments/${departmentId}/agents/${agentCode}`
    )
    return true
  } catch (error) {
    console.error('[Departments API] 解绑 Agent 失败:', error)
    return false
  }
}

export async function fetchDepartmentAgents(departmentId: string): Promise<string[]> {
  try {
    const data = await api<{ agents: string[] }>('GET', `/v1/departments/${departmentId}/agents`)
    return data.agents || []
  } catch (error) {
    console.error('[Departments API] 获取部门 Agents 失败:', error)
    return []
  }
}
