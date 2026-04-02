import * as electron from "electron"
const {
  app,
  ipcMain,
  dialog,
  shell,
  Menu,
  nativeImage,
  BrowserWindow,
  Tray,
} = electron
import path from "path"
import fs from "fs"
import { initDatabase, getDb, type ChatSession, type Message } from "./database.js"
import { initDefaultData } from "./init-database.js"

// DEBUG: 打印路径信息
console.log("[PATH] __dirname =", __dirname)
console.log("[PATH] app.getAppPath() =", app.getAppPath())
console.log("[PATH] process.cwd() =", process.cwd())
import { ClaudeClient } from "./claude-client.js"

// 环境检测
const isDev = process.env.NODE_ENV === "development" || (!app.isPackaged && !process.env.FORCE_DIST)

let mainWindow: Electron.BrowserWindow | null = null
let tray: Electron.Tray | null = null
let claudeClient: ClaudeClient | null = null
let db: ReturnType<typeof initDatabase> | null = null

// 创建主窗口
async function createWindow(): Promise<void> {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    title: "CyberTeam Desktop",
    backgroundColor: "#0a0a0f",
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
  })

  // 创建菜单
  createMenu()

  // 创建系统托盘
  createTray()

  // 加载内容 - 根据环境决定加载方式
  if (process.env.FORCE_DIST) {
    // FORCE_DIST 模式：启动内置 HTTP server 服务 dist/
    const http = await import("http")
    const distPath = app.getAppPath() + "/dist"
    const fsAsync = await import("fs/promises")

    // 检查 dist 是否存在
    try {
      await fsAsync.access(distPath + "/index.html")
    } catch {
      console.error("[Load] ERROR: dist/index.html not found at", distPath)
      console.error("[Load] Run: npm run build")
      app.quit()
      return
    }

    // 启动简单 HTTP server（使用 fs 而非 http.get）
    const mimeTypes: Record<string, string> = {
      ".html": "text/html; charset=utf-8",
      ".js": "text/javascript",
      ".css": "text/css",
      ".json": "application/json",
      ".png": "image/png",
      ".svg": "image/svg+xml",
      ".ico": "image/x-icon",
      ".woff2": "font/woff2",
    }
    const server = http.createServer(async (req, res) => {
      try {
        const urlPath = req.url?.split("?")[0] ?? "/index.html"
        const filePath2 = path.join(distPath, urlPath === "/" ? "/index.html" : urlPath)
        const ext = path.extname(filePath2)
        const content = await fs.promises.readFile(filePath2)
        res.writeHead(200, { "Content-Type": mimeTypes[ext] || "application/octet-stream", "Cache-Control": "no-cache" })
        res.end(content)
      } catch {
        res.writeHead(404)
        res.end("Not found: " + req.url)
      }
    })

    await new Promise<void>((resolve) => {
      server.listen(9999, "127.0.0.1", () => {
        console.log("[Load] → loadFile dist/ via HTTP server (port 9999)")
        resolve()
      })
    })

    await mainWindow.loadURL("http://127.0.0.1:9999/index.html")
  } else {
    // 开发模式：尝试连接 vite dev server
    console.log("[Load] → loadURL http://localhost:8888 (HTTP server mode)")
    await mainWindow.loadURL("http://localhost:8888")
  }
  mainWindow.webContents.openDevTools()

  mainWindow.on("ready-to-show", () => {
    mainWindow?.show()
  })

  mainWindow.on("closed", () => {
    mainWindow = null
  })

  mainWindow.on("close", (e) => {
    if (process.platform === "darwin") {
      e.preventDefault()
      mainWindow?.hide()
    }
  })
}

