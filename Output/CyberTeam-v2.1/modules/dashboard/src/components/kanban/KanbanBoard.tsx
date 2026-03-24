import { useDashboardStore } from '@/store'
import { Badge, Avatar } from '@/components/ui'
import { cn, formatRelativeTime } from '@/lib/utils'
import type { Task, TaskStatus } from '@/types'
import { MoreHorizontal, Plus } from 'lucide-react'

const columns: { id: TaskStatus; title: string; color: string }[] = [
  { id: 'pending', title: '待处理', color: 'bg-yellow-500' },
  { id: 'in_progress', title: '进行中', color: 'bg-blue-500' },
  { id: 'completed', title: '已完成', color: 'bg-green-500' },
  { id: 'blocked', title: '阻塞', color: 'bg-red-500' },
]

const priorityConfig = {
  low: { label: '低', variant: 'secondary' as const },
  medium: { label: '中', variant: 'warning' as const },
  high: { label: '高', variant: 'default' as const },
  urgent: { label: '紧急', variant: 'destructive' as const },
}

function TaskCard({ task, onDragStart }: { task: Task; onDragStart: (e: React.DragEvent, taskId: string) => void }) {
  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, task.id)}
      className="kanban-card cursor-grab active:cursor-grabbing"
    >
      <div className="flex items-start justify-between gap-2">
        <h4 className="font-medium text-sm">{task.title}</h4>
        <button className="text-muted-foreground hover:text-foreground">
          <MoreHorizontal className="h-4 w-4" />
        </button>
      </div>
      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{task.description}</p>

      <div className="mt-3 flex flex-wrap gap-1">
        {task.tags.map((tag) => (
          <Badge key={tag} variant="outline" className="text-xs">
            {tag}
          </Badge>
        ))}
      </div>

      <div className="mt-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant={priorityConfig[task.priority].variant} className="text-xs">
            {priorityConfig[task.priority].label}
          </Badge>
          {task.assignee && (
            <Avatar className="h-6 w-6">
              <div className="flex h-full w-full items-center justify-center bg-primary text-primary-foreground text-xs">
                {task.assignee.name.slice(0, 2)}
              </div>
            </Avatar>
          )}
        </div>
        <span className="text-xs text-muted-foreground">
          {formatRelativeTime(task.updatedAt)}
        </span>
      </div>
    </div>
  )
}

export function KanbanBoard() {
  const { tasks, moveTask } = useDashboardStore()

  const getColumnTasks = (status: TaskStatus) =>
    tasks.filter((task) => task.status === status)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent, status: TaskStatus) => {
    e.preventDefault()
    const taskId = e.dataTransfer.getData('taskId')
    if (taskId) {
      moveTask(taskId, status)
    }
  }

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.setData('taskId', taskId)
  }

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map((column) => {
        const columnTasks = getColumnTasks(column.id)
        return (
          <div
            key={column.id}
            className="w-72 shrink-0"
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, column.id)}
          >
            <div className="flex items-center gap-2 mb-3">
              <span className={cn('h-2 w-2 rounded-full', column.color)} />
              <h3 className="font-medium">{column.title}</h3>
              <Badge variant="secondary" className="ml-auto">
                {columnTasks.length}
              </Badge>
            </div>
            <div className="kanban-column space-y-3 min-h-[400px]">
              {columnTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onDragStart={handleDragStart}
                />
              ))}
              <button className="w-full flex items-center justify-center gap-2 p-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors">
                <Plus className="h-4 w-4" />
                添加任务
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
