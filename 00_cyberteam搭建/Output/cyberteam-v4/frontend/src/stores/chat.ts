import { create } from 'zustand'
import type { Conversation, Message } from '@/types'

interface ChatState {
  conversations: Conversation[]
  currentConversationId: string | null
  messages: Message[]
  isStreaming: boolean
  connectedAgents: string[]

  // Actions
  setConversations: (convos: Conversation[]) => void
  selectConversation: (id: string) => void
  addMessage: (msg: Message) => void
  setStreaming: (v: boolean) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  isStreaming: false,
  connectedAgents: [],

  setConversations: (convos) => set({ conversations: convos }),
  selectConversation: (id) => set({ currentConversationId: id, messages: [] }),
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setStreaming: (v) => set({ isStreaming: v }),
  clearMessages: () => set({ messages: [] }),
}))
