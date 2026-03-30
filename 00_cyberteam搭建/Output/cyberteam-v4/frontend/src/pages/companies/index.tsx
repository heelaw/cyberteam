/**
 * 公司管理页面 - 公司列表/创建/编辑/删除/详情
 * 数据来源: /api/v1/companies
 */
import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Space,
  Input,
  Modal,
  Form,
  message,
  Popconfirm,
  Drawer,
  Descriptions,
  Statistic,
  Row,
  Col,
  Tag,
  Card,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
  ReloadOutlined,
  TeamOutlined,
  ApartmentOutlined,
  RobotOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import {
  fetchCompanies,
  createCompany,
  updateCompany,
  deleteCompany,
  fetchCompanyDepartments,
  fetchCompanyAgents,
  fetchCompanyStats,
  type Company,
  type CompanyCreate,
  type CompanyUpdate,
  type DepartmentSummary,
  type AgentSummary,
  type CompanyStats,
} from '@/apis/modules/companies'

const { Search } = Input

// 状态颜色映射
const statusColor: Record<string, string> = {
  active: 'green',
  inactive: 'orange',
  deleted: 'red',
  suspended: 'default',
}

// 状态文本映射
const statusText: Record<string, string> = {
  active: '正常',
  inactive: '停用',
  deleted: '已删除',
  suspended: '挂起',
}

