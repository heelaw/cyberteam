import type { SeedState } from '@cyberteam/core'
import type {
  AgentRow,
  CompanyRow,
  ConversationRow,
  DbClient,
  DepartmentRow,
  MessageRow,
  PlaygroundDocumentRow,
  ReviewRecordRow,
  RoadmapPhaseRow,
  SkillRow,
  TemplateRow,
} from './client'
import { createDbClient } from './client'
import type { TemplateMarketItem } from '@cyberteam/market'

type SeededTable =
  | 'companies'
  | 'departments'
  | 'agents'
  | 'agent_skills'
  | 'conversations'
  | 'conversation_participants'
  | 'messages'
  | 'skills'
  | 'playground_documents'
  | 'review_records'
  | 'templates'
  | 'roadmap_phases'

export interface DatabaseSnapshot {
  path: string
  counts: Record<SeededTable, number>
  company?: CompanyRow
  departments: DepartmentRow[]
  agents: AgentRow[]
  conversations: ConversationRow[]
  messagesByConversation: Record<string, MessageRow[]>
  skills: SkillRow[]
  playgroundDocuments: PlaygroundDocumentRow[]
  reviewRecords: ReviewRecordRow[]
  templates: TemplateRow[]
  roadmapPhases: RoadmapPhaseRow[]
}

export interface CyberTeamDatabase {
  client: DbClient
  path: string
  seededTables: SeededTable[]
  snapshot(): DatabaseSnapshot
  addMessage(conversationId: string, message: {
    id: string
    senderId?: string
    senderType?: string
    content: string
    mentions?: string
    attachments?: string
    status?: string
    createdAt?: string
  }): number
  updateReviewRecord(documentId: string, patch: {
    decision?: string
    comments?: string
  }): number
  upsertRoadmapPhase(phase: RoadmapPhaseRow): number
  close(): void
}

function now() {
  return new Date().toISOString()
}

function seedRowsIfEmpty<T extends object>(
  client: DbClient,
  table: SeededTable,
  rows: T[],
  seededTables: SeededTable[],
) {
  if (rows.length === 0) {
    return
  }

  if (client.query(table).length > 0) {
    return
  }

  for (const row of rows) {
    client.insert(table, row)
  }

  seededTables.push(table)
}

function buildCounts(client: DbClient): Record<SeededTable, number> {
  return {
    companies: client.query('companies').length,
    departments: client.query('departments').length,
    agents: client.query('agents').length,
    agent_skills: client.query('agent_skills').length,
    conversations: client.query('conversations').length,
    conversation_participants: client.query('conversation_participants').length,
    messages: client.query('messages').length,
    skills: client.query('skills').length,
    playground_documents: client.query('playground_documents').length,
    review_records: client.query('review_records').length,
    templates: client.query('templates').length,
    roadmap_phases: client.query('roadmap_phases').length,
  }
}

function readSnapshot(client: DbClient): DatabaseSnapshot {
  const company = client.get<CompanyRow>('companies')
  const companyId = company?.id
  const conversations = companyId ? client.query<ConversationRow>('conversations', { companyId }) : client.query<ConversationRow>('conversations')
  const departments = companyId ? client.query<DepartmentRow>('departments', { companyId }) : client.query<DepartmentRow>('departments')
  const agents = companyId ? client.query<AgentRow>('agents', { companyId }) : client.query<AgentRow>('agents')
  const skills = client.query<SkillRow>('skills')
  const playgroundDocuments = client.query<PlaygroundDocumentRow>('playground_documents')
  const reviewRecords = client.query<ReviewRecordRow>('review_records')
  const templates = client.query<TemplateRow>('templates')
  const roadmapPhases = client.query<RoadmapPhaseRow>('roadmap_phases')

  const messagesByConversation = Object.fromEntries(
    conversations.map((conversation) => [
      conversation.id,
      client.query<MessageRow>('messages', { conversationId: conversation.id }),
    ]),
  )

  return {
    path: client.path,
    counts: buildCounts(client),
    company,
    departments,
    agents,
    conversations,
    messagesByConversation,
    skills,
    playgroundDocuments,
    reviewRecords,
    templates,
    roadmapPhases,
  }
}

function seedCompany(client: DbClient, state: SeedState, seededTables: SeededTable[]) {
  seedRowsIfEmpty(client, 'companies', [state.company as CompanyRow], seededTables)
}

function seedOrganization(client: DbClient, state: SeedState, seededTables: SeededTable[]) {
  const departments: DepartmentRow[] = state.organization.departments.map((department) => ({
    id: department.id,
    companyId: department.companyId,
    parentId: department.parentId,
    name: department.name,
    type: department.type,
    color: department.color,
    description: department.description,
    createdAt: department.createdAt,
    updatedAt: department.updatedAt,
  }))

  const agents: AgentRow[] = state.organization.agents.map((agent) => ({
    id: agent.id,
    companyId: agent.companyId,
    departmentId: agent.departmentId,
    name: agent.name,
    title: agent.title,
    avatar: agent.avatar,
    bio: agent.bio,
    personality: agent.personality,
    status: agent.status,
    isCEO: Number(agent.isCEO),
    isActive: Number(agent.isActive),
    createdAt: agent.createdAt,
    updatedAt: agent.updatedAt,
  }))

  seedRowsIfEmpty(client, 'departments', departments, seededTables)
  seedRowsIfEmpty(client, 'agents', agents, seededTables)

  if (client.query('agent_skills').length === 0) {
    for (const agent of agents) {
      if (agent.isCEO) {
        client.insert('agent_skills', { agentId: agent.id, skillId: 'ceo-review' })
      }
    }
    if (agents.length > 0) {
      seededTables.push('agent_skills')
    }
  }
}

