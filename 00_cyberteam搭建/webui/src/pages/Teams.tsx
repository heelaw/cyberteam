import { useEffect, useState } from 'react'
import { useStore } from '../stores'
import { Plus, Edit2, Trash2, X } from 'lucide-react'
import type { Team } from '../types'

export default function Teams() {
  const { teams, agents, departments, fetchTeams, fetchAgents, fetchDepartments, createTeam, updateTeam, deleteTeam } = useStore()
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Team | null>(null)
  const [form, setForm] = useState({ name: '', description: '', departmentId: '', members: [] as string[], settings: { collaborationMode: 'sequential', reportCycle: 'daily' } })

  useEffect(() => {
    fetchTeams()
    fetchAgents()
    fetchDepartments()
  }, [])

  const handleSubmit = async () => {
    if (editing) {
      await updateTeam(editing.id, form)
    } else {
      await createTeam(form)
    }
    setShowModal(false)
    setEditing(null)
  }

  const handleEdit = (team: Team) => {
    setEditing(team)
    setForm({
      name: team.name,
      description: team.description,
      departmentId: team.departmentId,
      members: team.members || [],
      settings: team.settings || { collaborationMode: 'sequential', reportCycle: 'daily' },
    })
    setShowModal(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('确认删除?')) await deleteTeam(id)
  }

  const toggleMember = (agentId: string) => {
    const current = form.members
    if (current.includes(agentId)) {
      setForm({ ...form, members: current.filter((m) => m !== agentId) })
    } else {
      setForm({ ...form, members: [...current, agentId] })
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">团队构建</h1>
        <button onClick={() => { setEditing(null); setForm({ name: '', description: '', departmentId: '', members: [], settings: { collaborationMode: 'sequential', reportCycle: 'daily' } }); setShowModal(true); }}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={18} /> 新建团队
        </button>
      </div>

      {/* Teams Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {teams.map((team) => (
          <div key={team.id} className="bg-slate-800 rounded-xl p-5 border border-slate-700">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="font-semibold text-white text-lg">{team.name}</div>
                <div className="text-sm text-slate-400">{departments.find((d) => d.id === team.departmentId)?.name || '未分配'}</div>
              </div>
              <div className="flex gap-1">
                <button onClick={() => handleEdit(team)} className="text-blue-400 hover:text-blue-300 p-1"><Edit2 size={16} /></button>
                <button onClick={() => handleDelete(team.id)} className="text-red-400 hover:text-red-300 p-1"><Trash2 size={16} /></button>
              </div>
            </div>
            <p className="text-sm text-slate-300 mb-3">{team.description}</p>
            <div className="flex flex-wrap gap-1">
              {(team.members || []).map((m: string) => (
                <span key={m} className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">
                  {agents.find((a) => a.id === m)?.name || m}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {teams.length === 0 && (
        <div className="text-center text-slate-500 py-12">暂无团队，点击上方按钮创建</div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-lg border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">{editing ? '编辑团队' : '新建团队'}</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-400 mb-1">团队名称</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">描述</label>
                <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">所属部门</label>
                <select value={form.departmentId} onChange={(e) => setForm({ ...form, departmentId: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600">
                  <option value="">选择部门</option>
                  {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-2">团队成员</label>
                <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
                  {agents.map((a) => (
                    <button key={a.id} onClick={() => toggleMember(a.id)}
                      className={`text-xs px-3 py-1 rounded-full border ${form.members.includes(a.id) ? 'bg-green-600 border-green-500 text-white' : 'bg-slate-700 border-slate-600 text-slate-300'}`}>
                      {a.name}
                    </button>
                  ))}
                </div>
              </div>
              <button onClick={handleSubmit} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                {editing ? '保存修改' : '创建团队'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
