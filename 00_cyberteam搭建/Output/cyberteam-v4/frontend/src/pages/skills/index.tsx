/**
 * Skill 配置管理页面
 * 功能：Skill CRUD、筛选、详情、执行
 */
import { useState, useEffect } from 'react'
import {
  fetchSkills,
  fetchSkillCategories,
  fetchSkill,
  createSkill,
  updateSkill,
  deleteSkill,
  fetchSkillAgents,
  executeSkill,
  type Skill,
  type SkillCategory,
  type SkillCreate,
  type SkillUpdate,
  type AgentBrief
} from '@/apis/modules/skills'

const DIFFICULTY_OPTIONS = ['easy', 'medium', 'hard', 'expert']
const CATEGORY_OPTIONS = ['custom', 'communication', 'analysis', 'creation', 'automation', 'integration']

export default function SkillsPage() {
  // 列表状态
  const [skills, setSkills] = useState<Skill[]>([])
  const [categories, setCategories] = useState<SkillCategory[]>([])
  const [loading, setLoading] = useState(false)

  // 筛选状态
  const [filterCategory, setFilterCategory] = useState<string>('')
  const [filterDifficulty, setFilterDifficulty] = useState<string>('')

  // 模态框状态
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showAgentsModal, setShowAgentsModal] = useState(false)
  const [showExecuteModal, setShowExecuteModal] = useState(false)

  // 当前操作的 Skill
  const [currentSkill, setCurrentSkill] = useState<Skill | null>(null)
  const [currentSkillAgents, setCurrentSkillAgents] = useState<AgentBrief[]>([])

  // 表单状态
  const [formData, setFormData] = useState<SkillCreate>({
    name: '',
    code: '',
    description: '',
    category: 'custom',
    difficulty: 'medium',
    trigger_keywords: [],
    success_metrics: {},
    config: {}
  })
  const [editFormData, setEditFormData] = useState<SkillUpdate>({})
  const [executeInput, setExecuteInput] = useState('')
  const [executeResult, setExecuteResult] = useState<string>('')

  // 触发关键词输入
  const [keywordInput, setKeywordInput] = useState('')
  const [keywordInputEdit, setKeywordInputEdit] = useState('')

  // 加载数据
  useEffect(() => {
    loadData()
  }, [filterCategory, filterDifficulty])

  async function loadData() {
    setLoading(true)
    try {
      const [skillsData, categoriesData] = await Promise.all([
        fetchSkills({
          category: filterCategory || undefined,
          difficulty: filterDifficulty || undefined
        }),
        fetchSkillCategories()
      ])
      setSkills(skillsData)
      setCategories(categoriesData)
    } catch (err) {
      console.error('加载失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 创建 Skill
  async function handleCreate() {
    try {
      await createSkill(formData)
      setShowCreateModal(false)
      resetForm()
      loadData()
    } catch (err) {
      console.error('创建失败:', err)
      alert(`创建失败: ${err}`)
    }
  }

  // 更新 Skill
  async function handleUpdate() {
    if (!currentSkill) return
    try {
      await updateSkill(currentSkill.code, editFormData)
      setShowEditModal(false)
      setCurrentSkill(null)
      loadData()
    } catch (err) {
      console.error('更新失败:', err)
      alert(`更新失败: ${err}`)
    }
  }

  // 删除 Skill
  async function handleDelete(skillCode: string) {
    if (!confirm(`确定删除 Skill "${skillCode}" 吗？`)) return
    try {
      await deleteSkill(skillCode)
      loadData()
    } catch (err) {
      console.error('删除失败:', err)
      alert(`删除失败: ${err}`)
    }
  }

  // 查看详情
  async function handleShowDetail(skillCode: string) {
    try {
      const skill = await fetchSkill(skillCode)
      setCurrentSkill(skill)
      setShowDetailModal(true)
    } catch (err) {
      console.error('获取详情失败:', err)
    }
  }

  // 查看使用此 Skill 的 Agent
  async function handleShowAgents(skillCode: string) {
    try {
      const agents = await fetchSkillAgents(skillCode)
      setCurrentSkillAgents(agents)
      setShowAgentsModal(true)
    } catch (err) {
      console.error('获取 Agent 列表失败:', err)
    }
  }

  // 执行 Skill
  async function handleExecute() {
    if (!currentSkill || !executeInput.trim()) return
    try {
      const result = await executeSkill(currentSkill.code, { input: executeInput })
      setExecuteResult(JSON.stringify(result, null, 2))
    } catch (err) {
      console.error('执行失败:', err)
      setExecuteResult(`执行失败: ${err}`)
    }
  }

  // 打开编辑弹窗
  function openEditModal(skill: Skill) {
    setCurrentSkill(skill)
    setEditFormData({
      name: skill.name,
      description: skill.description || '',
      category: skill.category,
      difficulty: skill.difficulty,
      trigger_keywords: skill.trigger_keywords,
      success_metrics: skill.success_metrics,
      config: skill.config
    })
    setKeywordInputEdit(skill.trigger_keywords.join(', '))
    setShowEditModal(true)
  }

  // 打开执行弹窗
  function openExecuteModal(skill: Skill) {
    setCurrentSkill(skill)
    setExecuteInput('')
    setExecuteResult('')
    setShowExecuteModal(true)
  }

  // 重置表单
  function resetForm() {
    setFormData({
      name: '',
      code: '',
      description: '',
      category: 'custom',
      difficulty: 'medium',
      trigger_keywords: [],
      success_metrics: {},
      config: {}
    })
    setKeywordInput('')
  }

  // 处理关键词添加
  function addKeyword(isEdit = false) {
    const input = isEdit ? keywordInputEdit : keywordInput
    const keywords = input.split(',').map(k => k.trim()).filter(k => k)
    if (isEdit) {
      setEditFormData(prev => ({ ...prev, trigger_keywords: keywords }))
      setKeywordInputEdit('')
    } else {
      setFormData(prev => ({ ...prev, trigger_keywords: keywords }))
      setKeywordInput('')
    }
  }

  // 难度标签颜色
  const difficultyColor = (d: string) => {
    const colors: Record<string, string> = {
      easy: 'green',
      medium: 'yellow',
      hard: 'orange',
      expert: 'red'
    }
    return colors[d] || 'gray'
  }

  return (
    <div className="skills-page">
      <h1>Skill 配置管理</h1>

      {/* 筛选栏 */}
      <div className="filters">
        <select
          value={filterCategory}
          onChange={e => setFilterCategory(e.target.value)}
        >
          <option value="">全部分类</option>
          {categories.map(cat => (
            <option key={cat.category} value={cat.category}>
              {cat.category} ({cat.count})
            </option>
          ))}
        </select>

        <select
          value={filterDifficulty}
          onChange={e => setFilterDifficulty(e.target.value)}
        >
          <option value="">全部难度</option>
          {DIFFICULTY_OPTIONS.map(d => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>

        <button onClick={() => setShowCreateModal(true)}>
          创建 Skill
        </button>
      </div>

      {/* Skill 列表 */}
      {loading ? (
        <div>加载中...</div>
      ) : (
        <table className="skills-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>Code</th>
              <th>分类</th>
              <th>难度</th>
              <th>触发关键词</th>
              <th>关联Agent</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {skills.map(skill => (
              <tr key={skill.code}>
                <td>{skill.name}</td>
                <td><code>{skill.code}</code></td>
                <td>{skill.category}</td>
                <td>
                  <span className={`badge badge-${difficultyColor(skill.difficulty)}`}>
                    {skill.difficulty}
                  </span>
                </td>
                <td>
                  <div className="keywords">
                    {skill.trigger_keywords.slice(0, 3).map(k => (
                      <span key={k} className="keyword-tag">{k}</span>
                    ))}
                    {skill.trigger_keywords.length > 3 && (
                      <span className="keyword-more">+{skill.trigger_keywords.length - 3}</span>
                    )}
                  </div>
                </td>
                <td>
                  <button
                    className="link-btn"
                    onClick={() => handleShowAgents(skill.code)}
                  >
                    {skill.agent_count} 个Agent
                  </button>
                </td>
                <td>
                  <button onClick={() => handleShowDetail(skill.code)}>详情</button>
                  <button onClick={() => openEditModal(skill)}>编辑</button>
                  <button onClick={() => openExecuteModal(skill)}>执行</button>
                  <button className="danger" onClick={() => handleDelete(skill.code)}>删除</button>
                </td>
              </tr>
            ))}
            {skills.length === 0 && (
              <tr>
                <td colSpan={7} className="empty">暂无 Skill</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      {/* 创建弹窗 */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>创建 Skill</h2>
            <form onSubmit={e => { e.preventDefault(); handleCreate() }}>
              <div className="form-group">
                <label>名称 *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>

              <div className="form-group">
                <label>Code *</label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={e => setFormData(prev => ({ ...prev, code: e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, '') }))}
                  pattern="^[a-z0-9_-]+$"
                  placeholder="my-skill"
                  required
                />
              </div>

              <div className="form-group">
                <label>描述</label>
                <textarea
                  value={formData.description || ''}
                  onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>分类</label>
                  <select
                    value={formData.category}
                    onChange={e => setFormData(prev => ({ ...prev, category: e.target.value }))}
                  >
                    {CATEGORY_OPTIONS.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>难度</label>
                  <select
                    value={formData.difficulty}
                    onChange={e => setFormData(prev => ({ ...prev, difficulty: e.target.value }))}
                  >
                    {DIFFICULTY_OPTIONS.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>触发关键词（逗号分隔）</label>
                <input
                  type="text"
                  value={keywordInput}
                  onChange={e => setKeywordInput(e.target.value)}
                  placeholder="关键词1, 关键词2, ..."
                />
                <button type="button" onClick={() => addKeyword(false)}>添加</button>
                {(formData.trigger_keywords?.length ?? 0) > 0 && (
                  <div className="keywords-preview">
                    {(formData.trigger_keywords ?? []).map(k => (
                      <span key={k} className="keyword-tag">{k}</span>
                    ))}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>成功指标（JSON）</label>
                <textarea
                  value={JSON.stringify(formData.success_metrics || {})}
                  onChange={e => {
                    try {
                      setFormData(prev => ({ ...prev, success_metrics: JSON.parse(e.target.value) }))
                    } catch {}
                  }}
                  placeholder='{"metric": "value"}'
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)}>取消</button>
                <button type="submit">创建</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 详情弹窗 */}
      {showDetailModal && currentSkill && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>Skill 详情</h2>
            <div className="detail-grid">
              <div className="detail-item">
                <label>名称</label>
                <span>{currentSkill.name}</span>
              </div>
              <div className="detail-item">
                <label>Code</label>
                <code>{currentSkill.code}</code>
              </div>
              <div className="detail-item">
                <label>分类</label>
                <span>{currentSkill.category}</span>
              </div>
              <div className="detail-item">
                <label>难度</label>
                <span className={`badge badge-${difficultyColor(currentSkill.difficulty)}`}>
                  {currentSkill.difficulty}
                </span>
              </div>
              <div className="detail-item">
                <label>触发关键词</label>
                <div className="keywords">
                  {currentSkill.trigger_keywords.map(k => (
                    <span key={k} className="keyword-tag">{k}</span>
                  ))}
                </div>
              </div>
              <div className="detail-item">
                <label>描述</label>
                <span>{currentSkill.description || '-'}</span>
              </div>
              <div className="detail-item">
                <label>成功指标</label>
                <pre>{JSON.stringify(currentSkill.success_metrics, null, 2)}</pre>
              </div>
              <div className="detail-item">
                <label>关联 Agent</label>
                <button className="link-btn" onClick={() => { setShowDetailModal(false); handleShowAgents(currentSkill.code) }}>
                  {currentSkill.agent_count} 个Agent
                </button>
              </div>
              <div className="detail-item">
                <label>创建时间</label>
                <span>{new Date(currentSkill.created_at).toLocaleString()}</span>
              </div>
              <div className="detail-item">
                <label>更新时间</label>
                <span>{new Date(currentSkill.updated_at).toLocaleString()}</span>
              </div>
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowDetailModal(false)}>关闭</button>
            </div>
          </div>
        </div>
      )}

      {/* 编辑弹窗 */}
      {showEditModal && currentSkill && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>编辑 Skill</h2>
            <form onSubmit={e => { e.preventDefault(); handleUpdate() }}>
              <div className="form-group">
                <label>名称</label>
                <input
                  type="text"
                  value={editFormData.name || ''}
                  onChange={e => setEditFormData(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>

              <div className="form-group">
                <label>描述</label>
                <textarea
                  value={editFormData.description || ''}
                  onChange={e => setEditFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>分类</label>
                  <select
                    value={editFormData.category || ''}
                    onChange={e => setEditFormData(prev => ({ ...prev, category: e.target.value }))}
                  >
                    {CATEGORY_OPTIONS.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>难度</label>
                  <select
                    value={editFormData.difficulty || ''}
                    onChange={e => setEditFormData(prev => ({ ...prev, difficulty: e.target.value }))}
                  >
                    {DIFFICULTY_OPTIONS.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>触发关键词（逗号分隔）</label>
                <input
                  type="text"
                  value={keywordInputEdit}
                  onChange={e => setKeywordInputEdit(e.target.value)}
                  placeholder="关键词1, 关键词2, ..."
                />
                <button type="button" onClick={() => addKeyword(true)}>更新关键词</button>
                {editFormData.trigger_keywords && editFormData.trigger_keywords.length > 0 && (
                  <div className="keywords-preview">
                    {editFormData.trigger_keywords.map(k => (
                      <span key={k} className="keyword-tag">{k}</span>
                    ))}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>成功指标（JSON）</label>
                <textarea
                  value={JSON.stringify(editFormData.success_metrics || {})}
                  onChange={e => {
                    try {
                      setEditFormData(prev => ({ ...prev, success_metrics: JSON.parse(e.target.value) }))
                    } catch {}
                  }}
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowEditModal(false)}>取消</button>
                <button type="submit">保存</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Agent 列表弹窗 */}
      {showAgentsModal && (
        <div className="modal-overlay" onClick={() => setShowAgentsModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>使用此 Skill 的 Agent</h2>
            {currentSkillAgents.length === 0 ? (
              <p className="empty">暂无 Agent 使用此 Skill</p>
            ) : (
              <table className="agents-table">
                <thead>
                  <tr>
                    <th>名称</th>
                    <th>Code</th>
                    <th>类型</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  {currentSkillAgents.map(agent => (
                    <tr key={agent.id}>
                      <td>{agent.name}</td>
                      <td><code>{agent.code}</code></td>
                      <td>{agent.agent_type}</td>
                      <td>
                        <span className={`badge badge-${agent.is_active ? 'green' : 'gray'}`}>
                          {agent.is_active ? '活跃' : '停用'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <div className="modal-actions">
              <button onClick={() => setShowAgentsModal(false)}>关闭</button>
            </div>
          </div>
        </div>
      )}

      {/* 执行弹窗 */}
      {showExecuteModal && currentSkill && (
        <div className="modal-overlay" onClick={() => setShowExecuteModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>执行 Skill: {currentSkill.name}</h2>
            <div className="form-group">
              <label>输入内容</label>
              <textarea
                value={executeInput}
                onChange={e => setExecuteInput(e.target.value)}
                placeholder="输入要执行的内容..."
                rows={4}
              />
            </div>
            <button onClick={handleExecute} disabled={!executeInput.trim()}>
              执行
            </button>
            {executeResult && (
              <div className="execute-result">
                <label>执行结果</label>
                <pre>{executeResult}</pre>
              </div>
            )}
            <div className="modal-actions">
              <button onClick={() => setShowExecuteModal(false)}>关闭</button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .skills-page {
          padding: 20px;
        }
        .filters {
          display: flex;
          gap: 12px;
          margin-bottom: 20px;
          align-items: center;
        }
        .filters select, .filters input {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }
        .filters button {
          padding: 8px 16px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        .filters button:hover {
          background: #0056b3;
        }
        .skills-table {
          width: 100%;
          border-collapse: collapse;
          background: white;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .skills-table th, .skills-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #eee;
        }
        .skills-table th {
          background: #f8f9fa;
          font-weight: 600;
        }
        .skills-table tr:hover {
          background: #f8f9fa;
        }
        .skills-table button {
          padding: 4px 8px;
          margin-right: 4px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
        }
        .skills-table button:hover {
          background: #e9ecef;
        }
        .skills-table button.danger {
          color: #dc3545;
          border-color: #dc3545;
        }
        .skills-table button.danger:hover {
          background: #dc3545;
          color: white;
        }
        .badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }
        .badge-green { background: #d4edda; color: #155724; }
        .badge-yellow { background: #fff3cd; color: #856404; }
        .badge-orange { background: #ffe5d0; color: #c94c0c; }
        .badge-red { background: #f8d7da; color: #721c24; }
        .badge-gray { background: #e9ecef; color: #6c757d; }
        .keywords {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
        .keyword-tag {
          padding: 2px 8px;
          background: #e9ecef;
          border-radius: 12px;
          font-size: 12px;
        }
        .keyword-more {
          font-size: 12px;
          color: #6c757d;
        }
        .link-btn {
          background: none !important;
          border: none !important;
          color: #007bff !important;
          padding: 0 !important;
          text-decoration: underline;
          cursor: pointer;
        }
        .empty {
          text-align: center;
          color: #6c757d;
          padding: 40px !important;
        }
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        .modal {
          background: white;
          padding: 24px;
          border-radius: 8px;
          width: 90%;
          max-width: 600px;
          max-height: 80vh;
          overflow-y: auto;
        }
        .modal h2 {
          margin-top: 0;
          margin-bottom: 20px;
        }
        .form-group {
          margin-bottom: 16px;
        }
        .form-group label {
          display: block;
          margin-bottom: 4px;
          font-weight: 500;
        }
        .form-group input, .form-group select, .form-group textarea {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          box-sizing: border-box;
        }
        .form-group textarea {
          resize: vertical;
        }
        .form-row {
          display: flex;
          gap: 16px;
        }
        .form-row .form-group {
          flex: 1;
        }
        .keywords-preview {
          margin-top: 8px;
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
        .detail-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }
        .detail-item {
          padding: 8px 0;
        }
        .detail-item label {
          display: block;
          font-weight: 500;
          color: #6c757d;
          font-size: 12px;
          margin-bottom: 4px;
        }
        .detail-item pre {
          background: #f8f9fa;
          padding: 8px;
          border-radius: 4px;
          overflow-x: auto;
          margin: 0;
        }
        .modal-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          margin-top: 20px;
        }
        .modal-actions button {
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
        }
        .modal-actions button:first-child {
          background: #6c757d;
          color: white;
          border: none;
        }
        .modal-actions button:not(:first-child) {
          background: #007bff;
          color: white;
          border: none;
        }
        .execute-result {
          margin-top: 16px;
        }
        .execute-result label {
          display: block;
          font-weight: 500;
          margin-bottom: 4px;
        }
        .execute-result pre {
          background: #f8f9fa;
          padding: 12px;
          border-radius: 4px;
          overflow-x: auto;
          max-height: 200px;
          overflow-y: auto;
        }
        .agents-table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 16px;
        }
        .agents-table th, .agents-table td {
          padding: 8px;
          text-align: left;
          border-bottom: 1px solid #eee;
        }
        .agents-table th {
          font-weight: 600;
          background: #f8f9fa;
        }
      `}</style>
    </div>
  )
}