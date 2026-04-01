export function reviewPlaygroundDocument(document: { content?: string }) {
  const approved = Boolean(document.content?.trim())
  return {
    status: approved ? 'approved' : 'pending',
    notes: approved ? [] : ['Document is empty'],
  }
}
