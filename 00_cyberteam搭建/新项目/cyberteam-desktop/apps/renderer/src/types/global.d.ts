import type { CyberTeamApi } from '../lib/runtime-api'

declare global {
  interface Window {
    cyberteam?: CyberTeamApi
    electronAPI?: CyberTeamApi
  }
}

export {}
