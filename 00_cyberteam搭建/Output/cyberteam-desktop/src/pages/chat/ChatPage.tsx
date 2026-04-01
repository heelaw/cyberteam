import React, { useState, useEffect, useRef, useCallback } from "react"
import { MarkdownRenderer } from "../../components/MarkdownRenderer"
import { StreamingCursor } from "../../components/StreamingCursor"
import { useTypingEffect } from "../../hooks/useTypingEffect"
import { AgentMentionSelector } from "../../components/AgentMentionSelector"
import {
  mockAgents,
  groupAgentsByDepartment,
  statusColorMap,
  type AgentData,
} from "../../data/mock-agents"

// ==================== 类型定义 ====================

interface ChatMessage {
  id: string
  session_id: string
  role: "user" | "assistant" | "system"
  content: string
  sender_id: string
  sender_name: string
  sender_avatar: string
  metadata: string // JSON string
  created_at: string
}

interface ChatSession {
  id: string
  title: string
  working_directory: string
  conversation_type: string
  created_at: string
}

// ==================== 辅助函数 ====================

/** 解析消息中的 @mention */
const parseMentions = (content: string): string[] => {
  const regex = /@\[([^\]]+)\]\(([^)]+)\)/g
  const mentions: string[] = []
  let match
  while ((match = regex.exec(content)) !== null) {
    mentions.push(match[2]) // agent_id
  }
  return mentions
}

/** 格式化时间 */
const formatTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })
}

/** 解析 metadata */
const parseMetadata = (meta: string): { mentions: string[]; reply_to?: string } => {
  try {
    return JSON.parse(meta)
  } catch {
    return { mentions: [] }
  }
}

// ==================== 组件 ====================

