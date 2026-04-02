class CyberTeamWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectDelay = 30000
  private heartbeatTimer: number | null = null
  private listeners = new Map<string, Function[]>()
  private reconnectTimer: number | null = null
  private shouldReconnect = true
  private url: string = ''
  private token: string = ''

  connect(url: string, token?: string): void {
    this.url = url
    this.token = token || ''
    this.shouldReconnect = true

    const wsUrl = token ? `${url}?token=${token}` : url
    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      this.startHeartbeat()
      this.emit('connected', {})
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emit(data.type, data.payload)
      } catch {
        this.emit('message', event.data)
      }
    }

    this.ws.onerror = () => {
      this.emit('error', {})
    }

    this.ws.onclose = () => {
      this.stopHeartbeat()
      this.emit('disconnected', {})
      if (this.shouldReconnect) {
        this.reconnect()
      }
    }
  }

  disconnect(): void {
    this.shouldReconnect = false
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: object): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  on(type: string, fn: Function): void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, [])
    }
    this.listeners.get(type)!.push(fn)
  }

  off(type: string, fn: Function): void {
    const callbacks = this.listeners.get(type)
    if (callbacks) {
      const index = callbacks.indexOf(fn)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  private emit(type: string, payload: unknown): void {
    const callbacks = this.listeners.get(type)
    if (callbacks) {
      callbacks.forEach(fn => fn(payload))
    }
  }

  private reconnect(): void {
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), this.maxReconnectDelay)
    this.reconnectAttempts++

    this.reconnectTimer = window.setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect(this.url, this.token)
      }
    }, delay)
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = window.setInterval(() => {
      this.send({ type: 'ping' })
    }, 30000)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }
}

export const wsClient = new CyberTeamWebSocket()
export default CyberTeamWebSocket