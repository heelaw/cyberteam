export interface Agent {
  id: string
  companyId: string
  departmentId?: string
  name: string
  title: string
  avatar?: string
  bio: string
  personality: string
  status: 'offline' | 'online' | 'busy'
  isCEO: boolean
  isActive: boolean
  createdAt: string
  updatedAt: string
}

let agentSequence = 0

function createTimestamp() {
  return new Date().toISOString()
}

export function createAgent(name: string, title = 'Member', avatar?: string, companyId = 'company_1'): Agent {
  const createdAt = createTimestamp()
  agentSequence += 1

  return {
    id: `agent_${agentSequence}`,
    companyId,
    name,
    title,
    avatar,
    bio: '',
    personality: 'calm, precise, helpful',
    status: 'offline',
    isCEO: title.toLowerCase() === 'ceo',
    isActive: true,
    createdAt,
    updatedAt: createdAt,
  }
}
