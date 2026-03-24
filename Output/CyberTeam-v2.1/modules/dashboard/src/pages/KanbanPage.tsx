import { KanbanBoard } from '@/components/kanban'

export function KanbanPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">任务看板</h1>
        <p className="text-muted-foreground">拖拽卡片以更新任务状态</p>
      </div>

      <KanbanBoard />
    </div>
  )
}
