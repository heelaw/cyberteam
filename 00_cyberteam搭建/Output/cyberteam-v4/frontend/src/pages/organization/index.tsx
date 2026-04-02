/**
 * 组织架构页 - CyberTeam 组织架构 Builder
 *
 * 功能：
 * - 左树右详情布局
 * - 可自定义的交互式树形 Builder
 * - 支持拖拽排序
 * - 支持内联编辑
 * - 支持上下文菜单
 * - 支持绑定 Agent
 * - 支持讨论层/执行层切换
 *
 * API:
 * - GET /api/v1/organization/structure/{company_id} - 获取组织结构
 * - PUT /api/v1/organization/structure/{company_id} - 更新组织结构
 * - GET /api/v1/agents - 获取所有可用 Agent
 * - POST /api/v1/organization/configs/{company_id} - 保存配置快照
 * - GET /api/v1/organization/configs/{company_id} - 加载配置快照
 */
import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Card,
  Button,
  Space,
  Typography,
  message,
  Modal,
  Input,
  Select,
  Spin,
  Tooltip,
  Divider,
} from 'antd'
import {
  PlusOutlined,
  SaveOutlined,
  ReloadOutlined,
  ExpandOutlined,
  NodeCollapseOutlined,
  SwapOutlined,
} from '@ant-design/icons'
import {
  OrgNodeComponent,
  NodeDetail,
  AddNodeModal,
  AddAgentModal,
  LayerTabs,
} from './components'
import type {
  OrgNode,
  OrgNodeType,
  OrgStructure,
  AvailableAgent,
  LayerType,
} from '@/types/organization'
import {
  createOrgNode,
  generateNodeId,
  NODE_COLORS,
} from '@/types/organization'
import { api } from '@/apis/clients/cyberteam'
import { fetchAgents } from '@/apis/modules/custom-agents'
import {
  adaptBackendToFrontend,
  adaptFrontendToBackend,
  type BackendOrgStructure,
} from '@/adapters/orgStructureAdapter'

const { Title, Text } = Typography

// 当前公司 ID（Mock）
const CURRENT_COMPANY_ID = 'cyberteam_default'

