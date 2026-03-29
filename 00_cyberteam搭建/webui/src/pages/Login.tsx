/**
 * Login Page
 * <!--zh
 * 登录页：用户名密码表单，登录成功后跳转到首页
 * -->
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Button, Alert, Typography } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useAuthStore } from '../stores/authStore'

const { Title, Text } = Typography

export default function Login() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleSubmit = async (values: { username: string; password: string }) => {
    setLoading(true)
    setError(null)
    try {
      await login(values.username, values.password)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0f1e 0%, #1a1f3e 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          background: 'rgba(26, 31, 62, 0.9)',
          border: '1px solid rgba(0, 245, 255, 0.2)',
          borderRadius: 12,
        }}
        styles={{ body: { padding: 32 } }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2} style={{ color: '#00f5ff', margin: 0 }}>
            CyberTeam Studio
          </Title>
          <Text style={{ color: '#8b9dc3' }}>企业级 AI Agent 协作系统</Text>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}

        <Form onFinish={handleSubmit} layout="vertical" size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined style={{ color: '#8b9dc3' }} />}
              placeholder="用户名 (demo)"
              style={{
                background: 'rgba(10, 15, 30, 0.8)',
                border: '1px solid rgba(0, 245, 255, 0.3)',
                color: '#fff',
              }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#8b9dc3' }} />}
              placeholder="密码 (demo123)"
              style={{
                background: 'rgba(10, 15, 30, 0.8)',
                border: '1px solid rgba(0, 245, 255, 0.3)',
                color: '#fff',
              }}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{
                background: 'linear-gradient(135deg, #00f5ff 0%, #0080ff 100%)',
                border: 'none',
                height: 44,
                fontSize: 16,
                fontWeight: 600,
              }}
            >
              登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Text style={{ color: '#8b9dc3', fontSize: 12 }}>
              测试账号: demo / demo123
            </Text>
          </div>
        </Form>
      </Card>
    </div>
  )
}
