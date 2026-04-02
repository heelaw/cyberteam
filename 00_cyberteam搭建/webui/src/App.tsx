/*
  CyberTeam Studio — Main App Router
  <!--zh
  CyberTeam 主应用：路由 + 认证守卫 + 全局布局
  -->
*/
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import { ConfigProvider, theme as antdTheme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { Layout, Menu, Avatar, Dropdown, Space } from 'antd'
import {
  DashboardOutlined,
  TeamOutlined,
  MessageOutlined,
  ApartmentOutlined,
  ThunderboltOutlined,
  LogoutOutlined,
  UserOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { useAuthStore } from './stores/authStore'
import React, { useEffect, useState } from 'react'

// Pages
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Agents from './pages/Agents'
import Departments from './pages/Departments'
import Skills from './pages/Skills'
import Teams from './pages/Teams'
import Templates from './pages/Templates'
import Settings from './pages/Settings'
import Login from './pages/Login'

const { Header, Content } = Layout

// ─── Auth Guard ───────────────────────────────────────────────────────────────

function RequireAuth({ children }: { children: JSX.Element }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const token = useAuthStore((s) => s.token)
  const fetchUser = useAuthStore((s) => s.fetchUser)
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    if (token && !isAuthenticated) {
      fetchUser().finally(() => setChecked(true))
    } else {
      setChecked(true)
    }
  }, [token, isAuthenticated])

  if (!checked) return null
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

// ─── Main Layout ──────────────────────────────────────────────────────────────

function MainLayout({ children }: { children: JSX.Element }) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: <Link to="/">仪表盘</Link> },
    { key: '/chat', icon: <MessageOutlined />, label: <Link to="/chat">对话</Link> },
    { key: '/agents', icon: <TeamOutlined />, label: <Link to="/agents">数字员工</Link> },
    { key: '/departments', icon: <ApartmentOutlined />, label: <Link to="/departments">部门</Link> },
    { key: '/skills', icon: <ThunderboltOutlined />, label: <Link to="/skills">技能</Link> },
    { key: '/teams', icon: <TeamOutlined />, label: <Link to="/teams">团队</Link> },
    { key: '/templates', icon: <SettingOutlined />, label: <Link to="/templates">模板</Link> },
    { key: '/settings', icon: <SettingOutlined />, label: <Link to="/settings">设置</Link> },
  ]

  const userMenuItems = [
    { key: 'profile', icon: <UserOutlined />, label: user?.username || 'User' },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true, onClick: handleLogout },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          background: 'rgba(10, 15, 30, 0.95)',
          borderBottom: '1px solid rgba(0, 245, 255, 0.15)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 16px',
          backdropFilter: 'blur(10px)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            color: '#00f5ff',
            fontSize: 18,
            fontWeight: 700,
            marginRight: 32,
            letterSpacing: '0.05em',
            whiteSpace: 'nowrap',
          }}
        >
          CYBERTEAM
        </div>

        <Menu
          mode="horizontal"
          theme="dark"
          items={menuItems}
          style={{ background: 'transparent', border: 'none', flex: 1, minWidth: 0 }}
        />

        <Space size={16}>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar
                size={32}
                style={{ background: 'rgba(0, 245, 255, 0.2)', color: '#00f5ff' }}
              >
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </Avatar>
              <span style={{ color: '#e2e8f0', fontSize: 14 }}>{user?.username}</span>
            </Space>
          </Dropdown>
        </Space>
      </Header>

      <Content style={{ background: '#0a0f1e', minHeight: 'calc(100vh - 64px)' }}>
        <div style={{ maxWidth: 1400, margin: '0 auto', padding: '24px 16px' }}>
          {children}
        </div>
      </Content>
    </Layout>
  )
}

// ─── Router ───────────────────────────────────────────────────────────────────

export default function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: antdTheme.darkAlgorithm,
        token: {
          colorPrimary: '#00f5ff',
          colorBgContainer: '#0a1929',
          colorBgElevated: '#0d1525',
          colorBgLayout: '#0a0f1e',
          colorBorder: 'rgba(0, 217, 255, 0.2)',
          colorText: '#e2e8f0',
          colorTextSecondary: '#94a3b8',
          colorTextTertiary: '#64748b',
          colorFillQuaternary: 'rgba(0, 240, 255, 0.04)',
          fontFamily: 'Inter, system-ui, sans-serif',
          borderRadius: 8,
        },
        components: {
          Menu: {
            darkItemBg: 'transparent',
            darkSubMenuItemBg: 'transparent',
            darkItemSelectedBg: 'rgba(0, 240, 255, 0.1)',
            darkItemHoverBg: 'rgba(0, 240, 255, 0.06)',
          },
          Button: {
            primaryShadow: '0 0 15px rgba(0, 245, 255, 0.3)',
          },
          Card: {
            colorBorderSecondary: 'rgba(0, 240, 255, 0.12)',
          },
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/"
            element={
              <RequireAuth>
                <MainLayout>
                  <Dashboard />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route
            path="/chat/*"
            element={
              <RequireAuth>
                <MainLayout>
                  <Chat />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route
            path="/agents"
            element={
              <RequireAuth>
                <MainLayout>
                  <Agents />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route
            path="/departments"
            element={
              <RequireAuth>
                <MainLayout>
                  <Departments />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route
            path="/skills"
            element={
              <RequireAuth>
                <MainLayout>
                  <Skills />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route
            path="/teams"
            element={
              <RequireAuth>
                <MainLayout>
                  <Teams />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route
            path="/templates"
            element={
              <RequireAuth>
                <MainLayout>
                  <Templates />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route
            path="/skills"
            element={
              <RequireAuth>
                <MainLayout>
                  <Skills />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route
            path="/settings"
            element={
              <RequireAuth>
                <MainLayout>
                  <Settings />
                </MainLayout>
              </RequireAuth>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}
