// SSE 流式响应处理
type SSECallbacks = {
  onMessage?: (data: string) => void
  onError?: (error: Error) => void
  onDone?: () => void
}

export function subscribeSSEStream(
  url: string,
  callbacks: SSECallbacks
): EventSource {
  const eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    const data = event.data
    if (data && callbacks.onMessage) {
      callbacks.onMessage(data)
    }
  }

  eventSource.onerror = (error) => {
    if (callbacks.onError) {
      callbacks.onError(new Error('SSE connection error'))
    }
    eventSource.close()
  }

  return eventSource
}

// WebSocket 客户端
export class WSClient {
  private ws: WebSocket | null = null
  private url: string
  private callbacks: Record<string, Function> = {}

  constructor(url: string) {
    this.url = url
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        resolve()
      }

      this.ws.onerror = (error) => {
        reject(error)
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          const type = data.type || 'message'
          if (this.callbacks[type]) {
            this.callbacks[type](data)
          }
        } catch (e) {
          console.error('WS message parse error:', e)
        }
      }
    })
  }

  on(type: string, callback: Function) {
    this.callbacks[type] = callback
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  close() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}
