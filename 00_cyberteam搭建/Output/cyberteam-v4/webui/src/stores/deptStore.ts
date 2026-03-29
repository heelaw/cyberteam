import { create } from 'zustand';
import { apiRequest } from '../api/client';
export interface Dept { id: string; name: string; description: string; parentId: string | null; level: number; rules: any; }
interface Store { depts: Dept[]; loading: boolean; fetchDepts: () => Promise<void>; addDept: (d: any) => Promise<void>; updateDept: (id: string, d: any) => Promise<void>; deleteDept: (id: string) => Promise<void>; }
export const useDeptStore = create<Store>((set, get) => ({
  depts: [], loading: false,
  fetchDepts: async () => { set({ loading: true }); try { set({ depts: await apiRequest('/departments'), loading: false }); } catch { set({ loading: false }); } },
  addDept: async (d) => { await apiRequest('/departments', { method: 'POST', body: d }); await get().fetchDepts(); },
  updateDept: async (id, d) => { await apiRequest(`/departments/${id}`, { method: 'PUT', body: d }); await get().fetchDepts(); },
  deleteDept: async (id) => { await apiRequest(`/departments/${id}`, { method: 'DELETE' }); await get().fetchDepts(); },
}));
