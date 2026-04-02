import { contextBridge, ipcRenderer } from "electron"

// ==================== 类型定义 ====================

interface ChatSession {
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

interface Message {
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

interface ApiProvider {
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

interface Project {
  id: string
  name: string
  description: string
  working_directory: string
  department_id: string | null
  status: string
  created_at: string
  updated_at: string
}

interface Department {
  id: string
  name: string
  icon: string
  parent_id: string | null
  description: string
  sort_order: number
  created_at: string
}

interface Agent {
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

interface MeetingMinutes {
  id: string
  project_id: string
  meeting_type: string
  title: string
  content: string
  review_status: string
  attachments: string
  created_at: string
}

interface CrewTemplate {
  id: string
  name: string
  description: string
  members: string
  departments: string
  is_preset: number
  created_at: string
}

interface Skill {
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

interface DirEntry {
  name: string
  path: string
}

interface BrowseResult {
  current: string
  parent: string | null
  directories: DirEntry[]
  error: string | null
}

// ==================== API 暴露 ====================

const api = {
  // ==================== 对话会话 ====================
  chat: {
    sessions: {
      list: (): Promise<ChatSession[]> => ipcRenderer.invoke("chat:sessions:list"),
      get: (id: string): Promise<ChatSession | null> => ipcRenderer.invoke("chat:sessions:get", id),
      create: (data: Partial<ChatSession>): Promise<ChatSession> =>
        ipcRenderer.invoke("chat:sessions:create", data),
      update: (id: string, data: Record<string, unknown>): Promise<ChatSession | null> =>
        ipcRenderer.invoke("chat:sessions:update", id, data),
      delete: (id: string): Promise<boolean> => ipcRenderer.invoke("chat:sessions:delete", id),
    },
    messages: {
      list: (sessionId: string): Promise<Message[]> =>
        ipcRenderer.invoke("chat:messages:list", sessionId),
      create: (data: Partial<Message>): Promise<Message> =>
        ipcRenderer.invoke("chat:messages:create", data),
    },
  },

  // ==================== Claude Code CLI ====================
  claude: {
    send: (data: {
      session_id: string
      message: string
      working_directory: string
      provider_id?: string
      model?: string
      system_prompt?: string
    }): Promise<{ content: string; messageId: string }> => ipcRenderer.invoke("claude:send", data),

    stream: (
      data: {
        session_id: string
        message: string
        working_directory: string
        provider_id?: string
        model?: string
        system_prompt?: string
      },
      onChunk: (event: { messageId: string; chunk: string; fullContent: string }) => void
    ): Promise<{ messageId: string }> => {
      // 设置流式监听
      const listener = (_: Electron.IpcRendererEvent, data: { messageId: string; chunk: string; fullContent: string }) => {
        onChunk(data)
      }
      ipcRenderer.on("claude:stream:chunk", listener)

      return ipcRenderer.invoke("claude:stream", data).finally(() => {
        ipcRenderer.removeListener("claude:stream:chunk", listener)
      })
    },
  },

  // ==================== 文件浏览 ====================
  files: {
    browse: (dirPath: string): Promise<BrowseResult> => ipcRenderer.invoke("files:browse", dirPath),
    validateDirectory: (dirPath: string): Promise<boolean> =>
      ipcRenderer.invoke("files:validate-directory", dirPath),
    selectDirectory: (): Promise<string | null> => ipcRenderer.invoke("files:select-directory"),
  },

  // ==================== Provider 管理 ====================
  providers: {
    list: (): Promise<ApiProvider[]> => ipcRenderer.invoke("providers:list"),
    get: (id: string): Promise<ApiProvider | null> => ipcRenderer.invoke("providers:get", id),
    create: (data: Partial<ApiProvider>): Promise<ApiProvider> =>
      ipcRenderer.invoke("providers:create", data),
    update: (id: string, data: Record<string, unknown>): Promise<ApiProvider | null> =>
      ipcRenderer.invoke("providers:update", id, data),
    delete: (id: string): Promise<boolean> => ipcRenderer.invoke("providers:delete", id),
    test: (id: string): Promise<{ success: boolean; error?: string }> =>
      ipcRenderer.invoke("providers:test", id),
  },

  // ==================== 项目管理 ====================
  projects: {
    list: (): Promise<Project[]> => ipcRenderer.invoke("projects:list"),
    get: (id: string): Promise<Project | null> => ipcRenderer.invoke("projects:get", id),
    create: (data: Partial<Project>): Promise<Project> =>
      ipcRenderer.invoke("projects:create", data),
    update: (id: string, data: Record<string, unknown>): Promise<Project | null> =>
      ipcRenderer.invoke("projects:update", id, data),
    delete: (id: string): Promise<boolean> => ipcRenderer.invoke("projects:delete", id),
  },

  // ==================== 部门管理 ====================
  departments: {
    list: (): Promise<Department[]> => ipcRenderer.invoke("departments:list"),
    create: (data: Partial<Department>): Promise<Department> =>
      ipcRenderer.invoke("departments:create", data),
    update: (id: string, data: Record<string, unknown>): Promise<Department | null> =>
      ipcRenderer.invoke("departments:update", id, data),
    delete: (id: string): Promise<boolean> => ipcRenderer.invoke("departments:delete", id),
  },

  // ==================== Agent 管理 ====================
  agents: {
    list: (): Promise<Agent[]> => ipcRenderer.invoke("agents:list"),
    get: (id: string): Promise<Agent | null> => ipcRenderer.invoke("agents:get", id),
    create: (data: Partial<Agent>): Promise<Agent> =>
      ipcRenderer.invoke("agents:create", data),
    update: (id: string, data: Record<string, unknown>): Promise<Agent | null> =>
      ipcRenderer.invoke("agents:update", id, data),
    delete: (id: string): Promise<boolean> => ipcRenderer.invoke("agents:delete", id),
  },

  // ==================== 会议纪要 ====================
  meetingMinutes: {
    list: (projectId?: string): Promise<MeetingMinutes[]> =>
      ipcRenderer.invoke("meeting-minutes:list", projectId),
    create: (data: Partial<MeetingMinutes>): Promise<MeetingMinutes> =>
      ipcRenderer.invoke("meeting-minutes:create", data),
    update: (id: string, data: Record<string, unknown>): Promise<MeetingMinutes | null> =>
      ipcRenderer.invoke("meeting-minutes:update", id, data),
  },

  // ==================== Crew 团队模板 ====================
  crewTemplates: {
    list: (): Promise<CrewTemplate[]> => ipcRenderer.invoke("crew-templates:list"),
    create: (data: Partial<CrewTemplate>): Promise<CrewTemplate> =>
      ipcRenderer.invoke("crew-templates:create", data),
    delete: (id: string): Promise<boolean> => ipcRenderer.invoke("crew-templates:delete", id),
  },

  // ==================== Skill 管理 ====================
  skills: {
    list: (): Promise<Skill[]> => ipcRenderer.invoke("skills:list"),
    get: (id: string): Promise<Skill | null> => ipcRenderer.invoke("skills:get", id),
    byAgent: (agentId: string): Promise<Skill[]> => ipcRenderer.invoke("skills:by-agent", agentId),
    byDepartment: (deptId: string): Promise<Skill[]> => ipcRenderer.invoke("skills:by-department", deptId),
    create: (data: Partial<Skill>): Promise<Skill> =>
      ipcRenderer.invoke("skills:create", data),
    update: (id: string, data: Record<string, unknown>): Promise<Skill | null> =>
      ipcRenderer.invoke("skills:update", id, data),
    delete: (id: string): Promise<boolean> => ipcRenderer.invoke("skills:delete", id),
  },

  // ==================== 系统 ====================
  system: {
    getHomeDirectory: (): Promise<string> => ipcRenderer.invoke("system:get-home-directory"),
    openExternal: (url: string): Promise<boolean> => ipcRenderer.invoke("system:open-external", url),
    showItemInFolder: (filePath: string): Promise<boolean> =>
      ipcRenderer.invoke("system:show-item-in-folder", filePath),
  },

  // ==================== 事件监听 ====================
  on: (channel: string, callback: (...args: unknown[]) => void) => {
    const validChannels = [
      "claude:stream:chunk",
      "open-settings",
      "new-session",
    ]
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (_, ...args) => callback(...args))
    }
  },

  off: (channel: string, callback: (...args: unknown[]) => void) => {
    ipcRenderer.removeListener(channel, callback)
  },
}

// ==================== 暴露给渲染进程 ====================

contextBridge.exposeInMainWorld("electronAPI", api)

// 类型声明
export type ElectronAPI = typeof api
