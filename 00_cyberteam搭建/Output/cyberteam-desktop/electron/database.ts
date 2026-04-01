import path from "path"
import fs from "fs"
import electron from "electron"
const app = electron.app

export interface ChatSession {
  id: string
  title: string
  working_directory: string
  provider_id: string
  model: string
  system_prompt: string
  conversation_type: string
  department_id: string | null
  project_id: string | null
  review_status: string
  review_notes: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  session_id: string
  role: "user" | "assistant" | "system"
  content: string
  sender_id: string
  sender_name: string
  sender_avatar: string
  metadata: string
  token_usage: string | null
  created_at: string
}

export interface ApiProvider {
  id: string
  name: string
  provider_type: string
  protocol: string
  base_url: string
  api_key: string
  is_active: number
  sort_order: number
  extra_env: string
  headers_json: string
  role_models_json: string
  notes: string
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  name: string
  description: string
  working_directory: string
  department_id: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface Department {
  id: string
  name: string
  icon: string
  parent_id: string | null
  description: string
  sort_order: number
  created_at: string
}

export interface Agent {
  id: string
  name: string
  avatar: string
  role: string
  department_id: string
  description: string
  soul_content: string
  status: string
  capabilities: string
  config: string
  created_at: string
}

export interface MeetingMinutes {
  id: string
  project_id: string
  meeting_type: string
  title: string
  content: string
  review_status: string
  attachments: string
  created_at: string
}

export interface CrewTemplate {
  id: string
  name: string
  description: string
  members: string
  departments: string
  is_preset: number
  created_at: string
}

export interface Skill {
  id: string
  name: string
  icon: string
  category: string
  description: string
  trigger: string
  workflow: string
  agent_id: string | null
  department_id: string | null
  is_preset: number
  config: string
  created_at: string
  updated_at: string
}

interface Database {
  providers: ApiProvider[]
  sessions: ChatSession[]
  messages: Message[]
  projects: Project[]
  departments: Department[]
  agents: Agent[]
  meetingMinutes: MeetingMinutes[]
  crewTemplates: CrewTemplate[]
  skills: Skill[]
}

// JSON 文件存储
class JsonDatabase {
  private dbPath: string
  private data: Database

  constructor(dbPath: string) {
    this.dbPath = dbPath
    this.data = this.load()
  }

  private load(): Database {
    try {
      if (fs.existsSync(this.dbPath)) {
        const content = fs.readFileSync(this.dbPath, "utf-8")
        return JSON.parse(content)
      }
    } catch (err) {
      console.error("[DB] Load error:", err)
    }

    // 返回默认数据结构
    return this.getDefaultData()
  }

  private save(): void {
    try {
      const dir = path.dirname(this.dbPath)
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
      }
      fs.writeFileSync(this.dbPath, JSON.stringify(this.data, null, 2))
    } catch (err) {
      console.error("[DB] Save error:", err)
    }
  }

