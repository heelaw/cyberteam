import { createAgent, type Agent } from './agent'
import { createDepartment, type Department } from './department'
import type { Company } from './company'

export interface Organization {
  company: Company
  departments: Department[]
  agents: Agent[]
}

export function createOrganization(company: Company): Organization {
  const ceoDepartment = createDepartment('CEO', undefined, company.id)
  ceoDepartment.type = 'review'
  ceoDepartment.color = '#f59e0b'
  ceoDepartment.description = '最终审核与决策中心'

  const discussionDepartment = createDepartment('讨论层', ceoDepartment.id, company.id)
  discussionDepartment.type = 'discussion'
  discussionDepartment.color = '#3b82f6'
  discussionDepartment.description = '用于发起讨论、汇总观点和形成方案'

  const executionDepartment = createDepartment('执行层', ceoDepartment.id, company.id)
  executionDepartment.type = 'execution'
  executionDepartment.color = '#10b981'
  executionDepartment.description = '用于拆解任务、推进执行和交付结果'

  const ceoAgent = createAgent('CEO', 'CEO', undefined, company.id)
  ceoAgent.departmentId = ceoDepartment.id
  ceoAgent.status = 'online'

  const discussionAgent = createAgent('讨论主管', 'Discussion Lead', undefined, company.id)
  discussionAgent.departmentId = discussionDepartment.id
  discussionAgent.bio = '负责把模糊需求拆成可以讨论的问题'

  const executionAgent = createAgent('执行主管', 'Delivery Lead', undefined, company.id)
  executionAgent.departmentId = executionDepartment.id
  executionAgent.bio = '负责把结论推进成可交付成果'

  return {
    company,
    departments: [ceoDepartment, discussionDepartment, executionDepartment],
    agents: [ceoAgent, discussionAgent, executionAgent],
  }
}
