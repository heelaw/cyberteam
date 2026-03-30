import { Card, Form, Input, InputNumber, Select, Switch, Slider, Button, Tabs, Typography, Space, message } from 'antd'
import { SettingOutlined, ApiOutlined, SafetyCertificateOutlined, DollarOutlined } from '@ant-design/icons'

const { Title } = Typography

export default function Settings() {
  const [messageApi, contextHolder] = message.useMessage()

  const handleSave = () => {
    messageApi.success('设置已保存')
  }

  return (
    <div className="p-6 max-w-4xl">
      {contextHolder}
      <Title level={3}><SettingOutlined className="mr-2" /> 系统设置</Title>

      <Tabs items={[
        {
          key: 'model',
          label: '模型配置',
          children: (
            <Card>
              <Form layout="vertical" onFinish={handleSave}>
                <Form.Item label="CEO 决策模型" initialValue="claude-opus-4-6">
                  <Select options={[
                    { value: 'claude-opus-4-6', label: 'Claude Opus 4.6 (最强)' },
                    { value: 'claude-sonnet-4-6', label: 'Claude Sonnet 4.6 (平衡)' },
                    { value: 'claude-haiku-4-5', label: 'Claude Haiku 4.5 (快速)' },
                  ]} />
                </Form.Item>
                <Form.Item label="执行层模型" initialValue="claude-haiku-4-5">
                  <Select options={[
                    { value: 'claude-sonnet-4-6', label: 'Claude Sonnet 4.6' },
                    { value: 'claude-haiku-4-5', label: 'Claude Haiku 4.5 (推荐)' },
                  ]} />
                </Form.Item>
                <Form.Item label="预算模式" initialValue="normal">
                  <Select options={[
                    { value: 'economy', label: '经济模式（使用快速模型）' },
                    { value: 'normal', label: '标准模式（平衡模型）' },
                    { value: 'premium', label: '高级模式（使用最强模型）' },
                  ]} />
                </Form.Item>
                <Button type="primary" htmlType="submit">保存</Button>
              </Form>
            </Card>
          ),
        },
        {
          key: 'budget',
          label: '预算设置',
          children: (
            <Card>
              <Form layout="vertical" onFinish={handleSave}>
                <Form.Item label="每日预算上限 (USD)" initialValue={50}>
                  <Slider min={1} max={200} marks={{ 1: '$1', 50: '$50', 100: '$100', 200: '$200' }} />
                </Form.Item>
                <Form.Item label="单任务预算上限 (USD)" initialValue={10}>
                  <InputNumber min={0.1} max={100} step={0.1} className="w-full" />
                </Form.Item>
                <Form.Item label="预算超限自动暂停" valuePropName="checked" initialValue={true}>
                  <Switch />
                </Form.Item>
                <Button type="primary" htmlType="submit">保存</Button>
              </Form>
            </Card>
          ),
        },
        {
          key: 'api',
          label: 'API Key',
          children: (
            <Card>
              <Form layout="vertical" onFinish={handleSave}>
                <Form.Item label="Anthropic API Key">
                  <Input.Password placeholder="sk-ant-..." />
                </Form.Item>
                <Form.Item label="OpenAI API Key (可选)">
                  <Input.Password placeholder="sk-..." />
                </Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit">保存</Button>
                  <Button>测试连接</Button>
                </Space>
              </Form>
            </Card>
          ),
        },
        {
          key: 'notification',
          label: '通知设置',
          children: (
            <Card>
              <Form layout="vertical" onFinish={handleSave}>
                <Form.Item label="Agent 任务完成通知" valuePropName="checked" initialValue={true}>
                  <Switch />
                </Form.Item>
                <Form.Item label="审批请求通知" valuePropName="checked" initialValue={true}>
                  <Switch />
                </Form.Item>
                <Form.Item label="预算预警通知" valuePropName="checked" initialValue={true}>
                  <Switch />
                </Form.Item>
                <Form.Item label="预算预警阈值 (%)" initialValue={80}>
                  <Slider min={50} max={100} marks={{ 50: '50%', 80: '80%', 100: '100%' }} />
                </Form.Item>
                <Button type="primary" htmlType="submit">保存</Button>
              </Form>
            </Card>
          ),
        },
      ]} />
    </div>
  )
}
