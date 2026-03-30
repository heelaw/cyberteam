import { create } from 'zustand'
import type { Project } from '@/types'

interface ProjectState {
  projects: Project[]
  currentProjectId: string | null

  setProjects: (projects: Project[]) => void
  selectProject: (id: string) => void
  updateStep: (projectId: string, stepIndex: number, status: string, output?: string) => void
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProjectId: null,

  setProjects: (projects) => set({ projects }),
  selectProject: (id) => set({ currentProjectId: id }),
  updateStep: (projectId, stepIndex, status, output) =>
    set((s) => ({
      projects: s.projects.map((p) =>
        p.id === projectId
          ? {
              ...p,
              steps: p.steps.map((st, i) =>
                i === stepIndex ? { ...st, status: status as Project['steps'][0]['status'], output: output ?? st.output } : st
              ),
              currentStep: p.steps.findIndex((st) => st.status === 'running' || st.status === 'pending'),
            }
          : p
      ),
    })),
}))
