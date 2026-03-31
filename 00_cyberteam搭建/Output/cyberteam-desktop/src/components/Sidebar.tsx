import type { Page } from '../types'

interface SidebarProps {
  currentPage: Page
  onNavigate: (page: Page) => void
}

export default function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  const navItems: { id: Page; label: string; icon: string }[] = [
    { id: 'chat', label: '对话', icon: '💬' },
    { id: 'agents', label: 'Agent', icon: '🤖' },
    { id: 'skills', label: '技能', icon: '⚡' },
    { id: 'settings', label: '设置', icon: '⚙️' },
  ]

  return (
    <aside className="w-56 bg-slate-800 border-r border-slate-700 flex flex-col">
      <div className="p-4 border-b border-slate-700">
        <h1 className="text-xl font-bold text-white">CyberTeam</h1>
        <p className="text-xs text-slate-400">Desktop v1.0</p>
      </div>
      <nav className="flex-1 p-2">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
              currentPage === item.id
                ? 'bg-blue-600 text-white'
                : 'text-slate-300 hover:bg-slate-700'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-slate-700">
        <div className="text-xs text-slate-500">Claude Code CLI</div>
        <div className="text-xs text-slate-400">Integrated</div>
      </div>
    </aside>
  )
}