function seedConversations(client: DbClient, state: SeedState, seededTables: SeededTable[]) {
  const conversations: ConversationRow[] = state.conversations.map((conversation) => ({
    id: conversation.id,
    companyId: state.company.id,
    type: conversation.type,
    title: conversation.title,
    departmentId: undefined,
    createdAt: conversation.createdAt,
    updatedAt: conversation.updatedAt,
  }))

  seedRowsIfEmpty(client, 'conversations', conversations, seededTables)

  if (client.query('conversation_participants').length === 0) {
    for (const conversation of state.conversations) {
      for (const participantId of conversation.participantIds ?? []) {
        client.insert('conversation_participants', {
          conversationId: conversation.id,
          participantId,
          participantType: 'agent',
        })
      }
    }

    if (conversations.length > 0) {
      seededTables.push('conversation_participants')
    }
  }

  if (client.query('messages').length === 0) {
    for (const [conversationId, messages] of Object.entries(state.messagesByConversation)) {
      for (const message of messages) {
        client.insert('messages', {
          id: message.id,
          conversationId,
          senderId: message.senderId,
          senderType: message.senderId ? 'agent' : 'system',
          content: message.content,
          mentions: JSON.stringify(message.mentions ?? []),
          attachments: JSON.stringify([]),
          status: message.status,
          createdAt: message.createdAt,
        })
      }
    }

    if (Object.keys(state.messagesByConversation).length > 0) {
      seededTables.push('messages')
    }
  }
}

function seedSkills(client: DbClient, state: SeedState, seededTables: SeededTable[]) {
  const skills: SkillRow[] = state.skills.map((skill) => ({
    id: skill.id,
    name: skill.name,
    category: skill.category,
    description: skill.description,
    prompt: skill.prompt,
    tools: JSON.stringify(skill.tools ?? []),
    version: skill.version,
    createdAt: now(),
    updatedAt: now(),
  }))

  seedRowsIfEmpty(client, 'skills', skills, seededTables)
}

function seedPlayground(client: DbClient, state: SeedState, seededTables: SeededTable[]) {
  const document: PlaygroundDocumentRow = {
    id: state.playgroundDocument.id,
    sourceConversationId: state.groupConversation.id,
    title: state.playgroundDocument.title,
    type: state.playgroundDocument.type,
    content: state.playgroundDocument.content,
    reviewStatus: state.playgroundDocument.reviewStatus,
    version: state.playgroundDocument.version,
    createdAt: now(),
    updatedAt: now(),
  }

  seedRowsIfEmpty(client, 'playground_documents', [document], seededTables)

  if (client.query('review_records').length === 0) {
    client.insert('review_records', {
      id: `${state.playgroundDocument.id}_review`,
      documentId: state.playgroundDocument.id,
      reviewerId: state.organization.agents[0]?.id,
      decision: state.playgroundReview.status,
      comments: JSON.stringify(state.playgroundReview.notes ?? []),
      createdAt: now(),
    })
    seededTables.push('review_records')
  }
}

function seedTemplates(client: DbClient, state: SeedState, seededTables: SeededTable[]) {
  const templates: TemplateRow[] = state.market.templates.map((template: TemplateMarketItem) => ({
    id: template.id,
    type: 'market-template',
    name: template.name,
    description: undefined,
    payload: JSON.stringify(template),
    createdAt: now(),
    updatedAt: now(),
  }))

  seedRowsIfEmpty(client, 'templates', templates, seededTables)
}

function seedRoadmap(client: DbClient, state: SeedState, seededTables: SeededTable[]) {
  const phases: RoadmapPhaseRow[] = (state.roadmap ?? []).map((phase, index) => ({
    id: phase.id,
    companyId: state.company.id,
    name: phase.name,
    status: phase.status,
    goal: phase.goal,
    proof: phase.proof,
    question: phase.question,
    sortOrder: index,
    createdAt: now(),
    updatedAt: now(),
  }))

  seedRowsIfEmpty(client, 'roadmap_phases', phases, seededTables)
}

export function createCyberTeamDatabase(dbPath: string, state: SeedState): CyberTeamDatabase {
  const client = createDbClient(dbPath)
  const seededTables: SeededTable[] = []

  seedCompany(client, state, seededTables)
  seedOrganization(client, state, seededTables)
  seedConversations(client, state, seededTables)
  seedSkills(client, state, seededTables)
  seedPlayground(client, state, seededTables)
  seedTemplates(client, state, seededTables)
  seedRoadmap(client, state, seededTables)

  return {
    client,
    path: dbPath,
    seededTables,
    addMessage(conversationId, message) {
      return client.insert('messages', {
        conversationId,
        ...message,
      }) ? 1 : 0
    },
    updateReviewRecord(documentId, patch) {
      return client.update('review_records', { documentId }, patch)
    },
    upsertRoadmapPhase(phase) {
      return client.insert('roadmap_phases', phase) ? 1 : 0
    },
    snapshot() {
      return readSnapshot(client)
    },
    close() {
      client.close()
    },
  }
}
