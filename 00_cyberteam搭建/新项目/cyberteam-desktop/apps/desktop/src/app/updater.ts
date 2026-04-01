import { app } from 'electron'

export interface UpdateState {
  enabled: boolean
  channel: 'manual'
  appVersion: string
  lastCheckedAt: string
}

export function setupUpdater(): UpdateState {
  const state: UpdateState = {
    enabled: false,
    channel: 'manual',
    appVersion: app.getVersion(),
    lastCheckedAt: new Date().toISOString(),
  }

  console.log('[Updater]', state)
  return state
}
