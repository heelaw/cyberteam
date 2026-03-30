/**
 * 组织架构页 - 公司 → 部门 → Agent 树形可视化
 *
 * API 调用:
 * - GET /api/v1/companies - 公司列表
 * - GET /api/v1/companies/{id}/departments - 部门列表
 * - GET /api/v1/companies/{id}/agents - Agent列表
 * - GET /api/v1/departments - 全部部门（用于获取部门树结构）
 */
import { useState, useEffect, useCallback } from 'react'
import {
  Card, Select, Typography, Space, Button, Spin, Empty,
  Modal, Form, Input, message, Drawer, Descriptions, Tag, Divider,
} from 'antd'
import {
  ApartmentOutlined, TeamOutlined, RobotOutlined,
  PlusOutlined, ExpandOutlined, CollapseOutlined, ReloadOutlined,
} from '@ant-design/icons'
import { api } from '@/apis/clients/cyberteam'
import { fetchDepartmentAgents } from '@/apis/modules/departments'

const { Title, Text } = Typography

// === 类型定义 ===

interface Company {
  id: string
  name: string
  description?: string
  status: string
  department_count: number
  agent_count: number
}

interface Department {
  id: string
  name: string
  code: string
  description?: string
  is_active: boolean
}

interface Agent {
  id: string
  name: string
  agent_type: string
  status: string
  description?: string
}

// 树节点类型
interface TreeNode {
  key: string
  title: string
  type: 'company' | 'department' | 'agent'
  data: Company | Department | Agent
  children?: TreeNode[]
  expanded?: boolean
}

// === API 函数 ===

async function fetchCompanies(): Promise<Company[]> {
  return api<Company[]>('GET', '/v1/companies')
}

async function fetchCompanyDepartments(companyId: string): Promise<Department[]> {
  return api<Department[]>('GET', `/v1/companies/${companyId}/departments`)
}

async function fetchCompanyAgents(companyId: string): Promise<Agent[]> {
  return api<Agent[]>('GET', `/v1/companies/${companyId}/agents`)
}

async function fetchAllDepartments(): Promise<Department[]> {
  return api<Department[]>('GET', '/v1/departments')
}

// === 树形组件 ===

interface TreeNodeProps {
  node: TreeNode
  onToggle: (key: string) => void
  onSelect: (node: TreeNode) => void
  level?: number
}

