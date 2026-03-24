import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import { Sidebar, Header } from '@/components/layout'
import {
  DashboardPage,
  KanbanPage,
  AgentsPage,
  MessagesPage,
  SettingsPage,
} from '@/pages'
import { useDashboardStore } from '@/store'
import { cn } from '@/lib/utils'

function AppContent() {
  const sidebarCollapsed = useDashboardStore((state) => state.sidebarCollapsed)

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <Header />
      <main
        className={cn(
          'pt-16 transition-all duration-300',
          sidebarCollapsed ? 'pl-16' : 'pl-64'
        )}
      >
        <div className="p-6">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/kanban" element={<KanbanPage />} />
            <Route path="/agents" element={<AgentsPage />} />
            <Route path="/messages" element={<MessagesPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>
      </main>
      <Toaster position="top-right" />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}

export default App
