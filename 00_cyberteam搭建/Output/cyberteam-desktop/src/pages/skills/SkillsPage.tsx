import { useState, useEffect } from 'react'

interface Skill {
  id: string
  name: string
  icon: string
  category: string
  description: string
  trigger: string
  workflow: string
  agent_id: string | null
  department_id: string | null
  is_preset: number
  config: string
  created_at: string
  updated_at: string
}

const CATEGORIES = [
  { value: 'all', label: '全部', icon: '⚡' },
  { value: 'content', label: '内容', icon: '✍️' },
  { value: 'analytics', label: '数据', icon: '📊' },
  { value: 'marketing', label: '营销', icon: '📢' },
  { value: 'strategy', label: '战略', icon: '🎯' },
  { value: 'product', label: '产品', icon: '💡' },
  { value: 'management', label: '管理', icon: '📋' },
  { value: 'custom', label: '自定义', icon: '🔧' },
]

const emptySkill: Partial<Skill> = {
  name: '',
  icon: '⚡',
  category: 'custom',
  description: '',
  trigger: '',
  workflow: '',
  agent_id: null,
  department_id: null,
  is_preset: 0,
  config: '{}',
}

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Skill | null>(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState<Partial<Skill>>(emptySkill)
  const [creating, setCreating] = useState(false)

  useEffect(() => { loadData() }, [])

  async function loadData() {
    try {
      const api = window.electronAPI as any
      if (!api?.skills) return
      const list = await api.skills.list()
      setSkills(list || [])
    } catch (err) {
      console.error('Failed to load skills:', err)
    }
  }

  function startCreate() {
    setForm({ ...emptySkill })
    setCreating(true)
    setEditing(false)
    setSelected(null)
  }

  function startEdit(skill: Skill) {
    setForm({ ...skill })
    setEditing(true)
    setCreating(false)
  }

  async function handleSave() {
    try {
      const api = window.electronAPI as any
      if (!api?.skills) return

      if (creating) {
        await api.skills.create(form)
      } else if (editing && form.id) {
        await api.skills.update(form.id, form)
      }

      setCreating(false)
      setEditing(false)
      setForm({ ...emptySkill })
      await loadData()
    } catch (err) {
      console.error('Save failed:', err)
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('确定删除此 Skill？')) return
    try {
      const api = window.electronAPI as any
      if (!api?.skills) return
      await api.skills.delete(id)
      if (selected?.id === id) setSelected(null)
      await loadData()
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  function cancelEdit() {
    setCreating(false)
    setEditing(false)
    setForm({ ...emptySkill })
  }

  // Filtered skills
  const filtered = skills.filter(s => {
    if (filter !== 'all' && s.category !== filter) return false
    if (search) {
      const q = search.toLowerCase()
      return s.name.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q) ||
        (s.trigger || '').toLowerCase().includes(q)
    }
    return true
  })

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0f', color: '#fff' }}>
      {/* Left: list */}
      <div style={{ width: 280, borderRight: '1px solid #1f2937', display: 'flex', flexDirection: 'column', background: '#111827' }}>
        {/* Header */}
        <div style={{ padding: '16px', borderBottom: '1px solid #1f2937' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <span style={{ fontSize: 20 }}>⚡</span>
            <span style={{ fontSize: 16, fontWeight: 600 }}>Skill 管理</span>
          </div>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="搜索 Skill..."
            style={{ width: '100%', padding: '8px 12px', background: '#1f2937', border: '1px solid #374151', borderRadius: 6, color: '#fff', fontSize: 13, outline: 'none' }}
          />
        </div>

        {/* Categories */}
        <div style={{ padding: '8px 12px', borderBottom: '1px solid #1f2937', display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {CATEGORIES.map(c => (
            <button
              key={c.value}
              onClick={() => setFilter(c.value)}
              style={{
                padding: '4px 10px',
                fontSize: 11,
                borderRadius: 4,
                border: 'none',
                cursor: 'pointer',
                background: filter === c.value ? '#3b82f6' : '#1f2937',
                color: filter === c.value ? '#fff' : '#9ca3af',
              }}
            >
              {c.icon} {c.label}
            </button>
          ))}
        </div>

        {/* List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 8 }}>
          {filtered.map(s => (
            <div
              key={s.id}
              onClick={() => { setSelected(s); setCreating(false); setEditing(false); }}
              style={{
                padding: '10px 12px',
                borderRadius: 8,
                cursor: 'pointer',
                marginBottom: 4,
                background: selected?.id === s.id ? '#1f2937' : 'transparent',
                borderLeft: selected?.id === s.id ? '3px solid #3b82f6' : '3px solid transparent',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 18 }}>{s.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 500 }}>{s.name}</div>
                  <div style={{ fontSize: 11, color: '#6b7280' }}>{s.category} {s.is_preset ? '· 预设' : ''}</div>
                </div>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div style={{ padding: 40, textAlign: 'center', color: '#6b7280', fontSize: 13 }}>
              暂无 Skill
            </div>
          )}
        </div>

        {/* Create button */}
        <div style={{ padding: 12, borderTop: '1px solid #1f2937' }}>
          <button
            onClick={startCreate}
            style={{ width: '100%', padding: 10, background: '#3b82f6', border: 'none', borderRadius: 8, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
          >
            + 新建 Skill
          </button>
        </div>
      </div>

      {/* Right: detail / edit */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
        {(creating || editing) ? (
          /* Edit form */
          <div style={{ maxWidth: 600 }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24 }}>
              {creating ? '✨ 新建 Skill' : `✏️ 编辑: ${form.name}`}
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: 12, color: '#9ca3af', marginBottom: 4, display: 'block' }}>名称</label>
                  <input value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} style={inputStyle} placeholder="Skill 名称" />
                </div>
                <div style={{ width: 80 }}>
                  <label style={{ fontSize: 12, color: '#9ca3af', marginBottom: 4, display: 'block' }}>图标</label>
                  <input value={form.icon || ''} onChange={e => setForm({ ...form, icon: e.target.value })} style={inputStyle} />
                </div>
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#9ca3af', marginBottom: 4, display: 'block' }}>分类</label>
                <select value={form.category || 'custom'} onChange={e => setForm({ ...form, category: e.target.value })} style={{ ...inputStyle, background: '#1f2937' }}>
                  {CATEGORIES.filter(c => c.value !== 'all').map(c => (
                    <option key={c.value} value={c.value}>{c.icon} {c.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#9ca3af', marginBottom: 4, display: 'block' }}>描述</label>
                <textarea value={form.description || ''} onChange={e => setForm({ ...form, description: e.target.value })} rows={2} style={{ ...inputStyle, resize: 'vertical' }} placeholder="Skill 功能描述..." />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#9ca3af', marginBottom: 4, display: 'block' }}>触发词（空格分隔）</label>
                <input value={form.trigger || ''} onChange={e => setForm({ ...form, trigger: e.target.value })} style={inputStyle} placeholder="内容创作 / 文案 / 种草笔记" />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#9ca3af', marginBottom: 4, display: 'block' }}>工作流程</label>
                <textarea value={form.workflow || ''} onChange={e => setForm({ ...form, workflow: e.target.value })} rows={6} style={{ ...inputStyle, resize: 'vertical', fontFamily: 'monospace', fontSize: 12 }} placeholder="1. 步骤一&#10;2. 步骤二&#10;3. 步骤三" />
              </div>

              <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                <button onClick={handleSave} style={{ padding: '10px 24px', background: '#3b82f6', border: 'none', borderRadius: 6, color: '#fff', fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>
                  {creating ? '创建' : '保存'}
                </button>
                <button onClick={cancelEdit} style={{ padding: '10px 24px', background: '#374151', border: 'none', borderRadius: 6, color: '#fff', fontSize: 13, cursor: 'pointer' }}>
                  取消
                </button>
              </div>
            </div>
          </div>
        ) : selected ? (
          /* Detail view */
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
              <span style={{ fontSize: 48 }}>{selected.icon}</span>
              <div>
                <h2 style={{ fontSize: 22, fontWeight: 600 }}>{selected.name}</h2>
                <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
                  <span style={{ fontSize: 11, padding: '2px 8px', background: '#1f2937', borderRadius: 4, color: '#60a5fa' }}>{selected.category}</span>
                  {selected.is_preset ? <span style={{ fontSize: 11, padding: '2px 8px', background: '#1f2937', borderRadius: 4, color: '#f59e0b' }}>预设</span> : null}
                </div>
              </div>
            </div>

            <div style={{ background: '#111827', borderRadius: 12, padding: 20, marginBottom: 16, border: '1px solid #1f2937' }}>
              <h3 style={{ fontSize: 13, color: '#9ca3af', marginBottom: 8 }}>描述</h3>
              <p style={{ fontSize: 14, lineHeight: 1.6 }}>{selected.description || '暂无描述'}</p>
            </div>

            {selected.trigger && (
              <div style={{ background: '#111827', borderRadius: 12, padding: 20, marginBottom: 16, border: '1px solid #1f2937' }}>
                <h3 style={{ fontSize: 13, color: '#9ca3af', marginBottom: 8 }}>触发词</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {selected.trigger.split(/[\/,，、]/).map((t, i) => t.trim() && (
                    <span key={i} style={{ fontSize: 12, padding: '4px 10px', background: '#1f2937', borderRadius: 6, color: '#60a5fa' }}>{t.trim()}</span>
                  ))}
                </div>
              </div>
            )}

            {selected.workflow && (
              <div style={{ background: '#111827', borderRadius: 12, padding: 20, marginBottom: 16, border: '1px solid #1f2937' }}>
                <h3 style={{ fontSize: 13, color: '#9ca3af', marginBottom: 8 }}>工作流程</h3>
                <pre style={{ fontSize: 13, lineHeight: 1.8, fontFamily: 'monospace', color: '#e5e7eb', whiteSpace: 'pre-wrap' }}>{selected.workflow}</pre>
              </div>
            )}

            <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
              <button onClick={() => startEdit(selected)} style={{ padding: '10px 20px', background: '#3b82f6', border: 'none', borderRadius: 6, color: '#fff', fontSize: 13, cursor: 'pointer' }}>
                ✏️ 编辑
              </button>
              {!selected.is_preset && (
                <button onClick={() => handleDelete(selected.id)} style={{ padding: '10px 20px', background: '#991b1b', border: 'none', borderRadius: 6, color: '#fff', fontSize: 13, cursor: 'pointer' }}>
                  🗑️ 删除
                </button>
              )}
            </div>
          </div>
        ) : (
          /* Empty state */
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#6b7280' }}>
            <span style={{ fontSize: 48, marginBottom: 16 }}>⚡</span>
            <p style={{ fontSize: 16 }}>选择或创建一个 Skill</p>
            <button onClick={startCreate} style={{ marginTop: 16, padding: '10px 20px', background: '#3b82f6', border: 'none', borderRadius: 8, color: '#fff', fontSize: 13, cursor: 'pointer' }}>
              + 新建 Skill
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 12px',
  background: '#1f2937',
  border: '1px solid #374151',
  borderRadius: 6,
  color: '#fff',
  fontSize: 13,
  outline: 'none',
}
