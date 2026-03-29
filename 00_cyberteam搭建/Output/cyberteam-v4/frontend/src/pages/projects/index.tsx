import { Card, Row, Col, Steps, Tag, Button, List, Typography, Space, Progress, Badge } from 'antd'
import {
  ProjectOutlined,
  PlusOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title, Text, Paragraph } = Typography

const projectSteps = [
  'CEO-COO对齐', '策略讨论', '风险预案', 'CEO汇报',
  '设计联动', '文案产出', 'CEO汇总', '复盘进化',
]

const mockProjects = [
  {
    id: '1',
    name: '西北发面包子品牌策划',
    description: '海岸城200平餐厅的市场策略和品牌定位',
    status: 'executing' as const,
    currentStep: 3,
    totalSteps: 8,
    createdAt: '2026-03-27',
    agentCount: 6,
    messageCount: 47,
  },
  {
    id: '2',
    name: '新品上市全渠道推广',
    description: '全渠道营销推广方案策划',
    status: 'planning' as const,
    currentStep: 1,
    totalSteps: 8,
    createdAt: '2026-03-28',
    agentCount: 4,
    messageCount: 12,
  },
  {
    id: '3',
    name: '618大促活动方案',
    description: '618电商大促活动策划和执行方案',
    status: 'completed' as const,
    currentStep: 8,
    totalSteps: 8,
    createdAt: '2026-03-25',
    agentCount: 10,
    messageCount: 156,
  },
]

const statusMap: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
  planning: { color: 'warning', icon: <PlayCircleOutlined />, text: '规划中' },
  executing: { color: 'processing', icon: <SyncOutlined spin />, text: '执行中' },
  completed: { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
}

export default function ProjectList() {
  const navigate = useNavigate()

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <Title level={3} className="m-0">
          <ProjectOutlined className="mr-2 text-purple-500" />
          项目中心
        </Title>
        <Button type="primary" icon={<PlusOutlined />}>
          新建项目
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        {mockProjects.map((project) => {
          const s = statusMap[project.status]
          return (
            <Col span={24} key={project.id}>
              <Card hoverable onClick={() => navigate(`/projects/${project.id}`)}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Title level={4} className="m-0">{project.name}</Title>
                      <Tag color={s.color} icon={s.icon}>{s.text}</Tag>
                    </div>
                    <Paragraph type="secondary" className="mb-3">{project.description}</Paragraph>

                    <Steps
                      size="small"
                      current={project.currentStep - 1}
                      items={projectSteps.map((step, i) => ({
                        title: step,
                        status: i < project.currentStep ? 'finish' : i === project.currentStep ? 'process' : 'wait',
                      }))}
                    />
                  </div>
                  <div className="ml-6 text-right">
                    <Progress type="circle" percent={Math.round((project.currentStep / project.totalSteps) * 100)} size={80} />
                    <div className="mt-2 space-y-1">
                      <div className="text-xs text-gray-500"><ClockCircleOutlined /> {project.createdAt}</div>
                      <div className="text-xs text-gray-500">Agent: {project.agentCount}</div>
                      <div className="text-xs text-gray-500">消息: {project.messageCount}</div>
                    </div>
                  </div>
                </div>
              </Card>
            </Col>
          )
        })}
      </Row>
    </div>
  )
}
