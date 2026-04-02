// ==================== Electron API 类型定义 ====================

export interface ChatSession {
  id: string
  title: string
  working_directory: string
  provider_id: string
  model: string
  system_prompt: string
  conversation_type: 'single' | 'group' | 'department'
  department_id: string | null
  project_id: string | null
  review_status: 'pending' | 'approved' | 'rejected'
  review_notes: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  sender_id: string
  sender_name: string
  sender_avatar: string
  metadata: string // JSON string
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
  status: 'active' | 'archived'
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
  role: 'ceo' | 'manager' | 'expert' | 'executor'
  department_id: string
  description: string
  soul_content: string
  status: 'online' | 'offline' | 'busy'
  capabilities: string // JSON array string
  config: string // JSON object string
  created_at: string
}

export interface MeetingMinutes {
  id: string
  project_id: string
  meeting_type: 'ceo_coo' | 'strategy' | 'risk' | 'ceo_report'
  title: string
  content: string
  review_status: 'pending' | 'approved' | 'rejected'
  attachments: string // JSON array string
  created_at: string
}

export interface CrewTemplate {
  id: string
  name: string
  description: string
  members: string // JSON array string
  departments: string // JSON array string
  is_preset: number
  created_at: string
}

export interface DirEntry {
  name: string
  path: string
}

export interface BrowseResult {
  current: string
  parent: string | null
  directories: DirEntry[]
  error: string | null
}

// ==================== ElectronAPI 接口 ====================

export interface ElectronAPI {
  chat: {
    sessions: {
      list: () => Promise<ChatSession[]>
      get: (id: string) => Promise<ChatSession | null>
      create: (data: Partial<ChatSession>) => Promise<ChatSession>
      update: (id: string, data: Record<string, unknown>) => Promise<ChatSession | null>
      delete: (id: string) => Promise<boolean>
    }
    messages: {
      list: (sessionId: string) => Promise<Message[]>
      create: (data: Partial<Message>) => Promise<Message>
    }
  }

  claude: {
    send: (data: {
      session_id: string
      message: string
      working_directory: string
      provider_id?: string
      model?: string
      system_prompt?: string
    }) => Promise<{ content: string; messageId: string }>

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
    ) => Promise<{ messageId: string }>
  }

  files: {
    browse: (dirPath: string) => Promise<BrowseResult>
    validateDirectory: (dirPath: string) => Promise<boolean>
    selectDirectory: () => Promise<string | null>
  }

  providers: {
    list: () => Promise<ApiProvider[]>
    get: (id: string) => Promise<ApiProvider | null>
    create: (data: Partial<ApiProvider>) => Promise<ApiProvider>
    update: (id: string, data: Record<string, unknown>) => Promise<ApiProvider | null>
    delete: (id: string) => Promise<boolean>
    test: (id: string) => Promise<{ success: boolean; error?: string }>
  }

  projects: {
    list: () => Promise<Project[]>
    get: (id: string) => Promise<Project | null>
    create: (data: Partial<Project>) => Promise<Project>
    update: (id: string, data: Record<string, unknown>) => Promise<Project | null>
    delete: (id: string) => Promise<boolean>
  }

  departments: {
    list: () => Promise<Department[]>
    create: (data: Partial<Department>) => Promise<Department>
    update: (id: string, data: Record<string, unknown>) => Promise<Department | null>
    delete: (id: string) => Promise<boolean>
  }

  agents: {
    list: () => Promise<Agent[]>
    get: (id: string) => Promise<Agent | null>
    create: (data: Partial<Agent>) => Promise<Agent>
    update: (id: string, data: Record<string, unknown>) => Promise<Agent | null>
    delete: (id: string) => Promise<boolean>
  }

  meetingMinutes: {
    list: (projectId?: string) => Promise<MeetingMinutes[]>
    create: (data: Partial<MeetingMinutes>) => Promise<MeetingMinutes>
    update: (id: string, data: Record<string, unknown>) => Promise<MeetingMinutes | null>
  }

  crewTemplates: {
    list: () => Promise<CrewTemplate[]>
    create: (data: Partial<CrewTemplate>) => Promise<CrewTemplate>
    delete: (id: string) => Promise<boolean>
  }

  system: {
    getHomeDirectory: () => Promise<string>
    openExternal: (url: string) => Promise<boolean>
    showItemInFolder: (filePath: string) => Promise<boolean>
  }

  on: (channel: string, callback: (...args: unknown[]) => void) => void
  off: (channel: string, callback: (...args: unknown[]) => void) => void
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

export {}
