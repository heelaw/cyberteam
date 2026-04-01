export function createClaudeStream() {
  const listeners: Array<(chunk: string) => void> = []
  return {
    subscribe(listener: (chunk: string) => void) {
      listeners.push(listener)
      return () => {
        const index = listeners.indexOf(listener)
        if (index >= 0) listeners.splice(index, 1)
      }
    },
    emit(chunk: string) {
      listeners.forEach((listener) => listener(chunk))
    },
  }
}