// 默认组织结构（Mock 数据）
const DEFAULT_ORG_STRUCTURE: OrgStructure = {
  companyId: CURRENT_COMPANY_ID,
  companyName: 'CyberTeam',
  root: {
    id: 'ceo_001',
    name: 'CyberTeam CEO',
    type: 'ceo',
    layer: 'ceo',
    icon: '👑',
    color: NODE_COLORS.ceo,
    description: 'CyberTeam 总指挥，负责全局决策和调度',
    boundAgents: [],
    expanded: true,
    editable: false,
    deletable: false,
    children: [
      // 讨论层
      {
        id: 'discuss_group_001',
        name: '讨论层',
        type: 'discuss_group',
        layer: 'discuss',
        icon: '💭',
        color: NODE_COLORS.discuss_group,
        description: '讨论层负责策略制定和分析',
        boundAgents: [],
        expanded: true,
        children: [
          {
            id: 'discuss_team_001',
            name: '战略讨论组',
            type: 'discuss_team',
            layer: 'discuss',
            icon: '💬',
            color: NODE_COLORS.discuss_team,
            description: '负责战略方向和重大决策讨论',
            boundAgents: [],
            expanded: true,
            children: [
              {
                id: 'agent_001',
                name: '战略顾问',
                type: 'agent',
                layer: 'execute',
                icon: '🎯',
                color: NODE_COLORS.agent,
                description: '提供战略规划建议',
                boundAgents: ['agent_strategic_advisor'],
                expanded: true,
                children: [],
              },
              {
                id: 'agent_002',
                name: '质疑者',
                type: 'agent',
                layer: 'execute',
                icon: '🤖',
                color: NODE_COLORS.agent,
                description: '苏格拉底式提问，确保讨论质量',
                boundAgents: ['agent_questioner'],
                expanded: true,
                children: [],
              },
              {
                id: 'agent_003',
                name: '风险专家',
                type: 'agent',
                layer: 'execute',
                icon: '⚠️',
                color: NODE_COLORS.agent,
                description: '识别和评估项目风险',
                boundAgents: ['agent_risk_expert'],
                expanded: true,
                children: [],
              },
            ],
          },
          {
            id: 'discuss_team_002',
            name: '战术分析组',
            type: 'discuss_team',
            layer: 'discuss',
            icon: '💬',
            color: NODE_COLORS.discuss_team,
            description: '负责战术分析和执行方案制定',
            boundAgents: [],
            expanded: true,
            children: [
              {
                id: 'agent_004',
                name: '数据分析师',
                type: 'agent',
                layer: 'execute',
                icon: '📊',
                color: NODE_COLORS.agent,
                description: '数据分析支持',
                boundAgents: ['agent_data_analyst'],
                expanded: true,
                children: [],
              },
              {
                id: 'agent_005',
                name: '市场专家',
                type: 'agent',
                layer: 'execute',
                icon: '🚀',
                color: NODE_COLORS.agent,
                description: '市场分析和竞争情报',
                boundAgents: ['agent_market_expert'],
                expanded: true,
                children: [],
              },
            ],
          },
        ],
      },
      // 执行层
      {
        id: 'execute_group_001',
        name: '执行层',
        type: 'execute_group',
        layer: 'execute',
        icon: '⚙️',
        color: NODE_COLORS.execute_group,
        description: '执行层负责具体执行落地',
        boundAgents: [],
        expanded: true,
        children: [
          {
            id: 'execute_dept_001',
            name: '技术开发部',
            type: 'execute_dept',
            layer: 'execute',
            icon: '💻',
            color: NODE_COLORS.execute_dept,
            description: '负责产品和技术开发',
            boundAgents: [],
            expanded: true,
            children: [
              {
                id: 'agent_006',
                name: '前端工程师',
                type: 'agent',
                layer: 'execute',
                icon: '🎨',
                color: NODE_COLORS.agent,
                description: '前端开发',
                boundAgents: ['agent_frontend'],
                expanded: true,
                children: [],
              },
              {
                id: 'agent_007',
                name: '后端工程师',
                type: 'agent',
                layer: 'execute',
                icon: '⚙️',
                color: NODE_COLORS.agent,
                description: '后端开发',
                boundAgents: ['agent_backend'],
                expanded: true,
                children: [],
              },
              {
                id: 'agent_008',
                name: '测试工程师',
                type: 'agent',
                layer: 'execute',
                icon: '🧪',
                color: NODE_COLORS.agent,
                description: '质量保证和测试',
                boundAgents: ['agent_qa'],
                expanded: true,
                children: [],
              },
            ],
          },
          {
            id: 'execute_dept_002',
            name: '运营执行部',
            type: 'execute_dept',
            layer: 'execute',
            icon: '📢',
            color: NODE_COLORS.execute_dept,
            description: '负责运营和推广执行',
            boundAgents: [],
            expanded: true,
            children: [
              {
                id: 'agent_009',
                name: '内容运营',
                type: 'agent',
                layer: 'execute',
                icon: '✍️',
                color: NODE_COLORS.agent,
                description: '内容策划和创作',
                boundAgents: ['agent_content_ops'],
                expanded: true,
                children: [],
              },
              {
                id: 'agent_010',
                name: '数据运营',
                type: 'agent',
                layer: 'execute',
                icon: '📈',
                color: NODE_COLORS.agent,
                description: '数据分析和运营优化',
                boundAgents: ['agent_data_ops'],
                expanded: true,
                children: [],
              },
            ],
          },
        ],
      },
    ],
  },
}

