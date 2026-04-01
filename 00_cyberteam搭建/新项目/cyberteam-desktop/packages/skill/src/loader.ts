import type { Skill } from './skill'

const builtinSkills: Skill[] = [
  {
    id: 'ceo-review',
    name: 'CEO Review',
    description: 'Output review and decision gate',
    category: 'governance',
    prompt: 'Review outputs with CEO-level scrutiny.',
    tools: ['review', 'export'],
    version: 'v1',
  },
  {
    id: 'socratic-questioning',
    name: 'Socratic Questioning',
    description: 'Ask structured questions to clarify the problem',
    category: 'reasoning',
    prompt: 'Question assumptions and sharpen the problem definition.',
    tools: ['reason', 'reflect'],
    version: 'v1',
  },
]

export function loadSkills() {
  return builtinSkills.slice()
}
