/**
 * 技能管理 API
 */
import { request } from '@/apis/clients/request'

export interface Skill {
  id: string
  name: string
  description: string
  category: string
  keywords: string[]
  tools: string[]
}

export const fetchSkills = () => {
  return request.get<Skill[]>('/api/skills')
}

export const fetchSkillCategories = () => {
  return request.get<{ categories: string[] }>('/api/skills/categories')
}

export const fetchSkillByCategory = (category: string) => {
  return request.get<Skill[]>(`/api/skills/category/${category}`)
}

export const matchSkill = (task: string) => {
  return request.get<Skill>('/api/skills/match', { task } as any)
}

export const executeWithSkill = (task: string, skillId?: string) => {
  return request.post<{ task: string; skill_id: string; skill_name: string; result: string }>(
    '/api/skills/execute',
    { task, skill_id: skillId }
  )
}
