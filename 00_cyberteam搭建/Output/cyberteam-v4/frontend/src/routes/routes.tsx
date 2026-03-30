import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Spin } from 'antd'
import BaseLayout from '@/routes/BaseLayout'

const Dashboard = lazy(() => import('@/pages/dashboard'))
const Chat = lazy(() => import('@/pages/chat'))
const ChatRoom = lazy(() => import('@/pages/chat/ChatRoom'))
const AgentManagement = lazy(() => import('@/pages/agents'))
const Departments = lazy(() => import('@/pages/departments'))
const CustomAgents = lazy(() => import('@/pages/custom-agents'))
const ProjectList = lazy(() => import('@/pages/projects'))
const ProjectDetail = lazy(() => import('@/pages/projects/ProjectDetail'))
const Settings = lazy(() => import('@/pages/settings'))
const Organization = lazy(() => import('@/pages/organization'))

function LazyLoad({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<div className="flex h-screen items-center justify-center"><Spin size="large" /></div>}>{children}</Suspense>
}

export default function AppRoutes() {
  return (
    <LazyLoad>
      <Routes>
        <Route element={<BaseLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat/:id" element={<ChatRoom />} />
          <Route path="/agents" element={<AgentManagement />} />
          <Route path="/departments" element={<Departments />} />
          <Route path="/custom-agents" element={<CustomAgents />} />
          <Route path="/projects" element={<ProjectList />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/organization" element={<Organization />} />
        </Route>
      </Routes>
    </LazyLoad>
  )
}
