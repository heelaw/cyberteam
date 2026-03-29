import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Input, Button, Card, Tag, Avatar, Space, Timeline, Typography, Tooltip } from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import { useChatStore } from '@/stores/chat'
import { cn } from '@/utils/cn'

const { TextArea } = Input
const { Text } = Typography

// Mock messages for demo
const demoMessages = [
  { id: '1', role: 'user' as const, name: '用户', dept: '', content: '帮我分析一下西北发面包子品牌的海岸城200平餐厅的市场策略' },
  { id: '2', role: 'agent' as const, name: 'CEO', dept: '决策层', content: '收到任务，我来分析一下。\n\n**任务拆解：**\n1. 市场调研分析\n2. 竞品分析\n3. 用户画像研究\n4. 营销策略制定\n\n首先需要收集海岸城商圈的真实数据，我来路由到增长部。', status: 'done' },
  { id: '3', role: 'agent' as const, name: 'COO', dept: '决策层', content: 'CEO 已完成路由分拣。我来制定执行计划：\n\n**执行计划：**\n- 增长部：市场调研 + 竞品分析\n- 产品部：用户画像 + 场景分析\n- 运营部：渠道策略 + 内容规划\n\n⚠️ 在讨论前需要先收集真实数据，不能凭空想象。', status: 'done' },
  { id: '4', role: 'agent' as const, name: '质疑者', dept: '质量门禁', content: '**质疑者审查：**\n\n❓ 目前缺少以下关键信息：\n1. 海岸城商圈客流数据 - 来源？\n2. 竞品品牌信息 - 是否经过搜索验证？\n3. 用户画像依据 - 有调研支撑吗？\n\n⚠️ 建议：先执行 Web Search 收集真实数据，再启动讨论。', status: 'done' },
  { id: '5', role: 'agent' as const, name: '增长总监', dept: '协调层', content: '数据收集完毕：\n\n**海岸城商圈数据：**\n- 日均客流：约12万人次 [来源：海岸城官方公众号]\n- 餐饮业态占比：约35% [来源：深圳商报]\n- 周边竞品：庆芳包子、汤sir记、稻香等 [来源：大众点评]\n\n现在可以启动策略讨论了。', status: 'streaming' },
]

const agentStatusPanel = [
  { name: 'CEO', dept: '决策层', status: 'done' as const },
  { name: 'COO', dept: '决策层', status: 'done' as const },
  { name: '质疑者', dept: '质量门禁', status: 'done' as const },
  { name: '增长总监', dept: '协调层', status: 'running' as const },
  { name: '产品总监', dept: '协调层', status: 'pending' as const },
  { name: '运营总监', dept: '协调层', status: 'pending' as const },
]

const statusIcon = {
  done: <SafetyCertificateOutlined className="text-green-500" />,
  running: <ThunderboltOutlined className="text-blue-500 animate-pulse" />,
  pending: <EyeOutlined className="text-gray-400" />,
}

export default function ChatRoom() {
  const { id } = useParams()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  const handleSend = () => {
    if (!input.trim()) return
    // TODO: 发送消息到后端
    setInput('')
  }

  return (
    <div className="flex h-full">
      {/* 中栏：消息流 */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {demoMessages.map((msg) => (
            <div key={msg.id} className={cn('flex gap-3', msg.role === 'user' ? 'flex-row-reverse' : 'flex-row')}>
              <Avatar
                icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                className={cn(
                  'flex-shrink-0',
                  msg.dept === '决策层' ? 'bg-yellow-500' :
                  msg.dept === '质量门禁' ? 'bg-red-500' :
                  msg.dept === '协调层' ? 'bg-blue-500' :
                  'bg-gray-500'
                )}
              />
              <Card
                size="small"
                className={cn(
                  'max-w-[70%]',
                  msg.role === 'user' ? 'bg-blue-50' : 'bg-white'
                )}
              >
                {msg.role === 'agent' && (
                  <div className="flex items-center gap-2 mb-1">
                    <Text strong className="text-sm">{msg.name}</Text>
                    <Tag color={
                      msg.dept === '决策层' ? 'gold' :
                      msg.dept === '质量门禁' ? 'red' :
                      msg.dept === '协调层' ? 'blue' : 'default'
                    } className="text-xs">{msg.dept}</Tag>
                  </div>
                )}
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </Card>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区 */}
        <div className="border-t bg-white p-3">
          <Space.Compact className="w-full">
            <TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入消息... (@提及 Agent)"
              autoSize={{ minRows: 1, maxRows: 4 }}
              onPressEnter={(e) => {
                if (!e.shiftKey) { e.preventDefault(); handleSend() }
              }}
              className="flex-1"
            />
            <Button type="primary" icon={<SendOutlined />} onClick={handleSend} className="h-auto">
              发送
            </Button>
          </Space.Compact>
        </div>
      </div>

      {/* 右栏：Agent 状态面板 */}
      <div className="w-72 border-l bg-white p-4 overflow-auto">
        <Typography.Title level={5} className="mb-3">Agent 执行状态</Typography.Title>
        <Timeline
          items={agentStatusPanel.map((a) => ({
            color: a.status === 'running' ? 'blue' : a.status === 'done' ? 'green' : 'gray',
            children: (
              <div className="flex items-center justify-between">
                <Space>
                  {statusIcon[a.status]}
                  <div>
                    <div className="text-sm font-medium">{a.name}</div>
                    <div className="text-xs text-gray-400">{a.dept}</div>
                  </div>
                </Space>
                <Tag color={a.status === 'running' ? 'processing' : a.status === 'done' ? 'success' : 'default'} className="text-xs">
                  {a.status === 'running' ? '执行中' : a.status === 'done' ? '完成' : '等待'}
                </Tag>
              </div>
            ),
          }))}
        />

        <div className="mt-4 pt-4 border-t">
          <Typography.Title level={5} className="mb-2">任务节点</Typography.Title>
          <Timeline
            items={[
              { color: 'green', children: 'CEO-COO 对齐' },
              { color: 'green', children: '策略讨论' },
              { color: 'blue', children: '信息收集' },
              { color: 'gray', children: '风险预案' },
              { color: 'gray', children: 'CEO 汇报' },
              { color: 'gray', children: '设计联动' },
              { color: 'gray', children: '文案产出' },
              { color: 'gray', children: 'CEO 汇总' },
            ]}
          />
        </div>
      </div>
    </div>
  )
}
