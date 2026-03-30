/**
 * Expert Agent API - 数字员工市场
 * 调用后端 /api/expert-agents
 */
import { baseURL } from '../base'

export interface ExpertAgentProfile {
  agent_id: string
  name: string
  department: string
  description: string
  capabilities: string[]
  keywords: string[]
  avatar: string
  rating: number
  call_count: number
  avg_response_time_ms: number
  status: string
}

export async function fetchExpertMarket(department?: string): Promise<ExpertAgentProfile[]> {
  const url = department
    ? `${baseURL}/api/expert-agents?department=${encodeURIComponent(department)}`
    : `${baseURL}/api/expert-agents`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`获取失败: ${res.statusText}`)
  return res.json()
}

export async function discoverExperts(query: string): Promise<ExpertAgentProfile[]> {
  const res = await fetch(`${baseURL}/api/expert-agents/discover?q=${encodeURIComponent(query)}`)
  if (!res.ok) throw new Error(`搜索失败: ${res.statusText}`)
  return res.json()
}

export async function getExpert(agentId: string): Promise<ExpertAgentProfile> {
  const res = await fetch(`${baseURL}/api/expert-agents/${encodeURIComponent(agentId)}`)
  if (!res.ok) throw new Error(`获取失败: ${res.statusText}`)
  return res.json()
}

export async function invokeExpert(agentId: string, task: Record<string, any>): Promise<any> {
  const res = await fetch(`${baseURL}/api/expert-agents/${encodeURIComponent(agentId)}/invoke`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task)
  })
  if (!res.ok) throw new Error(`调用失败: ${res.statusText}`)
  return res.json()
}