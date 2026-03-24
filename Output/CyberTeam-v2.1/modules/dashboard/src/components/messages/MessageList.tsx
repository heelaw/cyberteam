import { useDashboardStore } from '@/store'
import { Card, Badge, Avatar, ScrollArea } from '@/components/ui'
import { cn, formatRelativeTime } from '@/lib/utils'
import type { Message } from '@/types'
import { CheckCheck, Bell, MessageCircle, FileText, Settings } from 'lucide-react'

const messageTypeConfig = {
  task: { icon: FileText, label: '任务', color: 'text-blue-500' },
  chat: { icon: MessageCircle, label: '对话', color: 'text-green-500' },
  notification: { icon: Bell, label: '通知', color: 'text-yellow-500' },
  system: { icon: Settings, label: '系统', color: 'text-gray-500' },
}

function MessageItem({ message }: { message: Message }) {
  const { markAsRead } = useDashboardStore()
  const typeConfig = messageTypeConfig[message.type]
  const isUnread = !message.read

  return (
    <div
      className={cn(
        'flex gap-3 p-4 border-b hover:bg-muted/50 cursor-pointer transition-colors',
        isUnread && 'bg-blue-500/5'
      )}
      onClick={() => markAsRead(message.id)}
    >
      {/* Avatar */}
      <div className="shrink-0">
        {message.sender === 'system' ? (
          <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
            <Settings className="h-5 w-5 text-muted-foreground" />
          </div>
        ) : (
          <Avatar className="h-10 w-10">
            <div className="flex h-full w-full items-center justify-center bg-primary text-primary-foreground text-sm font-medium">
              {message.sender.name.slice(0, 2).toUpperCase()}
            </div>
          </Avatar>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">
            {message.sender === 'system' ? '系统' : message.sender.name}
          </span>
          <Badge variant="outline" className={cn('text-xs', typeConfig.color)}>
            {typeConfig.label}
          </Badge>
          {isUnread && (
            <span className="ml-auto h-2 w-2 rounded-full bg-blue-500" />
          )}
        </div>
        <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
          {message.content}
        </p>
        <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
          <span>{formatRelativeTime(message.timestamp)}</span>
          {message.receiver && message.receiver !== 'all' && typeof message.receiver !== 'string' && (
            <span>→ {message.receiver.name}</span>
          )}
        </div>
      </div>
    </div>
  )
}

export function MessageList() {
  const { messages, markAllAsRead } = useDashboardStore()
  const unreadCount = messages.filter((m) => !m.read).length

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h3 className="font-semibold">消息流</h3>
          <p className="text-sm text-muted-foreground">
            {unreadCount} 条未读消息
          </p>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="text-sm text-primary hover:underline flex items-center gap-1"
          >
            <CheckCheck className="h-4 w-4" />
            全部已读
          </button>
        )}
      </div>
      <ScrollArea className="h-[400px]">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <MessageCircle className="h-12 w-12 mb-2" />
            <p>暂无消息</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))
        )}
      </ScrollArea>
    </Card>
  )
}
