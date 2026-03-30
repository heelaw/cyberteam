/**
 * Playground 生成器 API - 对接后端 /api/playground 端点
 *
 * 核心功能：
 * - POST /api/playground/generate - 触发 Playground 生成
 * - GET /api/playground/html/{task_id} - 获取生成的 HTML
 * - GET /api/playground/sse/{task_id} - SSE 进度流
 */
import { api } from '../clients/cyberteam'

// === Request/Response Types ===

export interface PlaygroundRequest {
  projectName: string
  projectDate: string
  funnel: {
    曝光: number
    点击: number
    注册: number
    成交: number
  }
  channels: Record<string, { 曝光: number; 成本: number; ROI: number }>
  budget: number
  riskLevel: string
  notes?: string
}

export interface PlaygroundResponse {
  task_id: string
}

export interface PlaygroundHTMLResponse {
  status?: string
  error?: string
  content?: string
}

// === API Functions ===

/**
 * 触发 Playground 生成
 * POST /api/playground/generate
 */
export async function generatePlayground(data: PlaygroundRequest): Promise<PlaygroundResponse> {
  return api<PlaygroundResponse>('POST', '/playground/generate', data)
}

/**
 * 获取生成的 HTML 内容
 * GET /api/playground/html/{task_id}
 */
export async function fetchPlaygroundHTML(taskId: string): Promise<string> {
  const baseURL = (window as any).__API_BASE_URL__ || ''
  const response = await fetch(`${baseURL}/api/playground/html/${taskId}`)
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: `HTTP ${response.status}` }))
    throw new Error(error.error || `获取失败: ${response.statusText}`)
  }
  const text = await response.text()
  // 如果返回的是 {"error": "not_found"} 等 JSON，说明还没生成完
  if (text.startsWith('{') && text.includes('"error"')) {
    try {
      const json = JSON.parse(text)
      if (json.error) throw new Error(json.error)
    } catch {}
  }
  return text
}

/**
 * 订阅 Playground 生成进度（SSE）
 * GET /api/playground/sse/{task_id}
 *
 * @param taskId - 生成任务的 task_id
 * @param callbacks - 进度回调
 * @returns 取消订阅的函数
 */
export function subscribePlaygroundSSE(
  taskId: string,
  callbacks: {
    onProgress?: (step: string, percent: number) => void
    onComplete?: (html: string) => void
    onError?: (error: string) => void
  }
): () => void {
  const baseURL = (window as any).__API_BASE_URL__ || ''
  const url = `${baseURL}/api/playground/sse/${taskId}`
  const eventSource = new EventSource(url)

  eventSource.addEventListener('progress', (e: MessageEvent) => {
    try {
      const { step, percent } = JSON.parse(e.data)
      callbacks.onProgress?.(step || '', percent || 0)
    } catch {
      callbacks.onProgress?.('处理中...', 0)
    }
  })

  eventSource.addEventListener('complete', (e: MessageEvent) => {
    try {
      const { html } = JSON.parse(e.data)
      callbacks.onComplete?.(html || '')
    } catch {
      callbacks.onError?.('解析响应失败')
    }
    eventSource.close()
  })

  eventSource.addEventListener('error', () => {
    callbacks.onError?.('SSE 连接错误')
    eventSource.close()
  })

  eventSource.onerror = () => {
    callbacks.onError?.('SSE 连接错误')
    eventSource.close()
  }

  return () => eventSource.close()
}
