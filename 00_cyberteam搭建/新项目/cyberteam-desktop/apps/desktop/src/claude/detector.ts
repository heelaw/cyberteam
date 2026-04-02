import { spawnSync } from 'node:child_process'

const CLAUDE_COMMANDS = ['claude', 'claude-code']

function isExecutableAvailable(command: string) {
  const result = spawnSync('which', [command], { encoding: 'utf8' })
  return result.status === 0 && Boolean(result.stdout.trim())
}

export function detectClaudeCodeCommand() {
  for (const command of CLAUDE_COMMANDS) {
    if (isExecutableAvailable(command)) {
      return command
    }
  }

  return null
}

export function isClaudeCodeInstalled() {
  return detectClaudeCodeCommand() !== null
}
