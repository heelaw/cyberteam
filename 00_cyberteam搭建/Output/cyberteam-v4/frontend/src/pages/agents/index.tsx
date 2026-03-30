/**
 * Agent 管理页 — 真实 API 驱动
 *
 * 数据来源: /api/agents
 * 降级策略: 后端不可用时显示连接状态
 */
import { useState, useEffect, useCallback } from 'react'
import {
  Card, Tabs, Tag, Row, Col, Avatar, Input, Select,
  Statistic, Typography, Space, Alert, Button, Spin,
} from 'antd'
import {
  TeamOutlined, RobotOutlined, CrownOutlined,
  AppstoreOutlined, BulbOutlined, ReloadOutlined,
  ApiOutlined,
} from '@ant-design/icons'
import { fetchAgents } from '@/apis/modules/agents'

const { Title, Text } = Typography

type AgentLayer = 'decision' | 'coordination' | 'execution'

interface AgentInfo {
  id: string
  name: string
  department: string
  layer: AgentLayer
  status: 'idle' | 'running' | 'active' | 'shutdown'
  rating: number
  skills: string[]
  description: string
  subordinates?: string[]
  type?: string
}

// 静态 Agent 定义（来自 v4 AGENTS 目录，供降级展示用）
const STATIC_AGENTS: AgentInfo[] = [
  { id: 'ceo', name: 'CEO', department: '决策层', layer: 'decision', status: 'idle', rating: 4.8, skills: ['5W1H1Y', 'MECE分析', '思维注入'], description: '总指挥，负责需求分拣和路由决策' },
  { id: 'coo', name: 'COO', department: '决策层', layer: 'decision', status: 'idle', rating: 4.6, skills: ['执行规划', '任务编排', '风险控制'], description: '首席运营官，负责执行规划和协调' },
  { id: 'pm', name: 'PM', department: '决策层', layer: 'decision', status: 'idle', rating: 4.5, skills: ['项目管理', '进度追踪'], description: '项目协调器，负责任务派发和进度管理' },
  { id: 'growth_director', name: '增长总监', department: '增长部', layer: 'coordination', status: 'idle', rating: 4.7, skills: ['增长策略', '数据分析'], description: '增长部总监', subordinates: ['用户运营', '内容运营', '渠道推广'] },
  { id: 'product_director', name: '产品总监', department: '产品部', layer: 'coordination', status: 'idle', rating: 4.4, skills: ['产品规划', '用户研究'], description: '产品部总监', subordinates: ['产品经理', '需求分析师'] },
  { id: 'finance_director', name: '财务总监', department: '财务部', layer: 'coordination', status: 'idle', rating: 4.3, skills: ['财务分析', '预算管理'], description: '财务部总监' },
  { id: 'socratic', name: '质疑者', department: '质量门禁', layer: 'coordination', status: 'idle', rating: 4.9, skills: ['苏格拉底提问', '逻辑审查', '数据验证'], description: '质量门禁，通过提问确保讨论质量' },
  { id: 'user_growth', name: '用户运营', department: '增长部', layer: 'execution', status: 'idle', rating: 4.2, skills: ['用户增长', '留存策略', 'A/B测试'], description: '用户运营专家' },
  { id: 'content_ops', name: '内容运营', department: '增长部', layer: 'execution', status: 'idle', rating: 4.1, skills: ['内容策略', '爆款分析', '选题法'], description: '内容运营专家' },
  { id: 'channel_promo', name: '渠道推广', department: '增长部', layer: 'execution', status: 'idle', rating: 4.0, skills: ['渠道分析', '投放策略', 'ROI优化'], description: '渠道推广专家' },
  { id: 'copywriter', name: '高级文案', department: '增长部', layer: 'execution', status: 'idle', rating: 4.3, skills: ['AIDA模型', '4P法则', '故事型文案'], description: '高级文案创作专家' },
  { id: 'design_lead', name: '设计主管', department: '设计部', layer: 'execution', status: 'idle', rating: 4.2, skills: ['视觉设计', '品牌规范', 'UI/UX'], description: '设计主管' },
  { id: 'data_analyst', name: '数据分析师', department: '增长部', layer: 'execution', status: 'idle', rating: 4.0, skills: ['数据分析', 'SQL', '可视化'], description: '数据分析专家' },
  { id: 'market_research', name: '市场研究员', department: '增长部', layer: 'execution', status: 'idle', rating: 4.1, skills: ['市场调研', '竞品分析', '用户访谈'], description: '市场研究专家' },
]

const layerLabels: Record<string, string> = {
  all: '全部',
  decision: '决策层（三省）',
  coordination: '协调层（总监）',
  execution: '执行层（六部）',
}

const layerIcons: Record<AgentLayer, React.ReactNode> = {
  decision: <CrownOutlined style={{ color: '#f59e0b' }} />,
  coordination: <AppstoreOutlined style={{ color: '#3b82f6' }} />,
  execution: <BulbOutlined style={{ color: '#10b981' }} />,
}

const layerBgColor: Record<AgentLayer, string> = {
  decision: '#fef3c7',
  coordination: '#dbeafe',
  execution: '#d1fae5',
}

