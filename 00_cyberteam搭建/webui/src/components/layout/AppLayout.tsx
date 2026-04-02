import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, Building2, Users, Network, FileText, Wrench, Settings, Cpu, Zap, User } from 'lucide-react'
import { Dropdown, Avatar, Layout } from 'antd'
import type { MenuProps } from 'antd'

const { Header, Sider, Content } = Layout

const navItems = [
  { path: '/', label: '首页', icon: LayoutDashboard },
  { path: '/chat', label: '对话', icon: MessageSquare },
  { path: '/departments', label: '部门管理', icon: Building2 },
  { path: '/agents', label: 'Agent管理', icon: Users },
  { path: '/teams', label: '团队构建', icon: Network },
  { path: '/templates', label: '模板市场', icon: FileText },
  { path: '/skills', label: '技能配置', icon: Wrench },
]

const userMenuItems: MenuProps['items'] = [
  { key: 'profile', label: '个人资料' },
  { key: 'settings', label: '设置' },
  { type: 'divider' },
  { key: 'logout', label: '退出登录' }
]

interface AppLayoutProps {
  children: ReactNode
}

export default function AppLayout({ children }: AppLayoutProps) {
  const location = useLocation()

  return (
    <Layout className="min-h-screen bg-cyber-dark">
      {/* Sidebar */}
      <Sider
        width={240}
        className="bg-cyber-panel border-r border-neon-cyan/20"
      >
        {/* Logo */}
        <div className="p-5 border-b border-neon-cyan/10">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-cyber-dark border border-neon-cyan/40 flex items-center justify-center">
              <Cpu className="text-neon-cyan w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-wider text-white">
                CYBER<span className="text-neon-cyan">TEAM</span>
              </h1>
              <p className="text-[10px] text-neon-cyan/60 font-mono tracking-widest">Studio v4.0</p>
            </div>
          </Link>
        </div>

        {/* Status */}
        <div className="mx-4 p-3 bg-cyber-dark/50 border border-neon-cyan/10 rounded-lg my-4">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500 font-mono">SYSTEM</span>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-neon-green rounded-full animate-pulse" />
              <span className="text-neon-green font-mono">ONLINE</span>
            </div>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Zap className="text-neon-yellow w-3 h-3" />
            <span className="text-slate-400 text-xs">Neural Link Active</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-3">
          <div className="text-[10px] text-slate-600 font-mono tracking-widest uppercase mb-3 px-3">导航</div>
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 mb-1 rounded-lg transition-all ${
                  isActive
                    ? 'bg-neon-cyan/10 text-neon-cyan border-l-2 border-neon-cyan'
                    : 'text-slate-400 hover:bg-cyber-dark/50 hover:text-slate-200'
                }`}
              >
                <Icon size={18} />
                <span className="font-semibold tracking-wide">{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </Sider>

      <Layout>
        {/* Header */}
        <Header className="bg-cyber-panel border-b border-neon-cyan/20 px-6 flex items-center justify-between">
          <div className="text-sm text-slate-400">
            <span className="text-neon-cyan/40">//</span> CyberTeam Studio <span className="text-neon-cyan/40">//</span>
          </div>

          <div className="flex items-center gap-4">
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div className="flex items-center gap-2 cursor-pointer hover:bg-cyber-dark/50 px-3 py-2 rounded-lg transition-colors">
                <Avatar icon={<User />} size="small" className="bg-neon-cyan" />
                <span className="text-slate-300 text-sm">Admin</span>
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* Content */}
        <Content className="p-6 bg-gradient-to-br from-cyber-dark via-cyber-black to-cyber-dark overflow-auto">
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}