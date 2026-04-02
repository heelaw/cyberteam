import { useEffect, useState } from 'react'
import { useStore } from '../stores'
import { Plus, Edit2, Trash2, X } from 'lucide-react'
import type { Department } from '../types'

export default function Departments() {
  const { departments, agents, fetchDepartments, fetchAgents, createDepartment, updateDepartment, deleteDepartment } = useStore()
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Department | null>(null)
  const [form, setForm] = useState({ name: '', description: '', parentId: '', rules: '' })

  useEffect(() => {
    fetchDepartments()
    fetchAgents()
  }, [])

  const handleSubmit = async () => {
    const data = {
      ...form,
      parentId: form.parentId || null,
    }
    if (editing) {
      await updateDepartment(editing.id, data)
    } else {
      await createDepartment(data)
    }
    setShowModal(false)
    setEditing(null)
    setForm({ name: '', description: '', parentId: '', rules: '' })
  }

  const handleEdit = (dept: Department) => {
    setEditing(dept)
    setForm({ name: dept.name, description: dept.description, parentId: dept.parentId || '', rules: dept.rules || '' })
    setShowModal(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('确认删除?')) await deleteDepartment(id)
  }

  const openNew = () => {
    setEditing(null)
    setForm({ name: '', description: '', parentId: '', rules: '' })
    setShowModal(true)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">部门管理</h1>
        <button onClick={openNew} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={18} />
          新增部门
        </button>
      </div>

      {/* Department Tree */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-4">组织架构</h2>
        <div className="space-y-3">
          {departments.filter((d) => !d.parentId).map((dept) => (
            <div key={dept.id}>
              <div className="flex items-center justify-between bg-slate-700 rounded-lg p-4">
                <div>
                  <div className="font-medium text-white">{dept.name}</div>
                  <div className="text-sm text-slate-400">{dept.description}</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => handleEdit(dept)} className="text-blue-400 hover:text-blue-300">
                    <Edit2 size={16} />
                  </button>
                  <button onClick={() => handleDelete(dept.id)} className="text-red-400 hover:text-red-300">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              {/* Children */}
              {departments.filter((d) => d.parentId === dept.id).map((child) => (
                <div key={child.id} className="flex items-center justify-between bg-slate-700 rounded-lg p-4 ml-8 mt-2">
                  <div>
                    <div className="font-medium text-white">{child.name}</div>
                    <div className="text-sm text-slate-400">{child.description}</div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleEdit(child)} className="text-blue-400 hover:text-blue-300">
                      <Edit2 size={16} />
                    </button>
                    <button onClick={() => handleDelete(child.id)} className="text-red-400 hover:text-red-300">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">{editing ? '编辑部门' : '新增部门'}</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">部门名称</label>
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600 focus:border-blue-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">描述</label>
                <input
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600 focus:border-blue-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">上级部门</label>
                <select
                  value={form.parentId}
                  onChange={(e) => setForm({ ...form, parentId: e.target.value })}
                  className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600 focus:border-blue-500 outline-none"
                >
                  <option value="">无（顶级部门）</option>
                  {departments.filter((d) => d.id !== editing?.id).map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">规章制度</label>
                <textarea
                  value={form.rules}
                  onChange={(e) => setForm({ ...form, rules: e.target.value })}
                  rows={3}
                  className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600 focus:border-blue-500 outline-none"
                />
              </div>
              <button onClick={handleSubmit} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                {editing ? '保存修改' : '创建部门'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