  private getDefaultData(): Database {
    const now = new Date().toISOString()

    return {
      providers: [
        {
          id: "provider_anthropic",
          name: "Anthropic",
          provider_type: "anthropic",
          protocol: "anthropic",
          base_url: "https://api.anthropic.com",
          api_key: "",
          is_active: 1,
          sort_order: 0,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now,
        },
        {
          id: "provider_minimax",
          name: "MiniMax",
          provider_type: "minimax",
          protocol: "openai-compatible",
          base_url: "https://api.minimax.chat/v",
          api_key: "",
          is_active: 0,
          sort_order: 1,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now,
        },
        {
          id: "provider_openrouter",
          name: "OpenRouter",
          provider_type: "openrouter",
          protocol: "openrouter",
          base_url: "https://openrouter.ai/api/v1",
          api_key: "",
          is_active: 0,
          sort_order: 2,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now,
        },
      ],
      sessions: [],
      messages: [],
      projects: [],
      departments: [
        { id: "dept_ceo", name: "CEO", icon: "👑", parent_id: null, description: "", sort_order: 0, created_at: now },
        { id: "dept_coo", name: "COO", icon: "🎯", parent_id: null, description: "", sort_order: 1, created_at: now },
        { id: "dept_strategy", name: "战略部", icon: "📊", parent_id: null, description: "", sort_order: 2, created_at: now },
        { id: "dept_product", name: "产品部", icon: "💼", parent_id: null, description: "", sort_order: 3, created_at: now },
        { id: "dept_eng", name: "研发部", icon: "⚙️", parent_id: null, description: "", sort_order: 4, created_at: now },
        { id: "dept_design", name: "设计部", icon: "🎨", parent_id: null, description: "", sort_order: 5, created_at: now },
        { id: "dept_ops", name: "运营部", icon: "🚀", parent_id: null, description: "", sort_order: 6, created_at: now },
        { id: "dept_finance", name: "财务部", icon: "💰", parent_id: null, description: "", sort_order: 7, created_at: now },
        { id: "dept_hr", name: "人力资源部", icon: "👥", parent_id: null, description: "", sort_order: 8, created_at: now },
        { id: "dept_marketing", name: "市场部", icon: "📢", parent_id: null, description: "", sort_order: 9, created_at: now },
      ],
      agents: [
        {
          id: "agent_ceo",
          name: "CEO",
          avatar: "👑",
          role: "ceo",
          department_id: "dept_ceo",
          description: "CyberTeam CEO，负责战略决策和整体协调",
          soul_content: "",
          status: "online",
          capabilities: "[]",
          config: "{}",
          created_at: now,
        },
      ],
      meetingMinutes: [],
      crewTemplates: [],
      skills: [
        {
          id: "skill_content_creation",
          name: "内容创作法",
          icon: "✍️",
          category: "content",
          description: "小红书/抖音多平台内容创作技能，包含选题、文案、排版全流程",
          trigger: "内容创作 / 文案 / 种草笔记 / 脚本",
          workflow: "1.分析目标用户画像\n2.确定内容选题方向\n3.撰写初稿\n4.优化标题和封面\n5.适配平台格式",
          agent_id: null,
          department_id: "dept_ops",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now,
        },
        {
          id: "skill_data_analysis",
          name: "数据分析法",
          icon: "📊",
          category: "analytics",
          description: "用户行为分析、AB测试、转化漏斗等数据驱动决策技能",
          trigger: "数据分析 / AB测试 / 转化率 / 用户行为",
          workflow: "1.明确分析目标\n2.数据采集和清洗\n3.构建分析模型\n4.可视化呈现\n5.输出决策建议",
          agent_id: null,
          department_id: "dept_ops",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now,
        },
        {
          id: "skill_seo_optimization",
          name: "SEO优化法",
          icon: "🔍",
          category: "marketing",
          description: "搜索引擎优化，包含关键词研究、技术SEO、外链建设全流程",
          trigger: "SEO / 关键词 / 搜索排名 / 自然流量",
          workflow: "1.关键词研究和分析\n2.站内优化（标题/描述/结构）\n3.技术SEO检查\n4.内容优化\n5.外链建设策略",
          agent_id: null,
          department_id: "dept_ops",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now,
        },
        {
          id: "skill_strategy_planning",
          name: "战略规划法",
          icon: "🎯",
          category: "strategy",
          description: "SWOT分析、OKR设定、路线图规划等战略规划技能",
          trigger: "战略规划 / SWOT / OKR / 路线图",
          workflow: "1.现状分析（SWOT）\n2.设定目标（OKR）\n3.制定路线图\n4.资源配置计划\n5.风险评估和预案",
          agent_id: null,
          department_id: "dept_ceo",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now,
        },
        {
          id: "skill_product_design",
          name: "产品设计法",
          icon: "💡",
          category: "product",
          description: "需求分析、PRD撰写、原型设计等产品技能",
          trigger: "产品 / PRD / 需求分析 / 原型 / 用户体验",
          workflow: "1.需求收集和分析\n2.用户故事编写\n3.PRD文档撰写\n4.原型设计\n5.评审和迭代",
          agent_id: null,
          department_id: "dept_product",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now,
        },
        {
          id: "skill_project_management",
          name: "项目管理法",
          icon: "📋",
          category: "management",
          description: "项目进度管理、风险评估、团队协调等项目管理技能",
          trigger: "项目管理 / 进度 / 里程碑 / 风险",
          workflow: "1.项目范围定义\n2.任务分解（WBS）\n3.进度排期\n4.风险识别和管理\n5.复盘和总结",
          agent_id: null,
          department_id: "dept_ceo",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now,
        },
      ],
    }
  }

