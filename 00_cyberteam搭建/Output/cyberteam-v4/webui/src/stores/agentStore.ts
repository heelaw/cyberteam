import { create } from 'zustand';
import { apiRequest } from '../api/client';
export interface Agent { id: string; name: string; type: string; department_id: string; level: string; capabilities: any; upstream: string[]; downstream: string[]; }
interface Store { agents: Agent[]; loading: boolean; fetchAgents: () => Promise<void>; addAgent: (a: any) => Promise<void>; updateAgent: (id: string, a: any) => Promise<void>; deleteAgent: (id: string) => Promise<void>; }
export const useAgentStore = create<Store>((set, get) => ({
  agents: [], loading: false,
  fetchAgents: async () => { set({ loading: true }); try { set({ agents: await apiRequest('/agents'), loading: false }); } catch { set({ loading: false }); } },
  addAgent: async (a) => { await apiRequest('/agents', { method: 'POST', body: a }); await get().fetchAgents(); },
  updateAgent: async (id, a) => { await apiRequest(`/agents/${id}`, { method: 'PUT', body: a }); await get().fetchAgents(); },
  deleteAgent: async (id) => { await apiRequest(`/agents/${id}`, { method: 'DELETE' }); await get().fetchAgents(); },
}));
