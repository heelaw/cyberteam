import type { WSEvent } from '@/types'

// WebSocket 客户端 - 抄 Magic 的自动重连、心跳检测
class CyberTeamWS {
  private ws: WebSocket | null = null
  private url = ''
  private reconnectAttempts = 0
  private maxReconnectDelay = 30000
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private listeners: Map<string, Set<(data: WSEvent) => void>> = new Map()
  private online = true

  connect(url: string) {
    this.url = url
    this.cleanup()
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      this.startHeartbeat()
      console.log('[WS] Connected')
    }

    this.ws.onmessage = (e) => {
      try {
        const event: WSEvent = JSON.parse(e.data)
        this.dispatch(event.type, event)
      } catch { /* ignore non-JSON */ }
    }

    this.ws.onclose = () => {
      this.stopHeartbeat()
      if (this.online) this.reconnect()
    }

    this.ws.onerror = () => {
      this.ws?.close()
    }

    window.addEventListener('online', () => { this.online = true; this.reconnect() })
    window.addEventListener('offline', () => { this.online = false })
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && (!this.ws || this.ws.readyState !== WebSocket.OPEN)) {
        this.reconnect()
      }
    })
  }

  private reconnect() {
    if (!this.url || !this.online) return
    const delay = Math.min(3000 * 2 ** this.reconnectAttempts, this.maxReconnectDelay)
    this.reconnectAttempts++
    setTimeout(() => this.connect(this.url), delay)
  }

  private startHeartbeat() {
    this.stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'heartbeat', data: {}, timestamp: new Date().toISOString() })
    }, 10000)
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) { clearInterval(this.heartbeatTimer); this.heartbeatTimer = null }
  }

  private dispatch(type: string, event: WSEvent) {
    this.listeners.get(type)?.forEach((fn) => fn(event))
    this.listeners.get('*')?.forEach((fn) => fn(event))
  }

  on(type: string, handler: (data: WSEvent) => void) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set())
    this.listeners.get(type)!.add(handler)
    return () => this.listeners.get(type)?.delete(handler)
  }

  send(data: Record<string, unknown>) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  private cleanup() {
    if (this.ws) {
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
    }
  }

  disconnect() {
    this.online = false
    this.cleanup()
    this.stopHeartbeat()
  }
}

export const wsClient = new CyberTeamWS()
export default wsClient
