/**
 * 自定义 Agent 管理页面
 * - Agent 列表（表格，支持按公司/技能筛选）
 * - 创建自定义 Agent（表单：名称、code、描述、技能绑定）
 * - 编辑/删除 Agent
 * - Agent 详情（含绑定的 Skill 列表）
 * API: /api/v1/agents
 */
import { useState, useEffect, useCallback } from 'react'
import {
  Table, Card, Button, Modal, Form, Input, Select, Tag, Space,
  Popconfirm, message, Row, Col, Statistic, Alert, Drawer,
  Typography, Tooltip, Divider, Descriptions, Timeline,
} from 'antd'
import {
  PlusOutlined, EditOutlined, DeleteOutlined, RobotOutlined,
  ApiOutlined, UserOutlined, CodeOutlined, TagsOutlined,
  SolutionOutlined, ClockCircleOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import {
  fetchAgents,
  fetchAgent,
  createAgent,
  updateAgent,
  deleteAgent,
  bindSkillToAgent,
  unbindSkillFromAgent,
  fetchSkills,
  type CustomAgent,
  type CreateAgentRequest,
  type UpdateAgentRequest,
  type Skill,
} from '@/apis/modules/custom-agents'

const { Title, Text, Paragraph } = Typography

export default function CustomAgentsPage() {
  const [agents, setAgents] = useState<CustomAgent[]>([])
  const [loading, setLoading] = useState(false)
  const [apiAvailable, setApiAvailable] = useState<boolean>(true)

  // 筛选
  const [filterCompany, setFilterCompany] = useState<string>('')
  const [filterSkill, setFilterSkill] = useState<string>('')
  const [searchText, setSearchText] = useState('')

  // 创建/编辑 Modal
  const [modalVisible, setModalVisible] = useState(false)
  const [editingAgent, setEditingAgent] = useState<CustomAgent | null>(null)
  const [form] = Form.useForm()

  // 详情 Drawer
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<CustomAgent | null>(null)
  const [agentSkills, setAgentSkills] = useState<Skill[]>([])

  // Skill 绑定 Modal
  const [skillModalVisible, setSkillModalVisible] = useState(false)
  const [availableSkills, setAvailableSkills] = useState<Skill[]>([])
  const [selectedSkillId, setSelectedSkillId] = useState<string>('')

  const loadAgents = useCallback(async () => {
    setLoading(true)
    try {
      const params: { companyId?: string; skillIds?: string[] } = {}
      if (filterCompany) params.companyId = filterCompany
      if (filterSkill) params.skillIds = [filterSkill]

      const data = await fetchAgents(params.companyId, params.skillIds)
      setAgents(data)
      setApiAvailable(true)
    } catch (error) {
      console.warn('[CustomAgents] 加载失败:', error)
      setApiAvailable(false)
    } finally {
      setLoading(false)
    }
  }, [filterCompany, filterSkill, apiAvailable])

  useEffect(() => {
    loadAgents()
  }, [loadAgents])

  // 加载可用 Skills
  const loadSkills = useCallback(async () => {
    const skills = await fetchSkills()
    setAvailableSkills(skills)
  }, [])

  // 打开创建 Modal
  const handleCreate = () => {
    setEditingAgent(null)
    form.resetFields()
    setModalVisible(true)
  }

  // 打开编辑 Modal
  const handleEdit = (agent: CustomAgent) => {
    setEditingAgent(agent)
    form.setFieldsValue({
      name: agent.name,
      code: agent.code,
      agent_type: agent.agent_type,
      description: agent.description,
      skills: agent.skills,
    })
    setModalVisible(true)
  }

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()

      if (editingAgent) {
        // 更新
        const request: UpdateAgentRequest = {
          name: values.name,
          description: values.description,
          skills: values.skills,
          is_active: values.is_active,
        }
        const result = await updateAgent(editingAgent.code, request)
        if (result) {
          message.success('Agent 更新成功')
          setModalVisible(false)
          loadAgents()
        } else {
          message.error('Agent 更新失败')
        }
      } else {
        // 创建
        const request: CreateAgentRequest = {
          name: values.name,
          code: values.code,
          agent_type: values.agent_type || 'custom',
          description: values.description,
          skills: values.skills || [],
        }
        const result = await createAgent(request)
        if (result) {
          message.success('Agent 创建成功')
          setModalVisible(false)
          loadAgents()
        } else {
          message.error('Agent 创建失败')
        }
      }
    } catch (error) {
      console.error('[CustomAgents] 提交失败:', error)
    }
  }

  // 删除 Agent
  const handleDelete = async (code: string) => {
    const success = await deleteAgent(code)
    if (success) {
      message.success('Agent 删除成功')
      loadAgents()
    } else {
      message.error('Agent 删除失败')
    }
  }

  // 打开详情 Drawer
  const handleViewDetail = async (agent: CustomAgent) => {
    setSelectedAgent(agent)
    setDetailDrawerVisible(true)

    // 加载 Agent 的 Skills
    const skills = await fetchSkills()
    const agentSkillsData = skills.filter(s => agent.skills.includes(s.code))
    setAgentSkills(agentSkillsData)
  }

  // 打开 Skill 绑定 Modal
  const handleBindSkill = async (agent: CustomAgent) => {
    setSelectedAgent(agent)
    await loadSkills()
    setSkillModalVisible(true)
  }

  // 绑定 Skill
  const handleAddSkill = async () => {
    if (!selectedAgent || !selectedSkillId) return

    const result = await bindSkillToAgent(selectedAgent.code, selectedSkillId)
    if (result) {
      message.success('Skill 绑定成功')
      // 更新本地数据
      setSelectedAgent(result)
      const skills = await fetchSkills()
      const agentSkillsData = skills.filter(s => result.skills.includes(s.code))
      setAgentSkills(agentSkillsData)
      loadAgents()
    } else {
      message.error('Skill 绑定失败')
    }
  }

  // 解绑 Skill
  const handleUnbindSkill = async (skillId: string) => {
    if (!selectedAgent) return

    const result = await unbindSkillFromAgent(selectedAgent.code, skillId)
    if (result) {
      message.success('Skill 解绑成功')
      setSelectedAgent(result)
      const skills = await fetchSkills()
      const agentSkillsData = skills.filter(s => result.skills.includes(s.code))
      setAgentSkills(agentSkillsData)
      loadAgents()
    } else {
      message.error('Skill 解绑失败')
    }
  }

  const filteredAgents = agents.filter(agent => {
    if (!searchText) return true
    const lower = searchText.toLowerCase()
    return (
      agent.name.toLowerCase().includes(lower) ||
      agent.code.toLowerCase().includes(lower) ||
      agent.description?.toLowerCase().includes(lower)
    )
  })

  const columns: ColumnsType<CustomAgent> = [
    {
      title: 'Agent',
      key: 'agent',
      width: 250,
      render: (_, record) => (
        <Space>
          <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#3b82f6' }} />
          <div>
            <div>
              <Text strong>{record.name}</Text>
              <Tag color={record.is_active ? 'success' : 'default'} style={{ marginLeft: 8 }}>
                {record.is_active ? '活跃' : '停用'}
              </Tag>
            </div>
            <Text type="secondary" style={{ fontSize: 12 }}>
              <CodeOutlined /> {record.code}
            </Text>
          </div>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'agent_type',
      key: 'agent_type',
      width: 100,
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '技能',
      key: 'skills',
      width: 200,
      render: (_, record) => (
        <div>
          {record.skills.slice(0, 2).map(skill => (
            <Tag key={skill} style={{ marginBottom: 2 }}>{skill}</Tag>
          ))}
          {record.skills.length > 2 && (
            <Tag style={{ marginBottom: 2 }}>+{record.skills.length - 2}</Tag>
          )}
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          active: 'green',
          inactive: 'red',
        }
        return <Tag color={colorMap[status] || 'default'}>{status}</Tag>
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          <ClockCircleOutlined /> {new Date(date).toLocaleString('zh-CN')}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 220,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<SolutionOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<TagsOutlined />}
            onClick={() => handleBindSkill(record)}
          >
            绑定技能
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除"
            description="确定要删除此 Agent 吗？"
            onConfirm={() => handleDelete(record.code)}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // 获取所有唯一的公司 ID
  const companyOptions = [...new Set(agents.map(a => a.company_id).filter(Boolean))].map(id => ({
    value: id as string,
    label: id as string,
  }))

  return (
    <div className="p-6">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <RobotOutlined className="mr-2 text-purple-500" />
          自定义 Agent 管理
        </Title>
        <Space>
          <Input.Search
            placeholder="搜索 Agent..."
            style={{ width: 200 }}
            onChange={e => setSearchText(e.target.value)}
          />
          <Select
            placeholder="按公司筛选"
            allowClear
            style={{ width: 150 }}
            value={filterCompany || undefined}
            onChange={val => setFilterCompany(val || '')}
            options={companyOptions}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建 Agent
          </Button>
        </Space>
      </div>

      {apiAvailable === false && (
        <Alert
          type="warning"
          showIcon
          icon={<ApiOutlined />}
          message="后端服务不可用"
          description="无法连接到 Agent 管理 API，请检查后端服务是否启动。"
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card><Statistic title="Agent 总数" value={agents.length} prefix={<RobotOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="活跃 Agent" value={agents.filter(a => a.is_active).length} valueStyle={{ color: '#10b981' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="技能绑定数" value={agents.reduce((sum, a) => sum + a.skill_count, 0)} suffix="次" /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="公司覆盖" value={companyOptions.length} valueStyle={{ color: '#3b82f6' }} /></Card>
        </Col>
      </Row>

      {/* Agent 表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredAgents}
          rowKey="code"
          loading={loading}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          scroll={{ x: 1100 }}
        />
      </Card>

      {/* 创建/编辑 Modal */}
      <Modal
        title={editingAgent ? '编辑 Agent' : '创建 Agent'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText={editingAgent ? '更新' : '创建'}
        cancelText="取消"
        width={500}
      >
        <Form form={form} layout="vertical">
          {!editingAgent && (
            <>
              <Form.Item
                name="code"
                label="Agent Code"
                rules={[
                  { required: true, message: '请输入 Agent Code' },
                  { pattern: /^[a-z0-9_-]+$/, message: '仅允许小写字母、数字、下划线和连字符' },
                ]}
              >
                <Input placeholder="如: my_custom_agent" />
              </Form.Item>
              <Form.Item name="agent_type" label="Agent 类型">
                <Select
                  placeholder="选择类型"
                  options={[
                    { value: 'custom', label: '自定义' },
                    { value: 'assistant', label: '助手' },
                    { value: 'specialist', label: '专家' },
                  ]}
                />
              </Form.Item>
            </>
          )}

          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
            <Input placeholder="如: 营销助手" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="Agent 功能描述" />
          </Form.Item>

          {editingAgent && (
            <Form.Item name="is_active" label="状态" valuePropName="checked">
              <Select
                options={[
                  { value: true, label: '活跃' },
                  { value: false, label: '停用' },
                ]}
              />
            </Form.Item>
          )}
        </Form>
      </Modal>

      {/* 详情 Drawer */}
      <Drawer
        title={`Agent 详情 - ${selectedAgent?.name || ''}`}
        placement="right"
        width={600}
        open={detailDrawerVisible}
        onClose={() => setDetailDrawerVisible(false)}
      >
        {selectedAgent && (
          <div>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="Code" span={1}>
                <Tag icon={<CodeOutlined />}>{selectedAgent.code}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="类型" span={1}>
                <Tag>{selectedAgent.agent_type}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="名称" span={2}>
                <Text strong>{selectedAgent.name}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                <Paragraph>{selectedAgent.description || '无'}</Paragraph>
              </Descriptions.Item>
              <Descriptions.Item label="状态" span={1}>
                <Tag color={selectedAgent.is_active ? 'success' : 'default'}>
                  {selectedAgent.is_active ? '活跃' : '停用'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="公司 ID" span={1}>
                {selectedAgent.company_id || '未绑定'}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间" span={1}>
                {new Date(selectedAgent.created_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
              <Descriptions.Item label="更新时间" span={1}>
                {new Date(selectedAgent.updated_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
            </Descriptions>

            <Divider>绑定的 Skills ({selectedAgent.skills.length})</Divider>

            {agentSkills.length > 0 ? (
              <Timeline
                items={agentSkills.map(skill => ({
                  color: 'blue',
                  children: (
                    <div>
                      <Text strong>{skill.name}</Text>
                      <Tag style={{ marginLeft: 8 }}>{skill.category}</Tag>
                      <Tag color={skill.difficulty === 'easy' ? 'green' : skill.difficulty === 'hard' ? 'red' : 'orange'}>
                        {skill.difficulty}
                      </Tag>
                      <br />
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {skill.description || '无描述'}
                      </Text>
                      <br />
                      <Space style={{ marginTop: 4 }}>
                        {skill.trigger_keywords.slice(0, 3).map(kw => (
                          <Tag key={kw}>{kw}</Tag>
                        ))}
                      </Space>
                      <br />
                      <Button
                        type="link"
                        size="small"
                        danger
                        onClick={() => handleUnbindSkill(skill.code)}
                      >
                        解绑
                      </Button>
                    </div>
                  ),
                }))}
              />
            ) : (
              <Text type="secondary">暂无绑定的 Skills</Text>
            )}
          </div>
        )}
      </Drawer>

      {/* 绑定 Skill Modal */}
      <Modal
        title={`绑定 Skill - ${selectedAgent?.name || ''}`}
        open={skillModalVisible}
        onOk={handleAddSkill}
        onCancel={() => {
          setSkillModalVisible(false)
          setSelectedSkillId('')
        }}
        okText="绑定"
        cancelText="取消"
      >
        <Form layout="vertical">
          <Form.Item label="选择 Skill" required>
            <Select
              placeholder="请选择要绑定的 Skill"
              value={selectedSkillId || undefined}
              onChange={setSelectedSkillId}
              showSearch
              filterOption={(input, option) =>
                (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
              }
              options={availableSkills
                .filter(s => !selectedAgent?.skills.includes(s.code))
                .map(s => ({
                  value: s.code,
                  label: `${s.name} (${s.code}) - ${s.category}`,
                }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

// Avatar 组件别名
function Avatar({ icon, style }: { icon: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div
      style={{
        width: 40,
        height: 40,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        ...style,
      }}
    >
      {icon}
    </div>
  )
}
