export interface Conversation {
  id: string
  title: string
  type: 'private' | 'group' | 'department'
  participantIds?: string[]
  createdAt: string
  updatedAt: string
}

let conversationSequence = 0

function createTimestamp() {
  return new Date().toISOString()
}

export function createConversation(title: string, type: Conversation['type'], participantIds: string[] = []): Conversation {
  const createdAt = createTimestamp()
  conversationSequence += 1

  return {
    id: `conv_${conversationSequence}`,
    title,
    type,
    participantIds,
    createdAt,
    updatedAt: createdAt,
  }
}
