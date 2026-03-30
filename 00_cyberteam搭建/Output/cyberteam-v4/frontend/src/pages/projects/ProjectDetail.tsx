import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect, useCallback } from 'react'
import {
  Card, Steps, Typography, Tabs, List, Tag, Avatar,
  Timeline, Button, Space, Row, Col, Statistic, Spin, message,
} from 'antd'
import {
  RobotOutlined,
  FileTextOutlined,
  LineChartOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons'
import { fetchProject } from '@/apis/modules/projects'
import type { Project } from '@/apis/modules/projects'

const { Title, Text, Paragraph } = Typography

const agentDiscussions = [
  { agent: 'CEO', dept: '决策层', message: '任务分析完毕，这是一个品牌+市场+营销的综合任务。建议分配给增长部主导。', time: '14:30' },
  { agent: 'COO', dept: '决策层', message: '同意。执行计划已制定，建议先收集海岸城商圈的真实数据。', time: '14:32' },
  { agent: '质疑者', dept: '质量门禁', message: '⚠️ 等一下。目前所有数据都是假设的，需要先通过 Web Search 收集真实竞品信息。', time: '14:35' },
  { agent: '增长总监', dept: '协调层', message: '已执行搜索。海岸城日均客流约12万人次（来源：官方公众号），餐饮占比约35%。', time: '14:40' },
]

const documents = [
  { name: '市场分析报告', type: 'report', status: 'completed' },
  { name: '竞品对比分析', type: 'report', status: 'completed' },
  { name: '品牌定位策略', type: 'plan', status: 'in_progress' },
  { name: '小红书内容方案', type: 'copy', status: 'pending' },
  { name: '抖音推广方案', type: 'copy', status: 'pending' },
]

export default function ProjectDetail() {
  const { id: projectId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)

  // Playground 状态
  const [playgroundHTML, setPlaygroundHTML] = useState<string | null>(null)
  const [playgroundLoading, setPlaygroundLoading] = useState(false)
  const [playgroundError, setPlaygroundError] = useState<string | null>(null)
  const [playgroundGenLoading, setPlaygroundGenLoading] = useState(false)

  const [activeTab, setActiveTab] = useState('discussion')

  // 加载项目信息
  useEffect(() => {
    if (!projectId) return
    fetchProject(projectId).then((p) => {
      setProject(p)
      setLoading(false)
    })
  }, [projectId])

  // 动态计算当前节点
  const currentStep = project?.currentStep ?? 2
  const totalSteps = project?.totalSteps ?? 8
  const projectName = project?.name ?? '项目详情'
  const agentCount = project?.agentCount ?? 6
  const messageCount = project?.messageCount ?? 47
  const completion = Math.round((currentStep / totalSteps) * 100)

  const projectSteps = [
    { name: 'CEO-COO对齐', agent: 'CEO + COO' },
    { name: '策略讨论', agent: '增长总监 + 产品总监 + 运营总监' },
    { name: '风险预案', agent: '质疑者 + 增长总监' },
    { name: 'CEO汇报', agent: 'COO' },
    { name: '设计联动', agent: '设计主管' },
    { name: '文案产出', agent: '高级文案' },
    { name: 'CEO汇总', agent: 'CEO' },
    { name: '复盘进化', agent: '全团队' },
  ]

  // 生成 Playground
  const handleGeneratePlayground = useCallback(async () => {
    if (!projectId) return
    setPlaygroundGenLoading(true)
    setPlaygroundError(null)
    setPlaygroundHTML(null)

    try {
      // 动态导入避免循环依赖
      const { generatePlayground, fetchPlaygroundHTML } = await import('@/apis/modules/projects')

      // 1. 调用生成 API
      await generatePlayground(projectId)

      // 2. 获取生成的 HTML
      const html = await fetchPlaygroundHTML(projectId)
      setPlaygroundHTML(html)
      message.success('Playground 生成成功')
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : String(err)
      setPlaygroundError(errMsg)
      message.error(`生成失败: ${errMsg}`)
    } finally {
      setPlaygroundGenLoading(false)
    }
  }, [projectId])

  // 预览已生成的 Playground
  const handlePreviewPlayground = useCallback(async () => {
    if (!projectId) return
    setPlaygroundLoading(true)
    setPlaygroundError(null)

    try {
      const { fetchPlaygroundHTML } = await import('@/apis/modules/projects')
      const html = await fetchPlaygroundHTML(projectId)
      setPlaygroundHTML(html)
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : String(err)
      setPlaygroundError(errMsg)
      message.error(`加载失败: ${errMsg}`)
    } finally {
      setPlaygroundLoading(false)
    }
  }, [projectId])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spin size="large" tip="加载项目信息..." />
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* 顶部标题 */}
      <div className="flex items-center justify-between mb-4">
        <Title level={3} className="mb-0">{projectName}</Title>
        <Space>
          <Tag color={project?.status === 'executing' ? 'processing' : project?.status === 'completed' ? 'success' : 'default'}>
            {project?.status === 'executing' ? '执行中' : project?.status === 'completed' ? '已完成' : '规划中'}
          </Tag>
        </Space>
      </div>

      {/* 八节点步骤条 */}
      <Card className="mb-4">
        <Steps
          current={currentStep - 1}
          size="small"
          items={projectSteps.map((s) => ({
            title: s.name,
            description: <span className="text-xs text-gray-400">{s.agent}</span>,
          }))}
        />
      </Card>

      {/* 统计 */}
      <Row gutter={16} className="mb-4">
        <Col span={6}><Card><Statistic title="参与 Agent" value={agentCount} prefix={<RobotOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="讨论消息" value={messageCount} prefix={<ThunderboltOutlined />} valueStyle={{ color: '#3b82f6' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="产出文档" value={2} suffix="/ 5" prefix={<FileTextOutlined />} valueStyle={{ color: '#f59e0b' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="完成度" value={completion} suffix="%" prefix={<LineChartOutlined />} valueStyle={{ color: '#10b981' }} /></Card></Col>
      </Row>

      {/* Tab 切换 */}
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'discussion',
              label: 'Agent 讨论',
              children: (
                <Timeline
                  items={agentDiscussions.map((d) => ({
                    color: d.dept === '决策层' ? 'gold' : d.dept === '质量门禁' ? 'red' : 'blue',
                    children: (
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Tag color={d.dept === '决策层' ? 'gold' : d.dept === '质量门禁' ? 'red' : 'blue'}>{d.agent}</Tag>
                          <Text type="secondary" className="text-xs">{d.time}</Text>
                        </div>
                        <Paragraph className="mb-0">{d.message}</Paragraph>
                      </div>
                    ),
                  }))}
                />
              ),
            },
            {
              key: 'documents',
              label: '文档产出',
              children: (
                <List
                  dataSource={documents}
                  renderItem={(doc) => (
                    <List.Item actions={[
                      <Tag color={doc.status === 'completed' ? 'success' : doc.status === 'in_progress' ? 'processing' : 'default'}>
                        {doc.status === 'completed' ? '已完成' : doc.status === 'in_progress' ? '进行中' : '待开始'}
                      </Tag>,
                    ]}>
                      <List.Item.Meta
                        avatar={<Avatar icon={<FileTextOutlined />} />}
                        title={doc.name}
                        description={doc.type === 'report' ? '分析报告' : doc.type === 'plan' ? '策略方案' : '文案产出'}
                      />
                    </List.Item>
                  )}
                />
              ),
            },
            {
              key: 'playground',
              label: 'Playground 看板',
              children: (
                <PlaygroundTab
                  html={playgroundHTML}
                  loading={playgroundLoading || playgroundGenLoading}
                  error={playgroundError}
                  onGenerate={handleGeneratePlayground}
                  onPreview={handlePreviewPlayground}
                  projectName={projectName}
                />
              ),
            },
          ]}
        />
      </Card>
    </div>
  )
}

// === Playground Tab 子组件 ===
interface PlaygroundTabProps {
  html: string | null
  loading: boolean
  error: string | null
  onGenerate: () => void
  onPreview: () => void
  projectName: string
}

function PlaygroundTab({ html, loading, error, onGenerate, onPreview, projectName }: PlaygroundTabProps) {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <Spin size="large" tip="正在生成 Playground..." />
        <Text type="secondary">从项目文档中提取数据并渲染交互式看板</Text>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4 text-sm">{error}</div>
        <Space>
          <Button type="primary" icon={<ReloadOutlined />} onClick={onGenerate}>
            重新生成
          </Button>
          <Button onClick={onPreview}>尝试预览</Button>
        </Space>
      </div>
    )
  }

  if (html) {
    return (
      <div className="flex flex-col" style={{ height: 'calc(100vh - 400px)' }}>
        {/* Toolbar */}
        <div className="flex items-center justify-between mb-2">
          <Text strong>交互式活动看板</Text>
          <Space>
            <Button size="small" icon={<ReloadOutlined />} onClick={onGenerate}>
              重新生成
            </Button>
            <Button size="small" icon={<PlayCircleOutlined />} onClick={onPreview}>
              刷新预览
            </Button>
          </Space>
        </div>
        {/* Playground iframe */}
        <iframe
          srcDoc={html}
          title={`${projectName} - Playground`}
          className="flex-1 w-full border rounded"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    )
  }

  // 默认空状态
  return (
    <div className="text-center py-16">
      <LineChartOutlined className="text-6xl text-gray-300 mb-4" />
      <Title level={5} type="secondary">Playground 交互式看板</Title>
      <Paragraph type="secondary" className="mb-6 max-w-md mx-auto">
        从项目文档（CEO对齐记录、策略讨论、风险预案、CEO汇报）中提取数据，
        自动生成可交互的漏斗图、模拟器和节点进度看板。
      </Paragraph>
      <Space direction="vertical" size="middle" className="w-64">
        <Button type="primary" size="large" block icon={<PlayCircleOutlined />} onClick={onGenerate}>
          生成 Playground
        </Button>
        <Text type="secondary" className="text-xs">
          CEO 批准执行后即可生成 · 约需 10-30 秒
        </Text>
      </Space>
    </div>
  )
}
