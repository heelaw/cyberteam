import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider, App as AntdApp } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import AppRoutes from '@/routes/routes'

export default function App() {
  return (
    <BrowserRouter>
      <ConfigProvider locale={zhCN} theme={{ token: { colorPrimary: '#3b82f6', borderRadius: 8 } }}>
        <AntdApp>
          <AppRoutes />
        </AntdApp>
      </ConfigProvider>
    </BrowserRouter>
  )
}
