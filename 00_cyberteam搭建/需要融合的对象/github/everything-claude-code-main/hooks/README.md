# 钩子

挂钩是事件驱动的自动化，在 Claude Code 工具执行之前或之后触发。他们加强代码质量，及早发现错误，并自动执行重复检查。

## 钩子如何工作```
User request → Claude picks a tool → PreToolUse hook runs → Tool executes → PostToolUse hook runs
```- **PreToolUse** 挂钩在工具执行之前运行。它们可以 **阻止**（退出代码 2）或 **警告**（不阻塞的 stderr）。
- **PostToolUse** 挂钩在工具完成后运行。他们可以分析输出但不能阻止。
- 每次 Claude 响应后都会运行 **Stop** 挂钩。
- **SessionStart/SessionEnd** 挂钩在会话生命周期边界运行。
- **PreCompact** 挂钩在上下文压缩之前运行，对于保存状态很有用。

## 这个插件中的钩子

### PreToolUse 挂钩

|钩|匹配器|行为 |退出代码 |
|------|---------|----------|------------|
| **开发服务器拦截器** | `重击` |在 tmux 之外阻止 `npm run dev` 等 — 确保日志访问 | 2（块）|
| **Tmux 提醒** | `重击` |建议使用 tmux 来执行长时间运行的命令（npm test、cargo build、docker） | 0（警告）|
| **Git 推送提醒** | `重击` |提醒在 `git push` 之前检查更改 | 0（警告）|
| **文档文件警告** | `写` |警告非标准 `.md`/`.txt` 文件（允许 README、CLAUDE、CONTRIBUTING、CHANGELOG、LICENSE、SKILL、docs/、skills/）；跨平台路径处理| 0（警告）|
| **战略契约** | `编辑\|写入` |建议按逻辑间隔手动执行“/compact”（每约 50 个工具调用）| 0（警告）|
| **安装安全监视器（选择加入）** | `Bash\|写入\|编辑\|MultiEdit` |针对高信号工具输入的可选安全扫描。除非“ECC_ENABLE_INSAITS=1”，否则禁用。阻止关键发现，对非关键发现发出警告，并将审核日志写入“.insaits_audit_session.jsonl”。需要“pip install insa-its”。 [详细信息](../scripts/hooks/insaits-security-monitor.py) | 2（阻止关键）/0（警告）|

### PostToolUse 挂钩

|钩|匹配器|它有什么作用 |
|------|---------|-------------|
| **公关记录器** | `重击` |在 `gh pr create` 之后记录 PR URL 并查看命令 |
| **构建分析** | `重击` |构建命令后的后台分析（异步、非阻塞） |
| **质量门** | `编辑\|写入\|多重编辑` |编辑后运行快速质量检查 |
| **更漂亮的格式** | `编辑` |编辑后使用 Prettier 自动格式化 JS/TS 文件 |
| **TypeScript 检查** | `编辑` |编辑 `.ts`/`.tsx` 文件后运行 `tsc --noEmit` |
| **console.log 警告** | `编辑` |警告编辑文件中的“console.log”语句 |

### 生命周期挂钩

|钩|活动 |它有什么作用 |
|------|--------|-------------|
| **会议开始** | `会话开始` |加载以前的上下文并检测包管理器 |
| **预压缩** | `预压缩` |在上下文压缩之前保存状态 |
| **控制台.log审计** | `停止` |每次响应后检查所有修改的文件中的“console.log” |
| **会议总结** | `停止` |当转录路径可用时保留会话状态 |
| **模式提取** | `停止` |评估可提取模式的会话（持续学习）|
| **成本跟踪** | `停止` |发出轻量级运行成本遥测标记
| **会话结束标记** | `会话结束` |生命周期标记和清理日志 |

## 自定义钩子

### 禁用钩子

删除或注释掉 `hooks.json` 中的钩子条目。如果作为插件安装，请在`~/.claude/settings.json`中覆盖：```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [],
        "description": "Override: allow all .md file creation"
      }
    ]
  }
}
```### 运行时挂钩控件（推荐）

使用环境变量来控制钩子行为，无需编辑 `hooks.json`：```bash
# minimal | standard | strict (default: standard)
export ECC_HOOK_PROFILE=standard

