import { app, BrowserWindow } from 'electron'

export function setupAppLifecycle(onReady: () => Promise<void> | void) {
  app.setName('CyberTeam Desktop')

  app.whenReady().then(async () => {
    await onReady()
  })

  app.on('activate', async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await onReady()
    }
  })

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit()
    }
  })
}
