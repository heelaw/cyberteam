var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// electron/claude-client.ts
var claude_client_exports = {};
__export(claude_client_exports, {
  ClaudeClient: () => ClaudeClient
});
module.exports = __toCommonJS(claude_client_exports);
var import_child_process = require("child_process");
var import_path = __toESM(require("path"), 1);
var import_fs = __toESM(require("fs"), 1);
var import_os = __toESM(require("os"), 1);
var ClaudeClient = class {
  sessionProcess = null;
  sessionId = "";
  buffer = "";
  pendingRequests = /* @__PURE__ */ new Map();
  constructor() {
  }
  /**
   * Claude Code CLI 使用 --output-format stream-json
   * 输出格式：每行一个 JSON 对象
   * {"type":"version","version":1}
   * {"type":"assistant","text":"..."}
   * {"type":"result","result":{"type":"success","...","text":"..."}}
   * {"type":"error","error":{"type":"...","message":"..."}}
   */
  async sendMessageStream(message, options = {}, onChunk) {
    const { cwd = import_os.default.homedir(), sessionId: optSessionId, systemPrompt } = options;
    return new Promise(async (resolve, reject) => {
      try {
        const { process: proc, sessionId: newSessionId } = await this.spawnClaudeProcess(cwd, systemPrompt);
        this.sessionProcess = proc;
        this.sessionId = newSessionId;
        const requestId = `req_${Date.now()}`;
        let fullContent = "";
        this.pendingRequests.set(requestId, {
          resolve: (content) => resolve(content),
          reject,
          onChunk
        });
        proc.stdout.on("data", (data) => {
          this.buffer += data.toString();
          const lines = this.buffer.split("\n");
          this.buffer = lines.pop() || "";
          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const event = JSON.parse(line);
              this.handleStreamEvent(event, requestId, (text) => {
                fullContent += text;
                onChunk?.(text);
              });
            } catch {
              console.log("[ClaudeClient raw]", line);
            }
          }
        });
        proc.stderr.on("data", (data) => {
          console.log("[ClaudeClient stderr]", data.toString().trim());
        });
        proc.on("close", (code) => {
          console.log("[ClaudeClient closed]", code);
          if (code !== 0 && code !== null) {
            const pending = this.pendingRequests.get(requestId);
            if (pending) {
              pending.reject(new Error(`Claude CLI exited with code ${code}`));
              this.pendingRequests.delete(requestId);
            }
          }
        });
        proc.on("error", (err) => {
          console.error("[ClaudeClient error]", err);
          const pending = this.pendingRequests.get(requestId);
          if (pending) {
            pending.reject(err);
            this.pendingRequests.delete(requestId);
          }
        });
        setTimeout(() => {
          if (this.sessionProcess) {
            this.sessionProcess.stdin.write(message + "\n");
          }
        }, 2e3);
        setTimeout(() => {
          if (this.pendingRequests.has(requestId)) {
            this.pendingRequests.delete(requestId);
            this.close();
            reject(new Error("Claude request timeout (5 minutes)"));
          }
        }, 3e5);
      } catch (err) {
        reject(err);
      }
    });
  }
  async spawnClaudeProcess(cwd, systemPrompt) {
    const claudePath = this.findClaudeCLI();
    if (!claudePath) {
      throw new Error(
        "Claude Code CLI not found. Please install it:\n  npm install -g @anthropic-ai/claude-code\n  or: curl -sL https://claude.ai | sh"
      );
    }
    const sessionId = `ct_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const env = {
      ...process.env,
      CLAUDE_SESSION_ID: sessionId
    };
    if (systemPrompt) {
      env.CLAUDE_SYSTEM_PROMPT = systemPrompt;
    }
    const args = [
      "--dangerously-skip-permissions",
      "--output-format",
      "stream-json",
      "--print"
    ];
    const proc = (0, import_child_process.spawn)(claudePath, args, {
      cwd,
      env,
      stdio: ["pipe", "pipe", "pipe"]
    });
    return { process: proc, sessionId };
  }
  handleStreamEvent(event, requestId, onText) {
    const pending = this.pendingRequests.get(requestId);
    if (!pending) return;
    switch (event.type) {
      case "version":
        break;
      case "assistant":
        if (event.text) {
          onText(event.text);
        }
        break;
      case "result": {
        let content = "";
        const result = event.result;
        if (result && typeof result === "object") {
          if ("text" in result && typeof result.text === "string") {
            content = result.text;
          } else {
            content = JSON.stringify(result);
          }
        }
        pending.resolve(content);
        this.pendingRequests.delete(requestId);
        break;
      }
      case "error": {
        const errorMsg = typeof event.error === "string" ? event.error : event.error?.message || "Unknown error";
        pending.reject(new Error(errorMsg));
        this.pendingRequests.delete(requestId);
        break;
      }
      case "ping":
      case "ready":
        break;
      default:
        break;
    }
  }
  findClaudeCLI() {
    const possiblePaths = [
      "/opt/homebrew/bin/claude",
      "/usr/local/bin/claude",
      import_path.default.join(import_os.default.homedir(), ".local/bin/claude"),
      import_path.default.join(import_os.default.homedir(), ".claude", "bin", "claude"),
      "claude"
      // PATH 中
    ];
    for (const p of possiblePaths) {
      try {
        if (p === "claude") {
          const which = (0, import_child_process.spawn)("which", ["claude"], { shell: true });
          const output = which.stdout.read() || "";
          const status = which.exitCode;
          if (status === 0 && output.toString().trim()) {
            return output.toString().trim();
          }
        } else if (import_fs.default.existsSync(p)) {
          return p;
        }
      } catch {
      }
    }
    return null;
  }
  close() {
    if (this.sessionProcess) {
      try {
        this.sessionProcess.stdin.write("");
        this.sessionProcess.kill("SIGTERM");
      } catch {
      }
      this.sessionProcess = null;
    }
    this.pendingRequests.clear();
    this.buffer = "";
  }
};
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ClaudeClient
});
