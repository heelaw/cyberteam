/**
 * 数字员工市场 - 专家列表/搜索/评分展示
 * 数据来源: /api/expert-agents
 */
import { useState, useEffect } from 'react'
import { fetchExpertMarket, discoverExperts, type ExpertAgentProfile } from '@/apis/modules/expert-agents'

export default function ExpertMarketPage() {
  const [agents, setAgents] = useState<ExpertAgentProfile[]>([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedDept, setSelectedDept] = useState<string>('')

  useEffect(() => {
    loadAgents()
  }, [selectedDept])

  async function loadAgents() {
    setLoading(true)
    try {
      const data = await fetchExpertMarket(selectedDept || undefined)
      setAgents(data)
    } finally {
      setLoading(false)
    }
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!query.trim()) {
      loadAgents()
      return
    }
    setLoading(true)
    try {
      const results = await discoverExperts(query)
      setAgents(results)
    } finally {
      setLoading(false)
    }
  }

  const departments = [...new Set(agents.map(a => a.department))]
  const ratingStars = (r: number) => '★'.repeat(Math.round(r)) + '☆'.repeat(5 - Math.round(r))

  return (
    <div>
      {/* 搜索栏 */}
      <form onSubmit={handleSearch}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="搜索专家（如：运营、活动、设计）..."
        />
        <button type="submit">搜索</button>
      </form>

      {/* 部门筛选 */}
      <div>
        <button onClick={() => setSelectedDept('')} className={!selectedDept ? 'active' : ''}>
          全部
        </button>
        {departments.map(dept => (
          <button
            key={dept}
            onClick={() => setSelectedDept(dept)}
            className={selectedDept === dept ? 'active' : ''}
          >
            {dept}
          </button>
        ))}
      </div>

      {/* 专家卡片列表 */}
      {loading ? (
        <div>加载中...</div>
      ) : (
        <div className="agent-grid">
          {agents.map(agent => (
            <div key={agent.agent_id} className="agent-card">
              <div className="agent-header">
                <span className="avatar">{agent.avatar}</span>
                <div>
                  <div className="name">{agent.name}</div>
                  <div className="dept">{agent.department}</div>
                </div>
                <div className="rating">{ratingStars(agent.rating)}</div>
              </div>
              <div className="description">{agent.description}</div>
              <div className="capabilities">
                {agent.capabilities.map(cap => (
                  <span key={cap} className="cap-tag">{cap}</span>
                ))}
              </div>
              <div className="stats">
                调用 {agent.call_count} 次 | 平均 {Math.round(agent.avg_response_time_ms)}ms
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}