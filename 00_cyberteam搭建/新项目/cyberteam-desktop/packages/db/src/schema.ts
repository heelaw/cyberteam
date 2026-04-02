export const schema = {
  companies: 'companies',
  departments: 'departments',
  agents: 'agents',
  agent_skills: 'agent_skills',
  conversations: 'conversations',
  conversation_participants: 'conversation_participants',
  messages: 'messages',
  skills: 'skills',
  playground_documents: 'playground_documents',
  review_records: 'review_records',
  templates: 'templates',
  roadmap_phases: 'roadmap_phases',
} as const

export const schemaStatements = {
  companies: `
    CREATE TABLE IF NOT EXISTS companies (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      avatar TEXT,
      description TEXT,
      theme TEXT,
      version TEXT,
      createdAt TEXT,
      updatedAt TEXT
    );
  `,
  departments: `
    CREATE TABLE IF NOT EXISTS departments (
      id TEXT PRIMARY KEY,
      companyId TEXT NOT NULL,
      parentId TEXT,
      name TEXT NOT NULL,
      type TEXT,
      color TEXT,
      description TEXT,
      createdAt TEXT,
      updatedAt TEXT
    );
  `,
  agents: `
    CREATE TABLE IF NOT EXISTS agents (
      id TEXT PRIMARY KEY,
      companyId TEXT NOT NULL,
      departmentId TEXT,
      name TEXT NOT NULL,
      title TEXT,
      avatar TEXT,
      bio TEXT,
      personality TEXT,
      status TEXT,
      isCEO INTEGER,
      isActive INTEGER,
      createdAt TEXT,
      updatedAt TEXT
    );
  `,
  agent_skills: `
    CREATE TABLE IF NOT EXISTS agent_skills (
      agentId TEXT NOT NULL,
      skillId TEXT NOT NULL,
      PRIMARY KEY (agentId, skillId)
    );
  `,
  conversations: `
    CREATE TABLE IF NOT EXISTS conversations (
      id TEXT PRIMARY KEY,
      companyId TEXT NOT NULL,
      type TEXT NOT NULL,
      title TEXT,
      departmentId TEXT,
      createdAt TEXT,
      updatedAt TEXT
    );
  `,
  conversation_participants: `
    CREATE TABLE IF NOT EXISTS conversation_participants (
      conversationId TEXT NOT NULL,
      participantId TEXT NOT NULL,
      participantType TEXT,
      PRIMARY KEY (conversationId, participantId)
    );
  `,
  messages: `
    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      conversationId TEXT NOT NULL,
      senderId TEXT,
      senderType TEXT,
      content TEXT NOT NULL,
      mentions TEXT,
      attachments TEXT,
      status TEXT,
      createdAt TEXT
    );
  `,
  skills: `
    CREATE TABLE IF NOT EXISTS skills (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      category TEXT,
      description TEXT,
      prompt TEXT,
      tools TEXT,
      version TEXT,
      createdAt TEXT,
      updatedAt TEXT
    );
  `,
  playground_documents: `
    CREATE TABLE IF NOT EXISTS playground_documents (
      id TEXT PRIMARY KEY,
      sourceConversationId TEXT,
      title TEXT NOT NULL,
      type TEXT,
      content TEXT,
      reviewStatus TEXT,
      version TEXT,
      createdAt TEXT,
      updatedAt TEXT
    );
  `,
  review_records: `
    CREATE TABLE IF NOT EXISTS review_records (
      id TEXT PRIMARY KEY,
      documentId TEXT NOT NULL,
      reviewerId TEXT,
      decision TEXT,
      comments TEXT,
      createdAt TEXT
    );
  `,
  templates: `
    CREATE TABLE IF NOT EXISTS templates (
      id TEXT PRIMARY KEY,
      type TEXT NOT NULL,
      name TEXT NOT NULL,
      description TEXT,
      payload TEXT,
      createdAt TEXT,
      updatedAt TEXT
    );
  `,
  roadmap_phases: `
    CREATE TABLE IF NOT EXISTS roadmap_phases (
      id TEXT PRIMARY KEY,
      companyId TEXT NOT NULL,
      name TEXT NOT NULL,
      status TEXT NOT NULL,
      goal TEXT NOT NULL,
      proof TEXT NOT NULL,
      question TEXT NOT NULL,
      sortOrder INTEGER,
      createdAt TEXT,
      updatedAt TEXT
    );
  `,
} as const

export type SchemaTableName = keyof typeof schema

export interface CompanyRow {
  id: string
  name: string
  avatar?: string
  description?: string
  theme?: string
  version?: string
  createdAt?: string
  updatedAt?: string
}

export interface DepartmentRow {
  id: string
  companyId: string
  parentId?: string
  name: string
  type?: string
  color?: string
  description?: string
  createdAt?: string
  updatedAt?: string
}

export interface AgentRow {
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
}

export interface SkillRow {
  id: string
  name: string
  category?: string
  description?: string
  prompt?: string
  tools?: string
  version?: string
  createdAt?: string
  updatedAt?: string
}

export interface ConversationRow {
  id: string
  companyId: string
  type: 'private' | 'group' | 'department'
  title?: string
  departmentId?: string
  createdAt?: string
  updatedAt?: string
}

export interface MessageRow {
  id: string
  conversationId: string
  senderId?: string
  senderType?: string
  content: string
  mentions?: string
  attachments?: string
  status?: string
  createdAt?: string
}

export interface PlaygroundDocumentRow {
  id: string
  sourceConversationId?: string
  title: string
  type?: string
  content: string
  reviewStatus?: string
  version?: string
  createdAt?: string
  updatedAt?: string
}

export interface ReviewRecordRow {
  id: string
  documentId: string
  reviewerId?: string
  decision?: string
  comments?: string
  createdAt?: string
}

export interface TemplateRow {
  id: string
  type: string
  name: string
  description?: string
  payload?: string
  createdAt?: string
  updatedAt?: string
}

export interface RoadmapPhaseRow {
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
}