  // ==================== Provider ====================

  getProviders(): ApiProvider[] {
    return this.data.providers.sort((a, b) => a.sort_order - b.sort_order)
  }

  getProvider(id: string): ApiProvider | undefined {
    return this.data.providers.find((p) => p.id === id)
  }

  createProvider(provider: ApiProvider): ApiProvider {
    this.data.providers.push(provider)
    this.save()
    return provider
  }

  updateProvider(id: string, data: Partial<ApiProvider>): ApiProvider | undefined {
    const index = this.data.providers.findIndex((p) => p.id === id)
    if (index !== -1) {
      this.data.providers[index] = { ...this.data.providers[index], ...data }
      this.save()
      return this.data.providers[index]
    }
    return undefined
  }

  deleteProvider(id: string): boolean {
    const index = this.data.providers.findIndex((p) => p.id === id)
    if (index !== -1) {
      this.data.providers.splice(index, 1)
      this.save()
      return true
    }
    return false
  }

  // ==================== Sessions ====================

  getSessions(): ChatSession[] {
    return this.data.sessions.sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  }

  getSession(id: string): ChatSession | undefined {
    return this.data.sessions.find((s) => s.id === id)
  }

  createSession(session: ChatSession): ChatSession {
    this.data.sessions.push(session)
    this.save()
    return session
  }

  updateSession(id: string, data: Partial<ChatSession>): ChatSession | undefined {
    const index = this.data.sessions.findIndex((s) => s.id === id)
    if (index !== -1) {
      this.data.sessions[index] = { ...this.data.sessions[index], ...data }
      this.save()
      return this.data.sessions[index]
    }
    return undefined
  }

  deleteSession(id: string): boolean {
    const index = this.data.sessions.findIndex((s) => s.id === id)
    if (index !== -1) {
      this.data.sessions.splice(index, 1)
      // 同时删除关联的消息
      this.data.messages = this.data.messages.filter((m) => m.session_id !== id)
      this.save()
      return true
    }
    return false
  }

  // ==================== Messages ====================

  getMessages(sessionId: string): Message[] {
    return this.data.messages
      .filter((m) => m.session_id === sessionId)
      .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
  }

  createMessage(message: Message): Message {
    this.data.messages.push(message)
    this.save()
    return message
  }

  // ==================== Projects ====================

  getProjects(): Project[] {
    return this.data.projects.sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  }

  getProject(id: string): Project | undefined {
    return this.data.projects.find((p) => p.id === id)
  }

  createProject(project: Project): Project {
    this.data.projects.push(project)
    this.save()
    return project
  }

  updateProject(id: string, data: Partial<Project>): Project | undefined {
    const index = this.data.projects.findIndex((p) => p.id === id)
    if (index !== -1) {
      this.data.projects[index] = { ...this.data.projects[index], ...data }
      this.save()
      return this.data.projects[index]
    }
    return undefined
  }

  deleteProject(id: string): boolean {
    const index = this.data.projects.findIndex((p) => p.id === id)
    if (index !== -1) {
      this.data.projects.splice(index, 1)
      this.save()
      return true
    }
    return false
  }

  // ==================== Departments ====================

  getDepartments(): Department[] {
    return this.data.departments.sort((a, b) => a.sort_order - b.sort_order)
  }

  getDepartment(id: string): Department | undefined {
    return this.data.departments.find((d) => d.id === id)
  }

  createDepartment(department: Department): Department {
    this.data.departments.push(department)
    this.save()
    return department
  }

  updateDepartment(id: string, data: Partial<Department>): Department | undefined {
    const index = this.data.departments.findIndex((d) => d.id === id)
    if (index !== -1) {
      this.data.departments[index] = { ...this.data.departments[index], ...data }
      this.save()
      return this.data.departments[index]
    }
    return undefined
  }

  deleteDepartment(id: string): boolean {
    const index = this.data.departments.findIndex((d) => d.id === id)
    if (index !== -1) {
      this.data.departments.splice(index, 1)
      this.save()
      return true
    }
    return false
  }

  // ==================== Agents ====================

