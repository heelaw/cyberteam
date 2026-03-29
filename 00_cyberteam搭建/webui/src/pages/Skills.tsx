import { useEffect, useState } from 'react'
import { useStore } from '../stores'
import { Plus, Edit2, Trash2, X, Wrench, BookOpen, Tag, Clock, User, FileText, ChevronRight } from 'lucide-react'
import type { Skill } from '../types'

export default function Skills() {
  const { skills, fetchSkills, createSkill, updateSkill, deleteSkill } = useStore()
  const [showModal, setShowModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [editing, setEditing] = useState<Skill | null>(null)
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [filter, setFilter] = useState('')
  const [form, setForm] = useState({
    name: '',
    category: '',
    description: '',
    triggerConditions: '',
    usageGuide: ''
  })

  useEffect(() => { fetchSkills() }, [])

  // 动态获取所有分类
  const categories = Array.from(new Set(skills.map(s => s.category).filter(Boolean))).sort()

  const handleSubmit = async () => {
    if (editing) {
      await updateSkill(editing.id, form)
    } else {
      await createSkill(form)
    }
    setShowModal(false)
    setEditing(null)
  }

  const handleEdit = (s: Skill) => {
    setEditing(s)
    setForm({
      name: s.name,
      category: s.category,
      description: s.description,
      triggerConditions: s.triggerConditions || s.trigger || '',
      usageGuide: s.usageGuide || ''
    })
    setShowModal(true)
  }

  const handleDetail = (s: Skill) => {
    setSelectedSkill(s)
    setShowDetailModal(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('确认删除?')) await deleteSkill(id)
  }

  const filtered = skills.filter((s) => !filter || s.category === filter)

  const difficultyColor: Record<string, string> = {
    low: 'bg-green-600',
    medium: 'bg-yellow-600',
    high: 'bg-red-600',
  }

  const getDifficultyLabel = (d: string) => {
    const map: Record<string, string> = { low: '简单', medium: '中等', high: '困难' }
    return map[d] || d
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">技能配置</h1>
        <button onClick={() => {
          setEditing(null);
          setForm({ name: '', category: categories[0] || '', description: '', triggerConditions: '', usageGuide: '' });
          setShowModal(true);
        }}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={18} /> 新增技能
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <button onClick={() => setFilter('')} className={`px-3 py-1 rounded-full text-sm ${!filter ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>全部</button>
        {categories.map((c) => (
          <button key={c} onClick={() => setFilter(c)} className={`px-3 py-1 rounded-full text-sm ${filter === c ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
            {c}
          </button>
        ))}
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((s) => (
          <div key={s.id} className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-slate-500 transition-colors">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="font-semibold text-white mb-1">{s.name}</div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs px-2 py-0.5 rounded text-white bg-slate-600">{s.category}</span>
                  {s.difficulty && (
                    <span className={`text-xs px-2 py-0.5 rounded text-white ${difficultyColor[s.difficulty] || 'bg-slate-600'}`}>
                      {getDifficultyLabel(s.difficulty)}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex gap-1">
                <button onClick={() => handleDetail(s)} className="text-green-400 hover:text-green-300 p-1" title="查看详情"><BookOpen size={16} /></button>
                <button onClick={() => handleEdit(s)} className="text-blue-400 hover:text-blue-300 p-1"><Edit2 size={16} /></button>
                <button onClick={() => handleDelete(s.id)} className="text-red-400 hover:text-red-300 p-1"><Trash2 size={16} /></button>
              </div>
            </div>
            <p className="text-sm text-slate-300 mb-3 line-clamp-2">{s.description}</p>
            {s.triggerConditions && (
              <div className="text-xs text-slate-500 mb-2 flex items-start gap-1">
                <Tag size={12} className="mt-0.5 shrink-0" />
                <span className="line-clamp-1">触发: {s.triggerConditions}</span>
              </div>
            )}
            {s.tags && s.tags.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                {s.tags.slice(0, 3).map((tag, i) => (
                  <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-slate-700 text-slate-400">#{tag}</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center text-slate-500 py-12">暂无技能，点击上方按钮创建</div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedSkill && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-2xl border border-slate-700 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">{selectedSkill.name}</h2>
              <button onClick={() => setShowDetailModal(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
            </div>

            {/* 基本信息 */}
            <div className="space-y-3 mb-6">
              <div className="flex gap-2 flex-wrap">
                <span className="text-xs px-2 py-1 rounded bg-slate-600 text-white">{selectedSkill.category}</span>
                {selectedSkill.difficulty && (
                  <span className={`text-xs px-2 py-1 rounded ${difficultyColor[selectedSkill.difficulty] || 'bg-slate-600'} text-white`}>
                    {getDifficultyLabel(selectedSkill.difficulty)}
                  </span>
                )}
                {selectedSkill.version && <span className="text-xs px-2 py-1 rounded bg-slate-600 text-slate-400">v{selectedSkill.version}</span>}
              </div>

              <p className="text-sm text-slate-300">{selectedSkill.description}</p>

              {selectedSkill.triggerConditions && (
                <div className="flex items-start gap-2">
                  <Tag size={14} className="text-slate-400 mt-0.5" />
                  <div>
                    <div className="text-xs text-slate-500 mb-1">触发条件</div>
                    <div className="text-sm text-slate-300">{selectedSkill.triggerConditions}</div>
                  </div>
                </div>
              )}

              {selectedSkill.author && (
                <div className="flex items-center gap-2">
                  <User size={14} className="text-slate-400" />
                  <span className="text-sm text-slate-400">{selectedSkill.author}</span>
                </div>
              )}

              {selectedSkill.tags && selectedSkill.tags.length > 0 && (
                <div className="flex items-start gap-2">
                  <Tag size={14} className="text-slate-400 mt-0.5" />
                  <div>
                    <div className="text-xs text-slate-500 mb-1">标签</div>
                    <div className="flex gap-1 flex-wrap">
                      {selectedSkill.tags.map((tag, i) => (
                        <span key={i} className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">#{tag}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 使用指南 */}
            {selectedSkill.usageGuide && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen size={14} className="text-slate-400" />
                  <h3 className="text-sm font-medium text-white">使用指南</h3>
                </div>
                <div className="bg-slate-900 rounded-lg p-4 text-sm text-slate-300 whitespace-pre-wrap max-h-64 overflow-y-auto">
                  {selectedSkill.usageGuide}
                </div>
              </div>
            )}

            {/* 引用文档 */}
            {selectedSkill.references && selectedSkill.references.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                  <FileText size={14} className="text-slate-400" />
                  <h3 className="text-sm font-medium text-white">引用文档</h3>
                </div>
                <div className="space-y-2">
                  {selectedSkill.references.map((ref, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-300">
                      <ChevronRight size={14} />
                      <span>{ref.name}</span>
                      <span className="text-xs text-slate-500">({ref.path})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 源路径 */}
            {selectedSkill.source_path && (
              <div className="text-xs text-slate-500 flex items-center gap-1">
                <FileText size={12} />
                <span>源路径: {selectedSkill.source_path}/SKILL.md</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Edit/Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">{editing ? '编辑技能' : '新增技能'}</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-400 mb-1">技能名称</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">分类</label>
                <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600">
                  <option value="">选择分类</option>
                  {categories.map((c) => <option key={c} value={c}>{c}</option>)}
                  <option value="custom">+ 自定义分类</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">描述</label>
                <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">触发条件</label>
                <input value={form.triggerConditions} onChange={(e) => setForm({ ...form, triggerConditions: e.target.value })} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600" placeholder="触发关键词，用逗号分隔" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">使用指南</label>
                <textarea value={form.usageGuide} onChange={(e) => setForm({ ...form, usageGuide: e.target.value })} rows={5} className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 border border-slate-600" placeholder="Markdown格式的使用指南" />
              </div>
              <button onClick={handleSubmit} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                {editing ? '保存修改' : '创建技能'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
