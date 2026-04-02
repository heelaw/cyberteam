export interface ClaudeSession {
  id: string
  conversationId: string
  status?: 'idle' | 'running' | 'done' | 'error'
}
