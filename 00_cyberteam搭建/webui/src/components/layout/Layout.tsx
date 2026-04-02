import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, Building2, Users, Network, FileText, Wrench, Cpu, Zap } from 'lucide-react'

const navItems = [
  { path: '/', label: '首页', icon: LayoutDashboard },
  { path: '/chat', label: '对话', icon: MessageSquare },
  { path: '/departments', label: '部门管理', icon: Building2 },
  { path: '/agents', label: 'Agent管理', icon: Users },
  { path: '/teams', label: '团队构建', icon: Network },
  { path: '/templates', label: '模板市场', icon: FileText },
  { path: '/skills', label: '技能配置', icon: Wrench },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()

  return (
    <div className="flex min-h-screen bg-cyber-dark cyber-grid scanlines noise">
      {/* Scanline Effect */}
      <div className="scanline-moving" />

      {/* Sidebar */}
      <aside className="w-64 bg-cyber-panel border-r border-neon-cyan/20 flex flex-col relative z-10">
        {/* Glowing Top Border */}
        <div className="h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent" />

        {/* Logo Section */}
        <div className="p-5 relative">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 bg-cyber-dark border border-neon-cyan/40 flex items-center justify-center clip-path-corner">
                <Cpu className="text-neon-cyan w-5 h-5 animate-pulse" />
              </div>
              <div className="absolute inset-0 bg-neon-cyan/20 blur-lg" />
            </div>
            <div>
              <h1 className="font-display font-bold text-lg tracking-wider text-white">
                CYBER<span className="text-neon-cyan text-glow-cyan">TEAM</span>
              </h1>
              <p className="text-[10px] text-neon-cyan/60 font-mono tracking-widest uppercase">Studio v4.0</p>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="mx-4 p-3 bg-cyber-dark/50 border border-neon-cyan/10 rounded-lg mb-4">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500 font-mono">SYSTEM</span>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-neon-green rounded-full animate-pulse shadow-[0_0_8px_var(--neon-green)]" />
              <span className="text-neon-green font-mono">ONLINE</span>
            </div>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Zap className="text-neon-yellow w-3 h-3" />
            <span className="text-slate-400 text-xs">Neural Link Active</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3">
          <div className="text-[10px] text-slate-600 font-mono tracking-widest uppercase mb-3 px-3">Navigation</div>
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`relative flex items-center gap-3 px-4 py-3 mb-1 rounded-lg transition-all duration-300 group ${
                  isActive
                    ? 'bg-neon-cyan/10 text-neon-cyan sidebar-item-active'
                    : 'text-slate-400 hover:bg-cyber-dark/50 hover:text-slate-200'
                }`}
              >
                {/* Active Indicator */}
                {isActive && (
                  <>
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-neon-cyan rounded-r shadow-[0_0_10px_var(--neon-cyan)]" />
                    <div className="absolute inset-0 bg-neon-cyan/5 rounded-lg border border-neon-cyan/20" />
                  </>
                )}

                {/* Icon */}
                <div className={`relative ${isActive ? 'text-neon-cyan' : 'text-slate-500 group-hover:text-slate-300'}`}>
                  <Icon size={18} className={isActive ? 'drop-shadow-[0_0_8px_var(--neon-cyan)]' : ''} />
                </div>

                {/* Label */}
                <span className={`font-semibold tracking-wide ${isActive ? 'text-glow-cyan' : ''}`}>
                  {item.label}
                </span>

                {/* Hover Arrow */}
                <div className={`ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-neon-cyan/40`}>
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M3 6H9M9 6L6 3M9 6L6 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                  </svg>
                </div>
              </Link>
            )
          })}
        </nav>

        {/* Bottom Section */}
        <div className="p-4 border-t border-neon-cyan/10">
          <div className="text-[10px] text-slate-600 font-mono tracking-widest uppercase mb-2 px-3">Core Modules</div>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-cyber-dark/50 p-2 rounded border border-neon-purple/20 hover:border-neon-purple/40 transition-colors">
              <div className="text-neon-purple text-xs font-bold">CEO</div>
              <div className="text-slate-600 text-[10px]">Engine</div>
            </div>
            <div className="bg-cyber-dark/50 p-2 rounded border border-neon-pink/20 hover:border-neon-pink/40 transition-colors">
              <div className="text-neon-pink text-xs font-bold">PM</div>
              <div className="text-slate-600 text-[10px]">Coord</div>
            </div>
          </div>
        </div>

        {/* Decorative Elements */}
        <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-cyber-dark to-transparent pointer-events-none" />
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-gradient-to-br from-cyber-dark via-cyber-black to-cyber-dark p-6 overflow-auto relative">
        {/* Corner Decorations */}
        <div className="fixed top-4 right-4 text-[10px] font-mono text-slate-600 tracking-widest">
          <span className="text-neon-cyan/40">//</span> CYBER_STUDIO <span className="text-neon-cyan/40">//</span>
        </div>

        {/* Main Content Area */}
        <div className="relative z-10">
          {children}
        </div>

        {/* Floating Particles */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="particle"
              style={{
                left: `${15 + i * 15}%`,
                animationDelay: `${i * 2}s`,
                animationDuration: `${8 + i * 2}s`,
              }}
            />
          ))}
        </div>
      </main>
    </div>
  )
}