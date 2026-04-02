import { ChatView } from '../../components/hybrid-pages'
import { createSeedState } from '../../lib/seed'

const seed = createSeedState()

export default function ChatPage() {
  return <ChatView seed={seed} />
}
