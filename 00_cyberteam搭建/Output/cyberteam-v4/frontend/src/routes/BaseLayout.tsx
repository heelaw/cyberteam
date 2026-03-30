import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  MessageOutlined,
  TeamOutlined,
  ProjectOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  UnorderedListOutlined,
  RobotOutlined,
} from '@ant-design/icons'

const { Sider, Content } = Layout

const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/chat', icon: <MessageOutlined />, label: '对话' },
  { key: '/agents', icon: <TeamOutlined />, label: 'Agent 管理' },
  { key: '/departments', icon: <UnorderedListOutlined />, label: '部门管理' },
  { key: '/custom-agents', icon: <RobotOutlined />, label: '自定义 Agent' },
  { key: '/projects', icon: <ProjectOutlined />, label: '项目中心' },
  { key: '/settings', icon: <SettingOutlined />, label: '系统设置' },
]

export default function BaseLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const selectedKey = '/' + (location.pathname.split('/')[1] || 'dashboard')

  return (
    <Layout className="h-screen">
      <Sider width={200} theme="dark" className="flex flex-col">
        <div className="flex items-center gap-2 px-4 py-4 text-white">
          <ThunderboltOutlined className="text-2xl text-yellow-400" />
          <span className="text-lg font-bold">CyberTeam</span>
          <span className="text-xs text-gray-400">v4.1</span>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          className="flex-1"
        />
        <div className="px-4 py-3 text-xs text-gray-500">
          三省六部 · 群体智能
        </div>
      </Sider>
      <Layout>
        <Content className="overflow-auto bg-gray-50">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
