import { createConversationStore } from '../../../../../packages/chat/src/conversation-store'

const store = createConversationStore()
const conv = store.createConversation('Chat Demo', 'group')
store.sendMessage(conv.id, 'Hello CyberTeam')
store.sendMessage(conv.id, '群聊已启动')

export default function ChatPage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Chat</h1>
      <pre>{JSON.stringify(store.listConversations(), null, 2)}</pre>
      <pre>{JSON.stringify(store.getMessages(conv.id), null, 2)}</pre>
    </main>
  )
}
