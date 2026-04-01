/**
 * SSE Client Hook — subscribes to /api/v1/sse/tasks/{taskId}/stream
 * <!--zh
 * SSE 实时通信 Hook：连接 SSE 流式端点，接收 Agent 执行状态事件
 * -->
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuthStore } from '../stores/authStore'

export interface SSEEvent {
  event_id: string
  event_type: string
  task_id: string
  agent_id?: string
  agent_name?: string
  content: string
  metadata?: Record<string, unknown>
  timestamp: string
}

export interface UseSSEOptions {
  onConnected?: () => void
  onDisconnected?: () => void
  onEvent?: (event: SSEEvent) => void
  onError?: (err: Event) => void
}

export function useSSE(taskId: string | null, options: UseSSEOptions = {}) {
  const { token } = useAuthStore()
  const [isConnected, setIsConnected] = useState(false)
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null)
  const [events, setEvents] = useState<SSEEvent[]>([])
  const esRef = useRef<EventSource | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const reconnectAttempts = useRef(0)

  const connect = useCallback(() => {
    if (!taskId || !token) return

    // Clean up existing connection
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }

    const url = `/api/v1/sse/tasks/${taskId}/stream`
    const es = new EventSource(url)
    esRef.current = es

    es.addEventListener('connected', () => {
      setIsConnected(true)
      reconnectAttempts.current = 0
      options.onConnected?.()
    })

    // Agent event types
    const agentEventTypes = [
      'agent.started',
      'agent.thinking',
      'agent.tool_call',
      'agent.completed',
      'agent.error',
    ]

    agentEventTypes.forEach((type) => {
      es.addEventListener(type, (e) => {
        try {
          const event: SSEEvent = JSON.parse((e as MessageEvent).data)
          setLastEvent(event)
          setEvents((prev) => [...prev.slice(-99), event]) // Keep last 100
          options.onEvent?.(event)
        } catch {
          console.error('[SSE] Failed to parse event data')
        }
      })
    })

    es.addEventListener('done', () => {
      setIsConnected(false)
      options.onDisconnected?.()
    })

    es.onerror = (err) => {
      console.error('[SSE] Error', err)
      setIsConnected(false)
      options.onError?.(err)

      // Auto-reconnect with exponential backoff (max 30s)
      es.close()
      const delay = Math.min(3000 * 2 ** reconnectAttempts.current, 30000)
      reconnectAttempts.current += 1
      reconnectTimer.current = setTimeout(() => {
        connect()
      }, delay)
    }
  }, [taskId, token]) // eslint-disable-line react-hooks/exhaustive-deps

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current)
      reconnectTimer.current = null
    }
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }
    setIsConnected(false)
  }, [])

  useEffect(() => {
    if (taskId) {
      connect()
    }
    return () => {
      disconnect()
    }
  }, [taskId]) // eslint-disable-line react-hooks/exhaustive-deps

  return {
    isConnected,
    lastEvent,
    events,
    connect,
    disconnect,
  }
}
