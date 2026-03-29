import { useEffect, useState } from 'react'
import { useStore } from '../stores'
import { Plus, Edit2, Trash2, X, Copy } from 'lucide-react'
import type { Template } from '../types'

export default function Templates() {
  const { templates, teams, fetchTemplates, fetchTeams, createTemplate, updateTemplate, deleteTemplate } = useStore()
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Template | null>(null)
  const [form, setForm] = useState({ name: '', description: '', teamConfig: {} as any })

  useEffect(() => {
    fetchTemplates()
    fetchTeams()
  }, [])

  const handleSubmit = async () => {
    if (editing) {
      await updateTemplate(editing.id, form)
    } else {
      await createTemplate(form)
    }
    setShowModal(false)
    setEditing(null)
  }

  const handleEdit = (t: Template) => {
    setEditing(t)
    setForm({ name: t.name, description: t.description, teamConfig: t.teamConfig || {} })
    setShowModal(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('确认删除?')) await deleteTemplate(id)
  }

  const handleApply = (t: Template) => {
    alert('模板应用功能开发中...')
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">模板市场</h1>
        <button onClick={() => { setEditing(null); setForm({ name: '', description: '', teamConfig: {} }); setShowModal(true); }}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={18} /> 新建模板
        </button>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((t) => (
          <div key={t.id} className="bg-slate-800 rounded-xl p-5 border border-slate-700">
            <div className="flex items-start justify-between mb-3">
              <div className="font-semibold text-white">{t.name}</div>
              <div className="flex gap-1">
                <button onClick={() => handleApply(t)} className="text-green-400 hover:text-green-300 p-1" title="应用"><Copy size={16} /></button>
                <button onClick={() => handleEdit(t)} className="text-blue-400 hover:text-blue-300 p-1"><Edit2 size={16} /></button>
                <button onClick={() => handleDelete(t.id)} className="text-red-400 hover:text-red-300 p-1"><Trash2 size={16} /></button>
              </div>
            </div>
            <p className="text-sm text-slate-400 mb-3">{t.description}</p>
            <pre className="text-xs text-slate-500 bg-slate-900 rounded p-2 overflow-x-auto">
              {JSON.stringify(t.teamConfig, null, 2)}
            </pre>
          </div>
        ))}
      </div>

      {templates.length === 0 && (
        <div className="text-center text-slate-500 py-12">
          <p className="mb-2">暂无模板</p>
          <p className="text-sm">从团队创建模板，或新建空白模板</p>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">{editing ? '编辑模板' : '新建模板'}</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-400 mb-1">模板名称</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">描述</label>
                <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">团队配置 (JSON)</label>
                <textarea value={JSON.stringify(form.teamConfig, null, 2)} onChange={(e) => { try { setForm({ ...form, teamConfig: JSON.parse(e.target.value) }) } catch {} }} rows={5} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600 font-mono text-xs" />
              </div>
              <button onClick={handleSubmit} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                {editing ? '保存修改' : '创建模板'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
