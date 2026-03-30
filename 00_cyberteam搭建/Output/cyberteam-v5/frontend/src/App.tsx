import { useState, useEffect } from 'react'
import { Layout, Menu, Button, theme } from 'antd'
import { MessageOutlined, TeamOutlined, SettingOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import Chat from './pages/chat'
import ChatRoom from './pages/chat/ChatRoom'
import EmployeeMarketplace from './pages/employees'

const { Header, Sider, Content } = Layout

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  // 根据当前路径确定选中的菜单
  const getSelectedKey = () => {
    if (location.pathname.startsWith('/chat/')) return 'chat'
    if (location.pathname === '/employees') return 'employees'
    if (location.pathname === '/') return 'chat'
    return 'chat'
  }

  const renderContent = () => {
    const path = location.pathname

    if (path === '/chat' || path === '/') {
      return <Chat />
    }

    if (path.startsWith('/chat/')) {
      const id = path.split('/chat/')[1]
      return <ChatRoom />
    }

    if (path === '/employees') {
      return <EmployeeMarketplace />
    }

    return <Chat />
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', background: '#001529' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', marginRight: '40px' }}>
          CyberTeam v5.0
        </div>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: colorBgContainer }}>
          <Menu
            mode="inline"
            selectedKeys={[getSelectedKey()]}
            style={{ height: '100%', borderRight: 0 }}
            items={[
              {
                key: 'chat',
                icon: <MessageOutlined />,
                label: '对话',
                onClick: () => navigate('/chat'),
              },
              {
                key: 'employees',
                icon: <TeamOutlined />,
                label: '数字员工',
                onClick: () => navigate('/employees'),
              },
            ]}
          />
        </Sider>
        <Layout style={{ padding: '0' }}>
          <Content
            style={{
              padding: 0,
              margin: 0,
              minHeight: 280,
              background: colorBgContainer,
            }}
          >
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}
