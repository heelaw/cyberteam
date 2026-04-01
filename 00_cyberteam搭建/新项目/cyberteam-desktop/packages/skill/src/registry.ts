import { loadSkills } from './loader'
import type { Skill } from './skill'

export function createSkillRegistry() {
  const registry = new Map<string, Skill>()

  for (const skill of loadSkills()) {
    registry.set(skill.id, skill)
  }

  return registry
}
