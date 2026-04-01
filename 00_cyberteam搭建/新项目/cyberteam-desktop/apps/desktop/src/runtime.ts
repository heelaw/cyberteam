import { app } from 'electron'
import path from 'node:path'
import { connectClaudeBridge, type ClaudeBridge } from './claude/bridge.js'
import { createSeedState, type SeedState } from '@cyberteam/core'
import { createCyberTeamDatabase, type CyberTeamDatabase } from '@cyberteam/db'

export interface DesktopRuntime {
  seedState: SeedState
  database: CyberTeamDatabase
  claudeBridge: ClaudeBridge
}

let runtime: DesktopRuntime | null = null

function resolveDatabasePath() {
  return path.resolve(app.getPath('userData'), 'cyberteam.sqlite')
}

export function getDesktopRuntime() {
  if (runtime) {
    return runtime
  }

  const seedState = createSeedState()
  const database = createCyberTeamDatabase(resolveDatabasePath(), seedState)
  const claudeBridge = connectClaudeBridge()

  runtime = {
    seedState,
    database,
    claudeBridge,
  }

  return runtime
}

export function closeDesktopRuntime() {
  if (!runtime) {
    return
  }

  runtime.database.close()
  runtime = null
}
