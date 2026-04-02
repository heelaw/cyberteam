import type { Mention } from './mention'

export interface Message {
  id: string
  conversationId: string
  content: string
  senderId?: string
  mentions?: Mention[]
  status: 'pending' | 'sent' | 'failed'
  createdAt: string
}

let messageSequence = 0

function createTimestamp() {
  return new Date().toISOString()
}

export function createMessage(conversationId: string, content: string, senderId?: string, mentions: Mention[] = []): Message {
  const createdAt = createTimestamp()
  messageSequence += 1

  return {
    id: `msg_${messageSequence}`,
    conversationId,
    content,
    senderId,
    mentions,
    status: 'sent',
    createdAt,
  }
}
