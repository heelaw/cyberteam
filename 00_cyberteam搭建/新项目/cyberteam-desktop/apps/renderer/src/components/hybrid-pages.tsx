'use client'

import { useEffect, useRef, useState } from 'react'
import type { SeedState } from '../lib/seed'
import { getCyberTeamApi, loadRuntimeState, type RuntimeState } from '../lib/runtime-api'

type MessageMention = {
  agentId: string
  agentName: string
  agentTitle?: string
}

type RoadmapStatus = 'done' | 'in-progress' | 'next' | 'planned'

type RoadmapDraft = {
  status: RoadmapStatus
  goal: string
  proof: string
  question: string
  sortOrder: number
}

type RoadmapSourcePhase = {
  id: string
  status: RoadmapStatus
  goal: string
  proof: string
  question: string
  sortOrder?: number
}

type ReviewDraft = {
  decision: string
  comments: string
}

function toReviewDraftFromSeed(review: { status: string; notes: string[] }): ReviewDraft {
  return {
    decision: review.status,
    comments: review.notes.join('；'),
  }
}

const roadmapStatuses: RoadmapStatus[] = ['done', 'in-progress', 'next', 'planned']

function toRoadmapDraft(phase: RoadmapSourcePhase): RoadmapDraft {
  return {
    status: phase.status,
    goal: phase.goal,
    proof: phase.proof,
    question: phase.question,
    sortOrder: phase.sortOrder ?? 0,
  }
}

function useRuntimeStateWithRefresh() {
  const [state, setState] = useState<RuntimeState | null>(null)
  const requestIdRef = useRef(0)
  const aliveRef = useRef(true)

  async function refresh() {
    const requestId = ++requestIdRef.current
    const nextState = await loadRuntimeState()

    if (aliveRef.current && requestId === requestIdRef.current) {
      setState(nextState)
    }

    return nextState
  }

  useEffect(() => {
    const timer = window.setInterval(() => {
      void refresh()
    }, 5000)

    void refresh()

    return () => {
      aliveRef.current = false
      window.clearInterval(timer)
    }
  }, [])

  return { state, refresh }
}

function parseMentions(value: unknown): MessageMention[] {
  if (Array.isArray(value)) {
    return value as MessageMention[]
  }

  if (typeof value !== 'string' || !value) {
    return []
  }

  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? (parsed as MessageMention[]) : []
  } catch {
    return []
  }
}

function parseNotes(value: unknown) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item))
  }

  if (typeof value !== 'string' || !value) {
    return []
  }

  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? parsed.map((item) => String(item)) : [value]
  } catch {
    return [value]
  }
}

function getDatabaseCounts(runtime: RuntimeState | null) {
  return runtime?.database?.counts ?? {}
}

function resolveRoadmap(seed: SeedState, runtime: RuntimeState | null) {
  const roadmap = runtime?.database?.roadmapPhases ?? []

  if (runtime) {
    return [...roadmap].sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
  }

  return seed.roadmap
}

function resolveConversation(seed: SeedState, runtime: RuntimeState | null, conversationId?: string) {
  if (runtime) {
    const runtimeConversations = runtime.database?.conversations ?? []

    if (!runtimeConversations.length) {
      return undefined
    }

    if (conversationId) {
      return runtimeConversations.find((conversation) => conversation.id === conversationId)
    }

    return runtimeConversations[0]
  }

  if (conversationId) {
    return seed.conversations.find((conversation) => conversation.id === conversationId) ?? seed.conversations[0]
  }

  return seed.conversations[0]
}

function resolveAgentName(seed: SeedState, runtime: RuntimeState | null, agentId?: string) {
  if (!agentId) {
    return 'System'
  }

  return runtime?.database?.agents.find((agent) => agent.id === agentId)?.name
    ?? seed.organization.agents.find((agent) => agent.id === agentId)?.name
    ?? 'System'
}

function getSeedConversationParticipantCount(seed: SeedState, conversationId: string) {
  return seed.conversations.find((conversation) => conversation.id === conversationId)?.participantIds?.length ?? 0
}

