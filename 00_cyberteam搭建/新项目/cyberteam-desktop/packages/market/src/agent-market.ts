export interface MarketItem {
  id: string
  name: string
  description?: string
  kind?: 'agent' | 'skill' | 'template'
}

export function createAgentMarketItem(id: string, name: string, description = ''): MarketItem {
  return { id, name, description, kind: 'agent' }
}
