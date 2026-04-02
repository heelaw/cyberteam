export interface Skill {
  id: string
  name: string
  description?: string
  category?: string
  prompt?: string
  tools?: string[]
  version?: string
}
