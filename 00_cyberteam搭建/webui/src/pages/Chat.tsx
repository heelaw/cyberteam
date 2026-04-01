import { useEffect, useRef, useState, useCallback } from 'react'
import { Layout, Input, Button, Empty, Spin, Dropdown, List, Avatar } from 'antd'
import { PlusOutlined, SendOutlined, SearchOutlined, RobotOutlined } from '@ant-design/icons'
import { useChatStore, type Conversation } from '../stores/chatStore'
import { useAgentStore } from '../stores/agentStore'
import ChatBubble from '../components/common/ChatBubble'
import ConversationList from '../components/common/ConversationList'
import AgentStatusPanel from '../components/common/AgentStatusPanel'

const { Sider, Content } = Layout

export default function Chat() {
  const {
    conversations,
    messages,
    currentConversation,
    isLoading,
    createConversation,
    loadConversations,
    loadMessages,
    sendMessageStream,
    deleteConversation
  } = useChatStore()

  const { agents, loadAgents } = useAgentStore()

  const [inputValue, setInputValue] = useState('')
  const [searchValue, setSearchValue] = useState('')
  const [mentionActive, setMentionActive] = useState(false)
  const [mentionQuery, setMentionQuery] = useState('')
  const [mentionSelectedIdx, setMentionSelectedIdx] = useState(0)
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)
  const [showAgentBadge, setShowAgentBadge] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const mentionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadConversations()
    loadAgents()
  }, [loadConversations, loadAgents])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 过滤 Agent 列表
  const filteredAgents = mentionQuery
    ? agents.filter(a => a.name.toLowerCase().includes(mentionQuery.toLowerCase()))
    : agents

  // 监听 @ 触发
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value
    setInputValue(val)

    // 检测 @ 触发
    const cursor = e.target.selectionStart ?? val.length
    const textBeforeCursor = val.slice(0, cursor)
    const atMatch = textBeforeCursor.match(/@(\w*)$/)

    if (atMatch) {
      setMentionActive(true)
      setMentionQuery(atMatch[1])
      setMentionSelectedIdx(0)
    } else {
      setMentionActive(false)
      setMentionQuery('')
    }
  }, [])

  // 键盘处理：方向键 + Enter 选择 Agent
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!mentionActive) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
      return
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setMentionSelectedIdx(i => Math.min(i + 1, filteredAgents.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setMentionSelectedIdx(i => Math.max(i - 1, 0))
    } else if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault()
      if (filteredAgents[mentionSelectedIdx]) {
        insertMention(filteredAgents[mentionSelectedIdx])
      }
    } else if (e.key === 'Escape') {
      setMentionActive(false)
    }
  }, [mentionActive, filteredAgents, mentionSelectedIdx])

  // 插入 mention 到 textarea（name 即是唯一标识）
  const insertMention = useCallback((agent: { name: string; description?: string }) => {
    const textarea = textareaRef.current
    if (!textarea) return

    const cursor = textarea.selectionStart ?? inputValue.length
    const textBeforeCursor = inputValue.slice(0, cursor)
    const textAfterCursor = inputValue.slice(cursor)

    const newTextBefore = textBeforeCursor.replace(/@\w*$/, `@${agent.name} `)
    const newValue = newTextBefore + textAfterCursor

    setInputValue(newValue)
    setSelectedAgentId(agent.name)   // name = agent_id
    setShowAgentBadge(true)
    setMentionActive(false)
    setMentionQuery('')

    setTimeout(() => {
      textarea.focus()
      const newCursor = newTextBefore.length
      textarea.setSelectionRange(newCursor, newCursor)
    }, 0)
  }, [inputValue])

  const handleSend = async () => {
    if (!inputValue.trim()) return

    // 确保有对话
    if (!currentConversation) {
      await createConversation(selectedAgentId || undefined)
    }

    if (inputValue.trim()) {
      await sendMessageStream(inputValue, selectedAgentId || undefined)
      setInputValue('')
      setSelectedAgentId(null)
      setShowAgentBadge(false)
    }
  }

  const handleSelectConversation = async (conv: Conversation) => {
    setSelectedAgentId(conv.agent_id)
    setShowAgentBadge(!!conv.agent_id)
    await loadMessages(conv.id)
  }

  const handleNewConversation = async () => {
    setSelectedAgentId(null)
    setShowAgentBadge(false)
    await createConversation()
  }

  const handleDeleteConversation = async (id: string) => {
    await deleteConversation(id)
  }

  const clearAgent = () => {
    setSelectedAgentId(null)
    setShowAgentBadge(false)
  }

  const filteredConversations = searchValue
    ? conversations.filter(c => c.title?.includes(searchValue))
    : conversations

  return (
    <Layout className="h-[calc(100vh-140px)]">
      {/* Left Sidebar - Conversation List */}
      <Sider
        width={220}
        className="bg-cyber-panel border-r border-neon-cyan/20 overflow-auto"
      >
        <ConversationList
          conversations={filteredConversations}
          currentConversation={currentConversation}
          searchValue={searchValue}
          onSearchChange={setSearchValue}
          onSelect={handleSelectConversation}
          onNew={handleNewConversation}
          onDelete={handleDeleteConversation}
        />
      </Sider>

      {/* Main Content - Messages */}
      <Content className="flex flex-col bg-cyber-dark">
        {currentConversation ? (
          <>
            {/* Messages Area */}
            <div className="flex-1 overflow-auto p-4 space-y-4">
              {messages.map((msg) => (
                <ChatBubble
                  key={msg.id}
                  message={msg}
                  isStreaming={msg.metadata?.status === 'streaming'}
                />
              ))}
              {isLoading && messages[messages.length - 1]?.sender_type === 'user' && (
                <div className="flex items-center gap-2 text-slate-400 pl-11">
                  <Spin size="small" />
                  <span className="text-sm">AI 正在思考...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-neon-cyan/20">
              {/* Agent Badge */}
              {showAgentBadge && selectedAgentId && (
                <div className="mb-2 flex items-center gap-2">
                  <div className="flex items-center gap-1 px-3 py-1 bg-neon-cyan/10 border border-neon-cyan/30 rounded-full">
                    <RobotOutlined className="text-neon-cyan text-xs" />
                    <span className="text-neon-cyan text-xs">
                      {agents.find(a => a.name === selectedAgentId)?.name || selectedAgentId}
                    </span>
                    <button
                      onClick={clearAgent}
                      className="ml-1 text-slate-500 hover:text-white text-xs"
                    >
                      ×
                    </button>
                  </div>
                </div>
              )}

              {/* Mention Picker */}
              {mentionActive && filteredAgents.length > 0 && (
                <div
                  ref={mentionRef}
                  className="mb-2 max-h-48 overflow-auto bg-cyber-panel border border-neon-cyan/30 rounded-lg shadow-xl"
                  style={{ zIndex: 1000 }}
                >
                  <List
                    size="small"
                    dataSource={filteredAgents.slice(0, 8)}
                    renderItem={(agent, idx) => (
                      <List.Item
                        key={agent.name}
                        className={`px-3 py-2 cursor-pointer transition-colors ${
                          idx === mentionSelectedIdx
                            ? 'bg-neon-cyan/20'
                            : 'hover:bg-neon-cyan/10'
                        }`}
                        onClick={() => insertMention(agent)}
                      >
                        <div className="flex items-center gap-2 w-full">
                          <Avatar
                            size="small"
                            icon={<RobotOutlined />}
                            className="bg-neon-cyan/20 text-neon-cyan"
                          />
                          <div className="flex-1 min-w-0">
                            <div className="text-white text-sm font-medium truncate">
                              @{agent.name}
                            </div>
                            <div className="text-slate-500 text-xs truncate">
                              {agent.description?.slice(0, 40) || agent.name}
                            </div>
                          </div>
                          {idx === mentionSelectedIdx && (
                            <span className="text-neon-cyan text-xs">Tab ↹</span>
                          )}
                        </div>
                      </List.Item>
                    )}
                  />
                </div>
              )}

              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Input.TextArea
                    ref={textareaRef}
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="输入消息，@提及Agent..."
                    autoSize={{ minRows: 1, maxRows: 4 }}
                    className="flex-1 bg-cyber-panel border-neon-cyan/30 text-white"
                  />
                </div>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSend}
                  loading={isLoading}
                  className="bg-neon-cyan border-neon-cyan hover:bg-neon-cyan/80"
                >
                  发送
                </Button>
              </div>
              <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
                <span>按 Enter 发送，</span>
                <span className="text-neon-cyan">@</span>
                <span>提及 Agent，Tab/Enter 选择</span>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <Empty
              description={
                <span className="text-slate-500">
                  选择一个会话或创建新对话
                </span>
              }
            >
              <Button type="primary" icon={<PlusOutlined />} onClick={handleNewConversation}>
                新建对话
              </Button>
            </Empty>
          </div>
        )}
      </Content>

      {/* Right Sidebar - Agent Status */}
      <Sider
        width={300}
        className="bg-cyber-panel border-l border-neon-cyan/20 overflow-auto"
      >
        <AgentStatusPanel />
      </Sider>
    </Layout>
  )
}
