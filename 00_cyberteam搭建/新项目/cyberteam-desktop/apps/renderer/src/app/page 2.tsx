import { createConversationStore } from '../../../../packages/chat/src/conversation-store'
import { createCompany, createDepartment, createAgent, createOrganization } from '../../../../packages/team/src'

const store = createConversationStore()
const company = createCompany('CyberTeam')
const org = createOrganization(company)
org.departments.push(createDepartment('CEO'))
org.agents.push(createAgent('Clark', 'CEO'))
const conversation = store.createConversation('默认会话', 'private', [org.agents[0].id])
store.sendMessage(conversation.id, 'CyberTeam ready', org.agents[0].id)
store.sendMessage(conversation.id, 'MVP 启动中', org.agents[0].id)

export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>CyberTeam</h1>
      <p>AI 军团操作系统</p>
      <section>
        <h2>Company</h2>
        <pre>{JSON.stringify(company, null, 2)}</pre>
      </section>
      <section>
        <h2>Organization</h2>
        <pre>{JSON.stringify(org, null, 2)}</pre>
      </section>
      <section>
        <h2>Conversation</h2>
        <pre>{JSON.stringify(store.getMessages(conversation.id), null, 2)}</pre>
      </section>
    </main>
  )
}
