import React, { Component, type ErrorInfo, type ReactNode } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import App from './App'
import ChatPage from './pages/chat/ChatPage'
import SettingsPage from './pages/settings/SettingsPage'
import DepartmentsPage from './pages/departments/DepartmentsPage'
import MarketPage from './pages/market/MarketPage'
import AgentsPage from './pages/agents/AgentsPage'
import SkillsPage from './pages/skills/SkillsPage'
import './index.css'

// 全局 ErrorBoundary — 防止任何页面 JS 报错导致黑屏
class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: string }> {
  state = { hasError: false, error: '' }

  static getDerivedStateFromError(err: Error) {
    return { hasError: true, error: err.message || String(err) }
  }

  componentDidCatch(err: Error, info: ErrorInfo) {
    console.error('[ErrorBoundary]', err, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 40, color: '#fff', background: '#0a0a0f', height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <h2 style={{ fontSize: 20, marginBottom: 12 }}>页面出错了</h2>
          <pre style={{ color: '#f87171', fontSize: 13, maxWidth: 600, whiteSpace: 'pre-wrap', background: '#1a1a2e', padding: 16, borderRadius: 8 }}>{this.state.error}</pre>
          <button onClick={() => { this.setState({ hasError: false, error: '' }); window.location.reload() }} style={{ marginTop: 20, padding: '8px 24px', background: '#3b82f6', border: 'none', borderRadius: 6, color: '#fff', cursor: 'pointer' }}>刷新页面</button>
        </div>
      )
    }
    return this.props.children
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<Navigate to="/chat" replace />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="chat/:sessionId" element={<ChatPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="departments" element={<DepartmentsPage />} />
            <Route path="market" element={<MarketPage />} />
            <Route path="agents" element={<AgentsPage />} />
          <Route path="skills" element={<SkillsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
)
