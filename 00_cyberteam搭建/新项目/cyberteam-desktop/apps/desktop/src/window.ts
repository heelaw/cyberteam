import { app, BrowserWindow } from 'electron'
import fs from 'node:fs'
import path from 'node:path'

let mainWindow: BrowserWindow | null = null

function resolveRendererFile() {
  const candidates = [
    path.resolve(process.resourcesPath, 'renderer', 'out', 'index.html'),
    path.resolve(app.getAppPath(), 'dist', 'renderer', 'out', 'index.html'),
    path.resolve(app.getAppPath(), '..', 'renderer', 'out', 'index.html'),
    path.resolve(app.getAppPath(), '..', '..', 'renderer', 'out', 'index.html'),
  ]

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate
    }
  }

  return candidates[0]
}

async function loadRenderer(window: BrowserWindow) {
  if (!app.isPackaged) {
    const devUrl = process.env.CYBERTEAM_RENDERER_URL ?? 'http://localhost:3000'
    try {
      await window.loadURL(devUrl)
      return
    } catch (error) {
      console.warn('[Window] Failed to load dev URL, falling back to file output:', error)
    }
  }

  await window.loadFile(resolveRendererFile())
}

export async function createMainWindow() {
  if (mainWindow) {
    mainWindow.focus()
    return mainWindow
  }

  const window = new BrowserWindow({
    width: 1520,
    height: 960,
    minWidth: 1280,
    minHeight: 780,
    show: false,
    backgroundColor: '#081120',
    title: 'CyberTeam Desktop',
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  })

  mainWindow = window

  window.once('ready-to-show', () => {
    window.show()
  })

  window.on('closed', () => {
    if (mainWindow === window) {
      mainWindow = null
    }
  })

  await loadRenderer(window)
  return window
}