// Mock 可用 Agent 列表
const MOCK_AVAILABLE_AGENTS: AvailableAgent[] = [
  { id: 'agent_strategic_advisor', code: 'strategic_advisor', name: '战略顾问', agentType: 'advisor', layer: 'execute', skills: ['战略规划', '商业分析'], status: 'active' },
  { id: 'agent_questioner', code: 'questioner', name: '质疑者', agentType: 'questioner', layer: 'execute', skills: ['批判性思维', '逻辑分析'], status: 'active' },
  { id: 'agent_risk_expert', code: 'risk_expert', name: '风险专家', agentType: 'expert', layer: 'execute', skills: ['风险评估', '危机管理'], status: 'active' },
  { id: 'agent_data_analyst', code: 'data_analyst', name: '数据分析师', agentType: 'analyst', layer: 'execute', skills: ['数据分析', '数据可视化'], status: 'active' },
  { id: 'agent_market_expert', code: 'market_expert', name: '市场专家', agentType: 'expert', layer: 'execute', skills: ['市场分析', '竞品调研'], status: 'active' },
  { id: 'agent_frontend', code: 'frontend', name: '前端工程师', agentType: 'engineer', layer: 'execute', skills: ['React', 'TypeScript'], status: 'active' },
  { id: 'agent_backend', code: 'backend', name: '后端工程师', agentType: 'engineer', layer: 'execute', skills: ['Python', 'FastAPI'], status: 'active' },
  { id: 'agent_qa', code: 'qa', name: '测试工程师', agentType: 'engineer', layer: 'execute', skills: ['测试用例', '自动化测试'], status: 'active' },
  { id: 'agent_content_ops', code: 'content_ops', name: '内容运营', agentType: 'operator', layer: 'execute', skills: ['内容策划', '文案撰写'], status: 'active' },
  { id: 'agent_data_ops', code: 'data_ops', name: '数据运营', agentType: 'operator', layer: 'execute', skills: ['数据分析', '运营优化'], status: 'active' },
  { id: 'agent_growth_expert', code: 'growth_expert', name: '增长专家', agentType: 'expert', layer: 'execute', skills: ['用户增长', 'A/B测试'], status: 'inactive' },
  { id: 'agent_designer', code: 'designer', name: 'UI设计师', agentType: 'designer', layer: 'execute', skills: ['UI设计', '交互设计'], status: 'active' },
]

// === 主页面组件 ===

