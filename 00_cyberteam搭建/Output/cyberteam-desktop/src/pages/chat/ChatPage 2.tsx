import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import type { ChatSession, Message, Agent, Project } from '../../types/electron.d'
import DirectoryBrowser from '../../components/DirectoryBrowser'

export default function ChatPage() {
  const { sessionId } = useParams()
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [agents, setAgents] = useState<Agent[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [workingDir, setWorkingDir] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showDirBrowser, setShowDirBrowser] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 加载会话列表
  useEffect(() => {
    loadSessions()
    loadAgents()
    loadProjects()
    initWorkingDir()
  }, [])

  // 加载指定会话的消息
  useEffect(() => {
    if (sessionId) {
      loadSession(sessionId)
    }
  }, [sessionId])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function initWorkingDir() {
    try {
      const homeDir = await window.electronAPI.system.getHomeDirectory()
      const savedDir = localStorage.getItem('cyberteam:last-working-directory')
      setWorkingDir(savedDir || homeDir)
    } catch (err) {
      console.error('Failed to get home directory:', err)
    }
  }

  async function loadSessions() {
    try {
      const list = await window.electronAPI.chat.sessions.list()
      setSessions(list)
    } catch (err) {
      console.error('Failed to load sessions:', err)
    }
  }

  async function loadSession(id: string) {
    try {
      const session = await window.electronAPI.chat.sessions.get(id)
      setCurrentSession(session)
      if (session?.working_directory) {
        setWorkingDir(session.working_directory)
        localStorage.setItem('cyberteam:last-working-directory', session.working_directory)
      }
      const msgs = await window.electronAPI.chat.messages.list(id)
      setMessages(msgs)
    } catch (err) {
      console.error('Failed to load session:', err)
    }
  }

  async function loadAgents() {
    try {
      const list = await window.electronAPI.agents.list()
      setAgents(list)
    } catch (err) {
      console.error('Failed to load agents:', err)
    }
  }

  async function loadProjects() {
    try {
      const list = await window.electronAPI.projects.list()
      setProjects(list)
    } catch (err) {
      console.error('Failed to load projects:', err)
    }
  }

  async function createProject(name: string, workingDir: string) {
    try {
      const project = await window.electronAPI.projects.create({
        name,
        working_directory: workingDir,
      })
      setProjects([project, ...projects])
      return project
    } catch (err) {
      console.error('Failed to create project:', err)
      return null
    }
  }

  function selectDirectory(dir: string) {
    setWorkingDir(dir)
    localStorage.setItem('cyberteam:last-working-directory', dir)
    if (currentSession) {
      window.electronAPI.chat.sessions.update(currentSession.id, {
        working_directory: dir,
      })
    }
    setShowDirBrowser(false)
  }

  async function createNewSession() {
    try {
      const session = await window.electronAPI.chat.sessions.create({
        title: '新会话',
        working_directory: workingDir,
        conversation_type: 'single',
      })
      setSessions([session, ...sessions])
      setCurrentSession(session)
      setMessages([])
    } catch (err) {
      console.error('Failed to create session:', err)
    }
  }

  async function selectDirectoryNative() {
    try {
      const dir = await window.electronAPI.files.selectDirectory()
      if (dir) {
        selectDirectory(dir)
      }
    } catch (err) {
      console.error('Failed to select directory:', err)
    }
  }

  async function sendMessage() {
    if (!inputValue.trim() || !currentSession || isLoading) return

    const userMessage = inputValue
    setInputValue('')
    setIsLoading(true)

    try {
      // 创建用户消息
      const msg = await window.electronAPI.chat.messages.create({
        session_id: currentSession.id,
        role: 'user',
        content: userMessage,
      })
      setMessages((prev) => [...prev, msg])

      // 调用 Claude Code CLI
      const response = await window.electronAPI.claude.send({
        session_id: currentSession.id,
        message: userMessage,
        working_directory: workingDir || currentSession.working_directory,
      })

      // 创建 AI 消息
      const aiMsg = await window.electronAPI.chat.messages.create({
        session_id: currentSession.id,
        role: 'assistant',
        content: response.content,
      })
      setMessages((prev) => [...prev, aiMsg])
    } catch (err) {
      console.error('Failed to send message:', err)
    } finally {
      setIsLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex h-full">
      {/* 左侧会话列表 */}
      <div className="w-64 bg-[#111118] border-r border-[#2a2a3a] flex flex-col">
        {/* 顶部操作 */}
        <div className="p-3 border-b border-[#2a2a3a] space-y-2">
          <button
            onClick={createNewSession}
            className="w-full btn btn-primary text-sm"
          >
            + 新建会话
          </button>

          {/* 目录选择 */}
          <div className="flex gap-1">
            <button
              onClick={() => setShowDirBrowser(true)}
              className="flex-1 btn btn-secondary text-xs"
              title={workingDir || '选择工作目录'}
            >
              📁 {workingDir ? workingDir.split('/').pop() : '浏览'}
            </button>
            <button
              onClick={selectDirectoryNative}
              className="btn btn-secondary text-xs px-2"
              title="系统目录选择器"
            >
              📂
            </button>
          </div>

          {/* 项目选择 */}
          {projects.length > 0 && (
            <select
              className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
              value={currentSession?.project_id || ''}
              onChange={async (e) => {
                if (currentSession && e.target.value) {
                  await window.electronAPI.chat.sessions.update(currentSession.id, {
                    project_id: e.target.value,
                  })
                  const project = projects.find(p => p.id === e.target.value)
                  if (project?.working_directory) {
                    selectDirectory(project.working_directory)
                  }
                }
              }}
            >
              <option value="">无项目</option>
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          )}

          {/* 快速创建项目 */}
          <button
            onClick={async () => {
              const name = prompt('项目名称:')
              if (name) {
                const project = await createProject(name, workingDir)
                if (project && currentSession) {
                  await window.electronAPI.chat.sessions.update(currentSession.id, {
                    project_id: project.id,
                  })
                  loadSessions()
                }
              }
            }}
            className="w-full text-xs text-[#6366f1] hover:text-[#818cf8] py-1"
          >
            + 创建新项目
          </button>
        </div>

        {/* 会话列表 */}
        <div className="flex-1 overflow-y-auto">
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => loadSession(session.id)}
              className={`p-3 cursor-pointer border-b border-[#2a2a3a] transition-colors ${
                currentSession?.id === session.id
                  ? 'bg-[#1a1a24]'
                  : 'hover:bg-[#1a1a24]'
              }`}
            >
              <div className="text-sm text-white truncate">{session.title}</div>
              <div className="text-xs text-[#606070] mt-1 truncate">
                {session.working_directory || '未设置目录'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 右侧聊天区 */}
      <div className="flex-1 flex flex-col">
        {currentSession ? (
          <>
            {/* 聊天头部 */}
            <div className="h-14 bg-[#111118] border-b border-[#2a2a3a] flex items-center px-4">
              <h2 className="text-white font-medium">{currentSession.title}</h2>
              <span className="ml-3 text-xs text-[#606070]">
                {workingDir}
              </span>
            </div>

            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-[#606070]">
                  <p className="text-lg mb-2">👋 开始对话</p>
                  <p className="text-sm">发送消息与 Claude Code 交流</p>
                </div>
              )}

              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`message ${msg.role}`}>
                    <pre className="whitespace-pre-wrap text-sm font-sans">
                      {msg.content}
                    </pre>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="message assistant">
                    <span className="animate-pulse">思考中...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* 输入区 */}
            <div className="p-4 bg-[#111118] border-t border-[#2a2a3a]">
              <div className="flex gap-3">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
                  className="flex-1 resize-none h-12 bg-[#1a1a24] border border-[#2a2a3a] rounded-lg px-4 py-2 text-sm"
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="btn btn-primary px-6"
                >
                  发送
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-[#606070]">
            <p className="text-lg mb-2">💬 选择一个会话</p>
            <p className="text-sm">或创建新会话开始对话</p>
          </div>
        )}
      </div>

      {/* 目录浏览器模态框 */}
      {showDirBrowser && (
        <DirectoryBrowser
          initialPath={workingDir}
          onSelect={selectDirectory}
          onCancel={() => setShowDirBrowser(false)}
        />
      )}
    </div>
  )
}