// 创建应用菜单
function createMenu(): void {
  const template: Electron.MenuItemConstructorOptions[] = [
    {
      label: "CyberTeam",
      submenu: [
        { label: "关于 CyberTeam", role: "about" },
        { type: "separator" },
        { label: "偏好设置...", accelerator: "Cmd+,", click: () => mainWindow?.webContents.send("open-settings") },
        { type: "separator" },
        { label: "隐藏 CyberTeam", accelerator: "Cmd+H", role: "hide" },
        { label: "隐藏其他", accelerator: "Cmd+Alt+H", role: "hideOthers" },
        { label: "显示全部", role: "unhide" },
        { type: "separator" },
        { label: "退出 CyberTeam", accelerator: "Cmd+Q", role: "quit" },
      ],
    },
    {
      label: "编辑",
      submenu: [
        { label: "撤销", accelerator: "Cmd+Z", role: "undo" },
        { label: "重做", accelerator: "Cmd+Shift+Z", role: "redo" },
        { type: "separator" },
        { label: "剪切", accelerator: "Cmd+X", role: "cut" },
        { label: "复制", accelerator: "Cmd+C", role: "copy" },
        { label: "粘贴", accelerator: "Cmd+V", role: "paste" },
        { label: "全选", accelerator: "Cmd+A", role: "selectAll" },
      ],
    },
    {
      label: "视图",
      submenu: [
        { label: "重新加载", accelerator: "Cmd+R", role: "reload" },
        { label: "强制重新加载", accelerator: "Cmd+Shift+R", role: "forceReload" },
        { label: "开发者工具", accelerator: "Alt+Cmd+I", role: "toggleDevTools" },
        { type: "separator" },
        { label: "放大", accelerator: "Cmd+Plus", role: "zoomIn" },
        { label: "缩小", accelerator: "Cmd+-", role: "zoomOut" },
        { label: "实际大小", accelerator: "Cmd+0", role: "resetZoom" },
        { type: "separator" },
        { label: "切换全屏", accelerator: "Ctrl+Cmd+F", role: "togglefullscreen" },
      ],
    },
    {
      label: "窗口",
      submenu: [
        { label: "最小化", accelerator: "Cmd+M", role: "minimize" },
        { label: "缩放", role: "zoom" },
        { type: "separator" },
        { label: "全部置于顶层", role: "front" },
      ],
    },
    {
      label: "帮助",
      submenu: [
        {
          label: "文档",
          click: () => shell.openExternal("https://github.com/heelaw/cyberteam-desktop"),
        },
      ],
    },
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

// 创建系统托盘
function createTray(): void {
  let icon: Electron.NativeImage
  try {
    const iconPath = path.join(__dirname, "../src-tauri.tauri.bak/icons/32x32.png")
    if (fs.existsSync(iconPath)) {
      icon = nativeImage.createFromPath(iconPath)
    } else {
      icon = nativeImage.createEmpty()
    }
  } catch {
    icon = nativeImage.createEmpty()
  }

  tray = new Tray(icon)
  tray.setToolTip("CyberTeam Desktop")

  const contextMenu = Menu.buildFromTemplate([
    { label: "显示 CyberTeam", click: () => mainWindow?.show() },
    { type: "separator" },
    { label: "新建对话", click: () => mainWindow?.webContents.send("new-session") },
    { label: "设置", click: () => mainWindow?.webContents.send("open-settings") },
    { type: "separator" },
    { label: "退出", click: () => app.quit() },
  ])

  tray.setContextMenu(contextMenu)
  tray.on("click", () => mainWindow?.show())
}

// 注册 IPC 处理程序
function registerIpcHandlers(): void {
  // ==================== 对话会话 ====================

  ipcMain.handle("chat:sessions:list", async () => {
    return db?.getSessions() || []
  })

  ipcMain.handle("chat:sessions:get", async (_, id: string) => {
    return db?.getSession(id) || null
  })

  ipcMain.handle("chat:sessions:create", async (_, data: {
    title?: string
    working_directory?: string
    provider_id?: string
    model?: string
    system_prompt?: string
    conversation_type?: string
    department_id?: string
    project_id?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    const now = new Date().toISOString()
    const session: ChatSession = {
      id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: data.title || "新会话",
      working_directory: data.working_directory || "",
      provider_id: data.provider_id || "",
      model: data.model || "",
      system_prompt: data.system_prompt || "",
      conversation_type: data.conversation_type || "single",
      department_id: data.department_id || null,
      project_id: data.project_id || null,
      review_status: "pending",
      review_notes: "",
      created_at: now,
      updated_at: now,
    }

    return db.createSession(session)
  })

  ipcMain.handle("chat:sessions:update", async (_, id: string, data: Record<string, unknown>) => {
    if (!db) return null
    return db.updateSession(id, data) || null
  })

  ipcMain.handle("chat:sessions:delete", async (_, id: string) => {
    if (!db) return false
    return db.deleteSession(id)
  })

  // ==================== 消息 ====================

  ipcMain.handle("chat:messages:list", async (_, sessionId: string) => {
    if (!db) return []
    return db.getMessages(sessionId)
  })

  ipcMain.handle("chat:messages:create", async (_, data: {
    session_id: string
    role: string
    content: string
    sender_id?: string
    sender_name?: string
    sender_avatar?: string
    metadata?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    const now = new Date().toISOString()
    const message: Message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      session_id: data.session_id,
      role: data.role as "user" | "assistant" | "system",
      content: data.content,
      sender_id: data.sender_id || "",
      sender_name: data.sender_name || "",
      sender_avatar: data.sender_avatar || "",
      metadata: data.metadata || "{}",
      token_usage: null,
      created_at: now,
    }

    // 更新会话的 updated_at
    db.updateSession(data.session_id, { updated_at: now })

    return db.createMessage(message)
  })

  // ==================== Claude Code CLI ====================

  ipcMain.handle("claude:send", async (_, data: {
    session_id: string
    message: string
    working_directory: string
    provider_id?: string
    model?: string
    system_prompt?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    if (!claudeClient) {
      claudeClient = new ClaudeClient()
    }

    // 保存用户消息
    const now = new Date().toISOString()
    db.createMessage({
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      session_id: data.session_id,
      role: "user",
      content: data.message,
      sender_id: "",
      sender_name: "",
      sender_avatar: "",
      metadata: "{}",
      token_usage: null,
      created_at: now,
    })

    db.updateSession(data.session_id, { updated_at: now })

    // 调用 Claude Code CLI
    const response = await claudeClient.sendMessage(data.message, {
      cwd: data.working_directory,
      providerId: data.provider_id,
      model: data.model,
      systemPrompt: data.system_prompt,
    })

    // 保存 AI 响应
    const aiMsgId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    db.createMessage({
      id: aiMsgId,
      session_id: data.session_id,
      role: "assistant",
      content: response,
      sender_id: "",
      sender_name: "",
      sender_avatar: "",
      metadata: "{}",
      token_usage: null,
      created_at: new Date().toISOString(),
    })

    return { content: response, messageId: aiMsgId }
  })

  ipcMain.handle("claude:stream", async (event, data: {
    session_id: string
    message: string
    working_directory: string
    provider_id?: string
    model?: string
    system_prompt?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    // 保存用户消息
    const now = new Date().toISOString()
    db.createMessage({
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      session_id: data.session_id,
      role: "user",
      content: data.message,
      sender_id: "",
      sender_name: "",
      sender_avatar: "",
      metadata: "{}",
      token_usage: null,
      created_at: now,
    })

    db.updateSession(data.session_id, { updated_at: now })

    if (!claudeClient) {
      claudeClient = new ClaudeClient()
    }

    const aiMsgId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    let fullContent = ""

    await claudeClient.sendMessageStream(data.message, {
      cwd: data.working_directory,
      providerId: data.provider_id,
      model: data.model,
      systemPrompt: data.system_prompt,
    }, (chunk: string) => {
      fullContent += chunk
      event.sender.send("claude:stream:chunk", {
        messageId: aiMsgId,
        chunk,
        fullContent,
      })
    })

    // 保存完整的 AI 消息
    db.createMessage({
      id: aiMsgId,
      session_id: data.session_id,
      role: "assistant",
      content: fullContent,
      sender_id: "",
      sender_name: "",
      sender_avatar: "",
      metadata: "{}",
      token_usage: null,
      created_at: new Date().toISOString(),
    })

    return { messageId: aiMsgId }
  })

  // ==================== 文件浏览 ====================

  // 限制文件浏览在用户主目录内
  const ALLOWED_ROOT = process.env.HOME || "/Users/cyberwiz"

  ipcMain.handle("files:browse", async (_, dirPath: string) => {
    try {
      const targetPath = path.resolve(dirPath || ALLOWED_ROOT)

      // 安全检查：确保路径在允许的目录内
      if (!targetPath.startsWith(ALLOWED_ROOT)) {
        return { current: targetPath, parent: null, directories: [], error: "访问被拒绝：只能在主目录内浏览" }
      }

      if (!fs.existsSync(targetPath)) {
        return { current: targetPath, parent: null, directories: [], error: "路径不存在" }
      }

      const stat = fs.statSync(targetPath)
      if (!stat.isDirectory()) {
        return { current: targetPath, parent: path.dirname(targetPath), directories: [], error: "不是目录" }
      }

      const parent = path.dirname(targetPath)
      const entries = fs.readdirSync(targetPath, { withFileTypes: true })

      const directories = entries
        .filter(entry => entry.isDirectory() && !entry.name.startsWith("."))
        .map(entry => ({
          name: entry.name,
          path: path.join(targetPath, entry.name),
        }))
        .sort((a, b) => a.name.localeCompare(b.name))

      return { current: targetPath, parent, directories, error: null }
    } catch (err) {
      return { current: dirPath, parent: null, directories: [], error: String(err) }
    }
  })

  ipcMain.handle("files:validate-directory", async (_, dirPath: string) => {
    try {
      if (!dirPath || !fs.existsSync(dirPath)) {
        return false
      }
      return fs.statSync(dirPath).isDirectory()
    } catch {
      return false
    }
  })

  ipcMain.handle("files:select-directory", async () => {
    if (!mainWindow) return null
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ["openDirectory"],
      title: "选择工作目录",
    })

    if (result.canceled || result.filePaths.length === 0) {
      return null
    }

    return result.filePaths[0]
  })

  // ==================== Provider 管理 ====================

  ipcMain.handle("providers:list", async () => {
    return db?.getProviders() || []
  })

  ipcMain.handle("providers:get", async (_, id: string) => {
    return db?.getProvider(id) || null
  })

  ipcMain.handle("providers:create", async (_, data: {
    name: string
    provider_type?: string
    protocol?: string
    base_url?: string
    api_key?: string
    is_active?: number
    sort_order?: number
    notes?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    const now = new Date().toISOString()
    const provider = {
      id: `provider_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      provider_type: data.provider_type || "anthropic",
      protocol: data.protocol || "",
      base_url: data.base_url || "",
      api_key: data.api_key || "",
      is_active: data.is_active ?? 0,
      sort_order: data.sort_order ?? 0,
      extra_env: "{}",
      headers_json: "{}",
      role_models_json: "{}",
      notes: data.notes || "",
      created_at: now,
      updated_at: now,
    }

    return db.createProvider(provider)
  })

  ipcMain.handle("providers:update", async (_, id: string, data: Record<string, unknown>) => {
    if (!db) return null
    return db.updateProvider(id, data) || null
  })

  ipcMain.handle("providers:delete", async (_, id: string) => {
    if (!db) return false
    return db.deleteProvider(id)
  })

  ipcMain.handle("providers:test", async (_, id: string) => {
    if (!db) return { success: false, error: "Database not initialized" }

    const provider = db.getProvider(id)
    if (!provider) {
      return { success: false, error: "Provider not found" }
    }

    try {
      const response = await fetch(provider.base_url + "/v1/models", {
        headers: {
          "Authorization": `Bearer ${provider.api_key}`,
          "Content-Type": "application/json",
        },
      })

      if (response.ok) {
        return { success: true }
      } else {
        const error = await response.text()
        return { success: false, error: `HTTP ${response.status}: ${error}` }
      }
    } catch (err) {
      return { success: false, error: String(err) }
    }
  })

  // ==================== 项目管理 ====================

  ipcMain.handle("projects:list", async () => {
    return db?.getProjects() || []
  })

  ipcMain.handle("projects:get", async (_, id: string) => {
    return db?.getProject(id) || null
  })

  ipcMain.handle("projects:create", async (_, data: {
    name: string
    description?: string
    working_directory?: string
    department_id?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    const now = new Date().toISOString()
    return db.createProject({
      id: `project_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      description: data.description || "",
      working_directory: data.working_directory || "",
      department_id: data.department_id || null,
      status: "active",
      created_at: now,
      updated_at: now,
    })
  })

  ipcMain.handle("projects:update", async (_, id: string, data: Record<string, unknown>) => {
    if (!db) return null
    return db.updateProject(id, data) || null
  })

  ipcMain.handle("projects:delete", async (_, id: string) => {
    if (!db) return false
    return db.deleteProject(id)
  })

  // ==================== 部门管理 ====================

  ipcMain.handle("departments:list", async () => {
    return db?.getDepartments() || []
  })

  ipcMain.handle("departments:create", async (_, data: {
    name: string
    icon?: string
    parent_id?: string
    description?: string
    sort_order?: number
  }) => {
    if (!db) throw new Error("Database not initialized")

    return db.createDepartment({
      id: `dept_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      icon: data.icon || "",
      parent_id: data.parent_id || null,
      description: data.description || "",
      sort_order: data.sort_order ?? 0,
      created_at: new Date().toISOString(),
    })
  })

  ipcMain.handle("departments:update", async (_, id: string, data: Record<string, unknown>) => {
    if (!db) return null
    return db.updateDepartment(id, data) || null
  })

  ipcMain.handle("departments:delete", async (_, id: string) => {
    if (!db) return false
    return db.deleteDepartment(id)
  })

  // ==================== Agent 管理 ====================

  ipcMain.handle("agents:list", async () => {
    return db?.getAgents() || []
  })

  ipcMain.handle("agents:get", async (_, id: string) => {
    return db?.getAgent(id) || null
  })

  ipcMain.handle("agents:create", async (_, data: {
    name: string
    avatar?: string
    role?: string
    department_id: string
    description?: string
    soul_content?: string
    capabilities?: string
    config?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    return db.createAgent({
      id: `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      avatar: data.avatar || "",
      role: data.role || "expert",
      department_id: data.department_id,
      description: data.description || "",
      soul_content: data.soul_content || "",
      status: "offline",
      capabilities: data.capabilities || "[]",
      config: data.config || "{}",
      created_at: new Date().toISOString(),
    })
  })

  ipcMain.handle("agents:update", async (_, id: string, data: Record<string, unknown>) => {
    if (!db) return null
    return db.updateAgent(id, data) || null
  })

  ipcMain.handle("agents:delete", async (_, id: string) => {
    if (!db) return false
    return db.deleteAgent(id)
  })

  // ==================== 会议纪要 ====================

  ipcMain.handle("meeting-minutes:list", async (_, projectId?: string) => {
    return db?.getMeetingMinutes(projectId) || []
  })

  ipcMain.handle("meeting-minutes:create", async (_, data: {
    project_id: string
    meeting_type: string
    title: string
    content?: string
    attachments?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    return db.createMeetingMinutes({
      id: `minutes_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      project_id: data.project_id,
      meeting_type: data.meeting_type,
      title: data.title,
      content: data.content || "",
      review_status: "pending",
      attachments: data.attachments || "[]",
      created_at: new Date().toISOString(),
    })
  })

  ipcMain.handle("meeting-minutes:update", async (_, id: string, data: Record<string, unknown>) => {
    if (!db) return null
    return db.updateMeetingMinutes(id, data) || null
  })

  // ==================== Crew 团队模板 ====================

  ipcMain.handle("crew-templates:list", async () => {
    return db?.getCrewTemplates() || []
  })

  ipcMain.handle("crew-templates:create", async (_, data: {
    name: string
    description?: string
    members?: string
    departments?: string
    is_preset?: number
  }) => {
    if (!db) throw new Error("Database not initialized")

    return db.createCrewTemplate({
      id: `crew_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      description: data.description || "",
      members: data.members || "[]",
      departments: data.departments || "[]",
      is_preset: data.is_preset ?? 0,
      created_at: new Date().toISOString(),
    })
  })

  ipcMain.handle("crew-templates:delete", async (_, id: string) => {
    if (!db) return false
    return db.deleteCrewTemplate(id)
  })

  // ==================== 系统 ====================

  ipcMain.handle("system:get-home-directory", async () => {
    return process.env.HOME || "/Users/cyberwiz"
  })

  ipcMain.handle("system:open-external", async (_, url: string) => {
    try {
      const parsed = new URL(url)
      // 只允许 http/https 协议
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        return false
      }
      await shell.openExternal(url)
      return true
    } catch {
      return false
    }
  })

  ipcMain.handle("system:show-item-in-folder", async (_, filePath: string) => {
    // 安全检查：确保文件路径在允许的目录内
    const resolvedPath = path.resolve(filePath)
    if (!resolvedPath.startsWith(ALLOWED_ROOT)) {
      return false
    }
    shell.showItemInFolder(filePath)
    return true
  })

  // ==================== Skill 管理 ====================

  ipcMain.handle("skills:list", async () => {
    return db?.getSkills() || []
  })

  ipcMain.handle("skills:get", async (_, id: string) => {
    return db?.getSkill(id) || null
  })

  ipcMain.handle("skills:by-agent", async (_, agentId: string) => {
    return db?.getSkillsByAgent(agentId) || []
  })

  ipcMain.handle("skills:by-department", async (_, deptId: string) => {
    return db?.getSkillsByDepartment(deptId) || []
  })

  ipcMain.handle("skills:create", async (_, data: {
    name: string
    icon?: string
    category?: string
    description?: string
    trigger?: string
    workflow?: string
    agent_id?: string | null
    department_id?: string | null
    is_preset?: number
    config?: string
  }) => {
    if (!db) throw new Error("Database not initialized")

    const now = new Date().toISOString()
    return db.createSkill({
      id: `skill_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      icon: data.icon || "⚡",
      category: data.category || "custom",
      description: data.description || "",
      trigger: data.trigger || "",
      workflow: data.workflow || "",
      agent_id: data.agent_id || null,
      department_id: data.department_id || null,
      is_preset: data.is_preset ?? 0,
      config: data.config || "{}",
      created_at: now,
      updated_at: now,
    })
  })

  ipcMain.handle("skills:update", async (_, id: string, data: Record<string, unknown>) => {
    if (!db) return null
    return db.updateSkill(id, { ...data, updated_at: new Date().toISOString() }) || null
  })

  ipcMain.handle("skills:delete", async (_, id: string) => {
    if (!db) return false
    return db.deleteSkill(id)
  })
}

// 应用启动
app.whenReady().then(async () => {
  console.log("[Main] CyberTeam Desktop starting...")

  // 初始化数据库
  db = initDatabase()

  // 初始化预设数据（部门、Agent、团队模板）
  initDefaultData()

  // 注册 IPC 处理程序
  registerIpcHandlers()

  // 创建窗口
  await createWindow()

  console.log("[Main] CyberTeam Desktop ready")
})

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit()
  }
})

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  } else {
    mainWindow?.show()
  }
})

app.on("before-quit", () => {
  if (claudeClient) {
    claudeClient.close()
  }
})
