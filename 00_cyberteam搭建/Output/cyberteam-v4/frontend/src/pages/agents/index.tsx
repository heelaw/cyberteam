import { useState } from 'react'
import { Card, Tabs, Tag, Row, Col, Avatar, Progress, Input, Select, Badge, Typography, Space, Statistic } from 'antd'
import {
  TeamOutlined,
  RobotOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  CrownOutlined,
  AppstoreOutlined,
  BulbOutlined,
} from '@ant-design/icons'

const { Title, Text } = Typography

type AgentLayer = 'decision' | 'coordination' | 'execution'

interface AgentInfo {
  id: string
  name: string
  department: string
  layer: AgentLayer
  status: 'idle' | 'running' | 'error'
  rating: number
  skills: string[]
  description: string
  subordinates?: string[]
}

const mockAgents: AgentInfo[] = [
  { id: 'ceo', name: 'CEO', department: '决策层', layer: 'decision', status: 'idle', rating: 4.8, skills: ['5W1H1Y', 'MECE分析', '思维注入'], description: '总指挥，负责需求分拣和路由决策' },
  { id: 'coo', name: 'COO', department: '决策层', layer: 'decision', status: 'running', rating: 4.6, skills: ['执行规划', '任务编排', '风险控制'], description: '首席运营官，负责执行规划和协调' },
  { id: 'pm', name: 'PM', department: '决策层', layer: 'decision', status: 'idle', rating: 4.5, skills: ['项目管理', '进度追踪'], description: '项目协调器，负责任务派发和进度管理' },
  { id: 'growth_director', name: '增长总监', department: '增长部', layer: 'coordination', status: 'running', rating: 4.7, skills: ['增长策略', '数据分析'], description: '增长部总监', subordinates: ['用户运营', '内容运营', '渠道推广'] },
  { id: 'product_director', name: '产品总监', department: '产品部', layer: 'coordination', status: 'idle', rating: 4.4, skills: ['产品规划', '用户研究'], description: '产品部总监', subordinates: ['产品经理', '需求分析师'] },
  { id: 'finance_director', name: '财务总监', department: '财务部', layer: 'coordination', status: 'idle', rating: 4.3, skills: ['财务分析', '预算管理'], description: '财务部总监' },
  { id: 'socratic', name: '质疑者', department: '质量门禁', layer: 'coordination', status: 'running', rating: 4.9, skills: ['苏格拉底提问', '逻辑审查', '数据验证'], description: '质量门禁，通过提问确保讨论质量' },
  { id: 'user_growth', name: '用户运营', department: '增长部', layer: 'execution', status: 'idle', rating: 4.2, skills: ['用户增长', '留存策略', 'A/B测试'], description: '用户运营专家' },
  { id: 'content_ops', name: '内容运营', department: '增长部', layer: 'execution', status: 'idle', rating: 4.1, skills: ['内容策略', '爆款分析', '选题法'], description: '内容运营专家' },
  { id: 'channel_promo', name: '渠道推广', department: '增长部', layer: 'execution', status: 'idle', rating: 4.0, skills: ['渠道分析', '投放策略', 'ROI优化'], description: '渠道推广专家' },
  { id: 'copywriter', name: '高级文案', department: '增长部', layer: 'execution', status: 'idle', rating: 4.3, skills: ['AIDA模型', '4P法则', '故事型文案'], description: '高级文案创作专家' },
  { id: 'design_lead', name: '设计主管', department: '设计部', layer: 'execution', status: 'idle', rating: 4.2, skills: ['视觉设计', '品牌规范', 'UI/UX'], description: '设计主管' },
  { id: 'data_analyst', name: '数据分析师', department: '增长部', layer: 'execution', status: 'idle', rating: 4.0, skills: ['数据分析', 'SQL', '可视化'], description: '数据分析专家' },
  { id: 'market_research', name: '市场研究员', department: '增长部', layer: 'execution', status: 'idle', rating: 4.1, skills: ['市场调研', '竞品分析', '用户访谈'], description: '市场研究专家' },
]

const layerLabels: Record<AgentLayer | 'all', string> = {
  all: '全部',
  decision: '决策层（三省）',
  coordination: '协调层（总监）',
  execution: '执行层（六部）',
}

const layerIcons: Record<AgentLayer, React.ReactNode> = {
  decision: <CrownOutlined className="text-yellow-500" />,
  coordination: <AppstoreOutlined className="text-blue-500" />,
  execution: <BulbOutlined className="text-green-500" />,
}

function AgentCard({ agent }: { agent: AgentInfo }) {
  return (
    <Card hoverable className="h-full">
      <div className="flex items-start gap-3">
        <Avatar
          size={48}
          icon={<RobotOutlined />}
          className={
            agent.layer === 'decision' ? 'bg-yellow-500' :
            agent.layer === 'coordination' ? 'bg-blue-500' :
            'bg-green-500'
          }
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <Text strong>{agent.name}</Text>
            <Tag color={agent.status === 'running' ? 'processing' : agent.status === 'error' ? 'error' : 'default'} className="text-xs">
              {agent.status === 'running' ? '运行中' : agent.status === 'error' ? '异常' : '空闲'}
            </Tag>
          </div>
          <Text type="secondary" className="text-xs">{agent.department}</Text>
          <div className="mt-1">
            <Text className="text-xs text-gray-500">{agent.description}</Text>
          </div>
          <div className="mt-2 flex flex-wrap gap-1">
            {agent.skills.slice(0, 3).map((s) => (
              <Tag key={s} className="text-xs">{s}</Tag>
            ))}
            {agent.skills.length > 3 && <Tag className="text-xs">+{agent.skills.length - 3}</Tag>}
          </div>
          {agent.subordinates && (
            <div className="mt-2 text-xs text-gray-400">
              下属: {agent.subordinates.join(', ')}
            </div>
          )}
          <div className="mt-2 flex items-center gap-1">
            <Progress percent={agent.rating * 20} size="small" className="flex-1" />
            <Text className="text-xs text-yellow-500">{agent.rating}</Text>
          </div>
        </div>
      </div>
    </Card>
  )
}

export default function AgentManagement() {
  const [filterDept, setFilterDept] = useState<string>('all')

  const filtered = filterDept === 'all' ? mockAgents : mockAgents.filter((a) => a.layer === filterDept)

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <Title level={3} className="m-0">
          <TeamOutlined className="mr-2 text-blue-500" />
          Agent 三省六部管理
        </Title>
        <Space>
          <Input.Search placeholder="搜索 Agent..." className="w-48" />
          <Select value={filterDept} onChange={setFilterDept} className="w-40"
            options={Object.entries(layerLabels).map(([k, v]) => ({ value: k, label: v }))} />
        </Space>
      </div>

      {/* 统计 */}
      <Row gutter={16} className="mb-4">
        <Col span={6}>
          <Card><Statistic title="总 Agent 数" value={mockAgents.length} prefix={<TeamOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="运行中" value={mockAgents.filter(a => a.status === 'running').length} prefix={<ThunderboltOutlined />} valueStyle={{ color: '#3b82f6' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="平均评分" value={4.4} suffix="/ 5.0" prefix={<SafetyCertificateOutlined />} valueStyle={{ color: '#f59e0b' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="部门数" value={4} prefix={<AppstoreOutlined />} valueStyle={{ color: '#10b981' }} /></Card>
        </Col>
      </Row>

      {/* Agent 网格 */}
      <Row gutter={[16, 16]}>
        {filtered.map((agent) => (
          <Col span={8} key={agent.id}>
            <AgentCard agent={agent} />
          </Col>
        ))}
      </Row>
    </div>
  )
}
