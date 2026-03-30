/**
 * 公司管理 API - 调用后端 /api/v1/companies
 */
import { api } from '../clients/cyberteam'

// === 类型定义 ===

export interface Company {
  id: string
  name: string
  description?: string
  status: string
  config: Record<string, any>
  created_at: string
  updated_at: string
  department_count: number
  agent_count: number
}

export interface CompanyCreate {
  name: string
  description?: string
  status?: string
  config?: Record<string, any>
}

export interface CompanyUpdate {
  name?: string
  description?: string
  status?: string
  config?: Record<string, any>
}

export interface CompanyStats {
  company_id: string
  department_count: number
  agent_count: number
  active_department_count: number
  active_agent_count: number
}

export interface DepartmentSummary {
  id: string
  name: string
  code: string
  description?: string
  is_active: boolean
}

export interface AgentSummary {
  id: string
  name: string
  agent_type: string
  status: string
  description?: string
}

export interface PaginatedCompanyResponse {
  items: Company[]
  total: number
  skip: number
  limit: number
}

export interface ListCompaniesParams {
  skip?: number
  limit?: number
  q?: string
}

// === API 函数 ===

/**
 * 获取公司列表（支持分页和搜索）
 * GET /api/v1/companies
 */
export async function fetchCompanies(params?: ListCompaniesParams): Promise<PaginatedCompanyResponse> {
  try {
    const data = await api<PaginatedCompanyResponse>('GET', '/v1/companies', params)
    return data
  } catch (error) {
    console.error('[Companies API] 获取公司列表失败:', error)
    return { items: [], total: 0, skip: 0, limit: 50 }
  }
}

/**
 * 创建公司
 * POST /api/v1/companies
 */
export async function createCompany(req: CompanyCreate): Promise<Company | null> {
  try {
    const data = await api<Company>('POST', '/v1/companies', req)
    return data
  } catch (error) {
    console.error('[Companies API] 创建公司失败:', error)
    return null
  }
}

/**
 * 获取公司详情
 * GET /api/v1/companies/{id}
 */
export async function fetchCompany(id: string): Promise<Company | null> {
  try {
    const data = await api<Company>('GET', `/v1/companies/${id}`)
    return data
  } catch (error) {
    console.error('[Companies API] 获取公司详情失败:', error)
    return null
  }
}

/**
 * 更新公司信息
 * PUT /api/v1/companies/{id}
 */
export async function updateCompany(id: string, req: CompanyUpdate): Promise<boolean> {
  try {
    await api<Company>('PUT', `/v1/companies/${id}`, req)
    return true
  } catch (error) {
    console.error('[Companies API] 更新公司失败:', error)
    return false
  }
}

/**
 * 删除公司（软删除）
 * DELETE /api/v1/companies/{id}
 */
export async function deleteCompany(id: string): Promise<boolean> {
  try {
    await api<{ status: string; company_id: string; message: string }>('DELETE', `/v1/companies/${id}`)
    return true
  } catch (error) {
    console.error('[Companies API] 删除公司失败:', error)
    return false
  }
}

/**
 * 获取公司部门列表
 * GET /api/v1/companies/{id}/departments
 */
export async function fetchCompanyDepartments(companyId: string): Promise<DepartmentSummary[]> {
  try {
    const data = await api<DepartmentSummary[]>('GET', `/v1/companies/${companyId}/departments`)
    return data
  } catch (error) {
    console.error('[Companies API] 获取公司部门列表失败:', error)
    return []
  }
}

/**
 * 获取公司 Agent 列表
 * GET /api/v1/companies/{id}/agents
 */
export async function fetchCompanyAgents(companyId: string): Promise<AgentSummary[]> {
  try {
    const data = await api<AgentSummary[]>('GET', `/v1/companies/${companyId}/agents`)
    return data
  } catch (error) {
    console.error('[Companies API] 获取公司 Agent 列表失败:', error)
    return []
  }
}

/**
 * 获取公司统计信息
 * GET /api/v1/companies/{id}/stats
 */
export async function fetchCompanyStats(companyId: string): Promise<CompanyStats | null> {
  try {
    const data = await api<CompanyStats>('GET', `/v1/companies/${companyId}/stats`)
    return data
  } catch (error) {
    console.error('[Companies API] 获取公司统计信息失败:', error)
    return null
  }
}