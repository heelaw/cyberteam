export interface SkillMarketItem {
  id: string
  name: string
}

export function createSkillMarketItem(id: string, name: string): SkillMarketItem {
  return { id, name }
}
