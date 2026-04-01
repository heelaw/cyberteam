import React, { useState } from 'react'
import Settings from './Settings'
import Skills from './Skills'
import Agents from './Agents'
import Chat from './Chat'
import {
  Settings as SettingsIcon,
  Puzzle,
  Bot,
  MessageSquare,
  ChevronRight,
} from 'lucide-react'

type Page = 'settings' | 'skills' | 'agents' | 'chat'

export default function Index() {
  const [activePage, setActivePage] = useState<Page>('chat')

  const navItems: { id: Page; label: string; icon: React.ReactNode }[] = [
    { id: 'chat', label: '对话', icon: <MessageSquare size={20} /> },
    { id: 'agents', label: '智能体', icon: <Bot size={20} /> },
    { id: 'skills', label: '技能中心', icon: <Puzzle size={20} /> },
    { id: 'settings', label: '设置', icon: <SettingsIcon size={20} /> },
  ]

  const renderPage = () => {
    switch (activePage) {
      case 'settings':
        return <Settings />
      case 'skills':
        return <Skills />
      case 'agents':
        return <Agents />
      case 'chat':
      default:
        return <Chat />
    }
  }

  return (
    <div style={styles.container}>
      {/* 侧边导航 */}
      <nav style={styles.sidebar}>
        <div style={styles.logo}>
          <span style={styles.logoText}>CyberTeam</span>
        </div>

        <div style={styles.navList}>
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              style={{
                ...styles.navItem,
                ...(activePage === item.id ? styles.navItemActive : {}),
              }}
            >
              <span style={styles.navIcon}>{item.icon}</span>
              <span style={styles.navLabel}>{item.label}</span>
              {activePage === item.id && <ChevronRight size={16} style={styles.navArrow} />}
            </button>
          ))}
        </div>

        <div style={styles.statusBar}>
          <div style={styles.statusDot} />
          <span style={styles.statusText}>Claude Code 已连接</span>
        </div>
      </nav>

      {/* 主内容区 */}
      <main style={styles.main}>
        {renderPage()}
      </main>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    height: '100vh',
    backgroundColor: '#0D1117',
    color: '#E6EDF3',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  sidebar: {
    width: 220,
    backgroundColor: '#161B22',
    borderRight: '1px solid #30363D',
    display: 'flex',
    flexDirection: 'column',
    padding: '16px 0',
  },
  logo: {
    padding: '0 16px 24px',
    borderBottom: '1px solid #30363D',
    marginBottom: 16,
  },
  logoText: {
    fontSize: 18,
    fontWeight: 700,
    color: '#58A6FF',
    letterSpacing: '-0.5px',
  },
  navList: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
    padding: '0 8px',
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '10px 12px',
    borderRadius: 8,
    border: 'none',
    background: 'transparent',
    color: '#8B949E',
    cursor: 'pointer',
    fontSize: 14,
    textAlign: 'left',
    width: '100%',
    transition: 'all 0.15s ease',
  },
  navItemActive: {
    backgroundColor: '#1F6FEB20',
    color: '#58A6FF',
  },
  navIcon: {
    display: 'flex',
    alignItems: 'center',
    flexShrink: 0,
  },
  navLabel: {
    flex: 1,
    fontWeight: 500,
  },
  navArrow: {
    opacity: 0.5,
  },
  statusBar: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '12px 16px',
    borderTop: '1px solid #30363D',
    marginTop: 16,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    backgroundColor: '#3FB950',
    boxShadow: '0 0 8px #3FB95080',
  },
  statusText: {
    fontSize: 12,
    color: '#8B949E',
  },
  main: {
    flex: 1,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
}
