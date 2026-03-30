/**
 * 项目列表页 — 真实 API 驱动
 *
 * 数据来源: /api/v1/projects
 * 降级策略: 后端不可用时显示空状态
 */
import { useState, useEffect, useCallback } from 'react'
import {
  Card, Row, Col, Steps, Tag, Button, List, Typography,
  Space, Progress, Modal, Form, Input, message, Alert,
} from 'antd'
import {
  ProjectOutlined, PlusOutlined, ClockCircleOutlined,
  CheckCircleOutlined, SyncOutlined, PlayCircleOutlined,
  ReloadOutlined, ApiOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { fetchProjects, createProject, type Project } from '@/apis/modules/projects'

const { Title, Paragraph, Text } = Typography

const projectSteps = [
  'CEO-COO对齐', '策略讨论', '风险预案', 'CEO汇报',
  '设计联动', '文案产出', 'CEO汇总', '复盘进化',
]

const statusMap: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
  planning: { color: 'warning', icon: <PlayCircleOutlined />, text: '规划中' },
  executing: { color: 'processing', icon: <SyncOutlined spin />, text: '执行中' },
  completed: { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
  paused: { color: 'default', icon: <ClockCircleOutlined />, text: '已暂停' },
}

export default function ProjectList() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [apiAvailable, setApiAvailable] = useState<boolean | null>(null)
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [creating, setCreating] = useState(false)
  const [form] = Form.useForm()

  const loadProjects = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchProjects()
      setProjects(data)
      setApiAvailable(true)
    } catch (error) {
      console.warn('[Projects] 加载失败:', error)
      setApiAvailable(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  const handleCreate = async (values: { name: string; description?: string }) => {
    setCreating(true)
    try {
      const newProject = await createProject({
        name: values.name,
        description: values.description,
      })
      if (newProject) {
        message.success(`项目「${values.name}」创建成功`)
        setProjects(prev => [newProject, ...prev])
        setCreateModalOpen(false)
        form.resetFields()
        navigate(`/projects/${newProject.id}`)
      }
    } finally {
      setCreating(false)
    }
  }

  const renderEmpty = () => (
    <Card>
      <div style={{ textAlign: 'center', padding: '48px 0' }}>
        <ProjectOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
        <Title level={4} type="secondary">暂无项目</Title>
        <Paragraph type="secondary">
          创建第一个项目，开启 AI 协作之旅
        </Paragraph>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setCreateModalOpen(true)}
        >
          新建项目
        </Button>
      </div>
    </Card>
  )

  const renderApiWarning = () => {
    if (apiAvailable === false) {
      return (
        <Alert
          type="warning"
          showIcon
          icon={<ApiOutlined />}
          message="后端服务未连接"
          description="无法从后端获取项目数据。请确保 uvicorn 后端已启动。"
          action={
            <Button size="small" icon={<ReloadOutlined />} onClick={loadProjects}>
              重试
            </Button>
          }
          style={{ marginBottom: 16 }}
        />
      )
    }
    return null
  }

  return (
    <div className="p-6">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <ProjectOutlined className="mr-2 text-purple-500" />
          项目中心
        </Title>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadProjects}
            loading={loading}
          >
            刷新
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalOpen(true)}
          >
            新建项目
          </Button>
        </Space>
      </div>

      {renderApiWarning()}

      {projects.length === 0 && !loading ? (
        renderEmpty()
      ) : (
        <Row gutter={[16, 16]}>
          {projects.map((project) => {
            const s = statusMap[project.status] || statusMap.planning
            return (
              <Col span={24} key={project.id}>
                <Card
                  hoverable
                  onClick={() => navigate(`/projects/${project.id}`)}
                  loading={loading}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                        <Title level={4} style={{ margin: 0 }}>{project.name}</Title>
                        <Tag color={s.color} icon={s.icon}>{s.text}</Tag>
                      </div>
                      <Paragraph type="secondary" style={{ marginBottom: 12 }}>
                        {project.description || '暂无描述'}
                      </Paragraph>

                      <Steps
                        size="small"
                        current={project.currentStep - 1}
                        items={projectSteps.map((step, i) => ({
                          title: step,
                          status: i < project.currentStep ? 'finish' :
                                  i === project.currentStep ? 'process' : 'wait',
                        }))}
                      />
                    </div>

                    <div style={{ marginLeft: 24, textAlign: 'right', minWidth: 100 }}>
                      <Progress
                        type="circle"
                        percent={Math.round((project.currentStep / project.totalSteps) * 100)}
                        size={80}
                      />
                      <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
                        <div><ClockCircleOutlined /> {project.createdAt}</div>
                        <div>Agent: {project.agentCount}</div>
                        <div>消息: {project.messageCount}</div>
                      </div>
                    </div>
                  </div>
                </Card>
              </Col>
            )
          })}
        </Row>
      )}

      {/* 创建项目 Modal */}
      <Modal
        title="新建项目"
        open={createModalOpen}
        onCancel={() => { setCreateModalOpen(false); form.resetFields() }}
        footer={null}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          style={{ marginTop: 16 }}
        >
          <Form.Item
            name="name"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="例如：西北发面包子品牌策划" />
          </Form.Item>
          <Form.Item
            name="description"
            label="项目描述（可选）"
          >
            <Input.TextArea
              placeholder="简要描述项目背景和目标..."
              rows={3}
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => { setCreateModalOpen(false); form.resetFields() }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={creating}>
                创建项目
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
