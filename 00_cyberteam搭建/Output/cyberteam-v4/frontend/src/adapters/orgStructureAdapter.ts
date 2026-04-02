/**
 * 组织架构数据适配器
 *
 * 后端模型（扁平）:
 *   OrgStructure {
 *     company_id, ceo_node, discussion_teams[], execution_departments[], updated_at
 *   }
 *   OrgNode { id, node_type, name, parent_id, icon, color, description, agent_ids, order, is_expanded, children[] }
 *
 * 前端模型（树形）:
 *   OrgStructure { companyId, companyName, root: OrgNode }
 *   OrgNode { id, name, type, layer, icon, color, description, boundAgents, children, expanded, editable, deletable }
 */

import type { OrgNode, OrgNodeType, OrgStructure, LayerType } from '@/types/organization'

// 后端扁平节点 → 前端树形节点
function backendNodeToFrontend(
  node: BackendOrgNode,
  parentType?: OrgNodeType,
  parentLayer?: LayerType
): OrgNode {
  // 根据 node_type 推断前端 type 和 layer
  let type: OrgNodeType
  let layer: LayerType

  switch (node.node_type) {
    case 'ceo':
      type = 'ceo'
      layer = 'ceo'
      break
    case 'discussion_layer':
      type = 'discuss_group'
      layer = 'discuss'
      break
    case 'execution_layer':
      type = 'execute_group'
      layer = 'execute'
      break
    case 'team':
      // team 在讨论层还是执行层？看 parent
      if (parentType === 'execute_group' || parentLayer === 'execute') {
        type = 'execute_dept'
        layer = 'execute'
      } else {
        type = 'discuss_team'
        layer = 'discuss'
      }
      break
    case 'department':
      type = 'execute_dept'
      layer = 'execute'
      break
    case 'agent':
      type = 'agent'
      layer = parentLayer ?? 'execute'
      break
    default:
      type = 'discuss_team'
      layer = 'discuss'
  }

  const children = (node.children || []).map((child) =>
    backendNodeToFrontend(child, type, layer)
  )

  return {
    id: node.id,
    name: node.name,
    type,
    layer,
    icon: node.icon,
    color: node.color,
    description: node.description,
    boundAgents: node.agent_ids || [],
    children,
    expanded: node.is_expanded ?? true,
    editable: type !== 'ceo',
    deletable: type !== 'ceo',
  }
}

// 前端树形节点 → 后端扁平节点
function frontendNodeToBackend(node: OrgNode, parentId?: string): BackendOrgNode {
  let nodeType: string

  switch (node.type) {
    case 'ceo':
      nodeType = 'ceo'
      break
    case 'discuss_group':
      nodeType = 'discussion_layer'
      break
    case 'execute_group':
      nodeType = 'execution_layer'
      break
    case 'discuss_team':
      nodeType = 'team'
      break
    case 'execute_dept':
      nodeType = 'department'
      break
    case 'agent':
      nodeType = 'agent'
      break
    default:
      nodeType = 'team'
  }

  return {
    id: node.id,
    node_type: nodeType,
    name: node.name,
    parent_id: parentId,
    icon: node.icon,
    color: node.color,
    description: node.description,
    agent_ids: node.boundAgents,
    order: 0,
    is_expanded: node.expanded ?? true,
    children: (node.children || []).map((child) =>
      frontendNodeToBackend(child, node.id)
    ),
  }
}

// 展开前端树形结构，提取后端扁平列表
export interface BackendOrgStructure {
  company_id: string
  ceo_node: BackendOrgNode
  discussion_teams: BackendOrgNode[]
  execution_departments: BackendOrgNode[]
  updated_at?: string
}

export interface BackendOrgNode {
  id: string
  node_type: string
  name: string
  parent_id?: string
  icon?: string
  color?: string
  description?: string
  agent_ids?: string[]
  order?: number
  is_expanded?: boolean
  children?: BackendOrgNode[]
}

function flattenTree(nodes: OrgNode[], parentId?: string): BackendOrgNode[] {
  const result: BackendOrgNode[] = []
  for (const node of nodes) {
    const backend = frontendNodeToBackend(node, parentId)
    // 扁平结构：把 children 也打平，但保留原始层级关系
    const { children: _, ...nodeWithoutChildren } = backend
    result.push(nodeWithoutChildren as BackendOrgNode)
    if (node.children && node.children.length > 0) {
      result.push(...flattenTree(node.children, node.id))
    }
  }
  return result
}

/**
 * 将后端 API 响应转换为前端树形结构
 */
export function adaptBackendToFrontend(
  backend: BackendOrgStructure,
  companyName = 'CyberTeam'
): OrgStructure {
  // 构建前端树：CEO → children = [讨论层节点, 执行层节点]
  const root: OrgNode = backendNodeToFrontend(backend.ceo_node)

  // 讨论层分组
  const discussGroup: OrgNode = {
    id: 'discuss_group_root',
    name: '讨论层',
    type: 'discuss_group',
    layer: 'discuss',
    icon: '💭',
    color: '#8b5cf6',
    description: '讨论层负责策略制定和分析',
    boundAgents: [],
    expanded: true,
    editable: true,
    deletable: false,
    children: backend.discussion_teams.map((t) => backendNodeToFrontend(t, 'discuss_group', 'discuss')),
  }

  // 执行层分组
  const executeGroup: OrgNode = {
    id: 'execute_group_root',
    name: '执行层',
    type: 'execute_group',
    layer: 'execute',
    icon: '⚙️',
    color: '#10b981',
    description: '执行层负责技术开发、设计实现、运营执行',
    boundAgents: [],
    expanded: true,
    editable: true,
    deletable: false,
    children: backend.execution_departments.map((d) => backendNodeToFrontend(d, 'execute_group', 'execute')),
  }

  // CEO children = [讨论层分组, 执行层分组]
  root.children = [discussGroup, executeGroup]

  return {
    companyId: backend.company_id,
    companyName,
    root,
    updatedAt: backend.updated_at,
  }
}

/**
 * 将前端树形结构转换为后端扁平结构用于保存
 */
export function adaptFrontendToBackend(
  frontend: OrgStructure
): { company_id: string; ceo_node: BackendOrgNode; discussion_teams: BackendOrgNode[]; execution_departments: BackendOrgNode[] } {
  // 从前端 root 提取 ceo_node
  const ceoNode = frontendNodeToBackend(frontend.root)

  // 从 root.children 提取讨论层和执行层
  const discussGroup = frontend.root.children?.find((c) => c.type === 'discuss_group')
  const executeGroup = frontend.root.children?.find((c) => c.type === 'execute_group')

  const discussion_teams = (discussGroup?.children || []).map((t) =>
    frontendNodeToBackend(t, 'discussion-default')
  )

  const execution_departments = (executeGroup?.children || []).map((d) =>
    frontendNodeToBackend(d, 'execution-default')
  )

  return {
    company_id: frontend.companyId,
    ceo_node: ceoNode,
    discussion_teams,
    execution_departments,
  }
}

/**
 * 从后端 OrgNode 递归构建带 children 的树
 */
function buildBackendTree(
  nodes: BackendOrgNode[],
  parentId?: string
): OrgNode[] {
  return nodes
    .filter((n) => n.parent_id === parentId)
    .sort((a, b) => (a.order || 0) - (b.order || 0))
    .map((n) => backendNodeToFrontend(n))
}
