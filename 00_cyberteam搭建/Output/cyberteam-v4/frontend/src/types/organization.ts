/**
 * 组织架构 Builder 类型定义
 *
 * 节点类型：
 * - CEO: 金色 👑，固定不可删除
 * - 讨论层分组: 紫色 💭，分组容器可折叠
 * - 执行层分组: 绿色 ⚙️，分组容器可折叠
 * - 讨论团队: 紫色 💬
 * - 执行部门: 绿色 💻
 * - Agent 节点: 蓝色 🤖，叶子节点
 */

// 节点类型枚举
export type OrgNodeType =
  | 'ceo'           // CEO 根节点
  | 'discuss_group' // 讨论层分组
  | 'execute_group' // 执行层分组
  | 'discuss_team'  // 讨论团队
  | 'execute_dept'  // 执行部门
  | 'agent'         // Agent 叶子节点

// 层级类型
export type LayerType = 'discuss' | 'execute' | 'ceo'

// 节点图标映射
export const NODE_ICONS: Record<OrgNodeType, string> = {
  ceo: '👑',
  discuss_group: '💭',
  execute_group: '⚙️',
  discuss_team: '💬',
  execute_dept: '💻',
  agent: '🤖',
}

// 节点颜色映射
export const NODE_COLORS: Record<OrgNodeType, string> = {
  ceo: '#f59e0b',           // 金色
  discuss_group: '#8b5cf6', // 紫色
  execute_group: '#10b981', // 绿色
  discuss_team: '#8b5cf6',  // 紫色
  execute_dept: '#10b981',  // 绿色
  agent: '#3b82f6',         // 蓝色
}

// 节点颜色 CSS 类映射
export const NODE_COLOR_CLASS: Record<OrgNodeType, string> = {
  ceo: 'bg-amber-50 border-amber-200',
  discuss_group: 'bg-purple-50 border-purple-200',
  execute_group: 'bg-green-50 border-green-200',
  discuss_team: 'bg-purple-50 border-purple-200',
  execute_dept: 'bg-green-50 border-green-200',
  agent: 'bg-blue-50 border-blue-200',
}

// 组织节点
export interface OrgNode {
  id: string
  name: string
  type: OrgNodeType
  layer: LayerType
  icon?: string
  color?: string
  description?: string
  boundAgents: string[]     // 绑定的 Agent ID 列表
  children: OrgNode[]       // 子节点
  expanded?: boolean        // 展开/折叠状态
  editable?: boolean        // 是否可编辑（CEO 不可编辑）
  deletable?: boolean       // 是否可删除（CEO 不可删除）
}

// 组织结构
export interface OrgStructure {
  companyId: string
  companyName: string
  root: OrgNode             // CEO 根节点
  version?: string
  updatedAt?: string
}

// 配置快照
export interface OrgConfig {
  id: string
  name: string
  structure: OrgStructure
  createdAt: string
  isDefault?: boolean
}

// 可用的 Agent（用于绑定选择）
export interface AvailableAgent {
  id: string
  code: string
  name: string
  agentType: string
  description?: string
  layer: LayerType
  skills: string[]
  status: 'active' | 'inactive'
}

// API 请求/响应类型
export interface UpdateOrgStructureRequest {
  structure: OrgStructure
}

export interface SaveOrgConfigRequest {
  name: string
  structure: OrgStructure
}

// 节点编辑表单数据
export interface OrgNodeFormData {
  name: string
  type: OrgNodeType
  layer: LayerType
  icon: string
  color: string
  description: string
  boundAgents: string[]
}

// 新增节点默认值
export const DEFAULT_NODE_FORM: OrgNodeFormData = {
  name: '',
  type: 'discuss_team',
  layer: 'discuss',
  icon: '💬',
  color: '#8b5cf6',
  description: '',
  boundAgents: [],
}

// 创建新的 OrgNode
export function createOrgNode(
  partial: Partial<OrgNode> & { id: string; name: string; type: OrgNodeType }
): OrgNode {
  const layer = partial.layer ?? (partial.type.includes('discuss') ? 'discuss' : partial.type.includes('execute') ? 'execute' : 'ceo')
  return {
    ...partial,
    id: partial.id,
    name: partial.name,
    type: partial.type,
    layer,
    icon: partial.icon ?? NODE_ICONS[partial.type],
    color: partial.color ?? NODE_COLORS[partial.type],
    boundAgents: partial.boundAgents ?? [],
    children: partial.children ?? [],
    expanded: partial.expanded ?? true,
    editable: partial.editable ?? partial.type !== 'ceo',
    deletable: partial.deletable ?? partial.type !== 'ceo',
  }
}

// 生成唯一 ID
export function generateNodeId(type: OrgNodeType): string {
  return `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 判断节点是否为叶子节点
export function isLeafNode(node: OrgNode): boolean {
  return node.type === 'agent'
}

// 判断节点是否为分组容器
export function isGroupNode(node: OrgNode): boolean {
  return node.type === 'discuss_group' || node.type === 'execute_group'
}

// 判断节点是否可以添加子节点
export function canAddChildren(node: OrgNode): boolean {
  return node.type !== 'agent'
}

// 判断节点是否可以绑定 Agent
export function canBindAgent(node: OrgNode): boolean {
  return node.type === 'discuss_team' || node.type === 'execute_dept' || node.type === 'agent'
}
