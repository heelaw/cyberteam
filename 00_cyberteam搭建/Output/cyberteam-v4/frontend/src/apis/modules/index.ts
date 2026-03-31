// API 模块导出（避免命名冲突，使用显式命名导出）
export { type Agent, fetchAgents, fetchAgent, sendMessageToAgent } from './agents'
export * from './stats'
export * from './chat'
export * from './departments'
export {
  type CustomAgent,
  type CreateAgentRequest,
  type UpdateAgentRequest,
  type BindSkillRequest,
  fetchAgents as fetchCustomAgents,
  fetchAgent as fetchCustomAgent,
  createAgent,
  updateAgent,
  deleteAgent,
  bindSkillToAgent,
  unbindSkillFromAgent,
} from './custom-agents'
export {
  type PlaygroundRequest,
  type PlaygroundResponse,
  type PlaygroundHTMLResponse,
  generatePlayground,
  fetchPlaygroundHTML,
  subscribePlaygroundSSE,
} from './playground'
export * from './expert-agents'
export {
  type Skill,
  type SkillCreate,
  type SkillUpdate,
  type SkillCategory,
  type AgentBrief,
  type ExecuteSkillRequest,
  type ExecuteSkillResponse,
  fetchSkills,
  fetchSkillCategories,
  fetchSkill,
} from './skills'
export {
  type Project,
  type CreateProjectRequest,
  fetchProjects,
  createProject,
  fetchProject,
  updateProject,
} from './projects'
