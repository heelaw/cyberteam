import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'

interface Agent {
  id: string
  name: string
  role: string
  description: string
  status: 'idle' | 'running' | 'error'
  lastActive: string
}

export default function Agents() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    setLoading(true)
    try {
      const result = await invoke<Agent[]>('list_agents')
      setAgents(result)
    } catch (e) {
      console.error('Failed to load agents:', e)
      // Use default agents
      setAgents([
        { id: '1', name: 'CEO', role: '总指挥', description: '负责决策和任务调度', status: 'idle', lastActive: '刚刚' },
        { id: '2', name: 'COO', role: '运营总监', description: '负责运营策略和执行', status: 'idle', lastActive: '刚刚' },
        { id: '3', name: 'CFO', role: '财务总监', description: '负责财务规划和预算', status: 'idle', lastActive: '刚刚' },
        { id: '4', name: 'CTO', role: '技术总监', description: '负责技术架构和开发', status: 'idle', lastActive: '刚刚' },
        { id: '5', name: '信息部', role: '信息收集', description: '负责信息采集和分析', status: 'idle', lastActive: '刚刚' },
        { id: '6', name: '质疑者', role: '质量把控', description: '负责质疑和验证', status: 'idle', lastActive: '刚刚' },
      ])
    }
    setLoading(false)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-slate-500'
    }
  }

  return (
    <div className="h-full overflow-auto p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Agent 管理</h2>
          <button
            onClick={loadAgents}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
          >
            刷新
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        ) : (
          <div className="grid gap-4">
            {agents.map(agent => (
              <div
                key={agent.id}
                className="bg-slate-800 rounded-lg p-4 border border-slate-700"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center text-2xl">
                        🤖
                      </div>
                      <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full ${getStatusColor(agent.status)} border-2 border-slate-800`}></div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-white">{agent.name}</h3>
                        <span className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300">
                          {agent.role}
                        </span>
                      </div>
                      <p className="text-sm text-slate-400 mt-1">{agent.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-500">最后活动</p>
                    <p className="text-sm text-slate-400">{agent.lastActive}</p>
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
                    启动
                  </button>
                  <button className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-sm rounded transition-colors">
                    配置
                  </button>
                  <button className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-sm rounded transition-colors">
                    日志
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
