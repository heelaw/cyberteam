/**
 * 数字员工市场页面
 *
 * 展示可用的数字员工模板，支持创建和调度
 */
import { useState, useEffect } from 'react'
import { Card, Row, Col, Button, Tag, Modal, Form, Input, Select, message, Space, Avatar, Spin } from 'antd'
import { PlusOutlined, UserOutlined, RocketOutlined, DeleteOutlined } from '@ant-design/icons'
import { fetchEmployees, fetchTemplates, createEmployee, executeTask, deleteEmployee } from '@/apis/modules/employees'
import type { Employee, Task } from '@/types'

const { Meta } = Card

export default function EmployeeMarketplace() {
  const [loading, setLoading] = useState(false)
  const [templates, setTemplates] = useState<Employee[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [taskModalOpen, setTaskModalOpen] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null)
  const [taskForm] = Form.useForm()
  const [createForm] = Form.useForm()

  // 加载数据
  const loadData = async () => {
    setLoading(true)
    try {
      const [templateData, employeeData] = await Promise.all([
        fetchTemplates(),
        fetchEmployees()
      ])
      setTemplates(templateData)
      setEmployees(employeeData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // 创建数字员工
  const handleCreate = async (values: { template_id: string; name?: string }) => {
    try {
      await createEmployee(values)
      message.success('创建成功')
      setCreateModalOpen(false)
      createForm.resetFields()
      loadData()
    } catch (error) {
      message.error('创建失败')
    }
  }

  // 执行任务
  const handleExecuteTask = async (values: { task: string }) => {
    if (!selectedEmployee) return

    try {
      message.loading({ content: '任务执行中...', key: 'task' })
      const result = await executeTask({
        task: values.task,
        employee_id: selectedEmployee.id
      })
      message.success({ content: '任务完成', key: 'task' })
      console.log('Task result:', result)
    } catch (error) {
      message.error({ content: '执行失败', key: 'task' })
    }
  }

  // 删除员工
  const handleDelete = async (employeeId: string) => {
    try {
      await deleteEmployee(employeeId)
      message.success('删除成功')
      loadData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 标签颜色映射
  const roleColors: Record<string, string> = {
    '首席执行官': 'gold',
    '首席运营官': 'blue',
    '产品管理': 'purple',
    '技术开发': 'green',
    '增长营销': 'red',
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">数字员工市场</h1>
        <p className="text-gray-500">选择数字员工，执行任务</p>
      </div>

      {/* 已创建的员工 */}
      {employees.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-4">我的数字员工</h2>
          <Row gutter={[16, 16]}>
            {employees.map((emp) => (
              <Col xs={24} sm={12} md={8} lg={6} key={emp.id}>
                <Card
                  hoverable
                  actions={[
                    <Button
                      type="text"
                      icon={<RocketOutlined />}
                      onClick={() => {
                        setSelectedEmployee(emp)
                        setTaskModalOpen(true)
                      }}
                    >
                      执行任务
                    </Button>,
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDelete(emp.id)}
                    />
                  ]}
                >
                  <Meta
                    avatar={<Avatar size={48} icon={<UserOutlined />} />}
                    title={emp.name}
                    description={
                      <Space direction="vertical" size={0}>
                        <Tag color={roleColors[emp.role] || 'default'}>
                          {emp.role}
                        </Tag>
                        <span className="text-xs text-gray-400">
                          状态: {emp.status}
                        </span>
                      </Space>
                    }
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}

      {/* 员工模板 */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">数字员工模板</h2>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalOpen(true)}
          >
            创建员工
          </Button>
        </div>

        <Spin spinning={loading}>
          <Row gutter={[16, 16]}>
            {templates.map((template) => (
              <Col xs={24} sm={12} md={8} lg={6} key={template.id}>
                <Card
                  hoverable
                  onClick={() => {
                    createForm.setFieldsValue({ template_id: template.id })
                    setCreateModalOpen(true)
                  }}
                >
                  <Meta
                    avatar={<Avatar size={48} icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />}
                    title={template.name}
                    description={
                      <Space direction="vertical" size={0}>
                        <Tag color={roleColors[template.role] || 'default'}>
                          {template.role}
                        </Tag>
                        <span className="text-xs text-gray-500">
                          {template.description}
                        </span>
                        <div className="mt-2">
                          {template.skills?.slice(0, 3).map((skill, idx) => (
                            <Tag key={idx} className="mr-1">{skill}</Tag>
                          ))}
                        </div>
                      </Space>
                    }
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </Spin>
      </div>

      {/* 创建员工 Modal */}
      <Modal
        title="创建数字员工"
        open={createModalOpen}
        onCancel={() => {
          setCreateModalOpen(false)
          createForm.resetFields()
        }}
        footer={null}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={handleCreate}
        >
          <Form.Item
            name="template_id"
            label="选择模板"
            rules={[{ required: true, message: '请选择模板' }]}
          >
            <Select placeholder="选择员工模板">
              {templates.map((t) => (
                <Select.Option key={t.id} value={t.id}>
                  {t.name} - {t.role}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="name"
            label="员工名称（可选）"
          >
            <Input placeholder="自定义名称，留空使用模板名称" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              创建
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 执行任务 Modal */}
      <Modal
        title={`执行任务 - ${selectedEmployee?.name}`}
        open={taskModalOpen}
        onCancel={() => {
          setTaskModalOpen(false)
          taskForm.resetFields()
        }}
        footer={null}
        width={600}
      >
        <Form
          form={taskForm}
          layout="vertical"
          onFinish={handleExecuteTask}
        >
          <Form.Item
            name="task"
            label="任务描述"
            rules={[{ required: true, message: '请输入任务' }]}
          >
            <Input.TextArea
              rows={6}
              placeholder="描述你要执行的任务..."
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              执行任务
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
