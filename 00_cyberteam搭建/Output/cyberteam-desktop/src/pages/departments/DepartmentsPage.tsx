import { useState, useEffect } from 'react'
import type { Department, Agent } from '../../types/electron.d'

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedDept, setSelectedDept] = useState<Department | null>(null)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      const [deptList, agentList] = await Promise.all([
        window.electronAPI.departments.list(),
        window.electronAPI.agents.list(),
      ])
      setDepartments(deptList || [])
      setAgents(agentList || [])
    } catch (err) {
      console.error('Failed to load data:', err)
    }
  }

  async function createDepartment(data: Partial<Department>) {
    try {
      const dept = await window.electronAPI.departments.create(data)
      setDepartments([...departments, dept])
      setSelectedDept(dept)
      setIsEditing(false)
    } catch (err) {
      console.error('Failed to create department:', err)
    }
  }

  async function updateDepartment(id: string, data: Record<string, unknown>) {
    try {
      const dept = await window.electronAPI.departments.update(id, data)
      if (dept) {
        setDepartments(departments.map((d) => (d.id === id ? dept : d)))
        setSelectedDept(dept)
      }
      setIsEditing(false)
    } catch (err) {
      console.error('Failed to update department:', err)
    }
  }

  async function deleteDepartment(id: string) {
    try {
      await window.electronAPI.departments.delete(id)
      setDepartments(departments.filter((d) => d.id !== id))
      if (selectedDept?.id === id) {
        setSelectedDept(null)
      }
    } catch (err) {
      console.error('Failed to delete department:', err)
    }
  }

  const deptAgents = selectedDept
    ? agents.filter((a) => a.department_id === selectedDept.id)
    : []

  return (
    <div className="flex h-full">
      {/* 左侧部门列表 */}
      <div className="w-72 bg-[#111118] border-r border-[#2a2a3a] flex flex-col">
        <div className="p-4 border-b border-[#2a2a3a]">
          <h2 className="text-white font-semibold">部门架构</h2>
        </div>

        <div className="flex-1 overflow-y-auto">
          {departments.map((dept) => (
            <div
              key={dept.id}
              onClick={() => {
                setSelectedDept(dept)
                setIsEditing(false)
              }}
              className={`p-4 cursor-pointer border-b border-[#2a2a3a] transition-colors ${
                selectedDept?.id === dept.id ? 'bg-[#1a1a24]' : 'hover:bg-[#1a1a24]'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{dept.icon || '🏢'}</span>
                <span className="text-white font-medium">{dept.name}</span>
              </div>
              <div className="text-xs text-[#606070] mt-2">
                {agents.filter((a) => a.department_id === dept.id).length} 个 Agent
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-[#2a2a3a]">
          <button
            onClick={() => {
              setSelectedDept(null)
              setIsEditing(true)
            }}
            className="w-full btn btn-primary text-sm"
          >
            + 添加部门
          </button>
        </div>
      </div>

      {/* 右侧详情区 */}
      <div className="flex-1 overflow-y-auto p-6">
        {isEditing ? (
          <div className="max-w-lg">
            <h3 className="text-white text-lg font-semibold mb-6">新建部门</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">部门名称</label>
                <input
                  type="text"
                  value={selectedDept?.name || ''}
                  onChange={(e) =>
                    setSelectedDept({ ...(selectedDept || {} as Department), name: e.target.value } as Department)
                  }
                  className="w-full"
                  placeholder="例如：增长部"
                />
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">图标</label>
                <input
                  type="text"
                  value={selectedDept?.icon || ''}
                  onChange={(e) =>
                    setSelectedDept({ ...(selectedDept || {} as Department), icon: e.target.value } as Department)
                  }
                  className="w-full"
                  placeholder="例如：🚀"
                />
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">描述</label>
                <textarea
                  value={selectedDept?.description || ''}
                  onChange={(e) =>
                    setSelectedDept({ ...(selectedDept || {} as Department), description: e.target.value } as Department)
                  }
                  className="w-full h-20 resize-none"
                  placeholder="部门职责描述..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() =>
                    createDepartment({
                      name: selectedDept?.name || '新部门',
                      icon: selectedDept?.icon || '🏢',
                      description: selectedDept?.description || '',
                    })
                  }
                  className="btn btn-primary"
                >
                  创建
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  className="btn btn-secondary"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        ) : selectedDept ? (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <span className="text-4xl">{selectedDept.icon || '🏢'}</span>
                <div>
                  <h3 className="text-white text-xl font-semibold">{selectedDept.name}</h3>
                  <p className="text-[#606070] text-sm mt-1">
                    {selectedDept.description || '暂无描述'}
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
                  onClick={() => deleteDepartment(selectedDept.id)}
                  className="btn btn-danger text-sm"
                >
                  删除
                </button>
              </div>
            </div>

            {/* 部门成员 */}
            <div className="mt-8">
              <h4 className="text-white font-medium mb-4">部门成员 ({deptAgents.length})</h4>

              {deptAgents.length === 0 ? (
                <div className="card text-center py-8">
                  <p className="text-[#606070]">暂无成员</p>
                  <p className="text-[#606070] text-sm mt-1">
                    在 Agent 页面添加成员到此部门
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {deptAgents.map((agent) => (
                    <div key={agent.id} className="card flex items-center gap-3">
                      <div className="agent-avatar">
                        {agent.avatar || '🤖'}
                      </div>
                      <div>
                        <div className="text-white font-medium">{agent.name}</div>
                        <div className="text-xs text-[#606070]">{agent.role}</div>
                      </div>
                      <span
                        className={`status-dot ml-auto ${
                          agent.status === 'online'
                            ? 'online'
                            : agent.status === 'busy'
                            ? 'busy'
                            : 'offline'
                        }`}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-[#606070]">
            <p className="text-lg mb-2">🏢 选择一个部门</p>
            <p className="text-sm">查看部门详情和成员</p>
          </div>
        )}
      </div>
    </div>
  )
}
