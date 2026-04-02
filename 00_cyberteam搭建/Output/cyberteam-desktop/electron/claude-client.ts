import { spawn, ChildProcessWithoutNullStreams } from "child_process"
import path from "path"
import fs from "fs"
import os from "os"

interface ClaudeClientOptions {
  cwd?: string
  providerId?: string
  model?: string
  systemPrompt?: string
  sessionId?: string
}

interface StreamChunk {
  type: string
  text?: string
  content?: string
  result?: unknown
  error?: string
  version?: number
  requestId?: string
}

export class ClaudeClient {
  private sessionProcess: ChildProcessWithoutNullStreams | null = null
  private sessionId: string = ""
  private buffer: string = ""
  private pendingRequests: Map<string, {
    resolve: (value: string) => void
    reject: (error: Error) => void
    onChunk?: (chunk: string) => void
  }> = new Map()

  constructor() {}

  /**
   * Claude Code CLI 使用 --output-format stream-json
   * 输出格式：每行一个 JSON 对象
   * {"type":"version","version":1}
   * {"type":"assistant","text":"..."}
   * {"type":"result","result":{"type":"success","...","text":"..."}}
   * {"type":"error","error":{"type":"...","message":"..."}}
   */
  async sendMessageStream(
    message: string,
    options: ClaudeClientOptions = {},
    onChunk?: (chunk: string) => void
  ): Promise<string> {
    const { cwd = os.homedir(), sessionId: optSessionId, systemPrompt } = options

    return new Promise(async (resolve, reject) => {
      try {
        // 每次都启动新进程（Claude Code 不支持持久化会话）
        const { process: proc, sessionId: newSessionId } = await this.spawnClaudeProcess(cwd, systemPrompt)

        this.sessionProcess = proc
        this.sessionId = newSessionId

        const requestId = `req_${Date.now()}`
        let fullContent = ""

        this.pendingRequests.set(requestId, {
          resolve: (content) => resolve(content),
          reject,
          onChunk,
        })

        // 监听 stdout
        proc.stdout.on("data", (data: Buffer) => {
          this.buffer += data.toString()
          const lines = this.buffer.split("\n")
          this.buffer = lines.pop() || ""

          for (const line of lines) {
            if (!line.trim()) continue
            try {
              const event: StreamChunk = JSON.parse(line)
              this.handleStreamEvent(event, requestId, (text) => {
                fullContent += text
                onChunk?.(text)
              })
            } catch {
              // 非 JSON 行，可能是普通文本输出
              console.log("[ClaudeClient raw]", line)
            }
          }
        })

        // 监听 stderr
        proc.stderr.on("data", (data: Buffer) => {
          console.log("[ClaudeClient stderr]", data.toString().trim())
        })

        // 监听进程退出
        proc.on("close", (code) => {
          console.log("[ClaudeClient closed]", code)
          if (code !== 0 && code !== null) {
            const pending = this.pendingRequests.get(requestId)
            if (pending) {
              pending.reject(new Error(`Claude CLI exited with code ${code}`))
              this.pendingRequests.delete(requestId)
            }
          }
        })

        proc.on("error", (err) => {
          console.error("[ClaudeClient error]", err)
          const pending = this.pendingRequests.get(requestId)
          if (pending) {
            pending.reject(err)
            this.pendingRequests.delete(requestId)
          }
        })

        // 发送消息（通过 stdin）
        setTimeout(() => {
          if (this.sessionProcess) {
            this.sessionProcess.stdin.write(message + "\n")
          }
        }, 2000) // 等待 CLI 初始化

        // 超时处理（5 分钟）
        setTimeout(() => {
          if (this.pendingRequests.has(requestId)) {
            this.pendingRequests.delete(requestId)
            this.close()
            reject(new Error("Claude request timeout (5 minutes)"))
          }
        }, 300000)

      } catch (err) {
        reject(err)
      }
    })
  }

  private async spawnClaudeProcess(
    cwd: string,
    systemPrompt?: string
  ): Promise<{ process: ChildProcessWithoutNullStreams; sessionId: string }> {
    const claudePath = this.findClaudeCLI()
    if (!claudePath) {
      throw new Error(
        "Claude Code CLI not found. Please install it:\n" +
        "  npm install -g @anthropic-ai/claude-code\n" +
        "  or: curl -sL https://claude.ai | sh"
      )
    }

    const sessionId = `ct_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    // 构建环境变量
    const env: NodeJS.ProcessEnv = {
      ...process.env,
      CLAUDE_SESSION_ID: sessionId,
    }

    if (systemPrompt) {
      env.CLAUDE_SYSTEM_PROMPT = systemPrompt
    }

    // Claude Code CLI 参数
    // --dangerously-skip-permissions: 跳过权限确认
    // --output-format stream-json: 流式 JSON 输出
    // --print: 打印最终结果到 stdout
    const args = [
      "--dangerously-skip-permissions",
      "--output-format", "stream-json",
      "--print",
    ]

    const proc = spawn(claudePath, args, {
      cwd,
      env,
      stdio: ["pipe", "pipe", "pipe"],
    })

    return { process: proc, sessionId }
  }

  private handleStreamEvent(
    event: StreamChunk,
    requestId: string,
    onText: (text: string) => void
  ): void {
    const pending = this.pendingRequests.get(requestId)
    if (!pending) return

    switch (event.type) {
      case "version":
        // ignore
        break

      case "assistant":
        if (event.text) {
          onText(event.text)
        }
        break

      case "result": {
        // 最终结果
        let content = ""
        const result = event.result as Record<string, unknown>
        if (result && typeof result === "object") {
          // 尝试从 result 中提取文本
          if ("text" in result && typeof (result as {text?:string}).text === "string") {
            content = (result as {text:string}).text
          } else {
            content = JSON.stringify(result)
          }
        }
        pending.resolve(content)
        this.pendingRequests.delete(requestId)
        break
      }

      case "error": {
        const errorMsg = typeof event.error === "string"
          ? event.error
          : (event.error as Record<string, unknown>)?.message || "Unknown error"
        pending.reject(new Error(errorMsg))
        this.pendingRequests.delete(requestId)
        break
      }

      case "ping":
      case "ready":
        // ignore
        break

      default:
        // 未知事件类型，忽略
        break
    }
  }

  private findClaudeCLI(): string | null {
    const possiblePaths = [
      "/opt/homebrew/bin/claude",
      "/usr/local/bin/claude",
      path.join(os.homedir(), ".local/bin/claude"),
      path.join(os.homedir(), ".claude", "bin", "claude"),
      "claude", // PATH 中
    ]

    for (const p of possiblePaths) {
      try {
        if (p === "claude") {
          const which = spawn("which", ["claude"], { shell: true })
          const output = which.stdout.read() || ""
          const status = which.exitCode
          if (status === 0 && output.toString().trim()) {
            return output.toString().trim()
          }
        } else if (fs.existsSync(p)) {
          return p
        }
      } catch {
        // 忽略错误，继续检查下一个路径
      }
    }

    return null
  }

  close(): void {
    if (this.sessionProcess) {
      try {
        this.sessionProcess.stdin.write("\x03") // Ctrl+C
        this.sessionProcess.kill("SIGTERM")
      } catch {
        // 忽略关闭错误
      }
      this.sessionProcess = null
    }
    this.pendingRequests.clear()
    this.buffer = ""
  }
}
