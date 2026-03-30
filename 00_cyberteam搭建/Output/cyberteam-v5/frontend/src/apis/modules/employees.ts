// 数字员工 API
import { request } from '@/apis/clients/request'
import type { Employee, Task } from '@/types'

export async function fetchTemplates(): Promise<Employee[]> {
  return request.get<Employee[]>('/api/employees/templates')
}

export async function fetchEmployees(): Promise<Employee[]> {
  return request.get<Employee[]>('/api/employees')
}

export async function createEmployee(data: {
  template_id: string
  name?: string
}): Promise<Employee> {
  return request.post<Employee>('/api/employees', data)
}

export async function getEmployee(id: string): Promise<Employee> {
  return request.get<Employee>(`/api/employees/${id}`)
}

export async function deleteEmployee(id: string): Promise<void> {
  return request.delete(`/api/employees/${id}`)
}

export async function executeTask(data: {
  task: string
  employee_id?: string
  template_id?: string
}): Promise<Task> {
  return request.post<Task>('/api/employees/tasks', data)
}

export async function getTaskStatus(taskId: string): Promise<Task> {
  return request.get<Task>(`/api/employees/tasks/${taskId}`)
}
