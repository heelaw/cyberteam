import { MessageList } from '@/components/messages'

export function MessagesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">消息流</h1>
        <p className="text-muted-foreground">查看所有团队消息和通知</p>
      </div>

      <MessageList />
    </div>
  )
}
