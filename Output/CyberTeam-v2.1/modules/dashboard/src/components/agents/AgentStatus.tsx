import { useDashboardStore } from '@/store'
import { Card, Badge, Avatar, Progress } from '@/components/ui'
import { cn, formatRelativeTime } from '@/lib/utils'
import type { Agent, AgentStatus } from '@/types'

const statusConfig: Record<AgentStatus, { label: string; color: string; bgColor: string }> = {
  online: { label: '在线', color: 'text-green-500', bgColor: 'bg-green-500' },
  busy: { label: '忙碌', color: 'text-yellow-500', bgColor: 'bg-yellow-500' },
  offline: { label: '离线', color: 'text-gray-400', bgColor: 'bg-gray-400' },
  error: { label: '异常', color: 'text-red-500', bgColor: 'bg-red-500' },
}

function AgentCard({ agent }: { agent: Agent }) {
  const config = statusConfig[agent.status]

  return (
    <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer">
      <div className="flex items-start gap-3">
        <div className="relative">
          <Avatar className="h-10 w-10">
            <div className="flex h-full w-full items-center justify-center bg-primary text-primary-foreground text-sm font-medium">
              {agent.name.slice(0, 2).toUpperCase()}
            </div>
          </Avatar>
          <span
            className={cn(
              'absolute -bottom-0.5 -right-0.5 block h-3 w-3 rounded-full border-2 border-background',
              config.bgColor
            )}
          />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-medium truncate">{agent.name}</h4>
            <Badge variant={agent.status === 'online' ? 'success' : agent.status === 'error' ? 'destructive' : 'secondary'}>
              {config.label}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground truncate">{agent.role}</p>
          {agent.currentTask && (
            <p className="text-xs text-muted-foreground mt-1 truncate">
              当前任务: {agent.currentTask}
            </p>
          )}
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
        <span>已完成 {agent.tasksCompleted} 个任务</span>
        <span>{formatRelativeTime(agent.lastActive)}</span>
      </div>
    </Card>
  )
}

export function AgentStatusGrid() {
  const agents = useDashboardStore((state) => state.agents)

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {agents.map((agent) => (
        <AgentCard key={agent.id} agent={agent} />
      ))}
    </div>
  )
}

export function AgentDetail({ agentId }: { agentId: string }) {
  const agent = useDashboardStore((state) =>
    state.agents.find((a) => a.id === agentId)
  )

  if (!agent) return null

  const config = statusConfig[agent.status]
  const tasks = useDashboardStore((state) => state.tasks)
  const agentTasks = tasks.filter((t) => t.assignee?.id === agent.id)

  return (
    <Card className="p-6">
      <div className="flex items-start gap-4">
        <div className="relative">
          <Avatar className="h-16 w-16">
            <div className="flex h-full w-full items-center justify-center bg-primary text-primary-foreground text-xl font-medium">
              {agent.name.slice(0, 2).toUpperCase()}
            </div>
          </Avatar>
          <span
            className={cn(
              'absolute -bottom-1 -right-1 block h-4 w-4 rounded-full border-2 border-background',
              config.bgColor
            )}
          />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-xl font-semibold">{agent.name}</h3>
            <Badge variant={agent.status === 'online' ? 'success' : agent.status === 'error' ? 'destructive' : 'secondary'}>
              {config.label}
            </Badge>
          </div>
          <p className="text-muted-foreground">{agent.role}</p>
          <p className="text-sm text-muted-foreground mt-2">{agent.description}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">任务进度</span>
            <span className="font-medium">
              {agentTasks.filter((t) => t.status === 'completed').length} / {agentTasks.length}
            </span>
          </div>
          <Progress
            value={
              agentTasks.length
                ? (agentTasks.filter((t) => t.status === 'completed').length / agentTasks.length) * 100
                : 0
            }
          />
        </div>
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">总完成任务</p>
          <p className="text-2xl font-bold">{agent.tasksCompleted}</p>
        </div>
      </div>

      {agent.currentTask && (
        <div className="mt-4 rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">当前任务</p>
          <p className="text-sm text-muted-foreground">{agent.currentTask}</p>
        </div>
      )}
    </Card>
  )
}
