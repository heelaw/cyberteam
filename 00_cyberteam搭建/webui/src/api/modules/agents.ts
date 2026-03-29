import { api } from '../client'

export interface AgentProfile {
  name: string
  description: string
  llm: {
    provider: string
    model: string
    temperature: number
  }
  tools: string[]
  skills: string[]
  departments: string[]
  status: 'idle' | 'running' | 'error'
  avatar?: string
  created_at: string
  updated_at: string
}

export const agentsApi = {
  listAgents: () => api.get('/agents'),

  getAgent: (name: string) => api.get(`/agents/${name}`),

  runAgent: (name: string, data: { input: object }) =>
    api.post(`/agents/${name}/run`, data),

  getAgentSkills: (name: string) => api.get(`/agents/${name}/skills`),

  updateAgent: (name: string, data: Partial<AgentProfile>) =>
    api.put(`/agents/${name}`, data),

  deleteAgent: (name: string) => api.delete(`/agents/${name}`)
}