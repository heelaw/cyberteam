// 请求客户端
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

class RequestClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    method: string,
    path: string,
    data?: any
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    }

    if (data) {
      options.body = JSON.stringify(data)
    }

    const response = await fetch(url, options)

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path)
  }

  post<T>(path: string, data?: any): Promise<T> {
    return this.request<T>('POST', path, data)
  }

  put<T>(path: string, data?: any): Promise<T> {
    return this.request<T>('PUT', path, data)
  }

  delete<T>(path: string): Promise<T> {
    return this.request<T>('DELETE', path)
  }
}

export const request = new RequestClient()
