/**
 * 部门管理页面
 * - 部门列表（表格）
 * - 创建/编辑/删除部门
 * - 部门绑定 Agent
 * API: /api/v1/departments
 */
import { useState, useEffect, useCallback } from 'react'
import {
  Table, Card, Button, Modal, Form, Input, Select, Tag, Space,
  Popconfirm, message, Row, Col, Statistic, Alert, Drawer,
  Transfer, Typography, Tooltip, Divider,
} from 'antd'
import {
  PlusOutlined, EditOutlined, DeleteOutlined, TeamOutlined,
  SafetyCertificateOutlined, ApiOutlined, UnorderedListOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import {
  fetchDepartments,
  fetchDepartment,
  registerDepartment,
  updateDepartment,
  deleteDepartment,
  fetchDepartmentAgents,
  bindAgentToDepartment,
  unbindAgentFromDepartment,
  fetchDepartmentStatistics,
  type Department,
  type RegisterDepartmentRequest,
  type UpdateDepartmentRequest,
} from '@/apis/modules/departments'
import { fetchAgents, type CustomAgent } from '@/apis/modules/custom-agents'

const { Title, Text } = Typography

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(false)
  const [apiAvailable, setApiAvailable] = useState<boolean>(true)
  const [statistics, setStatistics] = useState<{
    total_count: number
    builtin_count: number
    custom_count: number
  } | null>(null)

  // 创建/编辑 Modal
  const [modalVisible, setModalVisible] = useState(false)
  const [editingDepartment, setEditingDepartment] = useState<Department | null>(null)
  const [form] = Form.useForm()

  // Agent 绑定 Drawer
  const [agentDrawerVisible, setAgentDrawerVisible] = useState(false)
  const [selectedDepartment, setSelectedDepartment] = useState<Department | null>(null)
  const [boundAgents, setBoundAgents] = useState<string[]>([])
  const [allAgents, setAllAgents] = useState<CustomAgent[]>([])
  const [agentLoading, setAgentLoading] = useState(false)

  const loadDepartments = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchDepartments()
      setDepartments(data)
      setApiAvailable(true)
    } catch (error) {
      console.warn('[Departments] 加载失败:', error)
      setApiAvailable(false)
    } finally {
      setLoading(false)
    }
  }, [apiAvailable])

  const loadStatistics = useCallback(async () => {
    const stats = await fetchDepartmentStatistics()
    if (stats) {
      setStatistics(stats)
    }
  }, [])

  useEffect(() => {
    loadDepartments()
    loadStatistics()
  }, [loadDepartments, loadStatistics])

  // 打开创建 Modal
  const handleCreate = () => {
    setEditingDepartment(null)
    form.resetFields()
    setModalVisible(true)
  }

  // 打开编辑 Modal
  const handleEdit = (dept: Department) => {
    setEditingDepartment(dept)
    form.setFieldsValue({
      name: dept.name,
      description: dept.description,
      responsibility: dept.responsibility,
      leader_role: dept.leader?.role,
      leader_skills: dept.leader?.skills,
      executor_role: dept.executor?.role,
      executor_skills: dept.executor?.skills,
      price_tier: dept.price_tier,
      tags: dept.tags,
    })
    setModalVisible(true)
  }

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()

      if (editingDepartment) {
        // 更新
        const request: UpdateDepartmentRequest = {
          name: values.name,
          description: values.description,
          responsibility: values.responsibility,
          leader_role: values.leader_role,
          leader_skills: values.leader_skills,
          executor_role: values.executor_role,
          executor_skills: values.executor_skills,
          price_tier: values.price_tier,
          tags: values.tags,
        }
        const result = await updateDepartment(editingDepartment.department_id, request)
        if (result) {
          message.success('部门更新成功')
          setModalVisible(false)
          loadDepartments()
          loadStatistics()
        } else {
          message.error('部门更新失败')
        }
      } else {
        // 创建
        const request: RegisterDepartmentRequest = {
          department_id: values.department_id,
          name: values.name,
          description: values.description,
          responsibility: values.responsibility,
          leader_role: values.leader_role,
          leader_skills: values.leader_skills,
          executor_role: values.executor_role,
          executor_skills: values.executor_skills,
          price_tier: values.price_tier || '免费',
          tags: values.tags || [],
        }
        const result = await registerDepartment(request)
        if (result) {
          message.success('部门创建成功')
          setModalVisible(false)
          loadDepartments()
          loadStatistics()
        } else {
          message.error('部门创建失败')
        }
      }
    } catch (error) {
      console.error('[Departments] 提交失败:', error)
    }
  }

  // 删除部门
  const handleDelete = async (departmentId: string) => {
    const success = await deleteDepartment(departmentId)
    if (success) {
      message.success('部门删除成功')
      loadDepartments()
      loadStatistics()
    } else {
      message.error('部门删除失败（内置部门无法删除）')
    }
  }

  // 打开 Agent 绑定 Drawer
  const handleBindAgent = async (dept: Department) => {
    setSelectedDepartment(dept)
    setAgentDrawerVisible(true)
    setAgentLoading(true)

    // 加载所有 Agents
    const agents = await fetchAgents()
    setAllAgents(agents)

    // 加载已绑定的 Agents
    const bound = await fetchDepartmentAgents(dept.department_id)
    setBoundAgents(bound)

    setAgentLoading(false)
  }

  // 绑定/解绑 Agent
  const handleAgentChange = async (
    targetKeys: React.Key[],
    direction: 'left' | 'right',
    moveKeys: React.Key[]
  ) => {
    if (!selectedDepartment) return

    const departmentId = selectedDepartment.department_id

    // 找出新增的和移除的
    const targetKeysStr = targetKeys.map(k => String(k))
    const toAdd = targetKeysStr.filter(key => !boundAgents.includes(key))
    const toRemove = boundAgents.filter(key => !targetKeysStr.includes(key))

    for (const agentCode of toAdd) {
      await bindAgentToDepartment(departmentId, agentCode)
    }
    for (const agentCode of toRemove) {
      await unbindAgentFromDepartment(departmentId, agentCode)
    }

    setBoundAgents(targetKeysStr)
    message.success('Agent 绑定更新成功')
  }

  const columns: ColumnsType<Department> = [
    {
      title: '部门ID',
      dataIndex: 'department_id',
      key: 'department_id',
      width: 150,
      render: (id: string, record) => (
        <Space>
          <Tag color={record.is_builtin ? 'gold' : 'blue'}>{id}</Tag>
          {record.is_builtin && (
            <Tooltip title="内置部门">
              <SafetyCertificateOutlined style={{ color: '#f59e0b' }} />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: '部门名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
      render: (name: string) => <Text strong>{name}</Text>,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '核心职责',
      dataIndex: 'responsibility',
      key: 'responsibility',
      ellipsis: true,
    },
    {
      title: 'Leader',
      key: 'leader',
      width: 150,
      render: (_, record) => (
        <div>
          <div>{record.leader?.role}</div>
          <Text type="secondary" style={{ fontSize: 11 }}>
            {record.leader?.skills?.slice(0, 2).join(', ')}
          </Text>
        </div>
      ),
    },
    {
      title: '价格层级',
      dataIndex: 'price_tier',
      key: 'price_tier',
      width: 100,
      render: (tier: string) => {
        const colorMap: Record<string, string> = {
          '免费': 'green',
          '基础': 'blue',
          '专业': 'purple',
          '企业': 'red',
        }
        return <Tag color={colorMap[tier] || 'default'}>{tier}</Tag>
      },
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 150,
      render: (tags: string[]) => (
        <>
          {tags?.slice(0, 2).map(tag => (
            <Tag key={tag} style={{ marginBottom: 2 }}>{tag}</Tag>
          ))}
          {tags?.length > 2 && <Tag style={{ marginBottom: 2 }}>+{tags.length - 2}</Tag>}
        </>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<TeamOutlined />}
            onClick={() => handleBindAgent(record)}
          >
            绑定Agent
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={record.is_builtin}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除"
            description={record.is_builtin ? '内置部门无法删除' : '确定要删除此部门吗？'}
            onConfirm={() => handleDelete(record.department_id)}
            disabled={record.is_builtin}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              disabled={record.is_builtin}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="p-6">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <UnorderedListOutlined className="mr-2 text-blue-500" />
          部门管理
        </Title>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建部门
          </Button>
        </Space>
      </div>

      {apiAvailable === false && (
        <Alert
          type="warning"
          showIcon
          icon={<ApiOutlined />}
          message="后端服务不可用"
          description="无法连接到部门管理 API，请检查后端服务是否启动。"
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 统计卡片 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Card><Statistic title="总部门数" value={statistics.total_count} prefix={<TeamOutlined />} /></Card>
          </Col>
          <Col span={6}>
            <Card><Statistic title="内置部门" value={statistics.builtin_count} valueStyle={{ color: '#f59e0b' }} /></Card>
          </Col>
          <Col span={6}>
            <Card><Statistic title="自定义部门" value={statistics.custom_count} valueStyle={{ color: '#3b82f6' }} /></Card>
          </Col>
          <Col span={6}>
            <Card><Statistic title="Agent 总数" value={departments.length * 3} suffix="+" valueStyle={{ color: '#10b981' }} /></Card>
          </Col>
        </Row>
      )}

      {/* 部门表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={departments}
          rowKey="department_id"
          loading={loading}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 创建/编辑 Modal */}
      <Modal
        title={editingDepartment ? '编辑部门' : '创建部门'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText={editingDepartment ? '更新' : '创建'}
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          {!editingDepartment && (
            <Form.Item
              name="department_id"
              label="部门ID"
              rules={[
                { required: true, message: '请输入部门ID' },
                { pattern: /^[a-z0-9_-]+$/, message: '仅允许小写字母、数字、下划线和连字符' },
              ]}
            >
              <Input placeholder="如: marketing_team" />
            </Form.Item>
          )}

          <Form.Item name="name" label="部门名称" rules={[{ required: true, message: '请输入部门名称' }]}>
            <Input placeholder="如: 增长部" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} placeholder="部门描述" />
          </Form.Item>

          <Form.Item name="responsibility" label="核心职责">
            <Input.TextArea rows={2} placeholder="如: 负责用户增长和运营策略" />
          </Form.Item>

          <Divider>Leader 配置</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="leader_role" label="Leader 角色">
                <Input placeholder="如: 增长总监" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="leader_skills" label="Leader 技能">
                <Select mode="tags" placeholder="输入技能后回车" />
              </Form.Item>
            </Col>
          </Row>

          <Divider>执行器配置</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="executor_role" label="执行器角色">
                <Input placeholder="如: 运营专家" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="executor_skills" label="执行器技能">
                <Select mode="tags" placeholder="输入技能后回车" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="price_tier" label="价格层级">
                <Select
                  placeholder="选择价格层级"
                  options={[
                    { value: '免费', label: '免费' },
                    { value: '基础', label: '基础' },
                    { value: '专业', label: '专业' },
                    { value: '企业', label: '企业' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="tags" label="标签">
                <Select mode="tags" placeholder="输入标签后回车" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Agent 绑定 Drawer */}
      <Drawer
        title={`绑定 Agent - ${selectedDepartment?.name || ''}`}
        placement="right"
        width={500}
        open={agentDrawerVisible}
        onClose={() => setAgentDrawerVisible(false)}
      >
        <Transfer
          dataSource={allAgents.map(agent => ({
            key: agent.code,
            title: `${agent.name} (${agent.code})`,
            description: agent.description || agent.agent_type,
          }))}
          targetKeys={boundAgents}
          onChange={handleAgentChange}
          render={item => item.title || ''}
          showSearch
          filterOption={(input, item) =>
            (item.title as string)?.toLowerCase().includes(input.toLowerCase())
          }
          listStyle={{ width: 450, height: 400 }}
          operations={['绑定', '解绑']}
          titles={['可选 Agent', '已绑定 Agent']}
        />
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">
            已绑定 {boundAgents.length} 个 Agent
          </Text>
        </div>
      </Drawer>
    </div>
  )
}
