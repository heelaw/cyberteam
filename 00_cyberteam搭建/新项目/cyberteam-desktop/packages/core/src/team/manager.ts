import { createLifecycleManager } from './lifecycle'
import type { TeamModel } from './models'

export function createTeamManager() {
  const lifecycle = createLifecycleManager()
  const companies: TeamModel[] = []
  const departments: TeamModel[] = []
  const agents: TeamModel[] = []

  return {
    lifecycle,
    createCompany(name: string) {
      const company = { id: `company_${companies.length + 1}`, name, kind: 'company' as const }
      companies.push(company)
      return company
    },
    listCompanies() {
      return companies
    },
    createDepartment(name: string) {
      const department = { id: `department_${departments.length + 1}`, name, kind: 'department' as const }
      departments.push(department)
      return department
    },
    createAgent(name: string) {
      const agent = { id: `agent_${agents.length + 1}`, name, kind: 'agent' as const }
      agents.push(agent)
      return agent
    },
  }
}
