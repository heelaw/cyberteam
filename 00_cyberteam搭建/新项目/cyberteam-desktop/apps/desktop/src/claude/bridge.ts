import { detectClaudeCodeCommand, isClaudeCodeInstalled } from './detector.js'

export interface ClaudeBridge {
  installed: boolean
  command: string | null
  status: 'detected' | 'missing'
  ping(): string
  send(prompt: string): Promise<string>
}

export function connectClaudeBridge(): ClaudeBridge {
  const command = detectClaudeCodeCommand()
  const installed = isClaudeCodeInstalled()

  return {
    installed,
    command,
    status: installed ? 'detected' : 'missing',
    ping() {
      return installed ? `Claude Code detected: ${command ?? 'unknown'}` : 'Claude Code not detected'
    },
    async send(prompt: string) {
      if (!installed) {
        return `Claude Code not detected locally. Bridge stub received: ${prompt}`
      }

      return `Claude Code bridge connected via ${command ?? 'unknown command'}. Prompt received: ${prompt}`
    },
  }
}