function TreeNodeComponent({ node, onToggle, onSelect, level = 0 }: TreeNodeProps) {
  const hasChildren = node.children && node.children.length > 0
  const indent = level * 24

  const getNodeIcon = () => {
    switch (node.type) {
      case 'company':
        return <TeamOutlined style={{ color: '#3b82f6' }} />
      case 'department':
        return <ApartmentOutlined style={{ color: '#10b981' }} />
      case 'agent':
        return <RobotOutlined style={{ color: '#f59e0b' }} />
    }
  }

  const getNodeColor = () => {
    switch (node.type) {
      case 'company':
        return 'bg-blue-50 border-blue-200'
      case 'department':
        return 'bg-green-50 border-green-200'
      case 'agent':
        return 'bg-amber-50 border-amber-200'
    }
  }

  const agent = node.data as Agent
  const isActive = node.type === 'agent' && agent.status === 'active'

  return (
    <div style={{ marginLeft: indent }}>
      <div
        className={`flex items-center gap-2 p-2 mb-1 rounded border cursor-pointer transition-all hover:shadow-sm ${getNodeColor()}`}
        onClick={() => onSelect(node)}
      >
        {hasChildren && (
          <Button
            type="text"
            size="small"
            icon={node.expanded ? <CollapseOutlined /> : <ExpandOutlined />}
            onClick={(e) => {
              e.stopPropagation()
              onToggle(node.key)
            }}
            className="w-6 h-6 min-w-6 p-0 flex items-center justify-center"
          />
        )}
        {!hasChildren && <span className="w-6" />}

        <span className="text-lg">{getNodeIcon()}</span>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <Text strong className="text-sm">{node.title}</Text>
            {node.type === 'agent' && (
              <Tag
                color={isActive ? 'processing' : 'default'}
                style={{ fontSize: 10 }}
              >
                {isActive ? '运行中' : '空闲'}
              </Tag>
            )}
          </div>
          {node.type === 'agent' && agent.description && (
            <Text type="secondary" className="text-xs block truncate">
              {agent.description}
            </Text>
          )}
          {node.type === 'company' && (node.data as Company).description && (
            <Text type="secondary" className="text-xs block truncate">
              {(node.data as Company).description}
            </Text>
          )}
        </div>

        <div className="text-xs text-gray-400">
          {node.type === 'company' && `${(node.data as Company).department_count}部门`}
          {node.type === 'department' && `${node.children?.length || 0} Agent`}
          {node.type === 'agent' && agent.agent_type}
        </div>
      </div>

      {node.expanded && hasChildren && (
        <div className="border-l-2 border-gray-200 ml-3">
          {node.children!.map((child) => (
            <TreeNodeComponent
              key={child.key}
              node={child}
              onToggle={onToggle}
              onSelect={onSelect}
              level={0}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// === 主页面 ===

export default function OrganizationPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null)
  const [departments, setDepartments] = useState<Department[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [treeData, setTreeData] = useState<TreeNode[]>([])
  const [departmentAgentMap, setDepartmentAgentMap] = useState<Record<string, string[]>>({})
  const [loading, setLoading] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null)
  const [addDeptVisible, setAddDeptVisible] = useState(false)
  const [addAgentVisible, setAddAgentVisible] = useState(false)
  const [form] = Form.useForm()
  const [agentForm] = Form.useForm()

  // 加载公司列表
  const loadCompanies = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchCompanies()
      setCompanies(data)
      if (data.length > 0 && !selectedCompany) {
        setSelectedCompany(data[0].id)
      }
    } catch (error) {
      console.error('[Organization] 加载公司失败:', error)
      message.error('加载公司列表失败')
    } finally {
      setLoading(false)
    }
  }, [selectedCompany])

  // 加载选中公司的部门和Agent
  const loadCompanyData = useCallback(async () => {
    if (!selectedCompany) return

    setLoading(true)
    try {
      const [deptData, agentData] = await Promise.all([
        fetchCompanyDepartments(selectedCompany),
        fetchCompanyAgents(selectedCompany),
      ])
      setDepartments(deptData)
      setAgents(agentData)

      // 加载每个部门的真实绑定Agent
      const deptAgentMap: Record<string, string[]> = {}
      for (const dept of deptData) {
        deptAgentMap[dept.id] = await fetchDepartmentAgents(dept.id)
      }
      setDepartmentAgentMap(deptAgentMap)
    } catch (error) {
      console.error('[Organization] 加载公司数据失败:', error)
      message.error('加载公司组织数据失败')
    } finally {
      setLoading(false)
    }
  }, [selectedCompany])

  useEffect(() => {
    loadCompanies()
  }, [])

  useEffect(() => {
    if (selectedCompany) {
      loadCompanyData()
    }
  }, [selectedCompany, loadCompanyData])

  // 构建树形数据
  useEffect(() => {
    if (!selectedCompany) {
      setTreeData([])
      return
    }

    const company = companies.find((c) => c.id === selectedCompany)
    if (!company) return

    // 构建公司节点
    const companyNode: TreeNode = {
      key: `company-${company.id}`,
      title: company.name,
      type: 'company',
      data: company,
      expanded: true,
      children: [],
    }

    // 按部门分组Agent（使用真实API绑定数据）
    const deptAgentsMap = new Map<string, Agent[]>()
    const departmentNodes: TreeNode[] = departments.map((dept) => {
      // 使用真实API返回的绑定Agent列表
      const boundAgentCodes = departmentAgentMap[dept.id] || []
      const deptAgents = (agents as Agent[]).filter((a) =>
        boundAgentCodes.includes(a.id)
      )

      return {
        key: `dept-${dept.id}`,
        title: dept.name,
        type: 'department',
        data: dept,
        expanded: false,
        children: deptAgents.map((agent) => ({
          key: `agent-${agent.id}`,
          title: agent.name,
          type: 'agent',
          data: agent,
        })),
      }
    })

    // 如果有未分配的Agent，创建"其他"部门
    const assignedAgentIds = new Set(
      departmentNodes.flatMap((d) => d.children?.map((a) => a.key) || [])
    )
    const unassignedAgents = agents.filter(
      (a) => !assignedAgentIds.has(`agent-${a.id}`)
    )

    if (unassignedAgents.length > 0) {
      departmentNodes.push({
        key: 'dept-unassigned',
        title: '未分类',
        type: 'department',
        data: { id: 'unassigned', name: '未分类', code: 'UNASSIGNED', is_active: true } as Department,
        expanded: false,
        children: unassignedAgents.map((agent) => ({
          key: `agent-${agent.id}`,
          title: agent.name,
          type: 'agent',
          data: agent,
        })),
      })
    }

    companyNode.children = departmentNodes
    setTreeData([companyNode])
  }, [companies, selectedCompany, departments, agents, departmentAgentMap])

  // 展开/折叠节点
  const handleToggle = useCallback((key: string) => {
    const toggleNode = (nodes: TreeNode[]): TreeNode[] => {
      return nodes.map((node) => {
        if (node.key === key) {
          return { ...node, expanded: !node.expanded }
        }
        if (node.children) {
          return { ...node, children: toggleNode(node.children) }
        }
        return node
      })
    }
    setTreeData((prev) => toggleNode(prev))
  }, [])

  // 展开全部
  const expandAll = useCallback(() => {
    const expand = (nodes: TreeNode[]): TreeNode[] => {
      return nodes.map((node) => ({
        ...node,
        expanded: true,
        children: node.children ? expand(node.children) : undefined,
      }))
    }
    setTreeData((prev) => expand(prev))
  }, [])

  // 折叠全部
  const collapseAll = useCallback(() => {
    const collapse = (nodes: TreeNode[]): TreeNode[] => {
      return nodes.map((node) => ({
        ...node,
        expanded: false,
        children: node.children ? collapse(node.children) : undefined,
      }))
    }
    setTreeData((prev) => collapse(prev))
  }, [])

  // 选择节点
  const handleSelect = useCallback((node: TreeNode) => {
    setSelectedNode(node)
    setDetailVisible(true)
  }, [])

  // 新增部门
  const handleAddDepartment = async () => {
    try {
      const values = await form.validateFields()
      message.info(`新增部门功能待后端支持: ${values.name}`)
      setAddDeptVisible(false)
      form.resetFields()
    } catch (error) {
      // 表单验证失败
    }
  }

  // 新增Agent
  const handleAddAgent = async () => {
    try {
      const values = await agentForm.validateFields()
      message.info(`新增Agent功能待后端支持: ${values.name}`)
      setAddAgentVisible(false)
      agentForm.resetFields()
    } catch (error) {
      // 表单验证失败
    }
  }

  const selectedCompanyData = companies.find((c) => c.id === selectedCompany)

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-4">
        <Title level={3} style={{ margin: 0 }}>
          <ApartmentOutlined className="mr-2 text-blue-500" />
          组织架构
        </Title>
        <Space>
          <Select
            placeholder="选择公司"
            value={selectedCompany}
            onChange={setSelectedCompany}
            style={{ width: 200 }}
            loading={loading && companies.length === 0}
          >
            {companies.map((company) => (
              <Select.Option key={company.id} value={company.id}>
                {company.name}
              </Select.Option>
            ))}
          </Select>
          <Button icon={<ReloadOutlined />} onClick={loadCompanyData} loading={loading}>
            刷新
          </Button>
          <Button icon={<ExpandOutlined />} onClick={expandAll}>
            展开
          </Button>
          <Button icon={<CollapseOutlined />} onClick={collapseAll}>
            折叠
          </Button>
        </Space>
      </div>

      {/* 统计信息 */}
      {selectedCompanyData && (
        <div className="mb-4 flex gap-4">
          <Card size="small" className="flex-1">
            <div className="flex items-center gap-2">
              <TeamOutlined className="text-blue-500" />
              <Text>公司: </Text>
              <Text strong>{selectedCompanyData.name}</Text>
            </div>
          </Card>
          <Card size="small" className="flex-1">
            <div className="flex items-center gap-2">
              <ApartmentOutlined className="text-green-500" />
              <Text>部门: </Text>
              <Text strong>{departments.length}</Text>
            </div>
          </Card>
          <Card size="small" className="flex-1">
            <div className="flex items-center gap-2">
              <RobotOutlined className="text-amber-500" />
              <Text>Agent: </Text>
              <Text strong>{agents.length}</Text>
            </div>
          </Card>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="mb-4 flex gap-2">
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddDeptVisible(true)}>
          新增部门
        </Button>
        <Button icon={<PlusOutlined />} onClick={() => setAddAgentVisible(true)}>
          新增Agent
        </Button>
      </div>

      {/* 树形结构 */}
      <Card>
        {loading && treeData.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Spin size="large" />
          </div>
        ) : treeData.length === 0 ? (
          <Empty description="请选择公司以查看组织架构" />
        ) : (
          <div className="min-h-[400px]">
            {treeData.map((node) => (
              <TreeNodeComponent
                key={node.key}
                node={node}
                onToggle={handleToggle}
                onSelect={handleSelect}
              />
            ))}
          </div>
        )}
      </Card>

      {/* 详情抽屉 */}
      <Drawer
        title="详情"
        placement="right"
        width={400}
        onClose={() => setDetailVisible(false)}
        open={detailVisible}
      >
        {selectedNode && (
          <div>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="类型">
                <Tag color={
                  selectedNode.type === 'company' ? 'blue' :
                  selectedNode.type === 'department' ? 'green' : 'amber'
                }>
                  {selectedNode.type === 'company' ? '公司' :
                   selectedNode.type === 'department' ? '部门' : 'Agent'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="名称">
                <Text strong>{selectedNode.title}</Text>
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            {selectedNode.type === 'company' && (
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="描述">
                  {(selectedNode.data as Company).description || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="部门数">
                  {(selectedNode.data as Company).department_count}
                </Descriptions.Item>
                <Descriptions.Item label="Agent数">
                  {(selectedNode.data as Company).agent_count}
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag>{(selectedNode.data as Company).status}</Tag>
                </Descriptions.Item>
              </Descriptions>
            )}

            {selectedNode.type === 'department' && (
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="编码">
                  {(selectedNode.data as Department).code}
                </Descriptions.Item>
                <Descriptions.Item label="描述">
                  {(selectedNode.data as Department).description || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag color={(selectedNode.data as Department).is_active ? 'success' : 'error'}>
                    {(selectedNode.data as Department).is_active ? '活跃' : '未激活'}
                  </Tag>
                </Descriptions.Item>
              </Descriptions>
            )}

            {selectedNode.type === 'agent' && (
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="类型">
                  {(selectedNode.data as Agent).agent_type}
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag color={(selectedNode.data as Agent).status === 'active' ? 'processing' : 'default'}>
                    {(selectedNode.data as Agent).status === 'active' ? '运行中' : '空闲'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="描述">
                  {(selectedNode.data as Agent).description || '-'}
                </Descriptions.Item>
              </Descriptions>
            )}
          </div>
        )}
      </Drawer>

      {/* 新增部门弹窗 */}
      <Modal
        title="新增部门"
        open={addDeptVisible}
        onOk={handleAddDepartment}
        onCancel={() => {
          setAddDeptVisible(false)
          form.resetFields()
        }}
        okText="创建"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="部门名称"
            rules={[{ required: true, message: '请输入部门名称' }]}
          >
            <Input placeholder="请输入部门名称" />
          </Form.Item>
          <Form.Item
            name="code"
            label="部门编码"
            rules={[{ required: true, message: '请输入部门编码' }]}
          >
            <Input placeholder="请输入部门编码，如 PRODUCT" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea placeholder="请输入部门描述" rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 新增Agent弹窗 */}
      <Modal
        title="新增Agent"
        open={addAgentVisible}
        onOk={handleAddAgent}
        onCancel={() => {
          setAddAgentVisible(false)
          agentForm.resetFields()
        }}
        okText="创建"
        cancelText="取消"
      >
        <Form form={agentForm} layout="vertical">
          <Form.Item
            name="name"
            label="Agent名称"
            rules={[{ required: true, message: '请输入Agent名称' }]}
          >
            <Input placeholder="请输入Agent名称" />
          </Form.Item>
          <Form.Item
            name="agent_type"
            label="Agent类型"
            rules={[{ required: true, message: '请选择Agent类型' }]}
          >
            <Select placeholder="请选择Agent类型">
              <Select.Option value="executor">执行器</Select.Option>
              <Select.Option value="coordinator">协调者</Select.Option>
              <Select.Option value="leader">领导者</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea placeholder="请输入Agent描述" rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}