import { create } from 'zustand'
import { api } from '../api/client'

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

interface AgentState {
  agents: AgentProfile[]
  currentAgent: AgentProfile | null
  isLoading: boolean

  loadAgents: () => Promise<void>
  getAgent: (name: string) => Promise<AgentProfile>
  runAgent: (name: string, input: object) => Promise<void>
}

export const useAgentStore = create<AgentState>((set, get) => ({
  agents: [],
  currentAgent: null,
  isLoading: false,

  loadAgents: async () => {
    set({ isLoading: true })
    try {
      const data = await api.get('/agents')
      set({ agents: data })
    } finally {
      set({ isLoading: false })
    }
  },

  getAgent: async (name: string) => {
    const cached = get().agents.find(a => a.name === name)
    if (cached) return cached

    const data = await api.get(`/agents/${name}`)
    return data
  },

  runAgent: async (name: string, input: object) => {
    set({ isLoading: true })
    try {
      const agent = get().agents.find(a => a.name === name)
      if (agent) {
        set({ currentAgent: { ...agent, status: 'running' } })
      }
      await api.post(`/agents/${name}/run`, input)
    } finally {
      set(state => ({
        isLoading: false,
        currentAgent: state.currentAgent ? { ...state.currentAgent, status: 'idle' } : null
      }))
    }
  }
}))