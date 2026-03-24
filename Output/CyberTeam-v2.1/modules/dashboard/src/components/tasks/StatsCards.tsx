import { Users, CheckCircle, Clock, AlertCircle, MessageSquare } from 'lucide-react'
import { Card } from '@/components/ui'
import { useStats } from '@/store'

const statsConfig = [
  {
    key: 'activeAgents',
    label: '在线 Agent',
    icon: Users,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  {
    key: 'completedTasks',
    label: '已完成任务',
    icon: CheckCircle,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
  },
  {
    key: 'pendingTasks',
    label: '待处理任务',
    icon: Clock,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
  },
  {
    key: 'blockedTasks',
    label: '阻塞任务',
    icon: AlertCircle,
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
  },
  {
    key: 'messagesToday',
    label: '今日消息',
    icon: MessageSquare,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
  },
]

export function StatsCards() {
  const stats = useStats()

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
      {statsConfig.map((config) => {
        const value = stats[config.key as keyof typeof stats]
        return (
          <Card key={config.key} className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{config.label}</p>
                <p className="text-2xl font-bold">{value}</p>
              </div>
              <div className={`rounded-lg p-2 ${config.bgColor}`}>
                <config.icon className={`h-5 w-5 ${config.color}`} />
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
