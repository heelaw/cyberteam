import { createConversationStore, createMention } from '@cyberteam/chat'
import { createCompany, createOrganization } from '@cyberteam/team'
import { exportMarkdown, generatePlaygroundDoc, reviewPlaygroundDocument } from '@cyberteam/playground'
import { createSkillRegistry } from '@cyberteam/skill'
import { createAgentMarketItem, createSkillMarketItem, createTemplateMarketItem } from '@cyberteam/market'
import { detectClaudeCode } from '@cyberteam/claude'
import { createRoadmap } from '../roadmap'

const company = createCompany('CyberTeam', 'CT', '本地 Claude Code 驱动的 AI 军团操作系统')
const organization = createOrganization(company)
const store = createConversationStore()
const [ceo, discussionLead, executionLead] = organization.agents

const privateConversation = store.createConversation('CEO 私聊', 'private', [ceo.id])
store.sendMessage(privateConversation.id, '先判断问题的本质，再决定要不要拆给团队。', ceo.id)
store.sendMessage(privateConversation.id, '确认 MVP 只保留最小闭环。', ceo.id)

const groupConversation = store.createConversation('产品增长讨论群', 'group', [ceo.id, discussionLead.id, executionLead.id])
store.sendMessage(
  groupConversation.id,
  '请围绕首屏、组织页、聊天页、设置页做一次苏格拉底式拆解。',
  ceo.id,
  [createMention(discussionLead.id, discussionLead.name, discussionLead.title)],
)
store.sendMessage(groupConversation.id, '先把信息流、组织感、交付感三件事做出来。', discussionLead.id)
store.sendMessage(groupConversation.id, '执行上优先打通页面和种子数据，再补 IPC 与状态同步。', executionLead.id)

const departmentConversation = store.createConversation('执行层部门群', 'department', [executionLead.id])
store.sendMessage(departmentConversation.id, '把占位符替换成能看见的页面与数据。', executionLead.id)

const playgroundDocument = generatePlaygroundDoc(
  'CyberTeam MVP 讨论纪要',
  '首屏已经对齐公司、组织、聊天、Playground、设置与市场六个关键入口，正在收口为可运行桌面骨架。',
)
const playgroundReview = reviewPlaygroundDocument(playgroundDocument)
const playgroundExport = exportMarkdown(playgroundDocument)
const skillRegistry = createSkillRegistry()

const market = {
  agents: [
    createAgentMarketItem('agent-ceo', 'CEO', '最终审核与方向决策'),
    createAgentMarketItem('agent-discussion', '讨论主管', '把问题推到可讨论的粒度'),
    createAgentMarketItem('agent-execution', '执行主管', '推动结论落地'),
  ],
  skills: [
    createSkillMarketItem('skill-ceo-review', 'CEO Review'),
    createSkillMarketItem('skill-socratic', 'Socratic Questioning'),
  ],
  templates: [
    createTemplateMarketItem('template-default', 'Default Company'),
    createTemplateMarketItem('template-sprint', 'MVP Sprint'),
  ],
}

export function createSeedState() {
  const conversations = store.listConversations()
  const messagesByConversation = Object.fromEntries(
    conversations.map((conversation) => [conversation.id, store.getMessages(conversation.id)]),
  )

  return {
    company,
    organization,
    conversations,
    messagesByConversation,
    privateConversation,
    groupConversation,
    departmentConversation,
    playgroundDocument,
    playgroundReview,
    playgroundExport,
    roadmap: createRoadmap(),
    skills: Array.from(skillRegistry.values()),
    market,
    claudeInstalled: detectClaudeCode(),
    metrics: [
      { label: '公司', value: '1', note: '已创建 CyberTeam 核心公司' },
      { label: '部门', value: String(organization.departments.length), note: 'CEO / 讨论层 / 执行层' },
      { label: 'Agent', value: String(organization.agents.length), note: '最小可协作阵列已就绪' },
      { label: '会话', value: String(conversations.length), note: '私聊 / 群聊 / 部门群' },
      { label: 'Skill', value: String(skillRegistry.size), note: '基础能力插件已加载' },
      { label: 'Claude Code', value: detectClaudeCode() ? '已检测' : '未检测', note: '本地执行引擎状态' },
    ],
    timeline: [
      '公司初始化',
      'CEO 节点生成',
      '讨论层与执行层展开',
      '群聊与 Playground 已串联',
    ],
  }
}

export type SeedState = ReturnType<typeof createSeedState>
