var __require = /* @__PURE__ */ ((x) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(x, {
  get: (a, b) => (typeof require !== "undefined" ? require : a)[b]
}) : x)(function(x) {
  if (typeof require !== "undefined") return require.apply(this, arguments);
  throw Error('Dynamic require of "' + x + '" is not supported');
});

// electron/main.ts
import {
  app as app2,
  BrowserWindow,
  ipcMain,
  dialog,
  shell,
  Menu,
  Tray,
  nativeImage
} from "electron";
import path3 from "path";
import fs3 from "fs";

// electron/database.ts
import path from "path";
import fs from "fs";
import { app } from "electron";
var JsonDatabase = class {
  dbPath;
  data;
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.data = this.load();
  }
  load() {
    try {
      if (fs.existsSync(this.dbPath)) {
        const content = fs.readFileSync(this.dbPath, "utf-8");
        return JSON.parse(content);
      }
    } catch (err) {
      console.error("[DB] Load error:", err);
    }
    return this.getDefaultData();
  }
  save() {
    try {
      const dir = path.dirname(this.dbPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.dbPath, JSON.stringify(this.data, null, 2));
    } catch (err) {
      console.error("[DB] Save error:", err);
    }
  }
  getDefaultData() {
    const now = (/* @__PURE__ */ new Date()).toISOString();
    return {
      providers: [
        {
          id: "provider_anthropic",
          name: "Anthropic",
          provider_type: "anthropic",
          protocol: "anthropic",
          base_url: "https://api.anthropic.com",
          api_key: "",
          is_active: 1,
          sort_order: 0,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now
        },
        {
          id: "provider_minimax",
          name: "MiniMax",
          provider_type: "minimax",
          protocol: "openai-compatible",
          base_url: "https://api.minimax.chat/v",
          api_key: "",
          is_active: 0,
          sort_order: 1,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now
        },
        {
          id: "provider_openrouter",
          name: "OpenRouter",
          provider_type: "openrouter",
          protocol: "openrouter",
          base_url: "https://openrouter.ai/api/v1",
          api_key: "",
          is_active: 0,
          sort_order: 2,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now
        }
      ],
      sessions: [],
      messages: [],
      projects: [],
      departments: [
        { id: "dept_ceo", name: "CEO", icon: "\u{1F451}", parent_id: null, description: "", sort_order: 0, created_at: now },
        { id: "dept_coo", name: "COO", icon: "\u{1F3AF}", parent_id: null, description: "", sort_order: 1, created_at: now },
        { id: "dept_strategy", name: "\u6218\u7565\u90E8", icon: "\u{1F4CA}", parent_id: null, description: "", sort_order: 2, created_at: now },
        { id: "dept_product", name: "\u4EA7\u54C1\u90E8", icon: "\u{1F4BC}", parent_id: null, description: "", sort_order: 3, created_at: now },
        { id: "dept_eng", name: "\u7814\u53D1\u90E8", icon: "\u2699\uFE0F", parent_id: null, description: "", sort_order: 4, created_at: now },
        { id: "dept_design", name: "\u8BBE\u8BA1\u90E8", icon: "\u{1F3A8}", parent_id: null, description: "", sort_order: 5, created_at: now },
        { id: "dept_ops", name: "\u8FD0\u8425\u90E8", icon: "\u{1F680}", parent_id: null, description: "", sort_order: 6, created_at: now },
        { id: "dept_finance", name: "\u8D22\u52A1\u90E8", icon: "\u{1F4B0}", parent_id: null, description: "", sort_order: 7, created_at: now },
        { id: "dept_hr", name: "\u4EBA\u529B\u8D44\u6E90\u90E8", icon: "\u{1F465}", parent_id: null, description: "", sort_order: 8, created_at: now },
        { id: "dept_marketing", name: "\u5E02\u573A\u90E8", icon: "\u{1F4E2}", parent_id: null, description: "", sort_order: 9, created_at: now }
      ],
      agents: [
        {
          id: "agent_ceo",
          name: "CEO",
          avatar: "\u{1F451}",
          role: "ceo",
          department_id: "dept_ceo",
          description: "CyberTeam CEO\uFF0C\u8D1F\u8D23\u6218\u7565\u51B3\u7B56\u548C\u6574\u4F53\u534F\u8C03",
          soul_content: "",
          status: "online",
          capabilities: "[]",
          config: "{}",
          created_at: now
        }
      ],
      meetingMinutes: [],
      crewTemplates: []
    };
  }
  // ==================== Provider ====================
  getProviders() {
    return this.data.providers.sort((a, b) => a.sort_order - b.sort_order);
  }
  getProvider(id) {
    return this.data.providers.find((p) => p.id === id);
  }
  createProvider(provider) {
    this.data.providers.push(provider);
    this.save();
    return provider;
  }
  updateProvider(id, data) {
    const index = this.data.providers.findIndex((p) => p.id === id);
    if (index !== -1) {
      this.data.providers[index] = { ...this.data.providers[index], ...data };
      this.save();
      return this.data.providers[index];
    }
    return void 0;
  }
  deleteProvider(id) {
    const index = this.data.providers.findIndex((p) => p.id === id);
    if (index !== -1) {
      this.data.providers.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Sessions ====================
  getSessions() {
    return this.data.sessions.sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
  }
  getSession(id) {
    return this.data.sessions.find((s) => s.id === id);
  }
  createSession(session) {
    this.data.sessions.push(session);
    this.save();
    return session;
  }
  updateSession(id, data) {
    const index = this.data.sessions.findIndex((s) => s.id === id);
    if (index !== -1) {
      this.data.sessions[index] = { ...this.data.sessions[index], ...data };
      this.save();
      return this.data.sessions[index];
    }
    return void 0;
  }
  deleteSession(id) {
    const index = this.data.sessions.findIndex((s) => s.id === id);
    if (index !== -1) {
      this.data.sessions.splice(index, 1);
      this.data.messages = this.data.messages.filter((m) => m.session_id !== id);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Messages ====================
  getMessages(sessionId) {
    return this.data.messages.filter((m) => m.session_id === sessionId).sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
  }
  createMessage(message) {
    this.data.messages.push(message);
    this.save();
    return message;
  }
  // ==================== Projects ====================
  getProjects() {
    return this.data.projects.sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
  }
  getProject(id) {
    return this.data.projects.find((p) => p.id === id);
  }
  createProject(project) {
    this.data.projects.push(project);
    this.save();
    return project;
  }
  updateProject(id, data) {
    const index = this.data.projects.findIndex((p) => p.id === id);
    if (index !== -1) {
      this.data.projects[index] = { ...this.data.projects[index], ...data };
      this.save();
      return this.data.projects[index];
    }
    return void 0;
  }
  deleteProject(id) {
    const index = this.data.projects.findIndex((p) => p.id === id);
    if (index !== -1) {
      this.data.projects.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Departments ====================
  getDepartments() {
    return this.data.departments.sort((a, b) => a.sort_order - b.sort_order);
  }
  getDepartment(id) {
    return this.data.departments.find((d) => d.id === id);
  }
  createDepartment(department) {
    this.data.departments.push(department);
    this.save();
    return department;
  }
  updateDepartment(id, data) {
    const index = this.data.departments.findIndex((d) => d.id === id);
    if (index !== -1) {
      this.data.departments[index] = { ...this.data.departments[index], ...data };
      this.save();
      return this.data.departments[index];
    }
    return void 0;
  }
  deleteDepartment(id) {
    const index = this.data.departments.findIndex((d) => d.id === id);
    if (index !== -1) {
      this.data.departments.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Agents ====================
  getAgents() {
    return this.data.agents.sort((a, b) => a.department_id.localeCompare(b.department_id));
  }
  getAgent(id) {
    return this.data.agents.find((a) => a.id === id);
  }
  createAgent(agent) {
    this.data.agents.push(agent);
    this.save();
    return agent;
  }
  updateAgent(id, data) {
    const index = this.data.agents.findIndex((a) => a.id === id);
    if (index !== -1) {
      this.data.agents[index] = { ...this.data.agents[index], ...data };
      this.save();
      return this.data.agents[index];
    }
    return void 0;
  }
  deleteAgent(id) {
    const index = this.data.agents.findIndex((a) => a.id === id);
    if (index !== -1) {
      this.data.agents.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Meeting Minutes ====================
  getMeetingMinutes(projectId) {
    let minutes = this.data.meetingMinutes;
    if (projectId) {
      minutes = minutes.filter((m) => m.project_id === projectId);
    }
    return minutes.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }
  createMeetingMinutes(minutes) {
    this.data.meetingMinutes.push(minutes);
    this.save();
    return minutes;
  }
  updateMeetingMinutes(id, data) {
    const index = this.data.meetingMinutes.findIndex((m) => m.id === id);
    if (index !== -1) {
      this.data.meetingMinutes[index] = { ...this.data.meetingMinutes[index], ...data };
      this.save();
      return this.data.meetingMinutes[index];
    }
    return void 0;
  }
  // ==================== Crew Templates ====================
  getCrewTemplates() {
    return this.data.crewTemplates.sort((a, b) => b.is_preset - a.is_preset);
  }
  createCrewTemplate(template) {
    this.data.crewTemplates.push(template);
    this.save();
    return template;
  }
  deleteCrewTemplate(id) {
    const index = this.data.crewTemplates.findIndex((t) => t.id === id);
    if (index !== -1) {
      this.data.crewTemplates.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
};
var dbInstance = null;
function initDatabase() {
  const userDataPath = app.getPath("userData");
  const dbPath = path.join(userDataPath, "cyberteam-data.json");
  dbInstance = new JsonDatabase(dbPath);
  console.log("[DB] Database initialized:", dbPath);
  return dbInstance;
}

// electron/claude-client.ts
import { spawn } from "child_process";
import path2 from "path";
import fs2 from "fs";
import os from "os";
var ClaudeClient = class {
  sessionProcess = null;
  sessionReady = false;
  pendingRequests = /* @__PURE__ */ new Map();
  buffer = "";
  constructor() {
  }
  async sendMessage(message, options = {}) {
    const { cwd = os.homedir(), providerId, model, systemPrompt } = options;
    return new Promise((resolve, reject) => {
      this.ensureSession(cwd, { providerId, model, systemPrompt }, (err) => {
        if (err) {
          reject(err);
          return;
        }
        const requestId = `req_${Date.now()}`;
        this.pendingRequests.set(requestId, { resolve, reject });
        if (this.sessionProcess) {
          this.sessionProcess.stdin.write(JSON.stringify({
            type: "user",
            content: message,
            requestId
          }) + "\n");
        }
        setTimeout(() => {
          if (this.pendingRequests.has(requestId)) {
            this.pendingRequests.delete(requestId);
            reject(new Error("Request timeout"));
          }
        }, 12e4);
      });
    });
  }
  async sendMessageStream(message, options = {}, onChunk) {
    const { cwd = os.homedir(), providerId, model, systemPrompt } = options;
    return new Promise((resolve, reject) => {
      this.ensureSession(cwd, { providerId, model, systemPrompt }, (err) => {
        if (err) {
          reject(err);
          return;
        }
        const requestId = `req_${Date.now()}`;
        this.sessionProcess?.stdout.on("data", (data) => {
          this.buffer += data.toString();
          const lines = this.buffer.split("\n");
          this.buffer = lines.pop() || "";
          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const parsed = JSON.parse(line);
              if (parsed.requestId === requestId) {
                if (parsed.type === "chunk") {
                  onChunk(parsed.content);
                } else if (parsed.type === "done") {
                  resolve();
                } else if (parsed.type === "error") {
                  reject(new Error(parsed.error));
                }
              }
            } catch {
            }
          }
        });
        if (this.sessionProcess) {
          this.sessionProcess.stdin.write(JSON.stringify({
            type: "user",
            content: message,
            requestId
          }) + "\n");
        }
        setTimeout(() => {
          reject(new Error("Stream timeout"));
        }, 12e4);
      });
    });
  }
  ensureSession(cwd, options, callback) {
    if (this.sessionProcess && this.sessionReady) {
      callback(null);
      return;
    }
    const claudePath = this.findClaudeCLI();
    if (!claudePath) {
      callback(new Error("Claude Code CLI not found. Please install it first."));
      return;
    }
    const args = [
      "--dangerously-skip-permissions",
      "--output-format",
      "json-stream"
    ];
    if (options.providerId) {
      args.push("--provider", options.providerId);
    }
    if (options.model) {
      args.push("--model", options.model);
    }
    this.sessionProcess = spawn(claudePath, args, {
      cwd,
      env: {
        ...process.env,
        // 添加 system prompt 到环境变量
        ...options.systemPrompt ? { CLAUDE_SYSTEM_PROMPT: options.systemPrompt } : {}
      },
      stdio: ["pipe", "pipe", "pipe"]
    });
    this.sessionProcess.stderr.on("data", (data) => {
      console.error("[ClaudeClient stderr]", data.toString());
    });
    this.sessionProcess.on("error", (err) => {
      console.error("[ClaudeClient error]", err);
      callback(err);
    });
    this.sessionProcess.on("close", (code) => {
      console.log("[ClaudeClient closed]", code);
      this.sessionProcess = null;
      this.sessionReady = false;
    });
    this.sessionProcess.stdout.on("data", (data) => {
      this.buffer += data.toString();
      const lines = this.buffer.split("\n");
      this.buffer = lines.pop() || "";
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const parsed = JSON.parse(line);
          if (parsed.type === "ready") {
            this.sessionReady = true;
            callback(null);
          } else if (parsed.type === "response" && parsed.requestId) {
            const pending = this.pendingRequests.get(parsed.requestId);
            if (pending) {
              pending.resolve(parsed.content);
              this.pendingRequests.delete(parsed.requestId);
            }
          } else if (parsed.type === "error" && parsed.requestId) {
            const pending = this.pendingRequests.get(parsed.requestId);
            if (pending) {
              pending.reject(new Error(parsed.error));
              this.pendingRequests.delete(parsed.requestId);
            }
          }
        } catch {
        }
      }
    });
    setTimeout(() => {
      if (!this.sessionReady) {
        this.sessionProcess?.stdin.write(JSON.stringify({
          type: "ping"
        }) + "\n");
      }
    }, 5e3);
  }
  findClaudeCLI() {
    const possiblePaths = [
      "/opt/homebrew/bin/claude",
      "/usr/local/bin/claude",
      path2.join(os.homedir(), ".local/bin/claude"),
      "claude"
      // PATH 中
    ];
    for (const p of possiblePaths) {
      try {
        if (p === "claude") {
          const which = __require("child_process").spawnSync("which", ["claude"], { shell: true });
          if (which.status === 0 && which.stdout.toString().trim()) {
            return which.stdout.toString().trim();
          }
        } else if (fs2.existsSync(p)) {
          return p;
        }
      } catch {
      }
    }
    return null;
  }
  close() {
    if (this.sessionProcess) {
      this.sessionProcess.stdin.write(JSON.stringify({ type: "quit" }) + "\n");
      setTimeout(() => {
        if (this.sessionProcess) {
          this.sessionProcess.kill();
          this.sessionProcess = null;
        }
      }, 1e3);
    }
  }
};

// electron/main.ts
var isDev = process.env.NODE_ENV === "development" || !app2.isPackaged;
var mainWindow = null;
var tray = null;
var claudeClient = null;
var db = null;
async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1e3,
    minHeight: 700,
    title: "CyberTeam Desktop",
    backgroundColor: "#0a0a0f",
    show: false,
    webPreferences: {
      preload: path3.join(__dirname, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false
    }
  });
  createMenu();
  createTray();
  if (isDev) {
    await mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    await mainWindow.loadFile(path3.join(__dirname, "../dist/index.html"));
  }
  mainWindow.on("ready-to-show", () => {
    mainWindow?.show();
  });
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
  mainWindow.on("close", (e) => {
    if (process.platform === "darwin") {
      e.preventDefault();
      mainWindow?.hide();
    }
  });
}
function createMenu() {
  const template = [
    {
      label: "CyberTeam",
      submenu: [
        { label: "\u5173\u4E8E CyberTeam", role: "about" },
        { type: "separator" },
        { label: "\u504F\u597D\u8BBE\u7F6E...", accelerator: "Cmd+,", click: () => mainWindow?.webContents.send("open-settings") },
        { type: "separator" },
        { label: "\u9690\u85CF CyberTeam", accelerator: "Cmd+H", role: "hide" },
        { label: "\u9690\u85CF\u5176\u4ED6", accelerator: "Cmd+Alt+H", role: "hideOthers" },
        { label: "\u663E\u793A\u5168\u90E8", role: "unhide" },
        { type: "separator" },
        { label: "\u9000\u51FA CyberTeam", accelerator: "Cmd+Q", role: "quit" }
      ]
    },
    {
      label: "\u7F16\u8F91",
      submenu: [
        { label: "\u64A4\u9500", accelerator: "Cmd+Z", role: "undo" },
        { label: "\u91CD\u505A", accelerator: "Cmd+Shift+Z", role: "redo" },
        { type: "separator" },
        { label: "\u526A\u5207", accelerator: "Cmd+X", role: "cut" },
        { label: "\u590D\u5236", accelerator: "Cmd+C", role: "copy" },
        { label: "\u7C98\u8D34", accelerator: "Cmd+V", role: "paste" },
        { label: "\u5168\u9009", accelerator: "Cmd+A", role: "selectAll" }
      ]
    },
    {
      label: "\u89C6\u56FE",
      submenu: [
        { label: "\u91CD\u65B0\u52A0\u8F7D", accelerator: "Cmd+R", role: "reload" },
        { label: "\u5F3A\u5236\u91CD\u65B0\u52A0\u8F7D", accelerator: "Cmd+Shift+R", role: "forceReload" },
        { label: "\u5F00\u53D1\u8005\u5DE5\u5177", accelerator: "Alt+Cmd+I", role: "toggleDevTools" },
        { type: "separator" },
        { label: "\u653E\u5927", accelerator: "Cmd+Plus", role: "zoomIn" },
        { label: "\u7F29\u5C0F", accelerator: "Cmd+-", role: "zoomOut" },
        { label: "\u5B9E\u9645\u5927\u5C0F", accelerator: "Cmd+0", role: "resetZoom" },
        { type: "separator" },
        { label: "\u5207\u6362\u5168\u5C4F", accelerator: "Ctrl+Cmd+F", role: "togglefullscreen" }
      ]
    },
    {
      label: "\u7A97\u53E3",
      submenu: [
        { label: "\u6700\u5C0F\u5316", accelerator: "Cmd+M", role: "minimize" },
        { label: "\u7F29\u653E", role: "zoom" },
        { type: "separator" },
        { label: "\u5168\u90E8\u7F6E\u4E8E\u9876\u5C42", role: "front" }
      ]
    },
    {
      label: "\u5E2E\u52A9",
      submenu: [
        {
          label: "\u6587\u6863",
          click: () => shell.openExternal("https://github.com/heelaw/cyberteam-desktop")
        }
      ]
    }
  ];
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}
function createTray() {
  let icon;
  try {
    const iconPath = path3.join(__dirname, "../src-tauri.tauri.bak/icons/32x32.png");
    if (fs3.existsSync(iconPath)) {
      icon = nativeImage.createFromPath(iconPath);
    } else {
      icon = nativeImage.createEmpty();
    }
  } catch {
    icon = nativeImage.createEmpty();
  }
  tray = new Tray(icon);
  tray.setToolTip("CyberTeam Desktop");
  const contextMenu = Menu.buildFromTemplate([
    { label: "\u663E\u793A CyberTeam", click: () => mainWindow?.show() },
    { type: "separator" },
    { label: "\u65B0\u5EFA\u5BF9\u8BDD", click: () => mainWindow?.webContents.send("new-session") },
    { label: "\u8BBE\u7F6E", click: () => mainWindow?.webContents.send("open-settings") },
    { type: "separator" },
    { label: "\u9000\u51FA", click: () => app2.quit() }
  ]);
  tray.setContextMenu(contextMenu);
  tray.on("click", () => mainWindow?.show());
}
function registerIpcHandlers() {
  ipcMain.handle("chat:sessions:list", async () => {
    return db?.getSessions() || [];
  });
  ipcMain.handle("chat:sessions:get", async (_, id) => {
    return db?.getSession(id) || null;
  });
  ipcMain.handle("chat:sessions:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    const session = {
      id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: data.title || "\u65B0\u4F1A\u8BDD",
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
      updated_at: now
    };
    return db.createSession(session);
  });
  ipcMain.handle("chat:sessions:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateSession(id, data) || null;
  });
  ipcMain.handle("chat:sessions:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteSession(id);
  });
  ipcMain.handle("chat:messages:list", async (_, sessionId) => {
    if (!db) return [];
    return db.getMessages(sessionId);
  });
  ipcMain.handle("chat:messages:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    const message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      session_id: data.session_id,
      role: data.role,
      content: data.content,
      sender_id: data.sender_id || "",
      sender_name: data.sender_name || "",
      sender_avatar: data.sender_avatar || "",
      metadata: data.metadata || "{}",
      token_usage: null,
      created_at: now
    };
    db.updateSession(data.session_id, { updated_at: now });
    return db.createMessage(message);
  });
  ipcMain.handle("claude:send", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    if (!claudeClient) {
      claudeClient = new ClaudeClient();
    }
    const now = (/* @__PURE__ */ new Date()).toISOString();
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
      created_at: now
    });
    db.updateSession(data.session_id, { updated_at: now });
    const response = await claudeClient.sendMessage(data.message, {
      cwd: data.working_directory,
      providerId: data.provider_id,
      model: data.model,
      systemPrompt: data.system_prompt
    });
    const aiMsgId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
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
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
    return { content: response, messageId: aiMsgId };
  });
  ipcMain.handle("claude:stream", async (event, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
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
      created_at: now
    });
    db.updateSession(data.session_id, { updated_at: now });
    if (!claudeClient) {
      claudeClient = new ClaudeClient();
    }
    const aiMsgId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    let fullContent = "";
    await claudeClient.sendMessageStream(data.message, {
      cwd: data.working_directory,
      providerId: data.provider_id,
      model: data.model,
      systemPrompt: data.system_prompt
    }, (chunk) => {
      fullContent += chunk;
      event.sender.send("claude:stream:chunk", {
        messageId: aiMsgId,
        chunk,
        fullContent
      });
    });
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
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
    return { messageId: aiMsgId };
  });
  ipcMain.handle("files:browse", async (_, dirPath) => {
    try {
      const targetPath = dirPath || process.env.HOME || ".";
      if (!fs3.existsSync(targetPath)) {
        return { current: targetPath, parent: null, directories: [], error: "\u8DEF\u5F84\u4E0D\u5B58\u5728" };
      }
      const stat = fs3.statSync(targetPath);
      if (!stat.isDirectory()) {
        return { current: targetPath, parent: path3.dirname(targetPath), directories: [], error: "\u4E0D\u662F\u76EE\u5F55" };
      }
      const parent = path3.dirname(targetPath);
      const entries = fs3.readdirSync(targetPath, { withFileTypes: true });
      const directories = entries.filter((entry) => entry.isDirectory() && !entry.name.startsWith(".")).map((entry) => ({
        name: entry.name,
        path: path3.join(targetPath, entry.name)
      })).sort((a, b) => a.name.localeCompare(b.name));
      return { current: targetPath, parent, directories, error: null };
    } catch (err) {
      return { current: dirPath, parent: null, directories: [], error: String(err) };
    }
  });
  ipcMain.handle("files:validate-directory", async (_, dirPath) => {
    try {
      if (!dirPath || !fs3.existsSync(dirPath)) {
        return false;
      }
      return fs3.statSync(dirPath).isDirectory();
    } catch {
      return false;
    }
  });
  ipcMain.handle("files:select-directory", async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ["openDirectory"],
      title: "\u9009\u62E9\u5DE5\u4F5C\u76EE\u5F55"
    });
    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }
    return result.filePaths[0];
  });
  ipcMain.handle("providers:list", async () => {
    return db?.getProviders() || [];
  });
  ipcMain.handle("providers:get", async (_, id) => {
    return db?.getProvider(id) || null;
  });
  ipcMain.handle("providers:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
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
      updated_at: now
    };
    return db.createProvider(provider);
  });
  ipcMain.handle("providers:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateProvider(id, data) || null;
  });
  ipcMain.handle("providers:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteProvider(id);
  });
  ipcMain.handle("providers:test", async (_, id) => {
    if (!db) return { success: false, error: "Database not initialized" };
    const provider = db.getProvider(id);
    if (!provider) {
      return { success: false, error: "Provider not found" };
    }
    try {
      const response = await fetch(provider.base_url + "/v1/models", {
        headers: {
          "Authorization": `Bearer ${provider.api_key}`,
          "Content-Type": "application/json"
        }
      });
      if (response.ok) {
        return { success: true };
      } else {
        const error = await response.text();
        return { success: false, error: `HTTP ${response.status}: ${error}` };
      }
    } catch (err) {
      return { success: false, error: String(err) };
    }
  });
  ipcMain.handle("projects:list", async () => {
    return db?.getProjects() || [];
  });
  ipcMain.handle("projects:get", async (_, id) => {
    return db?.getProject(id) || null;
  });
  ipcMain.handle("projects:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    return db.createProject({
      id: `project_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      description: data.description || "",
      working_directory: data.working_directory || "",
      department_id: data.department_id || null,
      status: "active",
      created_at: now,
      updated_at: now
    });
  });
  ipcMain.handle("projects:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateProject(id, data) || null;
  });
  ipcMain.handle("projects:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteProject(id);
  });
  ipcMain.handle("departments:list", async () => {
    return db?.getDepartments() || [];
  });
  ipcMain.handle("departments:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    return db.createDepartment({
      id: `dept_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      icon: data.icon || "",
      parent_id: data.parent_id || null,
      description: data.description || "",
      sort_order: data.sort_order ?? 0,
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
  });
  ipcMain.handle("departments:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateDepartment(id, data) || null;
  });
  ipcMain.handle("departments:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteDepartment(id);
  });
  ipcMain.handle("agents:list", async () => {
    return db?.getAgents() || [];
  });
  ipcMain.handle("agents:get", async (_, id) => {
    return db?.getAgent(id) || null;
  });
  ipcMain.handle("agents:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
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
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
  });
  ipcMain.handle("agents:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateAgent(id, data) || null;
  });
  ipcMain.handle("agents:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteAgent(id);
  });
  ipcMain.handle("meeting-minutes:list", async (_, projectId) => {
    return db?.getMeetingMinutes(projectId) || [];
  });
  ipcMain.handle("meeting-minutes:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    return db.createMeetingMinutes({
      id: `minutes_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      project_id: data.project_id,
      meeting_type: data.meeting_type,
      title: data.title,
      content: data.content || "",
      review_status: "pending",
      attachments: data.attachments || "[]",
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
  });
  ipcMain.handle("meeting-minutes:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateMeetingMinutes(id, data) || null;
  });
  ipcMain.handle("crew-templates:list", async () => {
    return db?.getCrewTemplates() || [];
  });
  ipcMain.handle("crew-templates:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    return db.createCrewTemplate({
      id: `crew_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      description: data.description || "",
      members: data.members || "[]",
      departments: data.departments || "[]",
      is_preset: data.is_preset ?? 0,
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
  });
  ipcMain.handle("crew-templates:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteCrewTemplate(id);
  });
  ipcMain.handle("system:get-home-directory", async () => {
    return process.env.HOME || "/Users/cyberwiz";
  });
  ipcMain.handle("system:open-external", async (_, url) => {
    await shell.openExternal(url);
    return true;
  });
  ipcMain.handle("system:show-item-in-folder", async (_, filePath) => {
    shell.showItemInFolder(filePath);
    return true;
  });
}
app2.whenReady().then(async () => {
  console.log("[Main] CyberTeam Desktop starting...");
  db = initDatabase();
  registerIpcHandlers();
  await createWindow();
  console.log("[Main] CyberTeam Desktop ready");
});
app2.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app2.quit();
  }
});
app2.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  } else {
    mainWindow?.show();
  }
});
app2.on("before-quit", () => {
  if (claudeClient) {
    claudeClient.close();
  }
});
