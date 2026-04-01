import { createConversation, type Conversation } from './conversation'
import { createMessage, type Message } from './message'

export function createConversationStore() {
  const conversations: Conversation[] = []
  const messages = new Map<string, Message[]>()

  return {
    createConversation(title: string, type: Conversation['type'], participantIds: string[] = []) {
      const conversation = createConversation(title, type, participantIds)
      conversations.push(conversation)
      messages.set(conversation.id, [])
      return conversation
    },
    listConversations() {
      return conversations
    },
    sendMessage(conversationId: string, content: string, senderId?: string, mentions: Message['mentions'] = []) {
      const message = createMessage(conversationId, content, senderId, mentions ?? [])
      const list = messages.get(conversationId) ?? []
      list.push(message)
      messages.set(conversationId, list)
      return message
    },
    getMessages(conversationId: string) {
      return messages.get(conversationId) ?? []
    },
    getConversation(conversationId: string) {
      return conversations.find((conversation) => conversation.id === conversationId)
    },
  }
}
