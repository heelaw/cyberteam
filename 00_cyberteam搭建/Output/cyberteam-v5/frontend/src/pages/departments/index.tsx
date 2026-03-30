/**
 * 部门管理页面
 */
import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Space, Modal, Form, Input, Select, message, Tree, Tag } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import { fetchDepartments, fetchDepartmentTree, createDepartment, updateDepartment, deleteDepartment, Department } from '@/apis/modules/departments'

const { TextArea } = Input

export default function DepartmentManagement() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingDept, setEditingDept] = useState<Department | null>(null)
  const [form] = Form.useForm()

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchDepartments()
      setDepartments(data)
    } catch (error) {
      message.error('加载部门失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleCreate = () => {
    setEditingDept(null)
    form.resetFields()
    setModalOpen(true)
  }

  const handleEdit = (record: Department) => {
    setEditingDept(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  const handleDelete = async (record: Department) => {
    try {
      await deleteDepartment(record.id)
      message.success('删除成功')
      loadData()
    } catch (error: any) {
      message.error(error.detail || '删除失败')
    }
  }

  const handleSubmit = async (values: any) => {
    try {
      if (editingDept) {
        await updateDepartment(editingDept.id, values)
        message.success('更新成功')
      } else {
        await createDepartment(values)
        message.success('创建成功')
      }
      setModalOpen(false)
      loadData()
    } catch (error: any) {
      message.error(error.detail || '操作失败')
    }
  }

  const columns = [
    {
      title: '部门名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Department) => (
        <Space>
          <Tag color={record.level === 1 ? 'red' : record.level === 2 ? 'blue' : 'green'}>
            {record.level === 1 ? '决策层' : record.level === 2 ? '协调层' : '执行层'}
          </Tag>
          {text}
        </Space>
      )
    },
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code'
    },
    {
      title: '负责人',
      dataIndex: 'manager_role',
      key: 'manager_role'
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: '技能',
      dataIndex: 'skills',
      key: 'skills',
      render: (skills: string[]) => (
        <Space wrap>
          {skills.map(s => <Tag key={s} color="purple">{s}</Tag>)}
        </Space>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Department) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record)}>
            删除
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div className="p-4">
      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-xl font-bold">部门管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          新建部门
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={departments}
        rowKey="id"
        loading={loading}
        pagination={false}
      />

      <Modal
        title={editingDept ? '编辑部门' : '新建部门'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="name" label="部门名称" rules={[{ required: true, message: '请输入部门名称' }]}>
            <Input placeholder="如：技术研发部" />
          </Form.Item>

          <Form.Item name="code" label="部门代码" rules={[{ required: true, message: '请输入部门代码' }]}>
            <Input placeholder="如：tech" disabled={!!editingDept} />
          </Form.Item>

          <Form.Item name="level" label="层级" rules={[{ required: true }]}>
            <Select placeholder="选择层级">
              <Select.Option value={1}>决策层</Select.Option>
              <Select.Option value={2}>协调层</Select.Option>
              <Select.Option value={3}>执行层</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="parent_id" label="上级部门">
            <Select placeholder="选择上级部门" allowClear>
              {departments.map(d => (
                <Select.Option key={d.id} value={d.id}>{d.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="manager_role" label="负责人角色">
            <Input placeholder="如：技术总监" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="部门职责描述" />
          </Form.Item>

          <Form.Item name="skills" label="专业技能">
            <Select mode="tags" placeholder="输入技能后回车添加">
              <Select.Option value="战略规划">战略规划</Select.Option>
              <Select.Option value="运营管理">运营管理</Select.Option>
              <Select.Option value="技术开发">技术开发</Select.Option>
              <Select.Option value="产品规划">产品规划</Select.Option>
              <Select.Option value="市场营销">市场营销</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingDept ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalOpen(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
