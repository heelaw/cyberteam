export interface TeamModel {
  id: string
  name: string
  kind?: 'company' | 'department' | 'agent'
}