  getAgents(): Agent[] {
    return this.data.agents.sort((a, b) => a.department_id.localeCompare(b.department_id))
  }

  getAgent(id: string): Agent | undefined {
    return this.data.agents.find((a) => a.id === id)
  }

  createAgent(agent: Agent): Agent {
    this.data.agents.push(agent)
    this.save()
    return agent
  }

  updateAgent(id: string, data: Partial<Agent>): Agent | undefined {
    const index = this.data.agents.findIndex((a) => a.id === id)
    if (index !== -1) {
      this.data.agents[index] = { ...this.data.agents[index], ...data }
      this.save()
      return this.data.agents[index]
    }
    return undefined
  }

  deleteAgent(id: string): boolean {
    const index = this.data.agents.findIndex((a) => a.id === id)
    if (index !== -1) {
      this.data.agents.splice(index, 1)
      this.save()
      return true
    }
    return false
  }

  // ==================== Meeting Minutes ====================

  getMeetingMinutes(projectId?: string): MeetingMinutes[] {
    let minutes = this.data.meetingMinutes
    if (projectId) {
      minutes = minutes.filter((m) => m.project_id === projectId)
    }
    return minutes.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  }

  createMeetingMinutes(minutes: MeetingMinutes): MeetingMinutes {
    this.data.meetingMinutes.push(minutes)
    this.save()
    return minutes
  }

  updateMeetingMinutes(id: string, data: Partial<MeetingMinutes>): MeetingMinutes | undefined {
    const index = this.data.meetingMinutes.findIndex((m) => m.id === id)
    if (index !== -1) {
      this.data.meetingMinutes[index] = { ...this.data.meetingMinutes[index], ...data }
      this.save()
      return this.data.meetingMinutes[index]
    }
    return undefined
  }

  // ==================== Crew Templates ====================

  getCrewTemplates(): CrewTemplate[] {
    return this.data.crewTemplates.sort((a, b) => b.is_preset - a.is_preset)
  }

  createCrewTemplate(template: CrewTemplate): CrewTemplate {
    this.data.crewTemplates.push(template)
    this.save()
    return template
  }

  deleteCrewTemplate(id: string): boolean {
    const index = this.data.crewTemplates.findIndex((t) => t.id === id)
    if (index !== -1) {
      this.data.crewTemplates.splice(index, 1)
      this.save()
      return true
    }
    return false
  }

  // ==================== Skills ====================

  getSkills(): Skill[] {
    return this.data.skills || []
  }

  getSkill(id: string): Skill | undefined {
    return (this.data.skills || []).find((s) => s.id === id)
  }

  getSkillsByAgent(agentId: string): Skill[] {
    return (this.data.skills || []).filter((s) => s.agent_id === agentId)
  }

  getSkillsByDepartment(deptId: string): Skill[] {
    return (this.data.skills || []).filter((s) => s.department_id === deptId)
  }

  createSkill(skill: Skill): Skill {
    if (!this.data.skills) this.data.skills = []
    this.data.skills.push(skill)
    this.save()
    return skill
  }

  updateSkill(id: string, data: Partial<Skill>): Skill | undefined {
    if (!this.data.skills) return undefined
    const index = this.data.skills.findIndex((s) => s.id === id)
    if (index !== -1) {
      this.data.skills[index] = { ...this.data.skills[index], ...data }
      this.save()
      return this.data.skills[index]
    }
    return undefined
  }

  deleteSkill(id: string): boolean {
    if (!this.data.skills) return false
    const index = this.data.skills.findIndex((s) => s.id === id)
    if (index !== -1) {
      this.data.skills.splice(index, 1)
      this.save()
      return true
    }
    return false
  }
}

// 导出单例
let dbInstance: JsonDatabase | null = null

export function initDatabase(): JsonDatabase {
  const userDataPath = app.getPath("userData")
  const dbPath = path.join(userDataPath, "cyberteam-data.json")
  dbInstance = new JsonDatabase(dbPath)
  console.log("[DB] Database initialized:", dbPath)
  return dbInstance
}

export function getDb(): JsonDatabase {
  if (!dbInstance) {
    throw new Error("Database not initialized. Call initDatabase first.")
  }
  return dbInstance
}