export default function ChatPage() {
  // ==================== 状态 ====================

  // 会话列表
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)

  // 消息列表
  const [messages, setMessages] = useState<ChatMessage[]>([])

  // 输入
  const [inputValue, setInputValue] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [streamingContent, setStreamingContent] = useState("")
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null)

  // @mention
  const [showMentionSelector, setShowMentionSelector] = useState(false)
  const [mentionSearchText, setMentionSearchText] = useState("")
  const [mentionPosition, setMentionPosition] = useState({ x: 0, y: 0 })
  const [mentionStartIndex, setMentionStartIndex] = useState(-1)

  // 侧边栏
  const [showDirectoryBrowser, setShowDirectoryBrowser] = useState(false)
  const [browsingDir, setBrowsingDir] = useState("")
  const [browseError, setBrowseError] = useState<string | null>(null)
  const [selectedProject, setSelectedProject] = useState<{ id: string; name: string; working_directory: string } | null>(null)
  const [projects, setProjects] = useState<Array<{ id: string; name: string; working_directory: string }>>([])

  // 消息列表滚动
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // ==================== 打字机效果 ====================

  const { displayedText, isTyping, reset: resetTyping } = useTypingEffect({
    text: streamingContent,
    speed: 12,
    enabled: isGenerating,
    append: true,
  })

  // 自动滚动到底部
  useEffect(() => {
    if (isGenerating) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }
  }, [displayedText, isGenerating])

  // ==================== 初始化加载 ====================

  useEffect(() => {
    loadSessions()
    loadProjects()

    // 监听来自 main process 的流式数据
    const api = (window as Window & { electronAPI?: ElectronAPI }).electronAPI
    if (api) {
      const unsubscribe = api.on("claude:stream:chunk", (data: {
        messageId: string
        chunk: string
        fullContent: string
      }) => {
        setStreamingContent(data.fullContent)
      })

      // 新建会话事件
      const unsubNewSession = api.on("new-session", () => {
        handleNewSession()
      })

      // 打开设置事件
      const unsubSettings = api.on("open-settings", () => {
        window.location.hash = "#/settings"
      })

      return () => {
        unsubscribe()
        unsubNewSession()
        unsubSettings()
      }
    }
  }, [])

  // ==================== 数据加载 ====================

  const loadSessions = async () => {
    try {
      const api = (window as Window & { electronAPI?: ElectronAPI }).electronAPI
      if (!api) return
      const list = await api.chat.sessions.list()
      setSessions(list)
    } catch (err) {
      console.error("加载会话失败:", err)
    }
  }

  const loadProjects = async () => {
    try {
      const api = (window as Window & { electronAPI?: ElectronAPI }).electronAPI
      if (!api) return
      const list = await api.projects.list()
      setProjects(list)
    } catch (err) {
      console.error("加载项目失败:", err)
    }
  }

  const loadMessages = async (sessionId: string) => {
    try {
      const api = (window as Window & { electronAPI?: ElectronAPI }).electronAPI
      if (!api) return
      const list = await api.chat.messages.list(sessionId)
      setMessages(list)
    } catch (err) {
      console.error("加载消息失败:", err)
    }
  }

  // ==================== 会话管理 ====================

  const handleNewSession = useCallback(async () => {
    try {
      const api = (window as Window & { electronAPI?: ElectronAPI }).electronAPI
      if (!api) return

      const session = await api.chat.sessions.create({
        title: "新会话",
        working_directory: selectedProject?.working_directory || "",
        conversation_type: "single",
        project_id: selectedProject?.id || undefined,
      })

      setSessions(prev => [session, ...prev])
      setCurrentSession(session)
      setMessages([])
      setStreamingContent("")
    } catch (err) {
      console.error("创建会话失败:", err)
    }
  }, [selectedProject])

  const handleSelectSession = useCallback((session: ChatSession) => {
    setCurrentSession(session)
    loadMessages(session.id)
    setStreamingContent("")
  }, [])

  // ==================== 发送消息 ====================

  const handleSend = useCallback(async () => {
    if (!inputValue.trim() || isGenerating) return
    if (!currentSession) {
      await handleNewSession()
      // 等待会话创建后再发送
      return
    }

    const api = (window as Window & { electronAPI?: ElectronAPI }).electronAPI
    if (!api) return

    const text = inputValue.trim()
    setInputValue("")
    setIsGenerating(true)
    resetTyping()
    setStreamingContent("")

    // 提取 @mention
    const mentions = parseMentions(text)
    const metadata = JSON.stringify({ mentions })

    try {
      // 保存用户消息
      const userMsg: ChatMessage = {
        id: `msg_${Date.now()}`,
        session_id: currentSession.id,
        role: "user",
        content: text,
        sender_id: "user",
        sender_name: "我",
        sender_avatar: "👤",
        metadata,
        created_at: new Date().toISOString(),
      }
      setMessages(prev => [...prev, userMsg])

      // 创建 AI 消息占位符
      const aiMsgId = `msg_${Date.now()}_ai`
      setStreamingMessageId(aiMsgId)

      // 调用 Claude 流式 API
      const result = await api.claude.stream(
        {
          session_id: currentSession.id,
          message: text,
          working_directory: currentSession.working_directory || "/Users/cyberwiz",
        },
        (data) => {
          // 流式数据通过 IPC 返回，但这里我们用轮询方式
        }
      )

      // 保存 AI 响应到数据库
      const aiMsg: ChatMessage = {
        id: result.messageId,
        session_id: currentSession.id,
        role: "assistant",
        content: text, // 会被后续更新
        sender_id: "",
        sender_name: "CyberTeam AI",
        sender_avatar: "🤖",
        metadata: "{}",
        created_at: new Date().toISOString(),
      }

      // 监听流式内容变化，实时更新消息
      const unsub = api.on("claude:stream:chunk", (chunkData: {
        messageId: string
        chunk: string
        fullContent: string
      }) => {
        if (chunkData.messageId === result.messageId) {
          setMessages(prev =>
            prev.map(m =>
              m.id === result.messageId
                ? { ...m, content: chunkData.fullContent }
                : m
            )
          )
        }
      })

      // 等待完成
      setTimeout(() => {
        unsub()
        setIsGenerating(false)
        setStreamingMessageId(null)
        loadMessages(currentSession.id)
      }, 3000)

    } catch (err) {
      console.error("发送消息失败:", err)
      setIsGenerating(false)
      setStreamingMessageId(null)
    }
  }, [inputValue, isGenerating, currentSession, handleNewSession, resetTyping])

  // ==================== @mention 处理 ====================

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    const cursorPos = e.target.selectionStart
    setInputValue(value)

    // 检测 @ 触发
    const textBeforeCursor = value.slice(0, cursorPos)
    const atIndex = textBeforeCursor.lastIndexOf("@")

    if (atIndex !== -1) {
      const textAfterAt = textBeforeCursor.slice(atIndex + 1)

      // 检查 @ 后面是否有空格（如果没有，说明正在输入 @mention）
      if (!textAfterAt.includes(" ") && !textAfterAt.includes("\n")) {
        setShowMentionSelector(true)
        setMentionSearchText(textAfterAt)
        setMentionStartIndex(atIndex)

        // 计算位置
        if (textareaRef.current) {
          const rect = textareaRef.current.getBoundingClientRect()
          setMentionPosition({
            x: rect.left + 20,
            y: rect.top - 10,
          })
        }
        return
      }
    }

    setShowMentionSelector(false)
    setMentionSearchText("")
  }, [])

  const handleMentionSelect = useCallback((agent: AgentData) => {
    if (mentionStartIndex === -1) return

    // 替换 @xxx 为格式化 mention
    const beforeAt = inputValue.slice(0, mentionStartIndex)
    const afterCursor = inputValue.slice(inputRef.current?.selectionStart || mentionStartIndex)

    const mentionText = `@[${agent.name}](${agent.id}) `
    const newValue = beforeAt + mentionText + afterCursor

    setInputValue(newValue)
    setShowMentionSelector(false)
    setMentionSearchText("")

    // 聚焦回输入框
    setTimeout(() => {
      inputRef.current?.focus()
      const newCursorPos = beforeAt.length + mentionText.length
      inputRef.current?.setSelectionRange(newCursorPos, newCursorPos)
    }, 0)
  }, [inputValue, mentionStartIndex])

  // ==================== 目录浏览 ====================

  const loadBrowseDirectory = useCallback(async (dirPath: string) => {
    const api = (window as Window & { electronAPI?: ElectronAPI }).electronAPI
    if (!api) return

    try {
      const result = await api.files.browse(dirPath)
      setBrowsingDir(result.current)
      setBrowseError(result.error)
    } catch (err) {
      setBrowseError(String(err))
    }
  }, [])

  useEffect(() => {
    if (showDirectoryBrowser && !browsingDir) {
      loadBrowseDirectory("")
    }
  }, [showDirectoryBrowser, browsingDir, loadBrowseDirectory])

  const handleBrowseDir = useCallback(async (dirPath: string) => {
    await loadBrowseDirectory(dirPath)
  }, [loadBrowseDirectory])

  const handleSelectDirectory = useCallback(async () => {
    const api = (window as Window & { electronAPI?: ElectronAPI }).electronAPI
    if (!api) return

    try {
      const selected = await api.files.selectDirectory()
      if (selected) {
        // 创建新项目
        const project = await api.projects.create({
          name: selected.split("/").pop() || "新项目",
          working_directory: selected,
        })
        setSelectedProject(project)
        await loadProjects()
      }
    } catch (err) {
      console.error("选择目录失败:", err)
    }
    setShowDirectoryBrowser(false)
  }, [])

  // ==================== 快捷键 ====================

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + Enter 发送消息
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault()
        handleSend()
      }

      // Escape 关闭 mention 选择器
      if (e.key === "Escape" && showMentionSelector) {
        setShowMentionSelector(false)
      }
    }

    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [handleSend, showMentionSelector])

  // ==================== JSX ====================

  const groupedAgents = groupAgentsByDepartment(mockAgents.filter(a => a.status !== "offline"))

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#0a0a0f", color: "#fff" }}>
      {/* ==================== 左侧边栏 ==================== */}
      <div
        style={{
          width: "260px",
          borderRight: "1px solid #1f2937",
          display: "flex",
          flexDirection: "column",
          backgroundColor: "#111827",
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: "20px 16px",
            borderBottom: "1px solid #1f2937",
            fontSize: "18px",
            fontWeight: 700,
            color: "#fff",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <span style={{ fontSize: "24px" }}>🚀</span>
          <span>CyberTeam</span>
        </div>

        {/* 目录操作 */}
        <div style={{ padding: "12px", borderBottom: "1px solid #1f2937" }}>
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={() => setShowDirectoryBrowser(!showDirectoryBrowser)}
              style={{
                flex: 1,
                padding: "8px",
                backgroundColor: "#1f2937",
                border: "1px solid #374151",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "12px",
                cursor: "pointer",
              }}
            >
              📁 浏览目录
            </button>
            <button
              onClick={handleSelectDirectory}
              style={{
                flex: 1,
                padding: "8px",
                backgroundColor: "#3b82f6",
                border: "none",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "12px",
                cursor: "pointer",
              }}
            >
              📂 选择目录
            </button>
          </div>

          {/* 项目下拉 */}
          {projects.length > 0 && (
            <select
              value={selectedProject?.id || ""}
              onChange={e => {
                const p = projects.find(p => p.id === e.target.value)
                setSelectedProject(p || null)
              }}
              style={{
                width: "100%",
                marginTop: "8px",
                padding: "6px 8px",
                backgroundColor: "#1f2937",
                border: "1px solid #374151",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "12px",
              }}
            >
              <option value="">选择项目</option>
              {projects.map(p => (
                <option key={p.id} value={p.id}>
                  📂 {p.name}
                </option>
              ))}
            </select>
          )}

          {/* 目录浏览器 */}
          {showDirectoryBrowser && (
            <div
              style={{
                marginTop: "8px",
                padding: "8px",
                backgroundColor: "#1f2937",
                borderRadius: "6px",
                maxHeight: "200px",
                overflowY: "auto",
                fontSize: "12px",
              }}
            >
              <div style={{ marginBottom: "8px", color: "#9ca3af", wordBreak: "break-all" }}>
                📍 {browsingDir || "加载中..."}
              </div>
              {browseError && (
                <div style={{ color: "#ef4444", marginBottom: "8px" }}>❌ {browseError}</div>
              )}
              {/* 父目录 */}
              {browsingDir && (
                <button
                  onClick={() => handleBrowseDir(browsingDir + "/..")}
                  style={{
                    display: "block",
                    width: "100%",
                    padding: "6px",
                    backgroundColor: "transparent",
                    border: "none",
                    borderRadius: "4px",
                    color: "#9ca3af",
                    textAlign: "left",
                    cursor: "pointer",
                    fontSize: "12px",
                  }}
                >
                  ⬆️ 返回上级
                </button>
              )}
              {/* 子目录列表 */}
              <div ref={undefined} />
            </div>
          )}
        </div>

        {/* 新建会话 */}
        <button
          onClick={handleNewSession}
          style={{
            margin: "12px",
            padding: "10px",
            backgroundColor: "#3b82f6",
            border: "none",
            borderRadius: "8px",
            color: "#fff",
            fontSize: "13px",
            fontWeight: 600,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px",
          }}
        >
          <span>+</span> 新建会话
        </button>

        {/* 会话列表 */}
        <div style={{ flex: 1, overflowY: "auto" }}>
          <div
            style={{
              padding: "8px 16px",
              fontSize: "11px",
              color: "#6b7280",
              fontWeight: 600,
              textTransform: "uppercase",
            }}
          >
            对话历史
          </div>
          {sessions.length === 0 ? (
            <div
              style={{
                padding: "20px 16px",
                textAlign: "center",
                color: "#6b7280",
                fontSize: "12px",
              }}
            >
              暂无会话记录
            </div>
          ) : (
            sessions.map(session => (
              <button
                key={session.id}
                onClick={() => handleSelectSession(session)}
                style={{
                  display: "block",
                  width: "100%",
                  padding: "10px 16px",
                  backgroundColor:
                    currentSession?.id === session.id ? "#1f2937" : "transparent",
                  border: "none",
                  borderLeft:
                    currentSession?.id === session.id ? "3px solid #3b82f6" : "3px solid transparent",
                  color: "#fff",
                  textAlign: "left",
                  cursor: "pointer",
                  fontSize: "13px",
                }}
              >
                💬 {session.title}
              </button>
            ))
          )}
        </div>

        {/* Agent 树 */}
        <div style={{ borderTop: "1px solid #1f2937", maxHeight: "300px", overflowY: "auto" }}>
          <div
            style={{
              padding: "8px 16px",
              fontSize: "11px",
              color: "#6b7280",
              fontWeight: 600,
              textTransform: "uppercase",
            }}
          >
            组织架构
          </div>
          {Object.entries(groupedAgents).map(([dept, agents]) => (
            <div key={dept}>
              <div
                style={{
                  padding: "6px 16px",
                  fontSize: "11px",
                  color: "#9ca3af",
                  fontWeight: 500,
                }}
              >
                {dept}
              </div>
              {agents.map(agent => (
                <button
                  key={agent.id}
                  onClick={() => {
                    // 在输入框插入 @mention
                    setInputValue(prev => prev + `@[${agent.name}](${agent.id}) `)
                    inputRef.current?.focus()
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    width: "100%",
                    padding: "6px 16px",
                    backgroundColor: "transparent",
                    border: "none",
                    color: "#fff",
                    textAlign: "left",
                    cursor: "pointer",
                    fontSize: "12px",
                  }}
                >
                  <span style={{ fontSize: "16px" }}>{agent.avatar}</span>
                  <span>{agent.name}</span>
                  <span
                    style={{
                      width: "8px",
                      height: "8px",
                      borderRadius: "50%",
                      backgroundColor: statusColorMap[agent.status],
                      marginLeft: "auto",
                    }}
                  />
                </button>
              ))}
            </div>
          ))}
        </div>

        {/* 设置入口 */}
        <button
          onClick={() => { window.location.hash = "#/settings" }}
          style={{
            padding: "12px 16px",
            borderTop: "1px solid #1f2937",
            backgroundColor: "transparent",
            border: "none",
            color: "#9ca3af",
            fontSize: "12px",
            cursor: "pointer",
            textAlign: "left",
          }}
        >
          ⚙️ 设置
        </button>
      </div>

      {/* ==================== 主聊天区域 ==================== */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* 顶部栏 */}
        <div
          style={{
            padding: "16px 24px",
            borderBottom: "1px solid #1f2937",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div style={{ fontSize: "16px", fontWeight: 600 }}>
              {currentSession?.title || "CyberTeam AI"}
            </div>
            {currentSession?.working_directory && (
              <div style={{ fontSize: "11px", color: "#6b7280", marginTop: "2px" }}>
                📁 {currentSession.working_directory}
              </div>
            )}
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            {currentSession && (
              <button
                onClick={() => loadMessages(currentSession.id)}
                style={{
                  padding: "6px 12px",
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "6px",
                  color: "#fff",
                  fontSize: "12px",
                  cursor: "pointer",
                }}
              >
                🔄 刷新
              </button>
            )}
          </div>
        </div>

        {/* 消息列表 */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "24px",
            display: "flex",
            flexDirection: "column",
            gap: "16px",
          }}
        >
          {/* 欢迎消息 */}
          {messages.length === 0 && (
            <div
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                color: "#6b7280",
              }}
            >
              <div style={{ fontSize: "48px", marginBottom: "16px" }}>🚀</div>
              <div style={{ fontSize: "18px", fontWeight: 600, marginBottom: "8px" }}>
                欢迎使用 CyberTeam
              </div>
              <div style={{ fontSize: "13px", textAlign: "center", maxWidth: "400px" }}>
                选择目录、创建会话，开始与 AI Agent 团队协作。
                <br />
                使用 @ 提到 Agent 分配任务。
              </div>

              {/* 快捷操作 */}
              <div
                style={{
                  marginTop: "24px",
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: "8px",
                  maxWidth: "360px",
                }}
              >
                {[
                  "📊 制定增长策略",
                  "🎯 产品需求分析",
                  "💬 用户运营方案",
                  "⚡ 技术架构设计",
                ].map((item, i) => (
                  <button
                    key={i}
                    onClick={() => setInputValue(item.replace(/^[^\s]+\s/, ""))}
                    style={{
                      padding: "10px 12px",
                      backgroundColor: "#1f2937",
                      border: "1px solid #374151",
                      borderRadius: "8px",
                      color: "#fff",
                      fontSize: "12px",
                      cursor: "pointer",
                      textAlign: "left",
                    }}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 消息列表 */}
          {messages.map(message => {
            const isUser = message.role === "user"
            const isAI = message.role === "assistant"
            const isStreaming = message.id === streamingMessageId
            const meta = parseMetadata(message.metadata)

            return (
              <div
                key={message.id}
                style={{
                  display: "flex",
                  flexDirection: isUser ? "row-reverse" : "row",
                  gap: "12px",
                  alignItems: "flex-start",
                }}
              >
                {/* 头像 */}
                <div
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "50%",
                    backgroundColor: isUser ? "#3b82f6" : "#1f2937",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "18px",
                    flexShrink: 0,
                  }}
                >
                  {isUser ? "👤" : "🤖"}
                </div>

                {/* 消息气泡 */}
                <div
                  style={{
                    maxWidth: "70%",
                    backgroundColor: isUser ? "#3b82f6" : "#1f2937",
                    borderRadius: "12px",
                    borderTopRightRadius: isUser ? "4px" : "12px",
                    borderTopLeftRadius: isUser ? "12px" : "4px",
                    padding: "12px 16px",
                  }}
                >
                  {/* 名称 */}
                  <div
                    style={{
                      fontSize: "11px",
                      fontWeight: 600,
                      marginBottom: "4px",
                      opacity: 0.8,
                    }}
                  >
                    {isUser ? "我" : message.sender_name || "CyberTeam AI"}
                  </div>

                  {/* 内容 */}
                  <div style={{ fontSize: "14px", lineHeight: 1.6 }}>
                    <MarkdownRenderer
                      content={isStreaming ? displayedText : message.content}
                      className={isUser ? "text-white" : "text-gray-100"}
                    />
                    {isStreaming && <StreamingCursor visible={isTyping} />}
                  </div>

                  {/* @mention 标签 */}
                  {meta.mentions.length > 0 && (
                    <div style={{ display: "flex", gap: "4px", marginTop: "8px", flexWrap: "wrap" }}>
                      {meta.mentions.map((m, i) => {
                        const agent = mockAgents.find(a => a.id === m)
                        return agent ? (
                          <span
                            key={i}
                            style={{
                              fontSize: "10px",
                              padding: "2px 6px",
                              backgroundColor: "rgba(255,255,255,0.2)",
                              borderRadius: "4px",
                            }}
                          >
                            @{agent.name}
                          </span>
                        ) : null
                      })}
                    </div>
                  )}

                  {/* 时间 */}
                  <div
                    style={{
                      fontSize: "10px",
                      opacity: 0.6,
                      marginTop: "4px",
                      textAlign: "right",
                    }}
                  >
                    {formatTime(message.created_at)}
                  </div>
                </div>
              </div>
            )
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div
          style={{
            padding: "16px 24px",
            borderTop: "1px solid #1f2937",
            backgroundColor: "#111827",
          }}
        >
          {/* @mention 选择器 */}
          <AgentMentionSelector
            visible={showMentionSelector}
            position={mentionPosition}
            searchText={mentionSearchText}
            onSelect={handleMentionSelect}
            onClose={() => setShowMentionSelector(false)}
          />

          <div
            style={{
              display: "flex",
              gap: "12px",
              alignItems: "flex-end",
            }}
          >
            {/* 输入框 */}
            <div style={{ flex: 1, position: "relative" }}>
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={handleInputChange}
                placeholder="输入消息... 使用 @ 提到 Agent"
                disabled={isGenerating}
                rows={1}
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "12px",
                  color: "#fff",
                  fontSize: "14px",
                  resize: "none",
                  outline: "none",
                  fontFamily: "inherit",
                  lineHeight: 1.5,
                  minHeight: "48px",
                  maxHeight: "200px",
                }}
                onKeyDown={e => {
                  if (e.key === "Enter" && !e.shiftKey && !showMentionSelector) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
              />

              {/* 快捷 Agent 提示 */}
              {inputValue.startsWith("@") && (
                <div
                  style={{
                    position: "absolute",
                    bottom: "100%",
                    left: 0,
                    right: 0,
                    padding: "4px 8px",
                    fontSize: "10px",
                    color: "#9ca3af",
                    backgroundColor: "#111827",
                    border: "1px solid #374151",
                    borderRadius: "6px",
                    marginBottom: "4px",
                  }}
                >
                  按空格完成选择，或使用 ↑↓ 选择后按 Enter
                </div>
              )}
            </div>

            {/* 发送按钮 */}
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isGenerating}
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                backgroundColor:
                  inputValue.trim() && !isGenerating ? "#3b82f6" : "#374151",
                border: "none",
                color: "#fff",
                fontSize: "18px",
                cursor: inputValue.trim() && !isGenerating ? "pointer" : "not-allowed",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isGenerating ? "⏳" : "➤"}
            </button>
          </div>

          {/* 底部提示 */}
          <div
            style={{
              marginTop: "8px",
              fontSize: "10px",
              color: "#6b7280",
              display: "flex",
              gap: "16px",
            }}
          >
            <span>Enter 发送</span>
            <span>Shift+Enter 换行</span>
            <span>⌘+Enter 也可发送</span>
          </div>
        </div>
      </div>
    </div>
  )
}
