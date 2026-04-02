export function createReviewEngine() {
  return {
    review(document: { title?: string; content?: string }) {
      const hasContent = Boolean(document.content?.trim())
      return { status: hasContent ? 'approved' : 'pending', notes: hasContent ? [] : ['Document is empty'] }
    },
  }
}
