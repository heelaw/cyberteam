export interface TemplateMarketItem {
  id: string
  name: string
}

export function createTemplateMarketItem(id: string, name: string): TemplateMarketItem {
  return { id, name }
}
