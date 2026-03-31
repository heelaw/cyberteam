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
import { Input, Button, Card, Tag, Avatar, Space, Timeline, Typography, message, Select, Alert } from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  EyeOutlined,
  ArrowLeftOutlined,
  ProjectOutlined,
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import { fetchMessages, sendMessage } from '@/apis/modules/chat'
import { fetchProjects, fetchProjectContext, type Project, type ProjectContext } from '@/apis/modules/projects'
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

// === 部门选项类型 ===
interface DeptOption {
  label: string      // 显示名称（部门名）
  value: string      // 部门代码
  agent: string      // 对应 Agent 名称
}

// 从 deptAgentMap 提取唯一的部门选项
const deptOptions: DeptOption[] = [
  { label: 'CEO', value: 'ceo', agent: 'CEO' },
  { label: 'COO', value: 'coo', agent: 'COO' },
  { label: '决策层', value: '决策层', agent: 'CEO' },
  { label: '质量门禁', value: '质量门禁', agent: '质疑者' },
  { label: '协调层', value: '协调层', agent: '增长总监' },
  { label: '增长总监', value: 'growth', agent: '增长总监' },
  { label: '产品总监', value: 'product', agent: '产品总监' },
  { label: '运营总监', value: 'ops', agent: '运营总监' },
  { label: '运营', value: '运营', agent: '运营总监' },
]

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

  // ========== 新增：项目选择相关状态 ==========
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [projectContext, setProjectContext] = useState<ProjectContext | null>(null)
  const [loadingProjects, setLoadingProjects] = useState(false)

  // 加载项目列表
  useEffect(() => {
    setLoadingProjects(true)
    fetchProjects()
      .then(setProjects)
      .catch(() => setProjects([]))
      .finally(() => setLoadingProjects(false))
  }, [])

  // 当选择项目时，加载项目上下文
  const handleProjectChange = useCallback(async (projectId: string | null) => {
    if (!projectId) {
      setSelectedProject(null)
      setProjectContext(null)
      return
    }
    const project = projects.find(p => p.id === projectId)
    setSelectedProject(project || null)
    if (project) {
      const ctx = await fetchProjectContext(projectId)
      setProjectContext(ctx)
      if (ctx?.has_context) {
        message.info(`已加载项目「${project.name}」的业务背景`)
      }
    } else {
      setProjectContext(null)
    }
  }, [projects])
  // ==========================================
  // StreamSessionManager session id，用于跨 HMR 保持订阅
  const sessionIdRef = useRef<string | null>(null)
  // unsubscribe 函数引用
  const unsubscribeRef = useRef<(() => void) | null>(null)

  // === @ 提及功能状态 ===
  const [mentionSearch, setMentionSearch] = useState<string | null>(null)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // 根据搜索过滤部门选项
  const filteredOptions = mentionSearch === null
    ? deptOptions
    : deptOptions.filter(opt =>
        opt.label.toLowerCase().includes(mentionSearch.toLowerCase()) ||
        opt.agent.toLowerCase().includes(mentionSearch.toLowerCase())
      )

  // 插入提及文本到光标位置
  const insertMention = useCallback((option: DeptOption) => {
    const textarea = textareaRef.current
    if (!textarea) return

    // 统一用 DOM value 计算，避免 React state 和 DOM 不同步
    const domValue = textarea.value
    const selStart = textarea.selectionStart
    const selEnd = textarea.selectionEnd
    const beforeCursor = domValue.substring(0, selStart)
    const afterCursor = domValue.substring(selEnd)

    // 找到最后一个 @ 符号的位置
    const atIndex = beforeCursor.lastIndexOf('@')
    if (atIndex === -1) return

    // 构建新文本：@部门名 + 空格（替换 @ 符号后的搜索词）
    const newText = beforeCursor.substring(0, atIndex) + `@${option.agent} ` + afterCursor
    setInput(newText)

    // 重置提及状态
    setMentionSearch(null)
    setSelectedIndex(0)

    // 设置光标位置到插入文本之后
    setTimeout(() => {
      const newPos = atIndex + option.agent.length + 2 // @ + agent名 + 空格
      textarea.focus()
      textarea.selectionStart = newPos
      textarea.selectionEnd = newPos
    }, 0)
  }, [])

  // 处理键盘事件
  const handleMentionKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (mentionSearch === null) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(i => Math.min(i + 1, filteredOptions.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(i => Math.max(i - 1, 0))
        break
      case 'Enter':
        e.preventDefault()
        if (filteredOptions[selectedIndex]) {
          insertMention(filteredOptions[selectedIndex])
        }
        break
      case 'Escape':
        e.preventDefault()
        setMentionSearch(null)
        setSelectedIndex(0)
        break
    }
  }, [mentionSearch, filteredOptions, selectedIndex, insertMention])

  // 处理 TextArea 变化，检测 @ 触发
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    const cursorPos = e.target.selectionStart
    setInput(value)

    // 查找光标前最近的 @
    const textBeforeCursor = value.substring(0, cursorPos)
    const lastAtIndex = textBeforeCursor.lastIndexOf('@')

    if (lastAtIndex !== -1) {
      // 检查 @ 后面是否有空格或其他分隔符
      const textAfterAt = textBeforeCursor.substring(lastAtIndex + 1)
      if (!textAfterAt.includes(' ') && !textAfterAt.includes('\n')) {
        // @ 后面没有分隔符，显示下拉
        const searchText = textAfterAt
        setMentionSearch(searchText)
        setSelectedIndex(0)
        return
      }
    }

    // 没有有效的 @，关闭下拉
    setMentionSearch(null)
  }, [])

  // 点击外部关闭下拉
  useEffect(() => {
    const handleClickOutside = () => setMentionSearch(null)
    if (mentionSearch !== null) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [mentionSearch])

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

    // ========== 新增：构建带项目上下文的完整消息 ==========
    let fullContent = userContent
    if (selectedProject && projectContext?.business_context) {
      fullContent = `【项目：${selectedProject.name}】\n\n` +
        `【业务背景】\n${projectContext.business_context}\n\n` +
        `【用户问题】\n${userContent}`
    }
    // ====================================================

    // 1. 发送用户消息
    let userMsg: Message
    try {
      userMsg = await sendMessage(conversationId, { content: fullContent })
      setMessages((prev) => [...prev, userMsg])
    } catch {
      message.error('发送失败，请检查后端服务')
      setSending(false)
      return
    }

    // 2. 重置 Agent 面板状态
    setAgentPanel(defaultAgents.map((a) => ({ ...a, status: 'thinking' as AgentStatus })))
    setProcessStep(0)
    setIsStreaming(true)

    // 3. 轮询获取 Agent 响应（SSE 尚未实现，临时用轮询）
    let pollCount = 0
    const MAX_POLLS = 20
    const POLL_INTERVAL = 2000
    const pollForResponse = async () => {
      if (pollCount >= MAX_POLLS) {
        setIsStreaming(false)
        setAgentPanel(prev => prev.map(a => ({ ...a, status: 'done' as AgentStatus, output: '处理完成' })))
        return
      }
      pollCount++
      try {
        const msgs = await fetchMessages(conversationId)
        const latest = msgs[msgs.length - 1]
        // 如果有新消息（非用户发的），说明 Agent 已响应
        if (latest && latest.senderType !== 'user') {
          setMessages(msgs)
          setAgentPanel(prev => prev.map(a => ({ ...a, status: 'done' as AgentStatus })))
          setIsStreaming(false)
          return
        }
      } catch { /* ignore */ }
      setTimeout(pollForResponse, POLL_INTERVAL)
    }
    pollForResponse()

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
      {/* 中栏：消息流 + 输入（Grid 布局确保输入区固定在底部） */}
      <div className="flex-1 flex flex-col" style={{ minHeight: 0 }}>
        {/* 顶部栏 */}
        <div className="border-b bg-white px-4 py-2 flex items-center gap-3 shrink-0">
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/chat')} type="text" />
          <Text strong>对话 {conversationId?.slice(0, 8)}...</Text>

          {/* ========== 新增：项目选择器 ========== */}
          <Select
            placeholder="选择项目（可选）"
            value={selectedProject?.id}
            onChange={handleProjectChange}
            allowClear
            loading={loadingProjects}
            style={{ width: 200 }}
            suffixIcon={<ProjectOutlined />}
            options={projects.map(p => ({
              value: p.id,
              label: (
                <Space>
                  <ProjectOutlined />
                  {p.name}
                  {p.local_path && <span className="text-gray-400 text-xs">📁</span>}
                </Space>
              ),
            }))}
          />
          {/* ==================================== */}

          <div className="flex-1" />
          {isStreaming && (
            <Tag color="processing" className="animate-pulse">
              <ThunderboltOutlined /> Agent 执行中...
            </Tag>
          )}
        </div>

        {/* 消息区域（flex-1 + overflow-auto 自动填满中间） */}
        <div className="flex-1 overflow-auto p-4 space-y-4" style={{ minHeight: 0 }}>
          {/* ========== 新增：项目上下文提示 ========== */}
          {selectedProject && projectContext?.has_context && (
            <Alert
              message={
                <Space>
                  <ProjectOutlined />
                  <span>当前项目：<Text strong>{selectedProject.name}</Text></span>
                  <Tag color="green">业务背景已加载</Tag>
                </Space>
              }
              description={
                <Text type="secondary" className="text-xs">
                  系统将基于业务背景进行分析。如需更新背景，请修改项目目录下的 context/business_context.md
                </Text>
              }
              type="info"
              showIcon
              style={{ marginBottom: 8 }}
            />
          )}
          {selectedProject && !projectContext?.has_context && (
            <Alert
              message={
                <Space>
                  <ProjectOutlined />
                  <span>当前项目：<Text strong>{selectedProject.name}</Text></span>
                  <Tag color="warning">暂无业务背景</Tag>
                </Space>
              }
              description={
                <Text type="secondary" className="text-xs">
                  项目目录下未找到 context/business_context.md。请创建该文件或关联已有项目文件夹。
                </Text>
              }
              type="warning"
              showIcon
              style={{ marginBottom: 8 }}
            />
          )}
          {/* ====================================== */}

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

        {/* 输入区（shrink-0 防止被压缩） */}
        <div className="border-t bg-white p-3 shrink-0">
          <div className="relative overflow-visible" style={{ position: 'relative', width: '100%' }}>
            <div className="flex w-full gap-2 items-end">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleMentionKeyDown}
                placeholder="输入消息... (@提及 Agent 如 @增长总监)"
                rows={1}
                className="flex-1 resize-none border rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-50 disabled:text-gray-400"
                disabled={sending || isStreaming}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={sending || isStreaming}
              >
                {isStreaming ? '执行中' : '发送'}
              </Button>
            </div>

            {/* @ 提及下拉框（内联样式确保 position:absolute 生效） */}
            {mentionSearch !== null && filteredOptions.length > 0 && (
              <div
                style={{
                  position: 'absolute',
                  zIndex: 9999,
                  top: 'calc(100% + 4px)',
                  left: 0,
                  width: '100%',
                  maxHeight: '256px',
                  overflowY: 'auto',
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)',
                }}
              >
                {filteredOptions.map((opt, index) => (
                  <div
                    key={opt.value}
                    className={cn(
                      'px-3 py-2 cursor-pointer flex items-center justify-between',
                      index === selectedIndex ? 'bg-blue-50' : 'hover:bg-gray-50'
                    )}
                    onClick={(e) => {
                      e.stopPropagation()
                      insertMention(opt)
                    }}
                  >
                    <div className="flex items-center gap-2">
                      <Tag color={tagColor(opt.label)} className="text-xs">{opt.label}</Tag>
                      <span className="text-sm text-gray-600">{opt.agent}</span>
                    </div>
                    {index === selectedIndex && (
                      <span className="text-xs text-blue-500">按 Enter 选择</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 右栏：Agent 状态面板 */}
      <div className="w-72 border-l border-t bg-white p-4 overflow-auto shrink-0">
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
