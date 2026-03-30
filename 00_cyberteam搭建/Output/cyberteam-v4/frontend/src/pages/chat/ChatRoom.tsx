/**
 * ChatRoom — 真实对话页面
 *
 * 集成模式（抄 CodePilot stream-session-manager + Magic digital employee）：
 * - 消息持久化到后端 /api/v1/chat/conversations/{id}/messages
 * - SSE 流订阅获取 Agent 实时输出（/api/sse/{task_id}）
 * - WebSocket 实时推送 Agent 状态事件（/ws/{user_id}）
 * - 右栏 Agent 状态面板随 SSE 事件实时更新
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
import { wsClient } from '@/apis/clients/websocket'
import type { Message } from '@/types'
import { cn } from '@/utils/cn'
import { StreamSessionManager } from '@/lib/stream-session-manager'
import type { SSEStreamCallbacks } from '@/lib/sse-event-types'

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
  { name: '运营总监', dept: '协调层', status: 'pending' },
]

// 流程节点
const processSteps = [
  { label: 'CEO-COO 对齐', key: 'ceo_aligned' },
  { label: '策略讨论', key: 'strategy' },
  { label: '信息收集', key: 'research' },
  { label: '风险预案', key: 'risk' },
  { label: 'CEO 汇报', key: 'ceo_report' },
  { label: '设计联动', key: 'design' },
  { label: '文案产出', key: 'content' },
  { label: 'CEO 汇总', key: 'ceo_summary' },
]

// === 部门 → Agent 映射 ===
const deptAgentMap: Record<string, string> = {
  ceo: 'CEO',
  coo: 'COO',
  决策层: 'CEO',
  质量门禁: '质疑者',
  协调层: '增长总监',
  growth: '增长总监',
  product: '产品总监',
  ops: '运营总监',
  运营: '运营总监',
}

const statusIcon = (s: AgentStatus) => {
  if (s === 'done') return <SafetyCertificateOutlined className="text-green-500" />
  if (s === 'running') return <ThunderboltOutlined className="text-blue-500 animate-pulse" />
  if (s === 'error') return <EyeOutlined className="text-red-500" />
  return <EyeOutlined className="text-gray-300" />
}

const deptColor = (dept: string) => {
  if (dept === '决策层') return 'bg-yellow-500'
  if (dept === '质量门禁') return 'bg-red-500'
  if (dept === '协调层') return 'bg-blue-500'
  return 'bg-gray-500'
}

const tagColor = (dept: string) => {
  if (dept === '决策层') return 'gold'
  if (dept === '质量门禁') return 'red'
  if (dept === '协调层') return 'blue'
  return 'default'
}

export default function ChatRoom() {
  const { id: conversationId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [agentPanel, setAgentPanel] = useState<AgentStatusItem[]>(defaultAgents)
  const [processStep, setProcessStep] = useState(0)
  const [streamingContent, setStreamingContent] = useState<string>('')
  const [streamingAgent, setStreamingAgent] = useState<string>('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  // StreamSessionManager session id，用于跨 HMR 保持订阅
  const sessionIdRef = useRef<string | null>(null)
  // unsubscribe 函数引用
  const unsubscribeRef = useRef<(() => void) | null>(null)

  // 滚动到底部
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingContent, scrollToBottom])

  // 加载消息历史
  useEffect(() => {
    if (!conversationId) return
    setLoading(true)
    fetchMessages(conversationId)
      .then(setMessages)
      .catch(() => setMessages([]))
      .finally(() => setLoading(false))
  }, [conversationId])

  // WebSocket 订阅 Agent 状态事件
  useEffect(() => {
    if (!conversationId) return

    // 监听 WebSocket 推送的 Agent 状态
    const unsubThinking = wsClient.on('agent_thinking', (event) => {
      const dept = (event.data as Record<string, unknown>).stage as string
      const agentName = deptAgentMap[dept] || dept
      setAgentPanel((prev) =>
        prev.map((a) => (a.name === agentName ? { ...a, status: 'running' as AgentStatus } : a))
      )
    })

    const unsubOutput = wsClient.on('agent_output', (event) => {
      const data = event.data as Record<string, unknown>
      const agentName = (data.agent as string) || ''
      const content = (data.content as string) || ''
      if (agentName) {
        setAgentPanel((prev) =>
          prev.map((a) => (a.name === agentName ? { ...a, output: content } : a))
        )
      }
    })

    const unsubComplete = wsClient.on('agent_complete', (event) => {
      const data = event.data as Record<string, unknown>
      const agentName = (data.agent as string) || ''
      if (agentName) {
        setAgentPanel((prev) =>
          prev.map((a) => (a.name === agentName ? { ...a, status: 'done' as AgentStatus } : a))
        )
      }
    })

    return () => {
      unsubThinking()
      unsubOutput()
      unsubComplete()
    }
  }, [conversationId])

  // 构建 SSE 回调
  const buildSSECallbacks = useCallback((): SSEStreamCallbacks => {
    return {
      onThinking: (stage, msg) => {
        const agentName = deptAgentMap[stage] || 'CEO'
        setAgentPanel((prev) =>
          prev.map((a) => (a.name === agentName ? { ...a, status: 'running', output: msg } : a))
        )
        setProcessStep(0)
      },
      onRouted: (dept, reason) => {
        const agentName = deptAgentMap[dept] || dept
        setAgentPanel((prev) =>
          prev.map((a) =>
            a.name === agentName
              ? { ...a, status: 'running', output: `[路由] ${reason}` }
              : a.name === 'CEO'
              ? { ...a, status: 'done', output: '路由完成' }
              : a
          )
        )
        setProcessStep(1)
      },
      onAgentStart: (agent, dept) => {
        setAgentPanel((prev) =>
          prev.map((a) =>
            a.name === agent
              ? { ...a, status: 'running', output: '开始执行...' }
              : a
          )
        )
        setProcessStep((s) => Math.max(s, 2))
      },
      onAgentOutput: (agent, content) => {
        setAgentPanel((prev) =>
          prev.map((a) =>
            a.name === agent ? { ...a, output: content } : a
          )
        )
        setStreamingAgent(agent)
        setStreamingContent(content)
      },
      onAgentComplete: (agent, durationMs) => {
        setAgentPanel((prev) =>
          prev.map((a) =>
            a.name === agent
              ? { ...a, status: 'done', output: `完成 (${durationMs}ms)` }
              : a
          )
        )
        setStreamingContent('')
        setStreamingAgent('')
        setIsStreaming(false)
        setProcessStep((s) => Math.min(s + 1, processSteps.length - 1))
      },
      onApprovalRequest: (data) => {
        // TODO: 审批弹窗
        message.info('收到审批请求，请确认是否继续')
      },
      onError: (errMsg) => {
        message.error(`错误: ${errMsg}`)
        setIsStreaming(false)
        setStreamingContent('')
      },
      onDone: () => {
        setIsStreaming(false)
        setStreamingContent('')
        // 刷新消息列表
        if (conversationId) {
          fetchMessages(conversationId).then(setMessages)
        }
      },
    }
  }, [conversationId]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSend = async () => {
    if (!input.trim() || !conversationId || isStreaming) return

    const userContent = input.trim()
    setInput('')
    setSending(true)

    // 1. 发送用户消息
    let userMsg: Message
    try {
      userMsg = await sendMessage(conversationId, { content: userContent })
      setMessages((prev) => [...prev, userMsg])
    } catch {
      message.error('发送失败，请检查后端服务')
      setSending(false)
      return
    }

    // 2. 重置 Agent 面板状态
    setAgentPanel(defaultAgents.map((a) => ({ ...a, status: 'pending' as AgentStatus })))
    setProcessStep(0)
    setIsStreaming(true)

    // 3. 通过 StreamSessionManager 启动并订阅 SSE 流
    const manager = StreamSessionManager.getInstance()
    const session = manager.startStream(conversationId, userContent)
    sessionIdRef.current = session.id
    const callbacks = buildSSECallbacks()
    const unsubscribe = manager.subscribe(session.id, callbacks)
    unsubscribeRef.current = unsubscribe

    setSending(false)
  }

  // 组件卸载时取消订阅并关闭 session
  useEffect(() => {
    return () => {
      unsubscribeRef.current?.()
      if (sessionIdRef.current) {
        StreamSessionManager.getInstance().closeSession(sessionIdRef.current)
      }
      wsClient.disconnect()
    }
  }, [])

  if (!conversationId) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-400">
          <Text type="secondary">请从左侧选择或创建对话</Text>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-full">
      {/* 中栏：消息流 */}
      <div className="flex-1 flex flex-col">
        {/* 顶部栏 */}
        <div className="border-b bg-white px-4 py-2 flex items-center gap-3">
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/chat')} type="text" />
          <Text strong>对话 {conversationId.slice(0, 8)}...</Text>
          <div className="flex-1" />
          {isStreaming && (
            <Tag color="processing" className="animate-pulse">
              <ThunderboltOutlined /> Agent 执行中...
            </Tag>
          )}
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {loading ? (
            <div className="text-center text-gray-400 mt-8">加载消息...</div>
          ) : messages.length === 0 && !isStreaming ? (
            <div className="text-center text-gray-400 mt-8">
              <RobotOutlined className="text-4xl mb-3 block" />
              <p>发送消息开始对话，CyberTeam 将自动路由到对应部门</p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={cn('flex gap-3', msg.senderType === 'user' ? 'flex-row-reverse' : 'flex-row')}
                >
                  <Avatar
                    icon={msg.senderType === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    className={cn('flex-shrink-0', msg.senderType !== 'user' ? deptColor(msg.department || '') : 'bg-blue-500')}
                  />
                  <Card
                    size="small"
                    className={cn('max-w-[70%]', msg.senderType === 'user' ? 'bg-blue-50' : 'bg-white')}
                  >
                    {msg.senderType !== 'user' && (
                      <div className="flex items-center gap-2 mb-1">
                        <Text strong className="text-sm">{msg.senderName || 'Agent'}</Text>
                        {msg.department && (
                          <Tag color={tagColor(msg.department)} className="text-xs">
                            {msg.department}
                          </Tag>
                        )}
                      </div>
                    )}
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </Card>
                </div>
              ))}

              {/* 流式输出（实时显示 Agent 输出） */}
              {isStreaming && streamingContent && (
                <div className="flex gap-3">
                  <Avatar
                    icon={<RobotOutlined />}
                    className={cn('flex-shrink-0', deptColor('协调层'))}
                  />
                  <Card size="small" className="max-w-[70%] bg-blue-50">
                    <div className="flex items-center gap-2 mb-1">
                      <Text strong className="text-sm">{streamingAgent}</Text>
                      <Tag color="blue" className="text-xs animate-pulse">流式输出</Tag>
                    </div>
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{streamingContent}</ReactMarkdown>
                    </div>
                  </Card>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区 */}
        <div className="border-t bg-white p-3">
          <Space.Compact className="w-full">
            <TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入消息... (@提及 Agent 如 @增长总监)"
              autoSize={{ minRows: 1, maxRows: 4 }}
              onPressEnter={(e) => {
                if (!e.shiftKey) { e.preventDefault(); handleSend() }
              }}
              className="flex-1"
              disabled={sending || isStreaming}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              className="h-auto"
              loading={sending || isStreaming}
            >
              {isStreaming ? '执行中' : '发送'}
            </Button>
          </Space.Compact>
        </div>
      </div>

      {/* 右栏：Agent 状态面板 */}
      <div className="w-72 border-l bg-white p-4 overflow-auto">
        <Typography.Title level={5} className="mb-3">Agent 执行状态</Typography.Title>
        <Timeline
          items={agentPanel.map((a) => ({
            color: a.status === 'running' ? 'blue' : a.status === 'done' ? 'green' : a.status === 'error' ? 'red' : 'gray',
            children: (
              <div>
                <div className="flex items-center justify-between">
                  <Space>
                    {statusIcon(a.status)}
                    <div>
                      <div className="text-sm font-medium">{a.name}</div>
                      <div className="text-xs text-gray-400">{a.dept}</div>
                    </div>
                  </Space>
                  <Tag
                    color={a.status === 'running' ? 'processing' : a.status === 'done' ? 'success' : a.status === 'error' ? 'error' : 'default'}
                    className="text-xs"
                  >
                    {a.status === 'running' ? '执行中' : a.status === 'done' ? '完成' : a.status === 'error' ? '错误' : '等待'}
                  </Tag>
                </div>
                {a.output && a.status === 'running' && (
                  <div className="text-xs text-gray-500 mt-1 truncate">{a.output}</div>
                )}
              </div>
            ),
          }))}
        />

        <div className="mt-4 pt-4 border-t">
          <Typography.Title level={5} className="mb-2">任务节点</Typography.Title>
          <Timeline
            items={processSteps.map((step, i) => ({
              color: i < processStep ? 'green' : i === processStep ? 'blue' : 'gray',
              children: (
                <span className={i < processStep ? 'text-green-600' : i === processStep ? 'text-blue-600 font-medium' : 'text-gray-400'}>
                  {step.label}
                </span>
              ),
            }))}
          />
        </div>
      </div>
    </div>
  )
}