function resolveMessages(seed: SeedState, runtime: RuntimeState | null, conversationId: string) {
  const runtimeMessages = runtime?.database?.messagesByConversation?.[conversationId] ?? []

  if (runtime) {
    return runtimeMessages.map((message) => ({
      id: message.id,
      content: message.content,
      senderId: message.senderId,
      createdAt: message.createdAt ?? '',
      mentions: parseMentions(message.mentions),
    }))
  }

  return seed.messagesByConversation[conversationId] ?? []
}

function resolveActiveConversation(seed: SeedState, runtime: RuntimeState | null) {
  const runtimeConversations = runtime?.database?.conversations

  if (runtime) {
    if (!runtimeConversations?.length) {
      return undefined
    }

    return runtimeConversations.find((conversation) => conversation.type !== 'private')
      ?? runtimeConversations[0]
  }

  // Fall back to seed: prefer non-private conversation, then first available
  return seed.conversations.find((conversation) => conversation.type !== 'private')
    ?? seed.conversations[0]
}

function buildRoadmapDrafts(phases: ReturnType<typeof resolveRoadmap>) {
  return Object.fromEntries(phases.map((phase) => [phase.id, toRoadmapDraft(phase)])) as Record<string, RoadmapDraft>
}

function toReviewDraft(review: { decision?: string; comments?: string }): ReviewDraft {
  return {
    decision: review.decision ?? 'pending',
    comments: parseNotes(review.comments).join('；'),
  }
}

