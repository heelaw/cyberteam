/**
 * ChatRoom — 数字军团对话页面
 *
 * 核心功能：
 * - 消息发送与接收
 * - SSE 流式响应
 * - Agent 状态面板
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Input, Button, Card, Tag, Avatar, Space, Timeline, Typography, message } from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  EyeOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import { fetchMessages, sendMessage } from '@/apis/modules/chat'
import type { Message } from '@/types'

const { TextArea } = Input
const { Text } = Typography

// === Agent 状态面板类型 ===
type AgentStatus = 'pending' | 'running' | 'done' | 'error'

interface AgentStatusItem {
  name: string
  dept: string
  status: AgentStatus
  output?: string
}

const defaultAgents: AgentStatusItem[] = [
  { name: 'CEO', dept: '决策层', status: 'pending' },
  { name: 'COO', dept: '决策层', status: 'pending' },
  { name: '质疑者', dept: '质量门禁', status: 'pending' },
  { name: '增长总监', dept: '协调层', status: 'pending' },
  { name: '产品总监', dept: '协调层', status: 'pending' },
]

// 流程节点
const processSteps = [
  { label: 'CEO-COO 对齐', key: 'ceo_aligned' },
  { label: '策略讨论', key: 'strategy' },
  { label: '信息收集', key: 'research' },
  { label: '风险预案', key: 'risk' },
  { label: 'CEO 汇总', key: 'ceo_summary' },
]

const statusIcon = (s: AgentStatus) => {
  if (s === 'done') return <SafetyCertificateOutlined className="text-green-500" />
  if (s === 'running') return <ThunderboltOutlined className="text-blue-500 animate-pulse" />
  if (s === 'error') return <EyeOutlined className="text-red-500" />
  return <EyeOutlined className="text-gray-300" />
}

export default function ChatRoom() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [agentStatuses, setAgentStatuses] = useState<AgentStatusItem[]>(defaultAgents)
  const [currentStep, setCurrentStep] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 加载消息
  const loadMessages = useCallback(async () => {
    if (!id) return
    try {
      const data = await fetchMessages(id)
      setMessages(data)
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }, [id])

  useEffect(() => {
    loadMessages()
  }, [loadMessages])

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 发送消息
  const handleSend = async () => {
    if (!input.trim() || !id) return

    const userMessage: Message = {
      id: `temp_${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: Date.now()
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    // 模拟 Agent 状态更新
    setAgentStatuses((prev) =>
      prev.map((a, i) => i === 0 ? { ...a, status: 'running' } : a)
    )
    setCurrentStep(1)

    try {
      const response = await sendMessage(id, input)

      // 更新消息
      setMessages((prev) => [...prev, response.message])

      // 更新 Agent 状态
      setAgentStatuses((prev) =>
        prev.map((a, i) => i === 0 ? { ...a, status: 'done' } : a)
      )
      setCurrentStep(5)

    } catch (error) {
      message.error('发送失败')
      setAgentStatuses((prev) =>
        prev.map((a, i) => i === 0 ? { ...a, status: 'error' } : a)
      )
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-full">
      {/* 左栏：消息列表 */}
      <div className="flex-1 flex flex-col">
        {/* 头部 */}
        <div className="h-14 border-b flex items-center px-4 bg-white">
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/chat')}
            className="mr-2"
          />
          <Text strong>对话 {id}</Text>
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-auto p-4 bg-gray-50">
          {messages.length === 0 ? (
            <div className="text-center text-gray-400 mt-20">
              <RobotOutlined className="text-4xl mb-2" />
              <p>开始一个新的对话</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex mb-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex max-w-[70%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <Avatar
                    size={32}
                    icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    className={msg.role === 'assistant' ? 'bg-blue-500' : ''}
                  />
                  <div className={`mx-2 ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-white'} p-3 rounded-lg shadow`}>
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="p-4 bg-white border-t">
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={loading}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={loading}
            >
              发送
            </Button>
          </Space.Compact>
        </div>
      </div>

      {/* 右栏：Agent 状态面板 */}
      <div className="w-72 border-l bg-white overflow-auto">
        <div className="p-4 border-b">
          <Text strong>执行流程</Text>
        </div>

        {/* 流程进度 */}
        <div className="p-4 border-b">
          <Timeline
            items={processSteps.map((step, index) => ({
              color: index < currentStep ? 'green' : index === currentStep ? 'blue' : 'gray',
              children: step.label
            }))}
          />
        </div>

        {/* Agent 状态 */}
        <div className="p-4">
          <Text strong>数字员工状态</Text>
          <div className="mt-3 space-y-2">
            {agentAgents.map((agent) => (
              <Card key={agent.name} size="small" className="bg-gray-50">
                <Space>
                  {statusIcon(agent.status)}
                  <div>
                    <Text strong>{agent.name}</Text>
                    <br />
                    <Text type="secondary" className="text-xs">{agent.dept}</Text>
                  </div>
                </Space>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

const agentAgents = [
  { name: 'CEO', dept: '决策层', status: 'done' as AgentStatus },
  { name: 'COO', dept: '决策层', status: 'done' as AgentStatus },
  { name: '质疑者', dept: '质量门禁', status: 'pending' as AgentStatus },
  { name: '增长总监', dept: '协调层', status: 'pending' as AgentStatus },
  { name: '产品总监', dept: '协调层', status: 'pending' as AgentStatus },
]