# Disable specific hook IDs (comma-separated)
export ECC_DISABLED_HOOKS="pre:bash:tmux-reminder,post:edit:typecheck"
```简介：
- “最小”——仅保留必要的生命周期和安全挂钩。
- `标准` — 默认；平衡的质量+安全检查。
- `strict` — 启用额外的提醒和更严格的护栏。

### 编写你自己的 Hook

Hook 是 shell 命令，它在 stdin 上接收 JSON 形式的工具输入，并且必须在 stdout 上输出 JSON。

**基本结构：**```javascript
// my-hook.js
let data = '';
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  const input = JSON.parse(data);

  // Access tool info
  const toolName = input.tool_name;        // "Edit", "Bash", "Write", etc.
  const toolInput = input.tool_input;      // Tool-specific parameters
  const toolOutput = input.tool_output;    // Only available in PostToolUse

  // Warn (non-blocking): write to stderr
  console.error('[Hook] Warning message shown to Claude');

  // Block (PreToolUse only): exit with code 2
  // process.exit(2);

  // Always output the original data to stdout
  console.log(data);
});
```**退出代码：**
- `0` — 成功（继续执行）
- `2` — 阻止工具调用（仅限 PreToolUse）
- 其他非零 — 错误（已记录但不阻塞）

### 挂钩输入架构```typescript
interface HookInput {
  tool_name: string;          // "Bash", "Edit", "Write", "Read", etc.
  tool_input: {
    command?: string;         // Bash: the command being run
    file_path?: string;       // Edit/Write/Read: target file
    old_string?: string;      // Edit: text being replaced
    new_string?: string;      // Edit: replacement text
    content?: string;         // Write: file content
  };
  tool_output?: {             // PostToolUse only
    output?: string;          // Command/tool output
  };
}
```### 异步钩子

对于不应阻塞主流程的钩子（例如，后台分析）：```json
{
  "type": "command",
  "command": "node my-slow-hook.js",
  "async": true,
  "timeout": 30
}
```异步挂钩在后台运行。它们无法阻止工具执行。

## 常见的钩子食谱

### 警告 TODO 评论```json
{
  "matcher": "Edit",
  "hooks": [{
    "type": "command",
    "command": "node -e \"let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const i=JSON.parse(d);const ns=i.tool_input?.new_string||'';if(/TODO|FIXME|HACK/.test(ns)){console.error('[Hook] New TODO/FIXME added - consider creating an issue')}console.log(d)})\""
  }],
  "description": "Warn when adding TODO/FIXME comments"
}
```### 阻止大文件创建```json
{
  "matcher": "Write",
  "hooks": [{
    "type": "command",
    "command": "node -e \"let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const i=JSON.parse(d);const c=i.tool_input?.content||'';const lines=c.split('\\n').length;if(lines>800){console.error('[Hook] BLOCKED: File exceeds 800 lines ('+lines+' lines)');console.error('[Hook] Split into smaller, focused modules');process.exit(2)}console.log(d)})\""
  }],
  "description": "Block creation of files larger than 800 lines"
}
```### 使用 ruff 自动格式化 Python 文件```json
{
  "matcher": "Edit",
  "hooks": [{
    "type": "command",
    "command": "node -e \"let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const i=JSON.parse(d);const p=i.tool_input?.file_path||'';if(/\\.py$/.test(p)){const{execFileSync}=require('child_process');try{execFileSync('ruff',['format',p],{stdio:'pipe'})}catch(e){}}console.log(d)})\""
  }],
  "description": "Auto-format Python files with ruff after edits"
}
```### 需要测试文件和新源文件```json
{
  "matcher": "Write",
  "hooks": [{
    "type": "command",
    "command": "node -e \"const fs=require('fs');let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const i=JSON.parse(d);const p=i.tool_input?.file_path||'';if(/src\\/.*\\.(ts|js)$/.test(p)&&!/\\.test\\.|\\.spec\\./.test(p)){const testPath=p.replace(/\\.(ts|js)$/,'.test.$1');if(!fs.existsSync(testPath)){console.error('[Hook] No test file found for: '+p);console.error('[Hook] Expected: '+testPath);console.error('[Hook] Consider writing tests first (/tdd)')}}console.log(d)})\""
  }],
  "description": "Remind to create tests when adding new source files"
}
```## 跨平台笔记

挂钩逻辑在 Node.js 脚本中实现，以实现 Windows、macOS 和 Linux 上的跨平台行为。保留少量外壳包装器用于持续学习的观察者钩子；这些包装器是配置文件门控的，并且具有 Windows 安全的后备行为。

## 相关

- [rules/common/hooks.md](../rules/common/hooks.md) — Hook 架构指南
- [skills/strategic-compact/](../skills/strategic-compact/) — 战略压缩技能
- [scripts/hooks/](../scripts/hooks/) — Hook 脚本实现