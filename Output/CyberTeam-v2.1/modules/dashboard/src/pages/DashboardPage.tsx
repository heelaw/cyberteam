import { StatsCards } from '@/components/tasks'
import { AgentStatusGrid } from '@/components/agents'
import { MessageList } from '@/components/messages'

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">概览</h1>
        <p className="text-muted-foreground">CyberTeam 工作台</p>
      </div>

      <StatsCards />

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h2 className="text-xl font-semibold mb-4">Agent 状态</h2>
          <AgentStatusGrid />
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4">最近消息</h2>
          <MessageList />
        </div>
      </div>
    </div>
  )
}
