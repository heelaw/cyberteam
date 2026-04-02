import React, { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Bot, Link2, Unlink, Plus, Search, FileText } from 'lucide-react'

interface Agent {
  id: string
  name: string
  description: string
  department_id?: string
  skills: string[]
  soul_content?: string
}

export default function Agents() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    setLoading(true)
    try {
      // 从 Tauri 后端加载 Agent 配置
      // 这里使用硬编码的示例数据，实际应从后端 API 获取
      const demoAgents: Agent[] = [
        {
          id: 'ceo',
          name: 'CEO（总指挥）',
          description: 'CyberTeam 核心调度引擎，负责任务分解、部门调度、结果汇总',
          skills: ['planning', 'coordination'],
          soul_content: '# CEO SOUL\n\n你是 CyberTeam 的 CEO，负责全局调度...',
        },
        {
          id: 'coo',
          name: 'COO（运营总监）',
          description: '协助 CEO 执行战略，管理日常运营流程',
          skills: ['operations', 'management'],
          soul_content: '# COO SOUL\n\n你是 COO，负责运营管理...',
        },
        {
          id: 'product-agent',
          name: '产品总监',
          description: '负责产品设计、需求分析、PRD 撰写',
          skills: ['product-design', 'prd'],
        },
        {
          id: 'ops-agent',
          name: '运营总监',
          description: '负责用户增长、活动策划、数据分析',
          skills: ['growth', 'analytics'],
        },
        {
          id: 'eng-agent',
          name: '技术总监',
          description: '负责技术方案、系统架构、代码实现',
          skills: ['architecture', 'coding'],
        },
        {
          id: 'design-agent',
          name: '设计总监',
          description: '负责 UI 设计、UX 规划、品牌设计',
          skills: ['ui-design', 'ux-research'],
        },
        {
          id: 'hr-agent',
          name: '人力总监',
          description: '负责招聘、激励、文化建设',
          skills: ['recruitment', 'culture'],
        },
        {
          id: 'finance-agent',
          name: '财务总监',
          description: '负责预算规划、成本控制、投资回报分析',
          skills: ['budgeting', 'analysis'],
        },
      ]
      setAgents(demoAgents)
    } catch (error) {
      console.error('Failed to load agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredAgents = agents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(search.toLowerCase()) ||
      agent.description.toLowerCase().includes(search.toLowerCase())
  )

  const handleUnbindSkill = async (agentId: string, skillId: string) => {
    // 调用 Tauri 命令解绑 Skill
    try {
      await invoke('unbind_skill', { agentId, skillId })
      // 刷新列表
      loadAgents()
    } catch (e) {
      console.error('Failed to unbind skill:', e)
    }
  }

  return (
    <div style={styles.container}>
      {/* 左侧列表 */}
      <div style={styles.list}>
        <div style={styles.header}>
          <h2 style={styles.title}>
            <Bot size={20} style={{ color: '#58A6FF', marginRight: 8 }} />
            智能体
          </h2>
          <button style={styles.addButton}>
            <Plus size={16} />
            新建
          </button>
        </div>

        <div style={styles.searchBox}>
          <Search size={16} style={{ color: '#8B949E' }} />
          <input
            type="text"
            placeholder="搜索智能体..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={styles.searchInput}
          />
        </div>

        <div style={styles.agentList}>
          {loading ? (
            <div style={styles.loading}>加载中...</div>
          ) : (
            filteredAgents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(agent)}
                style={{
                  ...styles.agentItem,
                  ...(selectedAgent?.id === agent.id ? styles.agentItemActive : {}),
                }}
              >
                <div style={styles.agentAvatar}>
                  <Bot size={18} />
                </div>
                <div style={styles.agentInfo}>
                  <span style={styles.agentName}>{agent.name}</span>
                  <span style={styles.agentDesc}>{agent.description}</span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* 右侧详情 */}
      <div style={styles.detail}>
        {selectedAgent ? (
          <>
            <div style={styles.detailHeader}>
              <div style={styles.detailAvatar}>
                <Bot size={32} style={{ color: '#58A6FF' }} />
              </div>
              <div>
                <h3 style={styles.detailName}>{selectedAgent.name}</h3>
                <p style={styles.detailDesc}>{selectedAgent.description}</p>
              </div>
            </div>

            <div style={styles.section}>
              <h4 style={styles.sectionTitle}>
                <Link2 size={16} style={{ marginRight: 6 }} />
                绑定的技能
              </h4>
              {selectedAgent.skills.length > 0 ? (
                <div style={styles.skillTags}>
                  {selectedAgent.skills.map((skill) => (
                    <span key={skill} style={styles.skillTag}>
                      {skill}
                      <button
                        onClick={() => handleUnbindSkill(selectedAgent.id, skill)}
                        style={styles.unbindBtn}
                      >
                        <Unlink size={12} />
                      </button>
                    </span>
                  ))}
                </div>
              ) : (
                <p style={styles.emptyText}>暂无绑定的技能</p>
              )}
            </div>

            <div style={styles.section}>
              <h4 style={styles.sectionTitle}>
                <FileText size={16} style={{ marginRight: 6 }} />
                SOUL 内容
              </h4>
              <pre style={styles.soulContent}>
                {selectedAgent.soul_content || '暂无 SOUL 内容'}
              </pre>
            </div>
          </>
        ) : (
          <div style={styles.noSelection}>
            <Bot size={48} style={{ color: '#30363D', marginBottom: 16 }} />
            <p style={{ color: '#8B949E' }}>选择一个智能体查看详情</p>
          </div>
        )}
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    height: '100%',
    backgroundColor: '#0D1117',
  },
  list: {
    width: 320,
    borderRight: '1px solid #30363D',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 20px',
    borderBottom: '1px solid #30363D',
  },
  title: {
    display: 'flex',
    alignItems: 'center',
    fontSize: 16,
    fontWeight: 600,
    color: '#E6EDF3',
    margin: 0,
  },
  addButton: {
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    padding: '6px 12px',
    backgroundColor: '#238636',
    border: 'none',
    borderRadius: 6,
    color: '#FFFFFF',
    fontSize: 13,
    cursor: 'pointer',
  },
  searchBox: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    margin: '12px 16px',
    padding: '8px 12px',
    backgroundColor: '#0D1117',
    borderRadius: 8,
    border: '1px solid #30363D',
  },
  searchInput: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    outline: 'none',
    color: '#E6EDF3',
    fontSize: 14,
  },
  agentList: {
    flex: 1,
    overflow: 'auto',
    padding: '0 8px',
  },
  loading: {
    padding: 20,
    textAlign: 'center',
    color: '#8B949E',
  },
  agentItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 12,
    width: '100%',
    padding: '12px',
    marginBottom: 4,
    background: 'transparent',
    border: 'none',
    borderRadius: 8,
    cursor: 'pointer',
    textAlign: 'left',
    transition: 'background 0.15s',
  },
  agentItemActive: {
    backgroundColor: '#1F6FEB20',
  },
  agentAvatar: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: '#30363D',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#58A6FF',
    flexShrink: 0,
  },
  agentInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    minWidth: 0,
  },
  agentName: {
    fontSize: 14,
    fontWeight: 500,
    color: '#E6EDF3',
  },
  agentDesc: {
    fontSize: 12,
    color: '#8B949E',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  detail: {
    flex: 1,
    padding: 24,
    overflow: 'auto',
  },
  detailHeader: {
    display: 'flex',
    gap: 16,
    marginBottom: 24,
    paddingBottom: 24,
    borderBottom: '1px solid #30363D',
  },
  detailAvatar: {
    width: 56,
    height: 56,
    borderRadius: 12,
    backgroundColor: '#161B22',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: '1px solid #30363D',
    flexShrink: 0,
  },
  detailName: {
    fontSize: 18,
    fontWeight: 600,
    color: '#E6EDF3',
    margin: '0 0 8px',
  },
  detailDesc: {
    fontSize: 14,
    color: '#8B949E',
    margin: 0,
    lineHeight: 1.5,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    display: 'flex',
    alignItems: 'center',
    fontSize: 14,
    fontWeight: 600,
    color: '#E6EDF3',
    marginBottom: 12,
  },
  skillTags: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 8,
  },
  skillTag: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '4px 10px',
    backgroundColor: '#388BFD20',
    border: '1px solid #388BFD40',
    borderRadius: 16,
    fontSize: 13,
    color: '#58A6FF',
  },
  unbindBtn: {
    display: 'flex',
    alignItems: 'center',
    background: 'transparent',
    border: 'none',
    color: '#58A6FF',
    cursor: 'pointer',
    padding: 2,
    opacity: 0.6,
  },
  emptyText: {
    fontSize: 13,
    color: '#8B949E',
    fontStyle: 'italic',
  },
  soulContent: {
    padding: 16,
    backgroundColor: '#161B22',
    border: '1px solid #30363D',
    borderRadius: 8,
    fontSize: 13,
    color: '#8B949E',
    lineHeight: 1.6,
    overflow: 'auto',
    maxHeight: 300,
    whiteSpace: 'pre-wrap',
    margin: 0,
  },
  noSelection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
  },
}
