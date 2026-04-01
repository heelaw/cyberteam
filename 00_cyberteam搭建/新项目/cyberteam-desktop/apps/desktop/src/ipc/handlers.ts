import { app, ipcMain, shell } from 'electron'
import type { DesktopRuntime } from '../runtime.js'

function registerHandler<T extends unknown[]>(
  channel: string,
  handler: (event: Electron.IpcMainInvokeEvent, ...args: T) => unknown,
) {
  ipcMain.removeHandler(channel)
  ipcMain.handle(channel, (event, ...args: T) => handler(event, ...args))
}

export function registerIpcHandlers(runtime: DesktopRuntime) {
  registerHandler('cyberteam:get-state', () => ({
    platform: process.platform,
    version: app.getVersion(),
    isPackaged: app.isPackaged,
    userData: app.getPath('userData'),
    home: app.getPath('home'),
    database: runtime.database.snapshot(),
    claude: {
      installed: runtime.claudeBridge.installed,
      command: runtime.claudeBridge.command,
      status: runtime.claudeBridge.status,
    },
  }))

  registerHandler('app:get-paths', () => ({
    appPath: app.getAppPath(),
    userData: app.getPath('userData'),
    home: app.getPath('home'),
    databasePath: runtime.database.path,
  }))

  registerHandler('claude:detect', () => runtime.claudeBridge.installed)
  registerHandler('claude:ping', () => runtime.claudeBridge.ping())
  registerHandler('claude:send', async (_event, prompt: string) => runtime.claudeBridge.send(prompt))

  registerHandler('chat:send-message', (_event, conversationId: string, message: {
    content: string
    senderId?: string
    mentions?: Array<{ agentId: string; agentName: string; agentTitle?: string }>
  }) => {
    const inserted = runtime.database.addMessage(conversationId, {
      id: `msg_${Date.now()}`,
      senderId: message.senderId,
      senderType: message.senderId ? 'agent' : 'system',
      content: message.content,
      mentions: JSON.stringify(message.mentions ?? []),
      attachments: JSON.stringify([]),
      status: 'sent',
      createdAt: new Date().toISOString(),
    })

    return inserted
  })

  registerHandler('playground:update-review', (_event, documentId: string, patch: { decision?: string; comments?: string }) => {
    return runtime.database.updateReviewRecord(documentId, patch)
  })

  registerHandler('roadmap:upsert-phase', (_event, phase: {
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
  }) => {
    return runtime.database.upsertRoadmapPhase({
      ...phase,
      createdAt: phase.createdAt ?? new Date().toISOString(),
      updatedAt: phase.updatedAt ?? new Date().toISOString(),
    })
  })

  registerHandler('claude:stream', async (event: Electron.IpcMainInvokeEvent, prompt: string) => {
    const response = await runtime.claudeBridge.send(prompt)
    const chunkSize = 24

    for (let index = 0; index < response.length; index += chunkSize) {
      const chunk = response.slice(index, index + chunkSize)
      event.sender.send('claude:stream:chunk', chunk)
      await new Promise((resolve) => setTimeout(resolve, 8))
    }

    return response
  })

  registerHandler('system:get-home-directory', () => app.getPath('home'))
  registerHandler('system:open-external', async (_event, url: string) => shell.openExternal(url))
  registerHandler('system:show-item-in-folder', async (_event, filePath: string) => shell.showItemInFolder(filePath))
}
