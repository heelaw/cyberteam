export interface GroupChat {
  id: string
  title: string
  participantIds: string[]
  createdAt: string
}

let groupSequence = 0

function createTimestamp() {
  return new Date().toISOString()
}

export function createGroupChat(title: string, participantIds: string[] = []): GroupChat {
  const createdAt = createTimestamp()
  groupSequence += 1

  return {
    id: `group_${groupSequence}`,
    title,
    participantIds,
    createdAt,
  }
}
