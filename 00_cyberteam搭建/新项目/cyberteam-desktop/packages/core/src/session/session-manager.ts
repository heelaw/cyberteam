export function createSessionManager() {
  const sessions = new Map<string, unknown>()
  return {
    save(id: string, data: unknown) {
      sessions.set(id, data)
      return data
    },
    load(id: string) {
      return sessions.get(id)
    },
  }
}
