export interface Mention {
  agentId: string
  agentName: string
  agentTitle?: string
}

export function createMention(agentId: string, agentName: string, agentTitle?: string): Mention {
  return { agentId, agentName, agentTitle }
}
