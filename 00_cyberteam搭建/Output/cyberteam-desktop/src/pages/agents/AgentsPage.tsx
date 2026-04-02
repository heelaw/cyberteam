import { useState, useEffect } from 'react'
import type { Agent, Department } from '../../types/electron.d'

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      const [agentList, deptList] = await Promise.all([
        window.electronAPI.agents.list(),
        window.electronAPI.departments.list(),
      ])
      setAgents(agentList || [])
      setDepartments(deptList || [])
    } catch (err) {
      console.error('Failed to load data:', err)
    }
  }

  async function createAgent(data: Partial<Agent>) {
    try {
      const agent = await window.electronAPI.agents.create(data)
      setAgents([...agents, agent])
      setSelectedAgent(agent)
      setIsEditing(false)
    } catch (err) {
      console.error('Failed to create agent:', err)
    }
  }

  async function updateAgent(id: string, data: Record<string, unknown>) {
    try {
      const agent = await window.electronAPI.agents.update(id, data)
      if (agent) {
        setAgents(agents.map((a) => (a.id === id ? agent : a)))
        setSelectedAgent(agent)
      }
      setIsEditing(false)
    } catch (err) {
      console.error('Failed to update agent:', err)
    }
  }

  async function deleteAgent(id: string) {
    try {
      await window.electronAPI.agents.delete(id)
      setAgents(agents.filter((a) => a.id !== id))
      if (selectedAgent?.id === id) {
        setSelectedAgent(null)
      }
    } catch (err) {
      console.error('Failed to delete agent:', err)
    }
  }

  function getDeptName(deptId: string) {
    const dept = departments.find((d) => d.id === deptId)
    return dept ? `${dept.icon} ${dept.name}` : '未知部门'
  }

  return (
    <div className="flex h-full">
      {/* 左侧 Agent 列表 */}
      <div className="w-72 bg-[#111118] border-r border-[#2a2a3a] flex flex-col">
        <div className="p-4 border-b border-[#2a2a3a]">
          <h2 className="text-white font-semibold">Agent 列表</h2>
          <p className="text-xs text-[#606070] mt-1">{agents.length} 个 Agent</p>
        </div>

        <div className="flex-1 overflow-y-auto">
          {agents.map((agent) => (
            <div
              key={agent.id}
              onClick={() => {
                setSelectedAgent(agent)
                setIsEditing(false)
              }}
              className={`p-4 cursor-pointer border-b border-[#2a2a3a] transition-colors ${
                selectedAgent?.id === agent.id ? 'bg-[#1a1a24]' : 'hover:bg-[#1a1a24]'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="agent-avatar">{agent.avatar || '🤖'}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-white font-medium truncate">{agent.name}</span>
                    <span
                      className={`status-dot ${
                        agent.status === 'online'
                          ? 'online'
                          : agent.status === 'busy'
                          ? 'busy'
                          : 'offline'
                      }`}
                    />
                  </div>
                  <div className="text-xs text-[#606070] truncate mt-1">
                    {getDeptName(agent.department_id)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-[#2a2a3a]">
          <button
            onClick={() => {
              setSelectedAgent(null)
              setIsEditing(true)
            }}
            className="w-full btn btn-primary text-sm"
          >
            + 创建 Agent
          </button>
        </div>
      </div>

      {/* 右侧详情区 */}
      <div className="flex-1 overflow-y-auto p-6">
        {isEditing ? (
          <div className="max-w-lg">
            <h3 className="text-white text-lg font-semibold mb-6">创建 Agent</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-[#a0a0b0] mb-1">名称</label>
                  <input
                    type="text"
                    value={selectedAgent?.name || ''}
                    onChange={(e) =>
                      setSelectedAgent({ ...(selectedAgent || {} as Agent), name: e.target.value } as Agent)
                    }
                    className="w-full"
                    placeholder="Agent 名称"
                  />
                </div>

                <div>
                  <label className="block text-sm text-[#a0a0b0] mb-1">头像</label>
                  <input
                    type="text"
                    value={selectedAgent?.avatar || ''}
                    onChange={(e) =>
                      setSelectedAgent({ ...(selectedAgent || {} as Agent), avatar: e.target.value } as Agent)
                    }
                    className="w-full"
                    placeholder="🤖"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">部门</label>
                <select
                  value={selectedAgent?.department_id || ''}
                  onChange={(e) =>
                    setSelectedAgent({ ...(selectedAgent || {} as Agent), department_id: e.target.value } as Agent)
                  }
                  className="w-full"
                >
                  <option value="">选择部门</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.icon} {dept.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">角色</label>
                <select
                  value={selectedAgent?.role || 'expert'}
                  onChange={(e) =>
                    setSelectedAgent({ ...(selectedAgent || {} as Agent), role: e.target.value as Agent['role'] } as Agent)
                  }
                  className="w-full"
                >
                  <option value="ceo">CEO</option>
                  <option value="manager">Manager</option>
                  <option value="expert">Expert</option>
                  <option value="executor">Executor</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">描述</label>
                <textarea
                  value={selectedAgent?.description || ''}
                  onChange={(e) =>
                    setSelectedAgent({ ...(selectedAgent || {} as Agent), description: e.target.value } as Agent)
                  }
                  className="w-full h-20 resize-none"
                  placeholder="Agent 职责描述..."
                />
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">SOUL (系统提示词)</label>
                <textarea
                  value={selectedAgent?.soul_content || ''}
                  onChange={(e) =>
                    setSelectedAgent({ ...(selectedAgent || {} as Agent), soul_content: e.target.value } as Agent)
                  }
                  className="w-full h-32 resize-none font-mono text-sm"
                  placeholder="定义 Agent 的灵魂和行事风格..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() =>
                    createAgent({
                      name: selectedAgent?.name || '新 Agent',
                      avatar: selectedAgent?.avatar || '🤖',
                      role: selectedAgent?.role || 'expert',
                      department_id: selectedAgent?.department_id || departments[0]?.id || '',
                      description: selectedAgent?.description || '',
                      soul_content: selectedAgent?.soul_content || '',
                    })
                  }
                  className="btn btn-primary"
                >
                  创建
                </button>
                <button onClick={() => setIsEditing(false)} className="btn btn-secondary">
                  取消
                </button>
              </div>
            </div>
          </div>
        ) : selectedAgent ? (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="agent-avatar text-2xl">{selectedAgent.avatar || '🤖'}</div>
                <div>
                  <h3 className="text-white text-xl font-semibold">{selectedAgent.name}</h3>
                  <p className="text-[#606070] text-sm mt-1">
                    {getDeptName(selectedAgent.department_id)} · {selectedAgent.role}
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setIsEditing(true)}
                  className="btn btn-secondary text-sm"
                >
                  编辑
                </button>
                <button
                  onClick={() => deleteAgent(selectedAgent.id)}
                  className="btn btn-danger text-sm"
                >
                  删除
                </button>
              </div>
            </div>

            <div className="space-y-6">
              <div className="card">
                <h4 className="text-white font-medium mb-2">描述</h4>
                <p className="text-[#a0a0b0]">
                  {selectedAgent.description || '暂无描述'}
                </p>
              </div>

              <div className="card">
                <h4 className="text-white font-medium mb-2">SOUL</h4>
                <pre className="text-sm text-[#a0a0b0] whitespace-pre-wrap font-sans">
                  {selectedAgent.soul_content || '暂无 SOUL 定义'}
                </pre>
              </div>

              <div className="card">
                <h4 className="text-white font-medium mb-2">状态</h4>
                <div className="flex items-center gap-2">
                  <span
                    className={`status-dot ${
                      selectedAgent.status === 'online'
                        ? 'online'
                        : selectedAgent.status === 'busy'
                        ? 'busy'
                        : 'offline'
                    }`}
                  />
                  <span className="text-[#a0a0b0] capitalize">{selectedAgent.status}</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-[#606070]">
            <p className="text-lg mb-2">🤖 选择一个 Agent</p>
            <p className="text-sm">查看或编辑 Agent 详情</p>
          </div>
        )}
      </div>
    </div>
  )
}
