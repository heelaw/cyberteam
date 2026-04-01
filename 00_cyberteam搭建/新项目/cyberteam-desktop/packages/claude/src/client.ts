import { detectClaudeCodeCommand, isClaudeCodeInstalled } from './detector'

export function detectClaudeCode(): boolean {
  return isClaudeCodeInstalled()
}

export function createClaudeClient() {
  const command = detectClaudeCodeCommand()

  return {
    command,
    installed: Boolean(command),
    send(message: string) {
      if (!command) {
        return `Claude Code not detected locally. Message: ${message}`
      }

      return `Claude Code bridge ready via ${command}. Message: ${message}`
    },
  }
}