export default function CompaniesPage() {
  // 列表状态
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchText, setSearchText] = useState('')

  // 创建/编辑弹窗状态
  const [modalVisible, setModalVisible] = useState(false)
  const [modalLoading, setModalLoading] = useState(false)
  const [editingCompany, setEditingCompany] = useState<Company | null>(null)
  const [form] = Form.useForm()

  // 详情抽屉状态
  const [detailVisible, setDetailVisible] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null)
  const [departments, setDepartments] = useState<DepartmentSummary[]>([])
  const [agents, setAgents] = useState<AgentSummary[]>([])
  const [stats, setStats] = useState<CompanyStats | null>(null)

  // 加载公司列表
  const loadCompanies = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchCompanies({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        q: searchText || undefined,
      })
      setCompanies(data.items)
      setTotal(data.total)
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, searchText])

  useEffect(() => {
    loadCompanies()
  }, [loadCompanies])

  // 搜索处理
  const handleSearch = (value: string) => {
    setSearchText(value)
    setPage(1)
  }

  // 打开创建弹窗
  const handleCreate = () => {
    setEditingCompany(null)
    form.resetFields()
    setModalVisible(true)
  }

  // 打开编辑弹窗
  const handleEdit = (record: Company) => {
    setEditingCompany(record)
    form.setFieldsValue({
      name: record.name,
      description: record.description,
      status: record.status,
      config: record.config,
    })
    setModalVisible(true)
  }

  // 提交表单（创建或更新）
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      setModalLoading(true)

      if (editingCompany) {
        // 更新
        const req: CompanyUpdate = {
          name: values.name,
          description: values.description,
          status: values.status,
        }
        const success = await updateCompany(editingCompany.id, req)
        if (success) {
          message.success('公司更新成功')
          setModalVisible(false)
          loadCompanies()
        } else {
          message.error('公司更新失败')
        }
      } else {
        // 创建
        const req: CompanyCreate = {
          name: values.name,
          description: values.description,
          status: values.status || 'active',
        }
        const result = await createCompany(req)
        if (result) {
          message.success('公司创建成功')
          setModalVisible(false)
          loadCompanies()
        } else {
          message.error('公司创建失败')
        }
      }
    } catch (error) {
      console.error('[Companies] 表单提交失败:', error)
    } finally {
      setModalLoading(false)
    }
  }

  // 删除公司
  const handleDelete = async (id: string) => {
    const success = await deleteCompany(id)
    if (success) {
      message.success('公司删除成功')
      loadCompanies()
    } else {
      message.error('公司删除失败')
    }
  }

  // 打开详情抽屉
  const handleDetail = async (record: Company) => {
    setSelectedCompany(record)
    setDetailVisible(true)
    setDetailLoading(true)

    try {
      const [deptsData, agentsData, statsData] = await Promise.all([
        fetchCompanyDepartments(record.id),
        fetchCompanyAgents(record.id),
        fetchCompanyStats(record.id),
      ])
      setDepartments(deptsData)
      setAgents(agentsData)
      setStats(statsData)
    } finally {
      setDetailLoading(false)
    }
  }

  // 表格列定义
  const columns: ColumnsType<Company> = [
    {
      title: '公司名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record) => (
        <a onClick={() => handleDetail(record)}>{name}</a>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc: string) => desc || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={statusColor[status] || 'default'}>
          {statusText[status] || status}
        </Tag>
      ),
    },
    {
      title: '部门数',
      dataIndex: 'department_count',
      key: 'department_count',
      width: 100,
      align: 'center',
    },
    {
      title: 'Agent数',
      dataIndex: 'agent_count',
      key: 'agent_count',
      width: 100,
      align: 'center',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => handleDetail(record)}
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          />
          <Popconfirm
            title="确认删除"
            description={`确定要删除公司 "${record.name}" 吗？`}
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button
              type="text"
              icon={<DeleteOutlined />}
              size="small"
              danger
            />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // 详情抽屉标题
  const detailTitle = selectedCompany ? `公司详情 - ${selectedCompany.name}` : '公司详情'

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>公司管理</h2>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadCompanies} loading={loading}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建公司
          </Button>
        </Space>
      </div>

      {/* 搜索栏 */}
      <div style={{ marginBottom: 16 }}>
        <Search
          placeholder="搜索公司名称..."
          allowClear
          enterButton={<><SearchOutlined /> 搜索</>}
          onSearch={handleSearch}
          style={{ width: 300 }}
        />
      </div>

      {/* 公司列表表格 */}
      <Table
        columns={columns}
        dataSource={companies}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 家公司`,
          onChange: (p, ps) => {
            setPage(p)
            setPageSize(ps)
          },
        }}
        scroll={{ x: 1000 }}
      />

      {/* 创建/编辑弹窗 */}
      <Modal
        title={editingCompany ? '编辑公司' : '创建公司'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={modalLoading}
        okText={editingCompany ? '保存' : '创建'}
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            status: 'active',
          }}
        >
          <Form.Item
            name="name"
            label="公司名称"
            rules={[{ required: true, message: '请输入公司名称' }]}
          >
            <Input placeholder="请输入公司名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea rows={3} placeholder="请输入公司描述" />
          </Form.Item>

          <Form.Item
            name="status"
            label="状态"
          >
            <Input placeholder="active / inactive" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 公司详情抽屉 */}
      <Drawer
        title={detailTitle}
        placement="right"
        width={600}
        open={detailVisible}
        onClose={() => setDetailVisible(false)}
        loading={detailLoading}
      >
        {selectedCompany && (
          <>
            {/* 基本信息 */}
            <Descriptions column={2} bordered size="small" style={{ marginBottom: 24 }}>
              <Descriptions.Item label="公司ID" span={2}>
                {selectedCompany.id}
              </Descriptions.Item>
              <Descriptions.Item label="公司名称">
                {selectedCompany.name}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={statusColor[selectedCompany.status]}>
                  {statusText[selectedCompany.status] || selectedCompany.status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                {selectedCompany.description || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {new Date(selectedCompany.created_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
              <Descriptions.Item label="更新时间">
                {new Date(selectedCompany.updated_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
            </Descriptions>

            {/* 统计卡片 */}
            {stats && (
              <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={12}>
                  <Card size="small">
                    <Statistic
                      title="部门数量"
                      value={stats.department_count}
                      prefix={<ApartmentOutlined />}
                      valueStyle={{ color: '#3b82f6' }}
                    />
                  </Card>
                </Col>
                <Col span={12}>
                  <Card size="small">
                    <Statistic
                      title="Agent数量"
                      value={stats.agent_count}
                      prefix={<RobotOutlined />}
                      valueStyle={{ color: '#10b981' }}
                    />
                  </Card>
                </Col>
              </Row>
            )}

            {/* 部门列表 */}
            <div style={{ marginBottom: 24 }}>
              <h4><ApartmentOutlined /> 部门列表</h4>
              {departments.length === 0 ? (
                <div style={{ color: '#999', textAlign: 'center', padding: 16 }}>
                  暂无部门
                </div>
              ) : (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {departments.map((dept) => (
                    <Tag key={dept.id} color={dept.is_active ? 'green' : 'default'}>
                      {dept.name}
                    </Tag>
                  ))}
                </div>
              )}
            </div>

            {/* Agent列表 */}
            <div>
              <h4><TeamOutlined /> Agent列表</h4>
              {agents.length === 0 ? (
                <div style={{ color: '#999', textAlign: 'center', padding: 16 }}>
                  暂无Agent
                </div>
              ) : (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {agents.map((agent) => (
                    <Tag key={agent.id} color={agent.status === 'active' ? 'blue' : 'default'}>
                      {agent.name}
                    </Tag>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </Drawer>
    </div>
  )
}