import { create } from 'zustand';
import { apiRequest } from '../api/client';
export interface Team { id: string; name: string; description: string; member_ids: string[]; }
interface Store { teams: Team[]; loading: boolean; fetchTeams: () => Promise<void>; addTeam: (t: any) => Promise<void>; updateTeam: (id: string, t: any) => Promise<void>; deleteTeam: (id: string) => Promise<void>; }
export const useTeamStore = create<Store>((set, get) => ({
  teams: [], loading: false,
  fetchTeams: async () => { set({ loading: true }); try { set({ teams: await apiRequest('/teams'), loading: false }); } catch { set({ loading: false }); } },
  addTeam: async (t) => { await apiRequest('/teams', { method: 'POST', body: t }); await get().fetchTeams(); },
  updateTeam: async (id, t) => { await apiRequest(`/teams/${id}`, { method: 'PUT', body: t }); await get().fetchTeams(); },
  deleteTeam: async (id) => { await apiRequest(`/teams/${id}`, { method: 'DELETE' }); await get().fetchTeams(); },
}));
