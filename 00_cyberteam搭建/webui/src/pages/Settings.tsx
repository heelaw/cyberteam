import { useState } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Switch,
  Button,
  Tabs,
  message,
  Divider,
  Space,
  Typography,
  Tag,
} from 'antd'
import {
  SettingOutlined,
  ApiOutlined,
  RobotOutlined,
  SafetyOutlined,
  SaveOutlined,
} from '@ant-design/icons'

const { Title, Text, Paragraph } = Typography
const { Option } = Select

interface EngineConfig {
  type: 'claude_cli' | 'api'
  model: string
  apiBase: string
  apiKey: string
}

interface SystemConfig {
  maxTokens: number
  temperature: number
  contextWindow: number
  streamOutput: boolean
  debugMode: boolean
}

const DEFAULT_ENGINE: EngineConfig = {
  type: 'claude_cli',
  model: 'claude-sonnet-4-6',
  apiBase: 'https://api.anthropic.com',
  apiKey: '',
}

const DEFAULT_SYSTEM: SystemConfig = {
  maxTokens: 4096,
  temperature: 0.7,
  contextWindow: 200000,
  streamOutput: true,
  debugMode: false,
}

export default function Settings() {
  const [engine, setEngine] = useState<EngineConfig>(() => {
    const saved = localStorage.getItem('cyberteam-engine')
    return saved ? JSON.parse(saved) : DEFAULT_ENGINE
  })
  const [system, setSystem] = useState<SystemConfig>(() => {
    const saved = localStorage.getItem('cyberteam-system')
    return saved ? JSON.parse(saved) : DEFAULT_SYSTEM
  })
  const [saving, setSaving] = useState(false)

  const handleSave = () => {
    setSaving(true)
    setTimeout(() => {
      localStorage.setItem('cyberteam-engine', JSON.stringify(engine))
      localStorage.setItem('cyberteam-system', JSON.stringify(system))
      message.success('设置已保存')
      setSaving(false)
    }, 500)
  }

  const handleReset = () => {
    setEngine(DEFAULT_ENGINE)
    setSystem(DEFAULT_SYSTEM)
    localStorage.removeItem('cyberteam-engine')
    localStorage.removeItem('cyberteam-system')
    message.info('已恢复默认设置')
  }

  const tabItems = [
    {
      key: 'engine',
      label: (
        <span>
          <RobotOutlined /> AI 引擎
        </span>
      ),
      children: (
        <div className="space-y-4">
          <Card size="small" title="引擎模式" className="bg-[var(--color-bg-elevated)]">
            <Form layout="vertical" size="small">
              <Form.Item label="引擎类型">
                <Select
                  value={engine.type}
                  onChange={(v) => setEngine({ ...engine, type: v })}
                >
                  <Option value="claude_cli">
                    <Space>
                      <Tag color="green">本地</Tag>
                      Claude Code CLI（使用本机 Claude Code）
                    </Space>
                  </Option>
                  <Option value="api">
                    <Space>
                      <Tag color="blue">云端</Tag>
                      API 模式（通过 API Key 调用）
                    </Space>
                  </Option>
                </Select>
              </Form.Item>

              {engine.type === 'claude_cli' && (
                <div className="p-3 rounded bg-[var(--color-bg-spotlight)] text-xs">
                  <Text type="secondary">
                    Claude Code 模式使用您本机安装的 Claude Code CLI，
                    通过 SSE 流式输出实现实时对话。
                    无需 API Key，使用您 Claude Code 自带的额度。
                  </Text>
                  <div className="mt-2 flex items-center gap-2">
                    <Tag color="success">零成本</Tag>
                    <Tag color="processing">完整 Tool Use</Tag>
                    <Tag color="warning">需安装 Claude Code</Tag>
                  </div>
                </div>
              )}

              {engine.type === 'api' && (
                <>
                  <Form.Item label="API 基础地址">
                    <Input
                      value={engine.apiBase}
                      onChange={(e) => setEngine({ ...engine, apiBase: e.target.value })}
                      placeholder="https://api.anthropic.com"
                    />
                  </Form.Item>
                  <Form.Item label="API Key">
                    <Input.Password
                      value={engine.apiKey}
                      onChange={(e) => setEngine({ ...engine, apiKey: e.target.value })}
                      placeholder="sk-ant-..."
                    />
                  </Form.Item>
                </>
              )}

              <Form.Item label="默认模型">
                <Select
                  value={engine.model}
                  onChange={(v) => setEngine({ ...engine, model: v })}
                >
                  <Option value="claude-opus-4-6">Claude Opus 4.6（最强）</Option>
                  <Option value="claude-sonnet-4-6">Claude Sonnet 4.6（平衡）</Option>
                  <Option value="claude-haiku-4-5">Claude Haiku 4.5（快速）</Option>
                </Select>
              </Form.Item>
            </Form>
          </Card>
        </div>
      ),
    },
    {
      key: 'system',
      label: (
        <span>
          <SettingOutlined /> 系统设置
        </span>
      ),
      children: (
        <Card size="small" title="对话参数" className="bg-[var(--color-bg-elevated)]">
          <Form layout="vertical" size="small">
            <Form.Item label={`最大输出 Tokens：${system.maxTokens}`}>
              <input
                type="range"
                min={1024}
                max={32000}
                step={1024}
                value={system.maxTokens}
                onChange={(e) => setSystem({ ...system, maxTokens: Number(e.target.value) })}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>1K</span>
                <span>32K</span>
              </div>
            </Form.Item>

            <Form.Item label={`温度：${system.temperature.toFixed(1)}`}>
              <input
                type="range"
                min={0}
                max={1}
                step={0.1}
                value={system.temperature}
                onChange={(e) => setSystem({ ...system, temperature: Number(e.target.value) })}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>精确 (0)</span>
                <span>创意 (1)</span>
              </div>
            </Form.Item>

            <Divider />

            <Form.Item label="流式输出">
              <Switch
                checked={system.streamOutput}
                onChange={(v) => setSystem({ ...system, streamOutput: v })}
              />
              <Text type="secondary" className="ml-3">
                实时显示 AI 生成内容（推荐开启）
              </Text>
            </Form.Item>

            <Form.Item label="调试模式">
              <Switch
                checked={system.debugMode}
                onChange={(v) => setSystem({ ...system, debugMode: v })}
              />
              <Text type="secondary" className="ml-3">
                显示完整的 Agent 执行日志和工具调用详情
              </Text>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'about',
      label: (
        <span>
          <ApiOutlined /> 关于
        </span>
      ),
      children: (
        <Card size="small" className="bg-[var(--color-bg-elevated)]">
          <Title level={4}>CyberTeam Studio v4.1.0</Title>
          <Paragraph type="secondary">
            企业级 AI Agent 协作系统，模拟真实公司组织架构，
            实现多 Agent 并行处理和智能协作。
          </Paragraph>
          <Divider />
          <div className="space-y-2">
            <div className="flex justify-between">
              <Text type="secondary">引擎版本</Text>
              <Text>v4.1.0 (Edict 三省六部)</Text>
            </div>
            <div className="flex justify-between">
              <Text type="secondary">Agent 数量</Text>
              <Text>14 个数字员工</Text>
            </div>
            <div className="flex justify-between">
              <Text type="secondary">部门数量</Text>
              <Text>9 个部门</Text>
            </div>
            <div className="flex justify-between">
              <Text type="secondary">AI 引擎</Text>
              <Tag color="green">Claude Code CLI</Tag>
            </div>
            <div className="flex justify-between">
              <Text type="secondary">通信协议</Text>
              <Text>SSE (Server-Sent Events)</Text>
            </div>
          </div>
          <Divider />
          <Text type="secondary" className="text-xs">
            Built with React 18 + Ant Design 5 + FastAPI + Claude Agent SDK
          </Text>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <Title level={3} className="!mb-0">
          <SettingOutlined className="mr-2" />
          系统设置
        </Title>
        <Space>
          <Button onClick={handleReset}>恢复默认</Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            loading={saving}
            onClick={handleSave}
          >
            保存设置
          </Button>
        </Space>
      </div>

      <Tabs items={tabItems} />
    </div>
  )
}
