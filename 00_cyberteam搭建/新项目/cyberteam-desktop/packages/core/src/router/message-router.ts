export function createMessageRouter() {
  return {
    route(message: { type?: string; targetIds?: string[] }) {
      if (!message.targetIds?.length) return []
      return message.targetIds.map((id) => ({ targetId: id, reason: message.type ?? 'default' }))
    },
    routeByRole(message: { role?: string; targetIds?: string[] }) {
      return this.route({ type: message.role, targetIds: message.targetIds })
    },
  }
}
