import { useState } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'

export default function App() {
  const location = useLocation()

  const navItems = [
    { path: '/chat', label: '对话', icon: '💬' },
    { path: '/departments', label: '部门', icon: '🏢' },
    { path: '/agents', label: 'Agent', icon: '🤖' },
    { path: '/skills', label: 'Skill', icon: '⚡' },
    { path: '/market', label: '市场', icon: '🛒' },
    { path: '/settings', label: '设置', icon: '⚙️' },
  ]

  return (
    <div className="flex h-full">
      {/* 侧边栏 */}
      <nav className="w-16 bg-[#111118] border-r border-[#2a2a3a] flex flex-col items-center py-4 gap-2">
        {/* Logo */}
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-lg font-bold mb-4">
          CT
        </div>

        {/* 导航项 */}
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `w-12 h-12 rounded-lg flex flex-col items-center justify-center text-xs transition-all ${
                isActive
                  ? 'bg-[#6366f1] text-white'
                  : 'text-[#606070] hover:text-white hover:bg-[#1a1a24]'
              }`
            }
          >
            <span className="text-xl">{item.icon}</span>
            <span className="mt-1">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* 主内容区 */}
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
