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

export async function api<T>(method: string, url: string, data?: unknown): Promise<T> {
  const res = await client.request<ApiResponse<T>>({ method, url, data, params: method === 'GET' ? data : undefined })
  return res.data.data
}

export default client
