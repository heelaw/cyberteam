import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { listen, UnlistenFn } from '@tauri-apps/api/event'
import type { Page } from './types'
import Sidebar from './components/Sidebar'
import Settings from './pages/settings'
import Skills from './pages/skills'
import Agents from './pages/agents'
import Chat from './pages/chat'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('chat')
  const [claudePath, setClaudePath] = useState<string>('/opt/homebrew/bin/claude')
  const [apiKey, setApiKey] = useState<string>('')

  useEffect(() => {
    // Load saved settings
    invoke<string>('get_setting', { key: 'claude_path' })
      .then(setClaudePath)
      .catch(() => {})
    invoke<string>('get_setting', { key: 'api_key' })
      .then(setApiKey)
      .catch(() => {})

    // Listen for events from backend
    const unlisten = listen<string>('claude-output', (event) => {
      console.log('Claude output:', event.payload)
    })

    return () => {
      unlisten.then((fn: UnlistenFn) => fn())
    }
  }, [])

  const renderPage = () => {
    switch (currentPage) {
      case 'chat':
        return <Chat claudePath={claudePath} apiKey={apiKey} />
      case 'settings':
        return <Settings claudePath={claudePath} setClaudePath={setClaudePath} apiKey={apiKey} setApiKey={setApiKey} />
      case 'skills':
        return <Skills />
      case 'agents':
        return <Agents />
      default:
        return <Chat claudePath={claudePath} apiKey={apiKey} />
    }
  }

  return (
    <div className="flex h-screen bg-slate-900">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <main className="flex-1 overflow-hidden">
        {renderPage()}
      </main>
    </div>
  )
}

export default App
