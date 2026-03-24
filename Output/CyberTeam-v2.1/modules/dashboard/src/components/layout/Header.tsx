import { Bell, Search, User } from 'lucide-react'
import { Button } from '@/components/ui'
import { useDashboardStore } from '@/store'

export function Header() {
  const { messages, sidebarCollapsed } = useDashboardStore()
  const unreadCount = messages.filter((m) => !m.read).length

  return (
    <header
      className={`fixed right-0 top-0 z-30 flex h-16 items-center justify-between border-b bg-background/95 px-6 backdrop-blur transition-all duration-300 ${
        sidebarCollapsed ? 'left-16' : 'left-64'
      }`}
    >
      {/* Search */}
      <div className="relative w-80">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="搜索任务、Agent、消息..."
          className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-xs text-white">
              {unreadCount}
            </span>
          )}
        </Button>

        {/* User */}
        <Button variant="ghost" size="icon">
          <User className="h-5 w-5" />
        </Button>
      </div>
    </header>
  )
}