export default function OrganizationBuilderPage() {
  // 状态
  const [orgStructure, setOrgStructure] = useState<OrgStructure>(DEFAULT_ORG_STRUCTURE)
  const [selectedNode, setSelectedNode] = useState<OrgNode | null>(null)
  const [activeLayer, setActiveLayer] = useState<'all' | 'discuss' | 'execute'>('all')
  const [availableAgents, setAvailableAgents] = useState<AvailableAgent[]>(MOCK_AVAILABLE_AGENTS)
  const [loading, setLoading] = useState(false)
  const [loadingAgents, setLoadingAgents] = useState(false)

  // Modal 状态
  const [addNodeModalVisible, setAddNodeModalVisible] = useState(false)
  const [addNodeParentNode, setAddNodeParentNode] = useState<OrgNode | null>(null)
  const [addNodeDefaultType, setAddNodeDefaultType] = useState<OrgNodeType | undefined>()
  const [addAgentModalVisible, setAddAgentModalVisible] = useState(false)
  const [addAgentTargetNode, setAddAgentTargetNode] = useState<OrgNode | null>(null)

  // 拖拽状态
  const [draggedNode, setDraggedNode] = useState<OrgNode | null>(null)

  // 保存 Modal 状态
  const [saveModalVisible, setSaveModalVisible] = useState(false)
  const [configName, setConfigName] = useState('')

  // 加载可用 Agent（Mock 暂时使用本地数据）
  const loadAvailableAgents = useCallback(async () => {
    setLoadingAgents(true)
    try {
      // 尝试从 API 获取
      const agents = await fetchAgents()
      if (agents.length > 0) {
        const mapped: AvailableAgent[] = agents.map((a) => ({
          id: a.code,
          code: a.code,
          name: a.name,
          agentType: a.agent_type,
          layer: 'execute' as LayerType,
          skills: a.skills,
          status: a.is_active ? 'active' : 'inactive',
        }))
        setAvailableAgents(mapped)
      }
    } catch (error) {
      console.warn('[Organization] 加载 Agent 列表失败，使用 Mock 数据:', error)
    } finally {
      setLoadingAgents(false)
    }
  }, [])

  // 加载组织架构（从后端 API）
  const loadOrgStructure = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api<BackendOrgStructure>('GET', `/v1/organization/structure/${CURRENT_COMPANY_ID}`)
      if (data && data.ceo_node) {
        const adapted = adaptBackendToFrontend(data)
        setOrgStructure(adapted)
      }
    } catch (error) {
      console.warn('[Organization] 从API加载组织架构失败，使用默认数据:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  // 初始化加载
  useEffect(() => {
    loadOrgStructure()
    loadAvailableAgents()
  }, [loadOrgStructure, loadAvailableAgents])

  // 统计各层级节点数量
  const layerCounts = useMemo(() => {
    const countNode = (node: OrgNode): { discuss: number; execute: number } => {
      let discuss = 0
      let execute = 0

      if (node.layer === 'discuss' && node.type !== 'ceo') {
        discuss++
      } else if (node.layer === 'execute') {
        execute++
      }

      if (node.children) {
        for (const child of node.children) {
          const childCounts = countNode(child)
          discuss += childCounts.discuss
          execute += childCounts.execute
        }
      }

      return { discuss, execute }
    }

    return countNode(orgStructure.root)
  }, [orgStructure.root])

  // 过滤显示的节点（根据层级）
  const getVisibleNodes = useCallback((nodes: OrgNode[]): OrgNode[] => {
    if (activeLayer === 'all') {
      return nodes
    }

    return nodes.filter((node) => {
      if (activeLayer === 'discuss') {
        return node.layer === 'discuss' || node.type === 'ceo'
      } else if (activeLayer === 'execute') {
        return node.layer === 'execute'
      }
      return true
    }).map((node) => ({
      ...node,
      children: node.children ? getVisibleNodes(node.children) : [],
    }))
  }, [activeLayer])

  // 展开/折叠节点
  const handleToggle = useCallback((nodeId: string) => {
    const toggleNode = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => {
        if (node.id === nodeId) {
          return { ...node, expanded: !node.expanded }
        }
        if (node.children) {
          return { ...node, children: toggleNode(node.children) }
        }
        return node
      })
    }
    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: toggleNode(prev.root.children) },
    }))
  }, [])

  // 展开全部
  const expandAll = useCallback(() => {
    const expand = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => ({
        ...node,
        expanded: true,
        children: node.children ? expand(node.children) : [],
      }))
    }
    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: expand(prev.root.children) },
    }))
  }, [])

  // 折叠全部
  const collapseAll = useCallback(() => {
    const collapse = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => ({
        ...node,
        expanded: false,
        children: node.children ? collapse(node.children) : [],
      }))
    }
    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: collapse(prev.root.children) },
    }))
  }, [])

  // 选择节点
  const handleSelect = useCallback((node: OrgNode) => {
    setSelectedNode(node)
  }, [])

  // 关闭详情面板
  const handleCloseDetail = useCallback(() => {
    setSelectedNode(null)
  }, [])

  // 新增节点
  const handleAddChild = useCallback((parentNode: OrgNode, type: OrgNodeType) => {
    setAddNodeParentNode(parentNode)
    setAddNodeDefaultType(type)
    setAddNodeModalVisible(true)
  }, [])

  // 确认新增节点
  const handleConfirmAddNode = useCallback((data: { name: string; type: OrgNodeType; description: string }) => {
    if (!addNodeParentNode) return

    const newNode = createOrgNode({
      id: generateNodeId(data.type),
      name: data.name,
      type: data.type,
      description: data.description,
      children: [],
    })

    // 添加到父节点
    const addToParent = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => {
        if (node.id === addNodeParentNode!.id) {
          return {
            ...node,
            children: [...(node.children || []), newNode],
            expanded: true,
          }
        }
        if (node.children) {
          return { ...node, children: addToParent(node.children) }
        }
        return node
      })
    }

    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: addToParent(prev.root.children) },
    }))

    message.success(`已添加「${data.name}」`)
    setAddNodeModalVisible(false)
    setAddNodeParentNode(null)
    setAddNodeDefaultType(undefined)
  }, [addNodeParentNode])

  // 删除节点
  const handleDelete = useCallback((nodeId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此节点吗？此操作不可撤销。',
      okText: '删除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: () => {
        const deleteNode = (nodes: OrgNode[]): OrgNode[] => {
          return nodes
            .filter((node) => node.id !== nodeId)
            .map((node) => ({
              ...node,
              children: node.children ? deleteNode(node.children) : [],
            }))
        }

        setOrgStructure((prev) => ({
          ...prev,
          root: { ...prev.root, children: deleteNode(prev.root.children) },
        }))

        if (selectedNode?.id === nodeId) {
          setSelectedNode(null)
        }

        message.success('节点已删除')
      },
    })
  }, [selectedNode])

  // 内联编辑节点名称
  const handleInlineEdit = useCallback((nodeId: string, newName: string) => {
    const updateNode = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => {
        if (node.id === nodeId) {
          return { ...node, name: newName }
        }
        if (node.children) {
          return { ...node, children: updateNode(node.children) }
        }
        return node
      })
    }

    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: updateNode(prev.root.children) },
    }))

    if (selectedNode?.id === nodeId) {
      setSelectedNode((prev) => prev ? { ...prev, name: newName } : null)
    }

    message.success('已更新名称')
  }, [selectedNode])

  // 保存节点属性更新
  const handleSaveNode = useCallback((nodeId: string, updates: Partial<OrgNode>) => {
    const updateNode = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => {
        if (node.id === nodeId) {
          return { ...node, ...updates }
        }
        if (node.children) {
          return { ...node, children: updateNode(node.children) }
        }
        return node
      })
    }

    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: updateNode(prev.root.children) },
    }))

    if (selectedNode?.id === nodeId) {
      setSelectedNode((prev) => prev ? { ...prev, ...updates } : null)
    }
  }, [selectedNode])

  // 绑定 Agent
  const handleBindAgent = useCallback((nodeId: string, agentId: string) => {
    const updateNode = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            boundAgents: [...node.boundAgents, agentId],
          }
        }
        if (node.children) {
          return { ...node, children: updateNode(node.children) }
        }
        return node
      })
    }

    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: updateNode(prev.root.children) },
    }))

    if (selectedNode?.id === nodeId) {
      setSelectedNode((prev) =>
        prev ? { ...prev, boundAgents: [...prev.boundAgents, agentId] } : null
      )
    }

    setAddAgentModalVisible(false)
    setAddAgentTargetNode(null)
    message.success('Agent 绑定成功')
  }, [selectedNode])

  // 解绑 Agent
  const handleUnbindAgent = useCallback((nodeId: string, agentId: string) => {
    const updateNode = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            boundAgents: node.boundAgents.filter((id) => id !== agentId),
          }
        }
        if (node.children) {
          return { ...node, children: updateNode(node.children) }
        }
        return node
      })
    }

    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: updateNode(prev.root.children) },
    }))

    if (selectedNode?.id === nodeId) {
      setSelectedNode((prev) =>
        prev
          ? { ...prev, boundAgents: prev.boundAgents.filter((id) => id !== agentId) }
          : null
      )
    }
  }, [selectedNode])

  // 打开添加 Agent Modal
  const handleOpenAddAgent = useCallback((node: OrgNode) => {
    setAddAgentTargetNode(node)
    setAddAgentModalVisible(true)
  }, [])

  // 拖拽开始
  const handleDragStart = useCallback((e: React.DragEvent, node: OrgNode) => {
    if (node.type === 'ceo') {
      e.preventDefault()
      return
    }
    setDraggedNode(node)
    e.dataTransfer.effectAllowed = 'move'
  }, [])

  // 拖拽经过
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }, [])

  // 放下节点
  const handleDrop = useCallback((e: React.DragEvent, targetNode: OrgNode) => {
    e.preventDefault()
    if (!draggedNode) return
    if (draggedNode.id === targetNode.id) return
    if (draggedNode.type === 'ceo') return

    // 如果目标节点是叶子节点，不允许放置
    if (targetNode.type === 'agent') {
      message.warning('不能将节点拖放到 Agent 上')
      setDraggedNode(null)
      return
    }

    // 从原位置删除
    const removeNode = (nodes: OrgNode[]): OrgNode[] => {
      return nodes
        .filter((n) => n.id !== draggedNode!.id)
        .map((node) => ({
          ...node,
          children: node.children ? removeNode(node.children) : [],
        }))
    }

    // 添加到新位置
    const addToTarget = (nodes: OrgNode[]): OrgNode[] => {
      return nodes.map((node) => {
        if (node.id === targetNode.id) {
          return {
            ...node,
            children: [...(node.children || []), { ...draggedNode!, expanded: true }],
            expanded: true,
          }
        }
        if (node.children) {
          return { ...node, children: addToTarget(node.children) }
        }
        return node
      })
    }

    const withoutDragged = removeNode(orgStructure.root.children || [])
    const withDropped = addToTarget(withoutDragged)

    setOrgStructure((prev) => ({
      ...prev,
      root: { ...prev.root, children: withDropped },
    }))

    message.success(`已将「${draggedNode.name}」移动到「${targetNode.name}」`)
    setDraggedNode(null)
  }, [draggedNode, orgStructure.root.children])

  // 保存结构
  const handleSave = useCallback(async () => {
    setLoading(true)
    try {
      // 将前端树形结构转换为后端扁平格式
      const backendData = adaptFrontendToBackend(orgStructure)
      await api('PUT', `/v1/organization/structure/${CURRENT_COMPANY_ID}`, backendData)
      message.success('组织结构已保存')
    } catch (error) {
      console.warn('[Organization] 保存失败（Mock 模式）:', error)
      localStorage.setItem('cyberteam_org_structure', JSON.stringify(orgStructure))
      message.success('组织结构已保存（本地 Mock）')
    } finally {
      setLoading(false)
    }
  }, [orgStructure])

  // 另存为配置
  const handleSaveAs = useCallback(async () => {
    if (!configName.trim()) {
      message.warning('请输入配置名称')
      return
    }

    try {
      const backendData = adaptFrontendToBackend(orgStructure)
      await api('POST', `/v1/organization/configs/${CURRENT_COMPANY_ID}`, {
        name: configName,
        structure: backendData,
      })
      message.success(`配置「${configName}」已保存`)
      setSaveModalVisible(false)
      setConfigName('')
    } catch (error) {
      console.warn('[Organization] 保存配置失败:', error)
      // Mock 模式
      const configs = JSON.parse(localStorage.getItem('cyberteam_org_configs') || '[]')
      configs.push({
        id: Date.now().toString(),
        name: configName,
        structure: orgStructure,
        createdAt: new Date().toISOString(),
      })
      localStorage.setItem('cyberteam_org_configs', JSON.stringify(configs))
      message.success(`配置「${configName}」已保存（本地 Mock）`)
      setSaveModalVisible(false)
      setConfigName('')
    }
  }, [configName, orgStructure])

  // 重置结构
  const handleReset = useCallback(() => {
    Modal.confirm({
      title: '确认重置',
      content: '确定要恢复默认结构吗？所有未保存的更改将丢失。',
      okText: '重置',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: () => {
        setOrgStructure(DEFAULT_ORG_STRUCTURE)
        setSelectedNode(null)
        message.success('已恢复默认结构')
      },
    })
  }, [])

  // 获取过滤后的可见节点
  const visibleNodes = useMemo(() => {
    return getVisibleNodes([orgStructure.root])
  }, [orgStructure.root, getVisibleNodes])

  return (
    <div className="h-full flex flex-col">
      {/* 顶部标题栏 */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Title level={4} className="m-0">
            🏢 CyberTeam 组织架构 Builder
          </Title>
        </div>
        <Space>
          <Button icon={<SaveOutlined />} onClick={handleSave} loading={loading}>
            保存结构
          </Button>
          <Button icon={<SwapOutlined />} onClick={() => setSaveModalVisible(true)}>
            另存为...
          </Button>
          <Button icon={<ReloadOutlined />} onClick={handleReset}>
            重置
          </Button>
        </Space>
      </div>

      {/* 主体内容 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧树形结构 */}
        <div className="w-1/2 border-r bg-gray-50 flex flex-col">
          {/* 层级切换 Tab */}
          <div className="bg-white border-b px-4">
            <LayerTabs
              activeLayer={activeLayer}
              onChange={setActiveLayer}
              discussCount={layerCounts.discuss}
              executeCount={layerCounts.execute}
            />
          </div>

          {/* 快捷操作按钮 */}
          <div className="px-4 py-2 flex gap-2 border-b bg-white">
            <Button
              size="small"
              icon={<PlusOutlined />}
              onClick={() => {
                setAddNodeParentNode(orgStructure.root)
                setAddNodeDefaultType('discuss_group')
                setAddNodeModalVisible(true)
              }}
            >
              添加讨论团队
            </Button>
            <Button
              size="small"
              icon={<PlusOutlined />}
              onClick={() => {
                setAddNodeParentNode(orgStructure.root)
                setAddNodeDefaultType('execute_group')
                setAddNodeModalVisible(true)
              }}
            >
              添加执行部门
            </Button>
            <div className="flex-1" />
            <Button size="small" icon={<ExpandOutlined />} onClick={expandAll}>
              展开
            </Button>
            <Button size="small" icon={<NodeCollapseOutlined />} onClick={collapseAll}>
              折叠
            </Button>
          </div>

          {/* 树形结构区域 */}
          <div className="flex-1 overflow-auto p-4">
            <Card className="mb-4 bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-xs text-gray-500">提示：</span>
                <span className="text-xs text-gray-500">单击选中 | 双击重命名</span>
                <span className="text-xs text-gray-500">| 右键菜单</span>
                <span className="text-xs text-gray-500">| 拖拽排序</span>
              </div>
            </Card>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Spin size="large" />
              </div>
            ) : (
              visibleNodes.map((node) => (
                <OrgNodeComponent
                  key={node.id}
                  node={node}
                  level={0}
                  selectedId={selectedNode?.id || null}
                  onSelect={handleSelect}
                  onToggle={handleToggle}
                  onAddChild={handleAddChild}
                  onDelete={handleDelete}
                  onInlineEdit={handleInlineEdit}
                  onDragStart={handleDragStart}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                />
              ))
            )}
          </div>
        </div>

        {/* 右侧详情面板 */}
        <div className="w-1/2 bg-gray-100 overflow-auto">
          <NodeDetail
            node={selectedNode}
            availableAgents={availableAgents}
            onSave={handleSaveNode}
            onAddChild={(node, type) => {
              if (type === 'agent') {
                handleOpenAddAgent(node)
              } else {
                handleAddChild(node, type)
              }
            }}
            onBindAgent={handleBindAgent}
            onUnbindAgent={handleUnbindAgent}
            onClose={handleCloseDetail}
          />
        </div>
      </div>

      {/* 新增节点 Modal */}
      <AddNodeModal
        open={addNodeModalVisible}
        parentNodeType={addNodeParentNode?.type}
        defaultType={addNodeDefaultType}
        onAdd={handleConfirmAddNode}
        onCancel={() => {
          setAddNodeModalVisible(false)
          setAddNodeParentNode(null)
          setAddNodeDefaultType(undefined)
        }}
      />

      {/* 绑定 Agent Modal */}
      <AddAgentModal
        open={addAgentModalVisible}
        nodeId={addAgentTargetNode?.id || ''}
        nodeName={addAgentTargetNode?.name || ''}
        nodeLayer={addAgentTargetNode?.layer || 'execute'}
        availableAgents={availableAgents}
        boundAgentIds={addAgentTargetNode?.boundAgents || []}
        loading={loadingAgents}
        onAdd={(agentId) => handleBindAgent(addAgentTargetNode!.id, agentId)}
        onCancel={() => {
          setAddAgentModalVisible(false)
          setAddAgentTargetNode(null)
        }}
      />

      {/* 另存为 Modal */}
      <Modal
        title="另存为配置"
        open={saveModalVisible}
        onOk={handleSaveAs}
        onCancel={() => {
          setSaveModalVisible(false)
          setConfigName('')
        }}
        okText="保存"
        cancelText="取消"
      >
        <div className="py-4">
          <label className="block mb-2 text-sm font-medium">配置名称</label>
          <Input
            placeholder="输入配置名称..."
            value={configName}
            onChange={(e) => setConfigName(e.target.value)}
            onPressEnter={handleSaveAs}
          />
          <Text type="secondary" className="text-xs">
            保存当前组织结构为命名配置快照，方便后续加载
          </Text>
        </div>
      </Modal>
    </div>
  )
}
