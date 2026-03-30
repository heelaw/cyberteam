/**
 * 部门管理 API
 */
import { request } from '@/apis/clients/request'

export interface Department {
  id: string
  name: string
  code: string
  parent_id?: string
  level: number
  description: string
  manager_role: string
  skills: string[]
  status: string
  order: number
}

export const fetchDepartments = () => {
  return request.get<Department[]>('/api/departments')
}

export const fetchDepartmentTree = () => {
  return request.get<any[]>('/api/departments/tree')
}

export const fetchDepartment = (id: string) => {
  return request.get<Department>(`/api/departments/${id}`)
}

export const createDepartment = (data: Partial<Department>) => {
  return request.post<Department>('/api/departments', data)
}

export const updateDepartment = (id: string, data: Partial<Department>) => {
  return request.put<Department>(`/api/departments/${id}`, data)
}

export const deleteDepartment = (id: string) => {
  return request.delete(`/api/departments/${id}`)
}
