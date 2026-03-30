/**
 * Dashboard 控制台 — 真实 API 驱动
 *
 * 数据来源:
 * - /api/tasks        → 活跃任务数、近期任务
 * - /api/agents       → Agent 数量、活动状态
 * - /api/v1/projects  → 近期项目进度
 *
 * 降级策略: 后端不可用时显示连接状态提示，而非假数据
 */
import { useState, useEffect, useCallback } from 'react'
import { Card, Col, Row, Statistic, List, Tag, Progress, Typography, Alert, Button, Space } from 'antd'
import {
  ThunderboltOutlined,
  TeamOutlined,
  ProjectOutlined,
  DollarOutlined,
  RocketOutlined,
  ReloadOutlined,
  ApiOutlined,
} from '@ant-design/icons'
import { Link } from 'react-router-dom'
import { fetchDashboardStats } from '@/apis/modules/stats'
import { fetchProjects } from '@/apis/modules/projects'
import type { DashboardStats, AgentActivity } from '@/apis/modules/stats'
import type { Project } from '@/apis/modules/projects'

const { Title, Text } = Typography

const statusColor: Record<string, string> = {
  running: 'processing',
  active: 'processing',
  idle: 'default',
  completed: 'success',
  done: 'success',
  planning: 'warning',
  executing: 'processing',
  shutdown: 'error',
}

const statusText: Record<string, string> = {
  running: 'running',
  active: 'running',
  idle: 'idle',
  completed: 'completed',
  done: 'completed',
  planning: 'planning',
  executing: 'executing',
  shutdown: 'shutdown',
}

// 8 步流程定义
const projectSteps = [
  'CEO-COO对齐', '策略讨论', '风险预案', 'CEO汇报',
  '设计联动', '文案产出', 'CEO汇总', '复盘进化',
]

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [agentActivity, setAgentActivity] = useState<AgentActivity[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [apiAvailable, setApiAvailable] = useState<boolean | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [statsData, projectsData] = await Promise.all([
        fetchDashboardStats(),
        fetchProjects(),
      ])

      setStats(statsData.stats)
      setAgentActivity(statsData.agentActivity)
      setProjects(projectsData.slice(0, 3))
      setApiAvailable(true)
      setLastUpdated(new Date())
    } catch (error) {
      console.warn('[Dashboard] 数据加载失败:', error)
      setApiAvailable(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
    // 每 30 秒自动刷新
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [loadData])

  // API 不可用警告
  const renderApiWarning = () => {
    if (apiAvailable === false) {
      return (
        <Alert
          type="warning"
          showIcon
          icon={<ApiOutlined />}
          message="后端服务未连接"
          description="无法从后端获取实时数据。请确保后端服务已启动 (uvicorn backend.app.main:app --port 49187)。"
          action={
            <Button size="small" icon={<ReloadOutlined />} onClick={loadData}>
              重试
            </Button>
          }
          style={{ marginBottom: 16 }}
        />
      )
    }
    return null
  }

  // 统计数据卡片
  const renderStatCards = () => {
    const items = [
      {
        title: '活跃任务',
        value: stats?.activeTasks ?? 0,
        icon: <RocketOutlined />,
        color: '#3b82f6',
      },
      {
        title: 'Agent 数量',
        value: stats?.agentCount ?? 0,
        icon: <TeamOutlined />,
        color: '#10b981',
      },
      {
        title: '今日 Token',
        value: stats?.todayTokens ?? 0,
        icon: <ThunderboltOutlined />,
        color: '#f59e0b',
        precision: 0,
      },
      {
        title: '今日费用',
        value: stats?.todayCost ?? 0,
        prefix: '$',
        icon: <DollarOutlined />,
        color: '#8b5cf6',
        precision: 2,
      },
    ]

    return (
      <Row gutter={[16, 16]} className="mb-6">
        {items.map((s) => (
          <Col span={6} key={s.title}>
            <Card hoverable loading={loading && stats === null}>
              <Statistic
                title={s.title}
                value={s.value}
                prefix={s.prefix ? s.prefix : s.icon}
                precision={s.precision}
                valueStyle={{ color: s.color }}
              />
            </Card>
          </Col>
        ))}
      </Row>
    )
  }

  // 近期项目
  const renderProjects = () => (
    <Card
      title="项目进度"
      extra={<Link to="/projects">查看全部</Link>}
      loading={loading && projects.length === 0}
    >
      {projects.length === 0 && !loading ? (
        <div style={{ textAlign: 'center', padding: '24px 0', color: '#999' }}>
          <ProjectOutlined style={{ fontSize: 32, marginBottom: 8 }} />
          <div>暂无项目</div>
          <Link to="/projects">
            <Button type="link" size="small">创建第一个项目</Button>
          </Link>
        </div>
      ) : (
        <List
          dataSource={projects}
          renderItem={(project) => (
            <List.Item>
              <List.Item.Meta
                title={<Link to={`/projects/${project.id}`}>{project.name}</Link>}
                description={
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {project.description || '暂无描述'}
                    </Text>
                    <Progress
                      percent={Math.round((project.currentStep / project.totalSteps) * 100)}
                      size="small"
                      steps={8}
                      strokeColor="#3b82f6"
                    />
                  </Space>
                }
              />
              <Tag color={statusColor[project.status] || 'default'}>
                {statusText[project.status] || project.status}
              </Tag>
            </List.Item>
          )}
        />
      )}
    </Card>
  )

  // Agent 活动状态
  const renderAgentActivity = () => (
    <Card
      title="Agent 活动状态"
      extra={
        <Space>
          {lastUpdated && (
            <Text type="secondary" style={{ fontSize: 11 }}>
              更新于 {lastUpdated.toLocaleTimeString()}
            </Text>
          )}
          <Button
            type="text"
            icon={<ReloadOutlined />}
            size="small"
            onClick={loadData}
            loading={loading}
          />
        </Space>
      }
      loading={loading && agentActivity.length === 0}
    >
      {agentActivity.length === 0 && !loading ? (
        <div style={{ textAlign: 'center', padding: '24px 0', color: '#999' }}>
          <TeamOutlined style={{ fontSize: 32, marginBottom: 8 }} />
          <div>暂无 Agent 在线</div>
        </div>
      ) : (
        <List
          dataSource={agentActivity}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                avatar={<TeamOutlined className="text-lg" />}
                title={`${item.name} · ${item.dept}`}
                description={item.task}
              />
              <Tag color={statusColor[item.status] || 'default'}>
                {statusText[item.status] || item.status}
              </Tag>
            </List.Item>
          )}
        />
      )}
    </Card>
  )

  return (
    <div className="p-6">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <ThunderboltOutlined className="mr-2 text-yellow-500" />
          CyberTeam 控制台
        </Title>
        <Space>
          {apiAvailable && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              实时数据 · {lastUpdated?.toLocaleTimeString() || '加载中...'}
            </Text>
          )}
        </Space>
      </div>

      {renderApiWarning()}
      {renderStatCards()}

      <Row gutter={[16, 16]}>
        <Col span={14}>
          {renderProjects()}
        </Col>
        <Col span={10}>
          {renderAgentActivity()}
        </Col>
      </Row>
    </div>
  )
}
