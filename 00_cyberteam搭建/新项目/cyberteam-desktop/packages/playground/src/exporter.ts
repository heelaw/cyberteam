export function exportMarkdown(doc: { title: string; content: string }) {
  return `# ${doc.title}\n\n${doc.content}`
}