export function DashboardView({ seed }: { seed: SeedState }) {
  const { state: runtime, refresh } = useRuntimeStateWithRefresh()
  const counts = getDatabaseCounts(runtime)
  const company = runtime ? runtime.database?.company : seed.company
  const departments = runtime ? runtime.database?.departments ?? [] : seed.organization.departments
  const agents = runtime ? runtime.database?.agents ?? [] : seed.organization.agents
  const roadmap = resolveRoadmap(seed, runtime)
  const roadmapById = new Map(roadmap.map((phase) => [phase.id, phase]))
  const [roadmapDrafts, setRoadmapDrafts] = useState<Record<string, RoadmapDraft>>(() => buildRoadmapDrafts(roadmap))
  const [roadmapSavingId, setRoadmapSavingId] = useState('')
  const [roadmapStatusMessage, setRoadmapStatusMessage] = useState('')
  const dirtyRoadmapIdsRef = useRef(new Set<string>())
  const playgroundDocument = runtime?.database?.playgroundDocuments?.[0]
    ? {
      ...runtime.database.playgroundDocuments[0],
      content: runtime.database.playgroundDocuments[0].content ?? '',
    }
    : seed.playgroundDocument
  const playgroundExport = runtime?.database?.playgroundDocuments?.[0]
    ? runtime.database.playgroundDocuments[0].content ?? '运行态尚无导出内容。'
    : seed.playgroundExport
  const playgroundReview = runtime?.database?.reviewRecords?.[0]
    ? {
      status: runtime.database.reviewRecords[0].decision ?? 'pending',
      notes: parseNotes(runtime.database.reviewRecords[0].comments),
    }
    : seed.playgroundReview
  const companyName = company?.name ?? (runtime ? '公司未初始化' : seed.company.name)
  const companyVersion = company?.version ?? (runtime ? '—' : seed.company.version)
  const companyDescription = company?.description ?? (runtime ? '运行态尚未写入公司信息' : seed.company.description)

  const metrics = runtime
    ? [
      { label: '公司', value: String(counts.companies ?? 0), note: companyName },
      { label: '部门', value: String(counts.departments ?? departments.length), note: '数据库中的组织结构' },
      { label: 'Agent', value: String(counts.agents ?? agents.length), note: '可协作节点已加载' },
      { label: '会话', value: String(counts.conversations ?? seed.conversations.length), note: '对话线程已持久化' },
      { label: 'Skill', value: String(counts.skills ?? seed.skills.length), note: '能力仓库已入库' },
      { label: 'Claude Code', value: runtime.claude.installed ? '已检测' : '未检测', note: runtime.claude.command ?? '本地执行引擎' },
    ]
    : seed.metrics

  useEffect(() => {
    setRoadmapDrafts((current) => {
      const next = buildRoadmapDrafts(roadmap)
      const merged: Record<string, RoadmapDraft> = {}

      for (const [phaseId, draft] of Object.entries(next)) {
        merged[phaseId] = dirtyRoadmapIdsRef.current.has(phaseId) && current[phaseId]
          ? current[phaseId]
          : draft
      }

      for (const phaseId of Object.keys(current)) {
        if (!merged[phaseId]) {
          dirtyRoadmapIdsRef.current.delete(phaseId)
        }
      }

      return merged
    })
  }, [roadmap])

  function updateRoadmapDraft(phaseId: string, patch: Partial<RoadmapDraft>) {
    dirtyRoadmapIdsRef.current.add(phaseId)
    setRoadmapDrafts((current) => {
      const source = roadmapById.get(phaseId)
      const base = current[phaseId] ?? (source ? toRoadmapDraft(source) : undefined)

      if (!base) {
        return current
      }

      return {
        ...current,
        [phaseId]: {
          ...base,
          ...patch,
        },
      }
    })
  }

  async function handleSaveRoadmapPhase(phaseId: string) {
    const api = getCyberTeamApi()
    const draft = roadmapDrafts[phaseId]
    const source = roadmap.find((phase) => phase.id === phaseId)

    if (!api?.roadmap?.upsertPhase || !draft || !source) {
      return
    }

    setRoadmapSavingId(phaseId)
    try {
      await api.roadmap.upsertPhase({
        id: source.id,
        companyId: runtime?.database?.company?.id ?? seed.company.id,
        name: source.name,
        status: draft.status,
        goal: draft.goal,
        proof: draft.proof,
        question: draft.question,
        sortOrder: draft.sortOrder,
        createdAt: source.createdAt,
        updatedAt: new Date().toISOString(),
      })
      await refresh()
      dirtyRoadmapIdsRef.current.delete(phaseId)
      setRoadmapStatusMessage('路线图已写入 SQLite 并刷新运行态')
    } catch (error) {
      console.error('[CyberTeam] Failed to save roadmap phase', error)
      setRoadmapStatusMessage('路线图保存失败，请检查运行态是否可写')
    } finally {
      setRoadmapSavingId('')
    }
  }

  return (
    <article className="sectionStack">
      <section className="hero">
        <div className="heroHeader">
          <div>
            <p className="eyebrow">Dashboard</p>
            <h2 className="heroTitle">CyberTeam 已经从设想进入最小闭环。</h2>
          </div>
          <div className="chip">{runtime ? 'Live runtime' : 'Bootstrap preview'}</div>
        </div>
        <p className="heroLead">
          这个版本先验证四件事：公司能否组织起来，Agent 能否协作，聊天能否承载任务，Playground 能否把讨论沉淀成交付物。
        </p>
        <div className="grid metrics">
          {metrics.map((metric) => (
            <div key={metric.label} className="metric">
              <div className="statusLabel">{metric.label}</div>
              <div className="metricValue">{metric.value}</div>
              <div className="metricNote">{metric.note}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <h3 className="sectionTitle">第一性原理路线图</h3>
        <div className="subtle" style={{ marginBottom: 12 }}>{roadmapStatusMessage || '编辑后会直接写回 SQLite，并在保存后刷新运行态。'}</div>
        <div className="sectionStack">
          {roadmap.map((phase) => {
            const draft = roadmapDrafts[phase.id]
            return (
            <div key={phase.id} className="panelNote" style={{ display: 'grid', gap: 12 }}>
              <div className="cardHeader">
                <div style={{ display: 'grid', gap: 4 }}>
                  <strong>{phase.name}</strong>
                  <span className="subtle">{phase.question}</span>
                </div>
                <span className="chip">{draft?.status ?? phase.status}</span>
              </div>
              <div className="grid two" style={{ gap: 12 }}>
                <label className="settingsTitle" style={{ display: 'grid', gap: 6 }}>
                  Status
                  <select
                    value={roadmapDrafts[phase.id]?.status ?? phase.status}
                  onChange={(event) => updateRoadmapDraft(phase.id, { status: event.target.value as RoadmapStatus })}
                    style={{ borderRadius: 14, padding: 10, background: 'rgba(255,255,255,0.04)', color: 'inherit', border: '1px solid rgba(148,163,184,0.2)' }}
                  >
                    {roadmapStatuses.map((status) => <option key={status} value={status}>{status}</option>)}
                  </select>
                </label>
                <label className="settingsTitle" style={{ display: 'grid', gap: 6 }}>
                  Sort Order
                  <input
                    type="number"
                    value={roadmapDrafts[phase.id]?.sortOrder ?? phase.sortOrder ?? 0}
                  onChange={(event) => updateRoadmapDraft(phase.id, { sortOrder: Number(event.target.value) })}
                    style={{ borderRadius: 14, padding: 10, background: 'rgba(255,255,255,0.04)', color: 'inherit', border: '1px solid rgba(148,163,184,0.2)' }}
                  />
                </label>
              </div>
              <label className="settingsTitle" style={{ display: 'grid', gap: 6 }}>
                Goal
                <input
                  value={roadmapDrafts[phase.id]?.goal ?? phase.goal}
                  onChange={(event) => updateRoadmapDraft(phase.id, { goal: event.target.value })}
                  style={{ borderRadius: 14, padding: 10, background: 'rgba(255,255,255,0.04)', color: 'inherit', border: '1px solid rgba(148,163,184,0.2)' }}
                />
              </label>
              <label className="settingsTitle" style={{ display: 'grid', gap: 6 }}>
                Proof
                <textarea
                  value={roadmapDrafts[phase.id]?.proof ?? phase.proof}
                  onChange={(event) => updateRoadmapDraft(phase.id, { proof: event.target.value })}
                  rows={2}
                  style={{ borderRadius: 14, padding: 10, background: 'rgba(255,255,255,0.04)', color: 'inherit', border: '1px solid rgba(148,163,184,0.2)' }}
                />
              </label>
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => void handleSaveRoadmapPhase(phase.id)}
                  disabled={roadmapSavingId === phase.id}
                  style={{ borderRadius: 999, padding: '10px 16px', background: 'linear-gradient(135deg, #77c6ff, #7cf0c8)', border: 0, color: '#06101c', fontWeight: 700 }}
                >
                  {roadmapSavingId === phase.id ? 'Saving...' : 'Save Phase'}
                </button>
              </div>
            </div>
            )
          })}
        </div>
      </section>

      <section className="panel">
        <h3 className="sectionTitle">运行时状态</h3>
        <div className="timeline">
          <div className="timelineItem">
            <span>Company</span>
            <span className="subtle">{companyName} · {companyVersion}</span>
          </div>
          <div className="timelineItem">
            <span>Database</span>
            <span className="subtle">{runtime?.database?.path ?? 'SQLite 未加载'}</span>
          </div>
          <div className="timelineItem">
            <span>Departments</span>
            <span className="subtle">{departments.length}</span>
          </div>
          <div className="timelineItem">
            <span>Agents</span>
            <span className="subtle">{agents.length}</span>
          </div>
        </div>
      </section>

      <section className="grid two">
        <div className="panel">
          <h3 className="sectionTitle">当前组织</h3>
          <div className="sectionStack">
            <div>
              <div className="cardHeader">
                <strong>{companyName}</strong>
                <span className="pill">{companyVersion}</span>
              </div>
              <div className="cardMeta">{companyDescription}</div>
            </div>
            <div className="timeline">
              {departments.length ? departments.map((department) => (
                <div key={department.id} className="timelineItem">
                  <span>{department.name}</span>
                  <span className="subtle">{department.type ?? 'custom'}</span>
                </div>
              )) : <div className="panelNote">运行态还没有部门数据。</div>}
            </div>
          </div>
        </div>

        <div className="panel">
          <h3 className="sectionTitle">核心 Agent</h3>
          <div className="nodeList">
            {agents.length ? agents.map((agent) => (
              <div key={agent.id} className="nodeCard">
                <div className="nodeHeader">
                  <strong>{agent.name}</strong>
                  <span className="tag">{agent.title}</span>
                </div>
                <div className="nodeMeta">{agent.bio || agent.personality || '已接入数据库'}</div>
              </div>
            )) : <div className="panelNote">运行态还没有 Agent 数据。</div>}
          </div>
        </div>
      </section>

      <section className="grid two">
        <div className="panel">
          <h3 className="sectionTitle">协作路线</h3>
          <div className="timeline">
            {(runtime ? ['数据库启动', '组织同步', '会话持久化', '实时桥接'] : seed.timeline).map((item, index) => (
              <div key={item} className="timelineItem">
                <span>{String(index + 1).padStart(2, '0')} · {item}</span>
                <span className="subtle">ready</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <h3 className="sectionTitle">交付预览</h3>
          <div className="footerGrid">
            <div>
              <div className="cardMeta">Playground Review</div>
              <div className="cardHeader">
                <strong>{playgroundDocument.title}</strong>
                <span className="chip">{playgroundReview.status}</span>
              </div>
              <div className="panelNote">{playgroundDocument.content}</div>
            </div>
            <div className="docPreview">{playgroundExport}</div>
          </div>
        </div>
      </section>
    </article>
  )
}

export function ChatView({ seed }: { seed: SeedState }) {
  const { state: runtime, refresh } = useRuntimeStateWithRefresh()
  const [draftMessage, setDraftMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')
  const activeConversation = resolveActiveConversation(seed, runtime)
  const activeConversationId = activeConversation?.id
  const conversations = runtime ? runtime.database?.conversations ?? [] : seed.conversations
  const activeMessages = activeConversationId && (runtime ? conversations.length > 0 : true)
    ? resolveMessages(seed, runtime, activeConversationId)
    : []
  const showRuntimeEmptyState = Boolean(runtime && (!activeConversationId || conversations.length === 0))

  async function handleSendMessage() {
    const content = draftMessage.trim()
    if (!content) {
      return
    }

    const api = getCyberTeamApi()
    if (!api?.chat?.sendMessage) {
      return
    }

    if (!activeConversationId || (runtime && conversations.length === 0)) {
      setStatusMessage('当前运行态没有可写入的会话')
      return
    }

    const senderId = runtime?.database?.agents?.[0]?.id ?? seed.organization.agents[0]?.id

    setSending(true)
    try {
      await api.chat.sendMessage(activeConversationId, {
        content,
        senderId,
        mentions: [],
      })

      setDraftMessage('')
      setStatusMessage('消息已写入 SQLite')
      await refresh()
    } finally {
      setSending(false)
    }
  }

  return (
    <section className="grid two">
      <div className="panel">
        <h3 className="sectionTitle">会话列表</h3>
        <div className="conversationList">
          {conversations.map((conversation) => (
            <div key={conversation.id} className={`conversationItem ${activeConversationId === conversation.id ? 'active' : ''}`}>
              <div className="conversationTitle">{conversation.title}</div>
              <div className="conversationMeta">
                {conversation.type} · {runtime ? 'live' : `${seed.conversations.find((item) => item.id === conversation.id)?.participantIds?.length ?? 0} participants`}
              </div>
            </div>
          ))}
        </div>
      </div>

      {showRuntimeEmptyState ? (
        <div className="panel">
          <h3 className="sectionTitle">Active Thread</h3>
          <div className="panelNote">当前运行态没有会话记录，先检查 SQLite 是否已完成 bootstrap。</div>
        </div>
      ) : activeConversation ? (
        <div className="sectionStack">
          <div className="threadCard">
            <div className="cardHeader">
              <div>
                <div className="statusLabel">Active Thread</div>
                <h3 className="sectionTitle" style={{ marginTop: 8 }}>{activeConversation.title}</h3>
              </div>
              <span className="chip">{activeConversation.type}</span>
            </div>
            <div className="messageList">
              {activeMessages.map((message) => {
                const sender = resolveAgentName(seed, runtime, message.senderId)
                return (
                  <div key={message.id} className="messageCard">
                    <div className="messageHeader">
                      <div className="messageAuthor">{sender}</div>
                      <div className="messageMeta">{message.createdAt || 'live'}</div>
                    </div>
                    <div className="messageBody">{message.content}</div>
                    {Boolean(message.mentions?.length) && (
                      <div className="messageMentions">
                        {message.mentions?.map((mention) => (
                          <span key={mention.agentId} className="tag">@{mention.agentName}</span>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
            <div className="messageComposer" style={{ marginTop: 16 }}>
              <textarea
                value={draftMessage}
                onChange={(event) => setDraftMessage(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault()
                    void handleSendMessage()
                  }
                }}
                placeholder="输入一条新消息，写入 SQLite"
                rows={3}
                style={{ width: '100%', borderRadius: 16, padding: 12, background: 'rgba(255,255,255,0.04)', color: 'inherit', border: '1px solid rgba(148,163,184,0.2)' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10, gap: 12 }}>
                <div className="subtle">{statusMessage || 'Enter 发送，Shift+Enter 换行'}</div>
                <button
                  type="button"
                  onClick={handleSendMessage}
                  disabled={sending}
                  style={{ borderRadius: 999, padding: '10px 16px', background: 'linear-gradient(135deg, #77c6ff, #7cf0c8)', border: 0, color: '#06101c', fontWeight: 700 }}
                >
                  {sending ? 'Sending...' : 'Send to DB'}
                </button>
              </div>
            </div>
          </div>

          <div className="panel">
            <h3 className="sectionTitle">群聊规则</h3>
            <div className="timeline">
              <div className="timelineItem"><span>@Agent 触发上下文</span><span className="subtle">mention</span></div>
              <div className="timelineItem"><span>讨论层负责拆解问题</span><span className="subtle">discussion</span></div>
              <div className="timelineItem"><span>执行层负责落地结果</span><span className="subtle">delivery</span></div>
              <div className="timelineItem"><span>CEO 负责最后审核</span><span className="subtle">review</span></div>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  )
}

export function OrganizationView({ seed }: { seed: SeedState }) {
  const { state: runtime } = useRuntimeStateWithRefresh()
  const company = runtime?.database?.company ?? seed.company
  const departments = runtime?.database?.departments ?? seed.organization.departments
  const agents = runtime?.database?.agents ?? seed.organization.agents

  return (
    <section className="sectionStack">
      <div className="panel">
        <div className="cardHeader">
          <div>
            <p className="eyebrow">Organization</p>
            <h3 className="sectionTitle" style={{ marginTop: 8 }}>{company.name}</h3>
          </div>
          <span className="chip">{agents.length} agents</span>
        </div>
        <div className="orgTree">
          {departments.map((department) => (
            <div key={department.id} className="nodeCard">
              <div className="nodeHeader">
                <strong>{department.name}</strong>
                <span className="pill" style={{ borderColor: department.color }}>{department.type}</span>
              </div>
              <div className="nodeMeta">{department.description}</div>
              <div className="orgBranch">
                {agents
                  .filter((agent) => agent.departmentId === department.id)
                  .map((agent) => (
                    <div key={agent.id} className="timelineItem">
                      <div>
                        <div className="conversationTitle">{agent.name}</div>
                        <div className="conversationMeta">{agent.title} · {agent.status}</div>
                      </div>
                      <span className="subtle">{agent.isCEO === 1 ? 'CEO' : 'Member'}</span>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid three">
        {agents.map((agent) => (
          <div key={agent.id} className="panel">
            <div className="cardHeader">
              <strong>{agent.name}</strong>
              <span className="chip">{agent.title}</span>
            </div>
            <div className="panelNote">{agent.bio || agent.personality}</div>
          </div>
        ))}
      </div>
    </section>
  )
}

export function PlaygroundView({ seed }: { seed: SeedState }) {
  const { state: runtime, refresh } = useRuntimeStateWithRefresh()
  const [reviewDraft, setReviewDraft] = useState<ReviewDraft>(() => toReviewDraftFromSeed(seed.playgroundReview))
  const [saving, setSaving] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')
  const reviewDraftDirtyRef = useRef(false)
  const runtimeDocument = runtime?.database?.playgroundDocuments?.[0]
  const sourceConversationId = runtimeDocument?.sourceConversationId ?? seed.groupConversation.id
  const document = runtimeDocument
    ? {
      ...runtimeDocument,
      sourceConversationId,
    }
    : seed.playgroundDocument
  const review = runtime?.database?.reviewRecords?.[0]
    ? runtime.database.reviewRecords[0]
    : { decision: seed.playgroundReview.status, comments: JSON.stringify(seed.playgroundReview.notes) }

  useEffect(() => {
    const liveReview = runtime?.database?.reviewRecords?.[0]
    if (!liveReview || reviewDraftDirtyRef.current) {
      return
    }

    setReviewDraft(toReviewDraft(liveReview))
  }, [runtime])

  function updateReviewDraft(patch: Partial<ReviewDraft>) {
    reviewDraftDirtyRef.current = true
    setReviewDraft((current) => ({
      ...current,
      ...patch,
    }))
  }

  async function handleSaveReview() {
    const api = getCyberTeamApi()
    if (!api?.playground?.updateReview) {
      return
    }

    setSaving(true)
    try {
      await api.playground.updateReview(document.id, {
        decision: reviewDraft.decision,
        comments: reviewDraft.comments,
      })

      await refresh()
      reviewDraftDirtyRef.current = false
      setStatusMessage('审核结果已同步到 SQLite 并刷新运行态')
    } catch (error) {
      console.error('[CyberTeam] Failed to save playground review', error)
      setStatusMessage('审核结果保存失败，请检查运行态是否可写')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="grid two">
      <div className="docCard">
        <div className="cardHeader">
          <div>
            <p className="eyebrow">Playground</p>
            <h3 className="sectionTitle" style={{ marginTop: 8 }}>{document.title}</h3>
          </div>
          <span className="chip">{document.version}</span>
        </div>
        <div className="tags">
          <span className="tag">{reviewDraft.decision}</span>
          <span className="tag">{document.type ?? 'meeting notes'}</span>
        </div>
        <div className="docPreview" style={{ marginTop: 16 }}>{document.content}</div>
      </div>

      <div className="sectionStack">
        <div className="panel">
          <h3 className="sectionTitle">审核结果</h3>
          <div className="timeline">
            <div className="timelineItem">
              <span>Review Status</span>
              <span className="subtle">{reviewDraft.decision}</span>
            </div>
            <div className="timelineItem">
              <span>Notes</span>
              <span className="subtle">{reviewDraft.comments || 'none'}</span>
            </div>
            <div className="timelineItem">
              <span>Source Conversation</span>
              <span className="subtle">{resolveConversation(seed, runtime, sourceConversationId)?.title ?? 'unknown'}</span>
            </div>
          </div>
          <div className="sectionStack" style={{ marginTop: 16 }}>
            <label className="settingsTitle">Decision</label>
            <input
              value={reviewDraft.decision}
              onChange={(event) => updateReviewDraft({ decision: event.target.value })}
              style={{ borderRadius: 14, padding: 10, background: 'rgba(255,255,255,0.04)', color: 'inherit', border: '1px solid rgba(148,163,184,0.2)' }}
            />
            <label className="settingsTitle">Comments</label>
            <textarea
              value={reviewDraft.comments}
              onChange={(event) => updateReviewDraft({ comments: event.target.value })}
              rows={4}
              style={{ borderRadius: 14, padding: 10, background: 'rgba(255,255,255,0.04)', color: 'inherit', border: '1px solid rgba(148,163,184,0.2)' }}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                type="button"
                onClick={handleSaveReview}
                disabled={saving}
                style={{ borderRadius: 999, padding: '10px 16px', background: 'linear-gradient(135deg, #f7b267, #77c6ff)', border: 0, color: '#06101c', fontWeight: 700 }}
              >
                {saving ? 'Saving...' : 'Save Review'}
              </button>
            </div>
            <div className="subtle">{statusMessage || '保存后会自动刷新上方状态'}</div>
          </div>
        </div>

        <div className="panel">
          <h3 className="sectionTitle">输出历史</h3>
          <div className="timeline">
            <div className="timelineItem"><span>v1 · draft</span><span className="subtle">生成纪要</span></div>
            <div className="timelineItem"><span>v1 · review</span><span className="subtle">CEO 审核</span></div>
            <div className="timelineItem"><span>v1 · export</span><span className="subtle">Markdown 导出</span></div>
          </div>
        </div>
      </div>
    </section>
  )
}

export function MarketView({ seed }: { seed: SeedState }) {
  const { state: runtime } = useRuntimeStateWithRefresh()
  const skillRows = runtime?.database?.skills ?? []
  const templateRows = runtime?.database?.templates ?? []
  const agentSource = runtime?.database?.agents?.length ? runtime.database.agents : seed.market.agents
  const skillSource = skillRows.length ? skillRows : seed.market.skills
  const templateSource = templateRows.length ? templateRows : seed.market.templates
  const agentCards: Array<{ id: string; name: string; description: string }> = agentSource.map((item) => ({
    id: item.id,
    name: item.name,
    description: 'description' in item && item.description
      ? String(item.description)
      : String('bio' in item && item.bio ? item.bio : '已写入运行态。'),
  }))
  const skillCards: Array<{ id: string; name: string; description: string }> = skillSource.map((item) => ({
    id: item.id,
    name: item.name,
    description: 'description' in item && item.description ? String(item.description) : '基础技能入口已预置。',
  }))
  const templateCards: Array<{ id: string; name: string; description: string }> = templateSource.map((item) => ({
    id: item.id,
    name: item.name,
    description: 'description' in item && item.description ? String(item.description) : '模板系统的初始槽位。',
  }))

  return (
    <section className="sectionStack">
      <div className="panel">
        <div className="cardHeader">
          <div>
            <p className="eyebrow">Market</p>
            <h3 className="sectionTitle" style={{ marginTop: 8 }}>Agent / Skill / Template</h3>
          </div>
          <span className="chip">{runtime ? 'live' : 'bootstrap'}</span>
        </div>
        <div className="grid three">
          {agentCards.map((item) => (
            <div key={item.id} className="marketCardItem">
              <div className="marketTitle">{item.name}</div>
              <div className="cardNote">{item.description}</div>
            </div>
          ))}
          {skillCards.map((item) => (
            <div key={item.id} className="marketCardItem">
              <div className="marketTitle">{item.name}</div>
              <div className="cardNote">{item.description}</div>
            </div>
          ))}
          {templateCards.map((item) => (
            <div key={item.id} className="marketCardItem">
              <div className="marketTitle">{item.name}</div>
              <div className="cardNote">{item.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <h3 className="sectionTitle">已加载 Skill</h3>
        <div className="skillList">
          {(skillRows.length ? skillRows : seed.skills).map((skill) => (
            <div key={skill.id} className="skillCard">
              <div className="cardHeader">
                <strong>{skill.name}</strong>
                <span className="tag">{skill.category ?? 'loaded'}</span>
              </div>
              <div className="cardNote">{skill.description ?? '技能已入库'}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export function SettingsView({ seed }: { seed: SeedState }) {
  const { state: runtime } = useRuntimeStateWithRefresh()
  const counts = getDatabaseCounts(runtime)

  return (
    <section className="sectionStack">
      <div className="panel">
        <div className="cardHeader">
          <div>
            <p className="eyebrow">Settings</p>
            <h3 className="sectionTitle" style={{ marginTop: 8 }}>Local Runtime</h3>
          </div>
          <span className="chip">{runtime?.claude.installed ? 'Claude detected' : 'Claude missing'}</span>
        </div>
        <div className="grid three">
          <div className="settingsCardItem">
            <div className="settingsTitle">Claude Code</div>
            <div className="cardNote">{runtime?.claude.installed ? '已检测到本地 Claude Code 可执行文件。' : '当前机器还未检测到 Claude Code。'}</div>
          </div>
          <div className="settingsCardItem">
            <div className="settingsTitle">User Data</div>
            <div className="cardNote">{runtime?.userData ?? 'Electron 侧将使用本地 userData 目录作为未来持久化入口。'}</div>
          </div>
          <div className="settingsCardItem">
            <div className="settingsTitle">Theme</div>
            <div className="cardNote">默认采用深色、玻璃质感与高对比信息面板。</div>
          </div>
        </div>
      </div>

      <div className="grid two">
        <div className="panel">
          <h3 className="sectionTitle">系统信息</h3>
          <div className="timeline">
            <div className="timelineItem"><span>Company</span><span className="subtle">{runtime?.database?.company?.name ?? seed.company.name}</span></div>
            <div className="timelineItem"><span>Agents</span><span className="subtle">{counts.agents ?? seed.organization.agents.length}</span></div>
            <div className="timelineItem"><span>Conversations</span><span className="subtle">{counts.conversations ?? seed.conversations.length}</span></div>
            <div className="timelineItem"><span>Database</span><span className="subtle">{runtime?.database?.path ?? 'SQLite 未加载'}</span></div>
          </div>
        </div>

        <div className="panel">
          <h3 className="sectionTitle">接入建议</h3>
          <div className="timeline">
            <div className="timelineItem"><span>本地 Claude Code</span><span className="subtle">优先</span></div>
            <div className="timelineItem"><span>SQLite 持久化</span><span className="subtle">已启用</span></div>
            <div className="timelineItem"><span>正式账号体系</span><span className="subtle">暂缓</span></div>
          </div>
        </div>
      </div>
    </section>
  )
}
