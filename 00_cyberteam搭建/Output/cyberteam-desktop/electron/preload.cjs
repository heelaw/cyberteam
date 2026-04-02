var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// electron/preload.ts
var preload_exports = {};
module.exports = __toCommonJS(preload_exports);
var import_electron = require("electron");
var api = {
  // ==================== 对话会话 ====================
  chat: {
    sessions: {
      list: () => import_electron.ipcRenderer.invoke("chat:sessions:list"),
      get: (id) => import_electron.ipcRenderer.invoke("chat:sessions:get", id),
      create: (data) => import_electron.ipcRenderer.invoke("chat:sessions:create", data),
      update: (id, data) => import_electron.ipcRenderer.invoke("chat:sessions:update", id, data),
      delete: (id) => import_electron.ipcRenderer.invoke("chat:sessions:delete", id)
    },
    messages: {
      list: (sessionId) => import_electron.ipcRenderer.invoke("chat:messages:list", sessionId),
      create: (data) => import_electron.ipcRenderer.invoke("chat:messages:create", data)
    }
  },
  // ==================== Claude Code CLI ====================
  claude: {
    send: (data) => import_electron.ipcRenderer.invoke("claude:send", data),
    stream: (data, onChunk) => {
      const listener = (_, data2) => {
        onChunk(data2);
      };
      import_electron.ipcRenderer.on("claude:stream:chunk", listener);
      return import_electron.ipcRenderer.invoke("claude:stream", data).finally(() => {
        import_electron.ipcRenderer.removeListener("claude:stream:chunk", listener);
      });
    }
  },
  // ==================== 文件浏览 ====================
  files: {
    browse: (dirPath) => import_electron.ipcRenderer.invoke("files:browse", dirPath),
    validateDirectory: (dirPath) => import_electron.ipcRenderer.invoke("files:validate-directory", dirPath),
    selectDirectory: () => import_electron.ipcRenderer.invoke("files:select-directory")
  },
  // ==================== Provider 管理 ====================
  providers: {
    list: () => import_electron.ipcRenderer.invoke("providers:list"),
    get: (id) => import_electron.ipcRenderer.invoke("providers:get", id),
    create: (data) => import_electron.ipcRenderer.invoke("providers:create", data),
    update: (id, data) => import_electron.ipcRenderer.invoke("providers:update", id, data),
    delete: (id) => import_electron.ipcRenderer.invoke("providers:delete", id),
    test: (id) => import_electron.ipcRenderer.invoke("providers:test", id)
  },
  // ==================== 项目管理 ====================
  projects: {
    list: () => import_electron.ipcRenderer.invoke("projects:list"),
    get: (id) => import_electron.ipcRenderer.invoke("projects:get", id),
    create: (data) => import_electron.ipcRenderer.invoke("projects:create", data),
    update: (id, data) => import_electron.ipcRenderer.invoke("projects:update", id, data),
    delete: (id) => import_electron.ipcRenderer.invoke("projects:delete", id)
  },
  // ==================== 部门管理 ====================
  departments: {
    list: () => import_electron.ipcRenderer.invoke("departments:list"),
    create: (data) => import_electron.ipcRenderer.invoke("departments:create", data),
    update: (id, data) => import_electron.ipcRenderer.invoke("departments:update", id, data),
    delete: (id) => import_electron.ipcRenderer.invoke("departments:delete", id)
  },
  // ==================== Agent 管理 ====================
  agents: {
    list: () => import_electron.ipcRenderer.invoke("agents:list"),
    get: (id) => import_electron.ipcRenderer.invoke("agents:get", id),
    create: (data) => import_electron.ipcRenderer.invoke("agents:create", data),
    update: (id, data) => import_electron.ipcRenderer.invoke("agents:update", id, data),
    delete: (id) => import_electron.ipcRenderer.invoke("agents:delete", id)
  },
  // ==================== 会议纪要 ====================
  meetingMinutes: {
    list: (projectId) => import_electron.ipcRenderer.invoke("meeting-minutes:list", projectId),
    create: (data) => import_electron.ipcRenderer.invoke("meeting-minutes:create", data),
    update: (id, data) => import_electron.ipcRenderer.invoke("meeting-minutes:update", id, data)
  },
  // ==================== Crew 团队模板 ====================
  crewTemplates: {
    list: () => import_electron.ipcRenderer.invoke("crew-templates:list"),
    create: (data) => import_electron.ipcRenderer.invoke("crew-templates:create", data),
    delete: (id) => import_electron.ipcRenderer.invoke("crew-templates:delete", id)
  },
  // ==================== Skill 管理 ====================
  skills: {
    list: () => import_electron.ipcRenderer.invoke("skills:list"),
    get: (id) => import_electron.ipcRenderer.invoke("skills:get", id),
    byAgent: (agentId) => import_electron.ipcRenderer.invoke("skills:by-agent", agentId),
    byDepartment: (deptId) => import_electron.ipcRenderer.invoke("skills:by-department", deptId),
    create: (data) => import_electron.ipcRenderer.invoke("skills:create", data),
    update: (id, data) => import_electron.ipcRenderer.invoke("skills:update", id, data),
    delete: (id) => import_electron.ipcRenderer.invoke("skills:delete", id)
  },
  // ==================== 系统 ====================
  system: {
    getHomeDirectory: () => import_electron.ipcRenderer.invoke("system:get-home-directory"),
    openExternal: (url) => import_electron.ipcRenderer.invoke("system:open-external", url),
    showItemInFolder: (filePath) => import_electron.ipcRenderer.invoke("system:show-item-in-folder", filePath)
  },
  // ==================== 事件监听 ====================
  on: (channel, callback) => {
    const validChannels = [
      "claude:stream:chunk",
      "open-settings",
      "new-session"
    ];
    if (validChannels.includes(channel)) {
      import_electron.ipcRenderer.on(channel, (_, ...args) => callback(...args));
    }
  },
  off: (channel, callback) => {
    import_electron.ipcRenderer.removeListener(channel, callback);
  }
};
import_electron.contextBridge.exposeInMainWorld("electronAPI", api);
