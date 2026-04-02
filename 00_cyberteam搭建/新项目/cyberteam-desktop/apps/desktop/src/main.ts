import { createMainWindow } from './window.js'
import { setupAppLifecycle } from './app/lifecycle.js'
import { registerIpcHandlers } from './ipc/handlers.js'
import { setupUpdater } from './app/updater.js'
import { closeDesktopRuntime, getDesktopRuntime } from './runtime.js'

console.log('CyberTeam desktop booting')

const runtime = getDesktopRuntime()

setupUpdater()
registerIpcHandlers(runtime)
setupAppLifecycle(async () => {
  await createMainWindow()
})

process.on('beforeExit', () => {
  closeDesktopRuntime()
})

process.on('SIGINT', () => {
  closeDesktopRuntime()
  process.exit(0)
})
