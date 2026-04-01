import { useState } from 'react'
import { AppProvider } from '@/contexts/AppContext'
import SettingsPage from '@/pages/Settings'
import SkillsPage from '@/pages/Skills'
import {
  Bot,
  Sparkles,
  MessageSquare,
  LayoutGrid,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/utils/cn'

type TabType = 'skills' | 'chat' | 'agents' | 'settings'

const TABS = [
  { key: 'skills' as const, label: '技能中心', icon: Sparkles },
  { key: 'chat' as const, label: '对话', icon: MessageSquare },
  { key: 'agents' as const, label: '智能体', icon: Bot },
  { key: 'settings' as const, label: '设置', icon: LayoutGrid },
]

function AppContent() {
  const [activeTab, setActiveTab] = useState<TabType>('skills')

  const renderContent = () => {
    switch (activeTab) {
      case 'skills':
        return <SkillsPage />
      case 'chat':
        return (
          <div className="h-full flex items-center justify-center text-[var(--color-text-muted)]">
            <div className="text-center">
              <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>对话功能开发中...</p>
            </div>
          </div>
        )
      case 'agents':
        return (
          <div className="h-full flex items-center justify-center text-[var(--color-text-muted)]">
            <div className="text-center">
              <Bot className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>智能体管理开发中...</p>
            </div>
          </div>
        )
      case 'settings':
        return <SettingsPage />
      default:
        return <SkillsPage />
    }
  }

  return (
    <div className="h-full flex flex-col bg-[var(--color-bg-primary)]">
      {/* Header */}
      <header className="h-14 flex items-center justify-between px-4 border-b border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-accent)] flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-[var(--color-text-primary)]">CyberTeam</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--color-text-muted)]">v4.1.0</span>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <nav className="w-48 border-r border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
          <div className="p-2 space-y-1">
            {TABS.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.key
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                    isActive
                      ? 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-primary)]'
                      : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-tertiary)]/50'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="flex-1 text-left">{tab.label}</span>
                  {isActive && <ChevronRight className="w-3 h-3" />}
                </button>
              )
            })}
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  )
}