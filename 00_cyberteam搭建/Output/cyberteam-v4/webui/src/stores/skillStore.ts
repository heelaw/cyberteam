import { create } from 'zustand';

export interface Skill {
  id: string;
  name: string;
  category: string;
  description: string;
  triggerConditions: string;
  usageGuide: string;
}

interface SkillStore {
  skills: Skill[];
  loading: boolean;
  fetchSkills: () => Promise<void>;
  addSkill: (skill: Omit<Skill, 'id'> & { id?: string }) => Promise<void>;
  updateSkill: (id: string, skill: Partial<Skill>) => Promise<void>;
  deleteSkill: (id: string) => Promise<void>;
}

const API = '/api';

async function apiRequest(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
    ...(options.body ? { body: JSON.stringify(options.body) } : {}),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const useSkillStore = create<SkillStore>((set, get) => ({
  skills: [],
  loading: false,

  fetchSkills: async () => {
    set({ loading: true });
    try {
      const skills = await apiRequest('/skills');
      set({ skills, loading: false });
    } catch {
      set({ loading: false });
    }
  },

  addSkill: async (skill) => {
    const id = skill.id || `skill-${Date.now()}`;
    await apiRequest('/skills', {
      method: 'POST',
      body: { ...skill, id },
    });
    await get().fetchSkills();
  },

  updateSkill: async (id, skill) => {
    await apiRequest(`/skills/${id}`, {
      method: 'PUT',
      body: skill,
    });
    await get().fetchSkills();
  },

  deleteSkill: async (id) => {
    await apiRequest(`/skills/${id}`, { method: 'DELETE' });
    await get().fetchSkills();
  },
}));
