'use client'

export interface RuntimeDatabaseSnapshot {
  path: string
  counts: Record<string, number>
  company?: {
    id: string
    name: string
    avatar?: string
    description?: string
    theme?: string
    version?: string
    createdAt?: string
    updatedAt?: string
  }
  departments: Array<{
    id: string
    companyId: string
    parentId?: string
    name: string
    type?: string
    color?: string
    description?: string
    createdAt?: string
    updatedAt?: string
  }>
  agents: Array<{
    id: string
    companyId: string
    departmentId?: string
    name: string
    title?: string
    avatar?: string
    bio?: string
    personality?: string
    status?: string
    isCEO?: number
    isActive?: number
    createdAt?: string
    updatedAt?: string
  }>
  conversations: Array<{
    id: string
    companyId: string
    type: 'private' | 'group' | 'department'
    title?: string
    departmentId?: string
    createdAt?: string
    updatedAt?: string
  }>
  messagesByConversation: Record<
    string,
    Array<{
      id: string
      conversationId: string
      senderId?: string
      senderType?: string
      content: string
      mentions?: string
      attachments?: string
      status?: string
      createdAt?: string
    }>
  >
  skills: Array<{
    id: string
    name: string
    category?: string
    description?: string
    prompt?: string
    tools?: string
    version?: string
    createdAt?: string
    updatedAt?: string
  }>
  playgroundDocuments: Array<{
    id: string
    sourceConversationId?: string
    title: string
    type?: string
    content?: string
    reviewStatus?: string
    version?: string
    createdAt?: string
    updatedAt?: string
  }>
  reviewRecords: Array<{
    id: string
    documentId: string
    reviewerId?: string
    decision?: string
    comments?: string
    createdAt?: string
  }>
  templates: Array<{
    id: string
    type: string
    name: string
    description?: string
    payload?: string
    createdAt?: string
    updatedAt?: string
  }>
  roadmapPhases: Array<{
    id: string
    companyId: string
    name: string
    status: 'done' | 'in-progress' | 'next' | 'planned'
    goal: string
    proof: string
    question: string
    sortOrder?: number
    createdAt?: string
    updatedAt?: string
  }>
}

export interface RuntimeState {
  platform: string
  version: string
  isPackaged: boolean
  userData: string
  home: string
  database?: RuntimeDatabaseSnapshot
  claude: {
    installed: boolean
    command: string | null
    status: 'detected' | 'missing'
  }
}

export interface AppPaths {
  appPath: string
  userData: string
  home: string
  databasePath: string
}

export interface CyberTeamApi {
  app: {
    getState: () => Promise<RuntimeState>
    getPaths: () => Promise<AppPaths>
  }
  chat: {
    sendMessage: (conversationId: string, message: {
      content: string
      senderId?: string
      mentions?: Array<{ agentId: string; agentName: string; agentTitle?: string }>
    }) => Promise<number>
  }
  playground: {
    updateReview: (documentId: string, patch: {
      decision?: string
      comments?: string
    }) => Promise<number>
  }
  roadmap: {
    upsertPhase: (phase: {
      id: string
      companyId: string
      name: string
      status: 'done' | 'in-progress' | 'next' | 'planned'
      goal: string
      proof: string
      question: string
      sortOrder?: number
      createdAt?: string
      updatedAt?: string
    }) => Promise<number>
  }
  claude: {
    detect: () => Promise<boolean>
    ping: () => Promise<unknown>
    send: (prompt: string) => Promise<string>
    stream: (prompt: string, onChunk: (chunk: string) => void) => Promise<string>
  }
  system: {
    getHomeDirectory: () => Promise<string>
    openExternal: (url: string) => Promise<unknown>
    showItemInFolder: (filePath: string) => Promise<unknown>
  }
}

function getInjectedApi() {
  return (window as Window & { cyberteam?: CyberTeamApi; electronAPI?: CyberTeamApi }).cyberteam
    ?? (window as Window & { cyberteam?: CyberTeamApi; electronAPI?: CyberTeamApi }).electronAPI
}

export function getCyberTeamApi() {
  if (typeof window === 'undefined') {
    return undefined
  }

  return getInjectedApi()
}

export async function loadRuntimeState() {
  const api = getCyberTeamApi()
  if (!api?.app?.getState) {
    return null
  }

  try {
    return await api.app.getState()
  } catch (error) {
    console.warn('[CyberTeam] Failed to load runtime state', error)
    return null
  }
}
