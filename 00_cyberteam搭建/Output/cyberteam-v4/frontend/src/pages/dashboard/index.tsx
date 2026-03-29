import { Card, Col, Row, Statistic, Typography, List, Tag, Progress } from 'antd'
import {
  ThunderboltOutlined,
  TeamOutlined,
  ProjectOutlined,
  DollarOutlined,
  RocketOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'

const { Title } = Typography

const stats = [
  { title: '活跃任务', value: 12, icon: <RocketOutlined />, color: '#3b82f6' },
  { title: 'Agent 数量', value: 14, icon: <TeamOutlined />, color: '#10b981' },
  { title: '今日 Token', value: 847293, icon: <ThunderboltOutlined />, color: '#f59e0b' },
  { title: '今日费用', value: 12.45, prefix: '$', icon: <DollarOutlined />, color: '#8b5cf6' },
]

const recentProjects = [
  { name: '西北发面包子品牌策划', status: 'executing', step: 5, total: 8 },
  { name: '新品上市全渠道推广', status: 'planning', step: 2, total: 8 },
  { name: '618 大促活动方案', status: 'completed', step: 8, total: 8 },
]

const agentActivity = [
  { name: 'CEO', dept: '决策层', status: 'running', task: '路由分拣中' },
  { name: '增长总监', dept: '协调层', status: 'running', task: '策略讨论中' },
  { name: '用户运营专家', dept: '执行层', status: 'idle', task: '等待任务' },
  { name: '质疑者', dept: '质量门禁', status: 'running', task: '审查数据来源' },
]

const statusColor: Record<string, string> = {
  running: 'processing',
  idle: 'default',
  completed: 'success',
  planning: 'warning',
  executing: 'processing',
}

export default function Dashboard() {
  return (
    <div className="p-6">
      <Title level={3}>
        <ThunderboltOutlined className="mr-2 text-yellow-500" />
        CyberTeam 控制台
      </Title>

      <Row gutter={[16, 16]} className="mb-6">
        {stats.map((s) => (
          <Col span={6} key={s.title}>
            <Card hoverable>
              <Statistic
                title={s.title}
                value={s.value}
                prefix={s.prefix ? s.prefix : s.icon}
                valueStyle={{ color: s.color }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={14}>
          <Card title="项目进度" extra={<a href="/projects">查看全部</a>}>
            <List
              dataSource={recentProjects}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={<a href={`/projects/${item.name}`}>{item.name}</a>}
                    description={
                      <Progress percent={Math.round((item.step / item.total) * 100)} size="small" />
                    }
                  />
                  <Tag color={statusColor[item.status]}>{item.status}</Tag>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={10}>
          <Card title="Agent 活动状态">
            <List
              dataSource={agentActivity}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<TeamOutlined className="text-lg" />}
                    title={`${item.name} · ${item.dept}`}
                    description={item.task}
                  />
                  <Tag color={statusColor[item.status]}>{item.status}</Tag>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
