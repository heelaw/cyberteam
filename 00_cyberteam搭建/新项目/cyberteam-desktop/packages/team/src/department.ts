export interface Department {
  id: string
  companyId: string
  name: string
  parentId?: string
  type: 'discussion' | 'execution' | 'review' | 'support' | 'custom'
  color: string
  description: string
  createdAt: string
  updatedAt: string
}

let departmentSequence = 0

function createTimestamp() {
  return new Date().toISOString()
}

export function createDepartment(name: string, parentId?: string, companyId = 'company_1'): Department {
  const createdAt = createTimestamp()
  departmentSequence += 1

  return {
    id: `dept_${departmentSequence}`,
    companyId,
    name,
    parentId,
    type: 'custom',
    color: '#64748b',
    description: '',
    createdAt,
    updatedAt: createdAt,
  }
}
