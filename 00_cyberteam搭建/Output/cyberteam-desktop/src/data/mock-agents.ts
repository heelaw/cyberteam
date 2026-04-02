// ==================== Agent 模拟数据 ====================
// 在真正的 Agent 市场实现之前，使用这些模拟数据

export type AgentStatus = "online" | "offline" | "busy" | "thinking"
export type AgentRole = "ceo" | "manager" | "expert" | "executor"

export interface AgentData {
  id: string
  name: string
  role: string // 岗位名称，如"增长总监"
  department: string // 部门名称，如"增长部"
  departmentId: string
  avatar: string // 头像 URL 或 emoji
  status: AgentStatus
  capabilities: string[] // 能力列表
  description: string
}

export const mockAgents: AgentData[] = [
  // 管理层
  {
    id: "agent-ceo",
    name: "CEO",
    role: "首席执行官",
    department: "管理",
    departmentId: "dept-management",
    avatar: "👑",
    status: "online",
    capabilities: ["战略规划", "决策审批", "风险把控", "资源分配"],
    description: "负责公司整体战略方向和重大决策审批",
  },
  {
    id: "agent-coo",
    name: "COO",
    role: "首席运营官",
    department: "管理",
    departmentId: "dept-management",
    avatar: "⚡",
    status: "online",
    capabilities: ["运营管理", "策略协调", "跨部门协作", "流程优化"],
    description: "负责公司日常运营和策略协调",
  },

  // 增长部
  {
    id: "agent-growth-director",
    name: "增长总监",
    role: "增长部门负责人",
    department: "增长部",
    departmentId: "dept-growth",
    avatar: "📈",
    status: "online",
    capabilities: ["小红书运营", "抖音运营", "SEO", "用户增长", "数据分析"],
    description: "负责用户增长和内容运营策略",
  },
  {
    id: "agent-seo-specialist",
    name: "SEO 专员",
    role: "增长部 - SEO 专家",
    department: "增长部",
    departmentId: "dept-growth",
    avatar: "🔍",
    status: "online",
    capabilities: ["关键词研究", "外链建设", "技术SEO", "数据分析"],
    description: "负责搜索引擎优化和自然流量增长",
  },
  {
    id: "agent-content-creator",
    name: "内容运营",
    role: "增长部 - 内容专家",
    department: "增长部",
    departmentId: "dept-growth",
    avatar: "✍️",
    status: "busy",
    capabilities: ["小红书内容", "抖音脚本", "文案撰写", "热点追踪"],
    description: "负责各平台内容策划和文案创作",
  },

  // 产品部
  {
    id: "agent-product-director",
    name: "产品总监",
    role: "产品部门负责人",
    department: "产品部",
    departmentId: "dept-product",
    avatar: "🎯",
    status: "busy",
    capabilities: ["产品设计", "需求分析", "用户体验", "竞品分析", "PRD 撰写"],
    description: "负责产品规划设计和需求管理",
  },
  {
    id: "agent-ux-researcher",
    name: "UX 研究员",
    role: "产品部 - 用户体验专家",
    department: "产品部",
    departmentId: "dept-product",
    avatar: "🔬",
    status: "online",
    capabilities: ["用户调研", "可用性测试", "数据分析", "用户画像"],
    description: "负责用户研究和体验优化",
  },

  // 技术部
  {
    id: "agent-cto",
    name: "CTO",
    role: "首席技术官",
    department: "技术部",
    departmentId: "dept-tech",
    avatar: "💻",
    status: "online",
    capabilities: ["架构设计", "技术选型", "代码审查", "性能优化"],
    description: "负责技术方向和技术团队管理",
  },
  {
    id: "agent-frontend-dev",
    name: "前端工程师",
    role: "技术部 - 前端专家",
    department: "技术部",
    departmentId: "dept-tech",
    avatar: "⚛️",
    status: "online",
    capabilities: ["React", "TypeScript", "CSS", "性能优化", "响应式设计"],
    description: "负责前端开发和界面实现",
  },
  {
    id: "agent-backend-dev",
    name: "后端工程师",
    role: "技术部 - 后端专家",
    department: "技术部",
    departmentId: "dept-tech",
    avatar: "🔧",
    status: "online",
    capabilities: ["Node.js", "Python", "数据库设计", "API 开发", "微服务"],
    description: "负责后端服务和数据架构",
  },

  // 运营部
  {
    id: "agent-ops-director",
    name: "运营总监",
    role: "运营部门负责人",
    department: "运营部",
    departmentId: "dept-ops",
    avatar: "🚀",
    status: "online",
    capabilities: ["活动策划", "用户运营", "数据分析", "渠道管理"],
    description: "负责用户运营和活动策划",
  },
  {
    id: "agent-user-ops",
    name: "用户运营",
    role: "运营部 - 用户运营专家",
    department: "运营部",
    departmentId: "dept-ops",
    avatar: "👥",
    status: "online",
    capabilities: ["用户分层", "生命周期管理", "社群运营", "转化优化"],
    description: "负责用户分层运营和生命周期管理",
  },

  // 质量部
  {
    id: "agent-qa-director",
    name: "质量总监",
    role: "质量部门负责人",
    department: "质量部",
    departmentId: "dept-qa",
    avatar: "🛡️",
    status: "online",
    capabilities: ["质量体系", "测试策略", "风险评估", "流程改进"],
    description: "负责质量保障和测试策略",
  },
]

/**
 * 按部门分组 Agent
 */
export const groupAgentsByDepartment = (agents: AgentData[]): Record<string, AgentData[]> => {
  const groups: Record<string, AgentData[]> = {}
  agents.forEach(agent => {
    if (!groups[agent.department]) {
      groups[agent.department] = []
    }
    groups[agent.department].push(agent)
  })
  return groups
}

/**
 * 获取在线 Agent
 */
export const getOnlineAgents = (agents: AgentData[]): AgentData[] => {
  return agents.filter(a => a.status !== "offline")
}

/**
 * 根据 ID 查找 Agent
 */
export const getAgentById = (agents: AgentData[], id: string): AgentData | undefined => {
  return agents.find(a => a.id === id)
}

/**
 * 状态颜色映射
 */
export const statusColorMap: Record<AgentStatus, string> = {
  online: "#22c55e",  // 绿色
  busy: "#f59e0b",    // 橙色
  thinking: "#3b82f6", // 蓝色
  offline: "#9ca3af", // 灰色
}
