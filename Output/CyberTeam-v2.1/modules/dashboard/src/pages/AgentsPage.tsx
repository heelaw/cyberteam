import { AgentStatusGrid, AgentDetail } from '@/components/agents'
import { useDashboardStore } from '@/store'

export function AgentsPage() {
  const selectedAgentId = useDashboardStore((state) => state.selectedAgentId)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Agent 状态</h1>
        <p className="text-muted-foreground">监控所有 Agent 的运行状态</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h2 className="text-xl font-semibold mb-4">所有 Agent</h2>
          <AgentStatusGrid />
        </div>
        {selectedAgentId && (
          <div>
            <h2 className="text-xl font-semibold mb-4">详情</h2>
            <AgentDetail agentId={selectedAgentId} />
          </div>
        )}
      </div>
    </div>
  )
}
