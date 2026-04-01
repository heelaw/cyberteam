// electron/preload.ts
import { contextBridge, ipcRenderer } from "electron";
var api = {
  // ==================== 对话会话 ====================
  chat: {
    sessions: {
      list: () => ipcRenderer.invoke("chat:sessions:list"),
      get: (id) => ipcRenderer.invoke("chat:sessions:get", id),
      create: (data) => ipcRenderer.invoke("chat:sessions:create", data),
      update: (id, data) => ipcRenderer.invoke("chat:sessions:update", id, data),
      delete: (id) => ipcRenderer.invoke("chat:sessions:delete", id)
    },
    messages: {
      list: (sessionId) => ipcRenderer.invoke("chat:messages:list", sessionId),
      create: (data) => ipcRenderer.invoke("chat:messages:create", data)
    }
  },
  // ==================== Claude Code CLI ====================
  claude: {
    send: (data) => ipcRenderer.invoke("claude:send", data),
    stream: (data, onChunk) => {
      const listener = (_, data2) => {
        onChunk(data2);
      };
      ipcRenderer.on("claude:stream:chunk", listener);
      return ipcRenderer.invoke("claude:stream", data).finally(() => {
        ipcRenderer.removeListener("claude:stream:chunk", listener);
      });
    }
  },
  // ==================== 文件浏览 ====================
  files: {
    browse: (dirPath) => ipcRenderer.invoke("files:browse", dirPath),
    validateDirectory: (dirPath) => ipcRenderer.invoke("files:validate-directory", dirPath),
    selectDirectory: () => ipcRenderer.invoke("files:select-directory")
  },
  // ==================== Provider 管理 ====================
  providers: {
    list: () => ipcRenderer.invoke("providers:list"),
    get: (id) => ipcRenderer.invoke("providers:get", id),
    create: (data) => ipcRenderer.invoke("providers:create", data),
    update: (id, data) => ipcRenderer.invoke("providers:update", id, data),
    delete: (id) => ipcRenderer.invoke("providers:delete", id),
    test: (id) => ipcRenderer.invoke("providers:test", id)
  },
  // ==================== 项目管理 ====================
  projects: {
    list: () => ipcRenderer.invoke("projects:list"),
    get: (id) => ipcRenderer.invoke("projects:get", id),
    create: (data) => ipcRenderer.invoke("projects:create", data),
    update: (id, data) => ipcRenderer.invoke("projects:update", id, data),
    delete: (id) => ipcRenderer.invoke("projects:delete", id)
  },
  // ==================== 部门管理 ====================
  departments: {
    list: () => ipcRenderer.invoke("departments:list"),
    create: (data) => ipcRenderer.invoke("departments:create", data),
    update: (id, data) => ipcRenderer.invoke("departments:update", id, data),
    delete: (id) => ipcRenderer.invoke("departments:delete", id)
  },
  // ==================== Agent 管理 ====================
  agents: {
    list: () => ipcRenderer.invoke("agents:list"),
    get: (id) => ipcRenderer.invoke("agents:get", id),
    create: (data) => ipcRenderer.invoke("agents:create", data),
    update: (id, data) => ipcRenderer.invoke("agents:update", id, data),
    delete: (id) => ipcRenderer.invoke("agents:delete", id)
  },
  // ==================== 会议纪要 ====================
  meetingMinutes: {
    list: (projectId) => ipcRenderer.invoke("meeting-minutes:list", projectId),
    create: (data) => ipcRenderer.invoke("meeting-minutes:create", data),
    update: (id, data) => ipcRenderer.invoke("meeting-minutes:update", id, data)
  },
  // ==================== Crew 团队模板 ====================
  crewTemplates: {
    list: () => ipcRenderer.invoke("crew-templates:list"),
    create: (data) => ipcRenderer.invoke("crew-templates:create", data),
    delete: (id) => ipcRenderer.invoke("crew-templates:delete", id)
  },
  // ==================== 系统 ====================
  system: {
    getHomeDirectory: () => ipcRenderer.invoke("system:get-home-directory"),
    openExternal: (url) => ipcRenderer.invoke("system:open-external", url),
    showItemInFolder: (filePath) => ipcRenderer.invoke("system:show-item-in-folder", filePath)
  },
  // ==================== 事件监听 ====================
  on: (channel, callback) => {
    const validChannels = [
      "claude:stream:chunk",
      "open-settings",
      "new-session"
    ];
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (_, ...args) => callback(...args));
    }
  },
  off: (channel, callback) => {
    ipcRenderer.removeListener(channel, callback);
  }
};
contextBridge.exposeInMainWorld("electronAPI", api);