function AgentCard({ agent }: { agent: AgentInfo }) {
  return (
    <Card hoverable style={{ height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        <Avatar
          size={48}
          icon={<RobotOutlined />}
          style={{
            backgroundColor: layerBgColor[agent.layer as AgentLayer],
            color: agent.layer === 'decision' ? '#d97706' : agent.layer === 'coordination' ? '#2563eb' : '#059669',
          }}
        />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong style={{ fontSize: 15 }}>{agent.name}</Text>
            <Tag
              color={agent.status === 'active' || agent.status === 'running' ? 'processing' :
                      agent.status === 'shutdown' ? 'error' : 'default'}
              style={{ fontSize: 11 }}
            >
              {agent.status === 'active' || agent.status === 'running' ? '运行中' :
               agent.status === 'shutdown' ? '已关闭' : '空闲'}
            </Tag>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 2 }}>
            {layerIcons[agent.layer as AgentLayer]}
            <Text type="secondary" style={{ fontSize: 12 }}>{agent.department}</Text>
          </div>
          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 4 }}>
            {agent.description}
          </Text>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 8 }}>
            {(agent.skills || []).slice(0, 3).map((s) => (
              <Tag key={s} style={{ fontSize: 11 }}>{s}</Tag>
            ))}
          </div>
          {agent.subordinates && (
            <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
              下属: {agent.subordinates.join(', ')}
            </div>
          )}
          {agent.rating > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
              <div style={{ flex: 1, height: 4, backgroundColor: '#f0f0f0', borderRadius: 2 }}>
                <div style={{ width: `${agent.rating * 20}%`, height: '100%', backgroundColor: '#f59e0b', borderRadius: 2 }} />
              </div>
              <Text style={{ fontSize: 12, color: '#f59e0b' }}>{agent.rating.toFixed(1)}</Text>
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}

export default function AgentManagement() {
  const [agents, setAgents] = useState<AgentInfo[]>(STATIC_AGENTS)
  const [loading, setLoading] = useState(true)
  const [apiAvailable, setApiAvailable] = useState<boolean | null>(null)
  const [filterLayer, setFilterLayer] = useState<string>('all')
  const [search, setSearch] = useState('')

  const loadAgents = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchAgents()
      if (data.length > 0) {
        // 合并后端数据与静态 Agent 定义
        const merged: AgentInfo[] = data.map((a) => {
          const staticDef = STATIC_AGENTS.find((s) =>
            s.name === a.name || s.id === a.id || s.name.includes(a.name) || a.name.includes(s.name)
          )
          return {
            ...a,
            layer: (staticDef?.layer || 'execution') as AgentLayer,
            rating: staticDef?.rating || 4.0,
            skills: a.capabilities || staticDef?.skills || [],
            description: staticDef?.description || a.type || '',
            subordinates: staticDef?.subordinates,
          }
        })
        setAgents(merged)
        setApiAvailable(true)
      } else {
        setApiAvailable(false)
      }
    } catch (error) {
      console.warn('[Agents] 加载失败，使用静态定义:', error)
      setApiAvailable(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAgents()
  }, [loadAgents])

  const runningCount = agents.filter((a) => a.status === 'active' || a.status === 'running').length
  const avgRating = agents.reduce((sum, a) => sum + (a.rating || 0), 0) / (agents.length || 1)

  const filtered = agents
    .filter((a) => filterLayer === 'all' || a.layer === filterLayer)
    .filter((a) => !search || a.name.includes(search) || a.department.includes(search))

  const layerOptions = [
    { value: 'all', label: `全部 (${agents.length})` },
    { value: 'decision', label: `决策层 (${agents.filter(a => a.layer === 'decision').length})` },
    { value: 'coordination', label: `协调层 (${agents.filter(a => a.layer === 'coordination').length})` },
    { value: 'execution', label: `执行层 (${agents.filter(a => a.layer === 'execution').length})` },
  ]

  return (
    <div className="p-6">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <TeamOutlined className="mr-2 text-blue-500" />
          Agent 三省六部管理
        </Title>
        <Space>
          <Input.Search
            placeholder="搜索 Agent..."
            style={{ width: 200 }}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Select
            value={filterLayer}
            onChange={setFilterLayer}
            style={{ width: 140 }}
            options={layerOptions}
          />
          <Button
            icon={<ReloadOutlined />}
            onClick={loadAgents}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {apiAvailable === false && (
        <Alert
          type="info"
          showIcon
          icon={<ApiOutlined />}
          message="使用静态 Agent 定义"
          description="后端服务未连接，当前显示 v4 内置 Agent 目录。启动后端后可获取实时 Agent 状态。"
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 统计 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card><Statistic title="总 Agent 数" value={agents.length} prefix={<TeamOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="运行中" value={runningCount} prefix={<RobotOutlined />} valueStyle={{ color: '#3b82f6' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="平均评分" value={avgRating.toFixed(1)} suffix="/ 5.0" valueStyle={{ color: '#f59e0b' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="部门数" value={new Set(agents.map(a => a.department)).size} valueStyle={{ color: '#10b981' }} /></Card>
        </Col>
      </Row>

      {/* Agent 网格 */}
      {loading && agents.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 48 }}>
          <Spin size="large" />
        </div>
      ) : (
        <Row gutter={[16, 16]}>
          {filtered.map((agent) => (
            <Col span={8} key={agent.id}>
              <AgentCard agent={agent} />
            </Col>
          ))}
        </Row>
      )}
    </div>
  )
}
