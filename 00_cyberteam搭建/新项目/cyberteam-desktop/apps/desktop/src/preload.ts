import { contextBridge, ipcRenderer } from 'electron'

const api: {
  app: {
    getState: () => Promise<unknown>
    getPaths: () => Promise<unknown>
  }
  chat: {
    sendMessage: (conversationId: string, message: { content: string; senderId?: string; mentions?: Array<{ agentId: string; agentName: string; agentTitle?: string }> }) => Promise<number>
  }
  playground: {
    updateReview: (documentId: string, patch: { decision?: string; comments?: string }) => Promise<number>
  }
  roadmap: {
    upsertPhase: (phase: {
      id: string
      companyId: string
      name: string
      status: 'done' | 'in-progress' | 'next' | 'planned'
      goal: string
      proof: string
      question: string
      sortOrder?: number
      createdAt?: string
      updatedAt?: string
    }) => Promise<number>
  }
  claude: {
    detect: () => Promise<boolean>
    ping: () => Promise<unknown>
    send: (prompt: string) => Promise<string>
    stream: (prompt: string, onChunk: (chunk: string) => void) => Promise<string>
  }
  system: {
    getHomeDirectory: () => Promise<string>
    openExternal: (url: string) => Promise<unknown>
    showItemInFolder: (filePath: string) => Promise<unknown>
  }
} = {
  app: {
    getState: () => ipcRenderer.invoke('cyberteam:get-state'),
    getPaths: () => ipcRenderer.invoke('app:get-paths'),
  },
  chat: {
    sendMessage: (conversationId: string, message: { content: string; senderId?: string; mentions?: Array<{ agentId: string; agentName: string; agentTitle?: string }> }) =>
      ipcRenderer.invoke('chat:send-message', conversationId, message),
  },
  playground: {
    updateReview: (documentId: string, patch: { decision?: string; comments?: string }) =>
      ipcRenderer.invoke('playground:update-review', documentId, patch),
  },
  roadmap: {
    upsertPhase: (phase: {
      id: string
      companyId: string
      name: string
      status: 'done' | 'in-progress' | 'next' | 'planned'
      goal: string
      proof: string
      question: string
      sortOrder?: number
      createdAt?: string
      updatedAt?: string
    }) => ipcRenderer.invoke('roadmap:upsert-phase', phase),
  },
  claude: {
    detect: () => ipcRenderer.invoke('claude:detect'),
    ping: () => ipcRenderer.invoke('claude:ping'),
    send: (prompt: string) => ipcRenderer.invoke('claude:send', prompt),
    stream: (prompt: string, onChunk: (chunk: string) => void) => {
      const listener = (_event: Electron.IpcRendererEvent, chunk: string) => {
        onChunk(chunk)
      }

      ipcRenderer.on('claude:stream:chunk', listener)

      return ipcRenderer.invoke('claude:stream', prompt).finally(() => {
        ipcRenderer.removeListener('claude:stream:chunk', listener)
      })
    },
  },
  system: {
    getHomeDirectory: () => ipcRenderer.invoke('system:get-home-directory'),
    openExternal: (url: string) => ipcRenderer.invoke('system:open-external', url),
    showItemInFolder: (filePath: string) => ipcRenderer.invoke('system:show-item-in-folder', filePath),
  },
}

contextBridge.exposeInMainWorld('cyberteam', api)
contextBridge.exposeInMainWorld('electronAPI', api)
