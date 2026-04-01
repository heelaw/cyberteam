export interface Company {
  id: string
  name: string
  avatar?: string
  description?: string
  theme?: string
  version?: string
  createdAt: string
  updatedAt: string
}

let companySequence = 0

function createTimestamp() {
  return new Date().toISOString()
}

export function createCompany(name: string, avatar?: string, description?: string): Company {
  const createdAt = createTimestamp()
  companySequence += 1

  return {
    id: `company_${companySequence}`,
    name,
    avatar,
    description,
    theme: 'midnight',
    version: '0.1.0',
    createdAt,
    updatedAt: createdAt,
  }
}
