/**
 * Chat API 模块 — 对接后端 /api/v1/chat 端点
 * 抄 CodePilot stream-session-manager 的 SSE 订阅模式
 */
import { api } from '../clients/cyberteam'
import type { Conversation, Message } from '@/types'

// === Conversation ===

export interface ConversationResponse {
  id: string
  user_id: string
  agent_id?: string
  title?: string
  status: string
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
  message_count: number
}

export interface CreateConversationParams {
  title?: string
  projectId?: string
  agentId?: string
}

export async function fetchConversations(limit = 50, offset = 0): Promise<Conversation[]> {
  const data = await api<ConversationResponse[]>('GET', '/v1/chat/conversations', { limit, offset })
  return (data || []).map(normalizeConversation)
}

export async function createConversation(params: CreateConversationParams): Promise<Conversation> {
  const payload: Record<string, unknown> = {}
  if (params.title) payload.title = params.title
  if (params.projectId) payload.metadata = { project_id: params.projectId }
  if (params.agentId) payload.metadata = { ...(payload.metadata as object), agent_id: params.agentId }

  const data = await api<ConversationResponse>('POST', '/v1/chat/conversations', payload)
  return normalizeConversation(data)
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await api('DELETE', `/v1/chat/conversations/${conversationId}`)
}

// === Messages ===

export interface MessageResponse {
  id: string
  conversation_id: string
  sender_type: string
  sender_id?: string
  content: string
  metadata: Record<string, unknown>
  created_at: string
}

export interface SendMessageParams {
  content: string
  metadata?: Record<string, unknown>
}

export async function fetchMessages(
  conversationId: string,
  limit = 50,
  offset = 0
): Promise<Message[]> {
  const data = await api<MessageResponse[]>('GET', `/v1/chat/conversations/${conversationId}/messages`, {
    limit,
    offset,
  })
  return (data || []).map(normalizeMessage)
}

export async function sendMessage(
  conversationId: string,
  params: SendMessageParams
): Promise<Message> {
  const data = await api<MessageResponse>('POST', `/v1/chat/conversations/${conversationId}/messages`, {
    content: params.content,
    metadata: params.metadata || {},
  })
  return normalizeMessage(data)
}

// === SSE Stream — 抄 CodePilot stream-session-manager 模式
// 连接 SSE 流式响应，通过回调实时推送消息片段

export interface SSEStreamCallbacks {
  onThinking?: (stage: string, message: string) => void
  onRouted?: (department: string, reason: string) => void
  onAgentStart?: (agent: string, department: string) => void
  onAgentOutput?: (agent: string, content: string) => void
  onAgentComplete?: (agent: string, durationMs: number) => void
  onApprovalRequest?: (data: Record<string, unknown>) => void
  onError?: (message: string) => void
  onDone?: () => void
}

export function subscribeSSEStream(
  taskId: string,
  message: string,
  callbacks: SSEStreamCallbacks
): () => void {
  const baseURL = '/api'
  // 注意：后端 SSE 端点是 /api/{task_id}?message=xxx，没有 /sse 前缀
  const url = `${baseURL}/${encodeURIComponent(taskId)}?message=${encodeURIComponent(message)}`
  const eventSource = new EventSource(url)

  eventSource.onmessage = (e) => {
    if (e.data === '[DONE]') {
      callbacks.onDone?.()
      eventSource.close()
      return
    }
    try {
      const event = JSON.parse(e.data)
      switch (event.type) {
        case 'thinking':
          callbacks.onThinking?.(event.data?.stage || '', event.data?.message || '')
          break
        case 'routed':
          callbacks.onRouted?.(event.data?.department || '', event.data?.reason || '')
          break
        case 'agent_start':
          callbacks.onAgentStart?.(event.data?.agent || '', event.data?.department || '')
          break
        case 'agent_output':
          callbacks.onAgentOutput?.(event.data?.agent || '', event.data?.content || '')
          break
        case 'agent_complete':
          callbacks.onAgentComplete?.(
            event.data?.agent || '',
            event.data?.duration_ms || 0
          )
          break
        case 'approval_request':
          callbacks.onApprovalRequest?.(event.data || {})
          break
        case 'error':
          callbacks.onError?.(event.data?.message || 'Unknown error')
          break
      }
    } catch {
      // ignore parse errors
    }
  }

  eventSource.onerror = () => {
    callbacks.onError?.('SSE connection error')
    eventSource.close()
  }

  return () => eventSource.close()
}

// === Normalizers ===

function normalizeConversation(r: ConversationResponse): Conversation {
  return {
    id: r.id,
    title: r.title || '新对话',
    status: r.status === 'active' ? 'active' : 'archived',
    projectId: r.metadata?.project_id as string | undefined,
    createdAt: r.created_at,
    updatedAt: r.updated_at,
  }
}

function normalizeMessage(r: MessageResponse): Message {
  const meta = r.metadata || {}
  return {
    id: r.id,
    conversationId: r.conversation_id,
    senderType: r.sender_type as Message['senderType'],
    senderId: r.sender_id || '',
    senderName: (meta.sender_name as string) || (r.sender_type === 'user' ? '用户' : 'Agent'),
    department: meta.department as string | undefined,
    content: r.content,
    contentType: (meta.content_type as Message['contentType']) || 'markdown',
    metadata: meta,
    createdAt: r.created_at,
  }
}
