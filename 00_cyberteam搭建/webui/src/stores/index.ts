import { create } from 'zustand'
import { api } from '../api/client'
import type { Department, Agent, Team, Template, Skill } from '../types'

export { useChatStore } from './chatStore'
export { useAgentStore } from './agentStore'
export type { Conversation, Message } from './chatStore'
export type { AgentProfile } from './agentStore'

interface AppState {
  departments: Department[]
  agents: Agent[]
  teams: Team[]
  templates: Template[]
  skills: Skill[]
  loading: boolean

  fetchDepartments: () => Promise<void>
  fetchAgents: () => Promise<void>
  fetchTeams: () => Promise<void>
  fetchTemplates: () => Promise<void>
  fetchSkills: () => Promise<void>

  createDepartment: (data: Partial<Department>) => Promise<void>
  updateDepartment: (id: string, data: Partial<Department>) => Promise<void>
  deleteDepartment: (id: string) => Promise<void>

  createAgent: (data: Partial<Agent>) => Promise<void>
  updateAgent: (id: string, data: Partial<Agent>) => Promise<void>
  deleteAgent: (id: string) => Promise<void>

  createTeam: (data: Partial<Team>) => Promise<void>
  updateTeam: (id: string, data: Partial<Team>) => Promise<void>
  deleteTeam: (id: string) => Promise<void>

  createTemplate: (data: Partial<Template>) => Promise<void>
  updateTemplate: (id: string, data: Partial<Template>) => Promise<void>
  deleteTemplate: (id: string) => Promise<void>

  createSkill: (data: Partial<Skill>) => Promise<void>
  updateSkill: (id: string, data: Partial<Skill>) => Promise<void>
  deleteSkill: (id: string) => Promise<void>
}

export const useStore = create<AppState>((set, get) => ({
  departments: [],
  agents: [],
  teams: [],
  templates: [],
  skills: [],
  loading: false,

  fetchDepartments: async () => {
    const data = await api.getDepartments()
    set({ departments: Array.isArray(data) ? data : (data.departments || []) })
  },
  fetchAgents: async () => {
    const data = await api.getAgents()
    set({ agents: data })
  },
  fetchTeams: async () => {
    const data = await api.getTeams()
    set({ teams: data })
  },
  fetchTemplates: async () => {
    const data = await api.getTemplates()
    set({ templates: data })
  },
  fetchSkills: async () => {
    const data = await api.getSkills()
    set({ skills: Array.isArray(data) ? data : (data.skills || []) })
  },

  createDepartment: async (data) => {
    await api.createDepartment(data)
    get().fetchDepartments()
  },
  updateDepartment: async (id, data) => {
    await api.updateDepartment(id, data)
    get().fetchDepartments()
  },
  deleteDepartment: async (id) => {
    await api.deleteDepartment(id)
    get().fetchDepartments()
  },

  createAgent: async (data) => {
    await api.createCustomAgent(data)
    get().fetchAgents()
  },
  updateAgent: async (id, data) => {
    await api.updateCustomAgent(id, data)
    get().fetchAgents()
  },
  deleteAgent: async (id) => {
    await api.deleteCustomAgent(id)
    get().fetchAgents()
  },

  createTeam: async (data) => {
    await api.createTeam(data)
    get().fetchTeams()
  },
  updateTeam: async (id, data) => {
    await api.updateTeam(id, data)
    get().fetchTeams()
  },
  deleteTeam: async (id) => {
    await api.deleteTeam(id)
    get().fetchTeams()
  },

  createTemplate: async (data) => {
    await api.createTemplate(data)
    get().fetchTemplates()
  },
  updateTemplate: async (id, data) => {
    await api.updateTemplate(id, data)
    get().fetchTemplates()
  },
  deleteTemplate: async (id) => {
    await api.deleteTemplate(id)
    get().fetchTemplates()
  },

  createSkill: async (data) => {
    await api.createSkill(data)
    get().fetchSkills()
  },
  updateSkill: async (id, data) => {
    await api.updateSkill(id, data)
    get().fetchSkills()
  },
  deleteSkill: async (id) => {
    await api.deleteSkill(id)
    get().fetchSkills()
  },
}))
