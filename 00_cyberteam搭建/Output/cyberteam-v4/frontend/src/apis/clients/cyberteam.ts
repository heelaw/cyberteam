import axios from 'axios'
import type { ApiResponse } from '@/types'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器：自动加 JWT
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('cyberteam_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('cyberteam_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'

export async function api<T>(method: HttpMethod, url: string, data?: unknown): Promise<T> {
  const res = await client.request<ApiResponse<T> | T>({ method, url, data, params: method === 'GET' ? data : undefined })
  // 兼容两种响应格式：{code, data, message} 或 裸数组/对象
  const body = res.data as Record<string, unknown>
  if (body && 'code' in body && 'data' in body) {
    const code = body.code as number
    if (code < 200 || code >= 300) {
      throw new Error((body.message as string) || `API error: code ${code}`)
    }
    return body.data as T
  }
  return res.data as T
}

export default client
