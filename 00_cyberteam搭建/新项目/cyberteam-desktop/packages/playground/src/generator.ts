export interface PlaygroundDocument {
  id: string
  title: string
  content: string
  type?: string
  reviewStatus: 'pending' | 'approved' | 'rejected'
  version: string
}

let documentSequence = 0

export function generatePlaygroundDoc(title: string, content: string): PlaygroundDocument {
  documentSequence += 1

  return {
    id: `playground_${documentSequence}`,
    title,
    content: `# ${title}\n\n${content}`,
    type: 'meeting notes',
    reviewStatus: 'pending',
    version: 'v1',
  }
}
