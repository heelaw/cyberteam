import { create } from 'zustand'
import type { Agent, AgentLayer } from '@/types'

interface AgentState {
  agents: Agent[]
  selectedAgentId: string | null
  filterLayer: AgentLayer | 'all'

  // Actions
  setAgents: (agents: Agent[]) => void
  selectAgent: (id: string | null) => void
  setFilterLayer: (layer: AgentLayer | 'all') => void
  updateAgentStatus: (id: string, status: Agent['status']) => void
  getAgentsByLayer: (layer: AgentLayer) => Agent[]
  getAgentsByDept: (dept: string) => Agent[]
}

export const useAgentStore = create<AgentState>((set, get) => ({
  agents: [],
  selectedAgentId: null,
  filterLayer: 'all',

  setAgents: (agents) => set({ agents }),
  selectAgent: (id) => set({ selectedAgentId: id }),
  setFilterLayer: (layer) => set({ filterLayer: layer }),
  updateAgentStatus: (id, status) =>
    set((s) => ({
      agents: s.agents.map((a) => (a.id === id ? { ...a, status } : a)),
    })),
  getAgentsByLayer: (layer) => get().agents.filter((a) => a.layer === layer),
  getAgentsByDept: (dept) => get().agents.filter((a) => a.department === dept),
}))
