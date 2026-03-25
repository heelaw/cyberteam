# 会话命令

管理 Claude Code 会话历史记录 - 列出、加载、别名和编辑存储在 `~/.claude/sessions/` 中的会话。

## 用法

`/sessions [列表|加载|别名|信息|帮助] [选项]`

## 行动

### 列出会话

显示带有元数据、过滤和分页的所有会话。

当您需要集群的操作员表面上下文时，请使用“/sessions info”：分支、工作树路径和会话新近度。```bash
/sessions                              # List all sessions (default)
/sessions list                         # Same as above
/sessions list --limit 10              # Show 10 sessions
/sessions list --date 2026-02-01       # Filter by date
/sessions list --search abc            # Search by session ID
```**脚本：**```bash
node -e "
const sm = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-manager');
const aa = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-aliases');
const path = require('path');

const result = sm.getAllSessions({ limit: 20 });
const aliases = aa.listAliases();
const aliasMap = {};
for (const a of aliases) aliasMap[a.sessionPath] = a.name;

console.log('Sessions (showing ' + result.sessions.length + ' of ' + result.total + '):');
console.log('');
console.log('ID        Date        Time     Branch       Worktree           Alias');
console.log('────────────────────────────────────────────────────────────────────');

for (const s of result.sessions) {
  const alias = aliasMap[s.filename] || '';
  const metadata = sm.parseSessionMetadata(sm.getSessionContent(s.sessionPath));
  const id = s.shortId === 'no-id' ? '(none)' : s.shortId.slice(0, 8);
  const time = s.modifiedTime.toTimeString().slice(0, 5);
  const branch = (metadata.branch || '-').slice(0, 12);
  const worktree = metadata.worktree ? path.basename(metadata.worktree).slice(0, 18) : '-';

  console.log(id.padEnd(8) + ' ' + s.date + '  ' + time + '   ' + branch.padEnd(12) + ' ' + worktree.padEnd(18) + ' ' + alias);
}
"
```### Load Session

Load and display a session's content (by ID or alias).```bash
/sessions load <id|alias>             # Load session
/sessions load 2026-02-01             # By date (for no-id sessions)
/sessions load a1b2c3d4               # By short ID
/sessions load my-alias               # By alias name
```**脚本：**```bash
node -e "
const sm = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-manager');
const aa = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-aliases');
const id = process.argv[1];

// First try to resolve as alias
const resolved = aa.resolveAlias(id);
const sessionId = resolved ? resolved.sessionPath : id;

const session = sm.getSessionById(sessionId, true);
if (!session) {
  console.log('Session not found: ' + id);
  process.exit(1);
}

const stats = sm.getSessionStats(session.sessionPath);
const size = sm.getSessionSize(session.sessionPath);
const aliases = aa.getAliasesForSession(session.filename);

console.log('Session: ' + session.filename);
console.log('Path: ~/.claude/sessions/' + session.filename);
console.log('');
console.log('Statistics:');
console.log('  Lines: ' + stats.lineCount);
console.log('  Total items: ' + stats.totalItems);
console.log('  Completed: ' + stats.completedItems);
console.log('  In progress: ' + stats.inProgressItems);
console.log('  Size: ' + size);
console.log('');

if (aliases.length > 0) {
  console.log('Aliases: ' + aliases.map(a => a.name).join(', '));
  console.log('');
}

if (session.metadata.title) {
  console.log('Title: ' + session.metadata.title);
  console.log('');
}

if (session.metadata.started) {
  console.log('Started: ' + session.metadata.started);
}

if (session.metadata.lastUpdated) {
  console.log('Last Updated: ' + session.metadata.lastUpdated);
}

if (session.metadata.project) {
  console.log('Project: ' + session.metadata.project);
}

if (session.metadata.branch) {
  console.log('Branch: ' + session.metadata.branch);
}

if (session.metadata.worktree) {
  console.log('Worktree: ' + session.metadata.worktree);
}
" "$ARGUMENTS"
```### 创建别名

为会话创建一个容易记住的别名。```bash
/sessions alias <id> <name>           # Create alias
/sessions alias 2026-02-01 today-work # Create alias named "today-work"
```**脚本：**```bash
node -e "
const sm = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-manager');
const aa = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-aliases');

const sessionId = process.argv[1];
const aliasName = process.argv[2];

if (!sessionId || !aliasName) {
  console.log('Usage: /sessions alias <id> <name>');
  process.exit(1);
}

// Get session filename
const session = sm.getSessionById(sessionId);
if (!session) {
  console.log('Session not found: ' + sessionId);
  process.exit(1);
}

const result = aa.setAlias(aliasName, session.filename);
if (result.success) {
  console.log('✓ Alias created: ' + aliasName + ' → ' + session.filename);
} else {
  console.log('✗ Error: ' + result.error);
  process.exit(1);
}
" "$ARGUMENTS"
```### 删除别名

删除现有别名。```bash
/sessions alias --remove <name>        # Remove alias
/sessions unalias <name>               # Same as above
```**脚本：**```bash
node -e "
const aa = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-aliases');

const aliasName = process.argv[1];
if (!aliasName) {
  console.log('Usage: /sessions alias --remove <name>');
  process.exit(1);
}

const result = aa.deleteAlias(aliasName);
if (result.success) {
  console.log('✓ Alias removed: ' + aliasName);
} else {
  console.log('✗ Error: ' + result.error);
  process.exit(1);
}
" "$ARGUMENTS"
```### 会议信息

显示有关会话的详细信息。```bash
/sessions info <id|alias>              # Show session details
```**脚本：**```bash
node -e "
const sm = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-manager');
const aa = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-aliases');

const id = process.argv[1];
const resolved = aa.resolveAlias(id);
const sessionId = resolved ? resolved.sessionPath : id;

const session = sm.getSessionById(sessionId, true);
if (!session) {
  console.log('Session not found: ' + id);
  process.exit(1);
}

const stats = sm.getSessionStats(session.sessionPath);
const size = sm.getSessionSize(session.sessionPath);
const aliases = aa.getAliasesForSession(session.filename);

console.log('Session Information');
console.log('════════════════════');
console.log('ID:          ' + (session.shortId === 'no-id' ? '(none)' : session.shortId));
console.log('Filename:    ' + session.filename);
console.log('Date:        ' + session.date);
console.log('Modified:    ' + session.modifiedTime.toISOString().slice(0, 19).replace('T', ' '));
console.log('Project:     ' + (session.metadata.project || '-'));
console.log('Branch:      ' + (session.metadata.branch || '-'));
console.log('Worktree:    ' + (session.metadata.worktree || '-'));
console.log('');
console.log('Content:');
console.log('  Lines:         ' + stats.lineCount);
console.log('  Total items:   ' + stats.totalItems);
console.log('  Completed:     ' + stats.completedItems);
console.log('  In progress:   ' + stats.inProgressItems);
console.log('  Size:          ' + size);
if (aliases.length > 0) {
  console.log('Aliases:     ' + aliases.map(a => a.name).join(', '));
}
" "$ARGUMENTS"
```### 列出别名

显示所有会话别名。```bash
/sessions aliases                      # List all aliases
```**脚本：**```bash
node -e "
const aa = require((()=>{var e=process.env.CLAUDE_PLUGIN_ROOT;if(e&&e.trim())return e.trim();var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(f.existsSync(p.join(d,q)))return d;try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q)))return c}}catch(x){}return d})()+'/scripts/lib/session-aliases');

const aliases = aa.listAliases();
console.log('Session Aliases (' + aliases.length + '):');
console.log('');

if (aliases.length === 0) {
  console.log('No aliases found.');
} else {
  console.log('Name          Session File                    Title');
  console.log('─────────────────────────────────────────────────────────────');
  for (const a of aliases) {
    const name = a.name.padEnd(12);
    const file = (a.sessionPath.length > 30 ? a.sessionPath.slice(0, 27) + '...' : a.sessionPath).padEnd(30);
    const title = a.title || '';
    console.log(name + ' ' + file + ' ' + title);
  }
}
"
```## 操作员注意事项

- 会话文件在标头中保留“Project”、“Branch”和“Worktree”，因此“/sessions info”可以消除并行 tmux/worktree 运行的歧义。
- 对于命令中心式监控，请结合 `/sessions info`、`git diff --stat` 以及 `scripts/hooks/cost-tracker.js` 发出的成本指标。

## 参数

$参数：
- `list [options]` - 列出会话
  - `--limit <n>` - 显示的最大会话数（默认值：50）
  - `--date <YYYY-MM-DD>` - 按日期过滤
  - `--search <pattern>` - 在会话 ID 中搜索
- `load <id|alias>` - 加载会话内容
- `alias <id> <name>` - 为会话创建别名
- `alias --remove <名称>` - 删除别名
- `unalias <name>` - 与 `--remove` 相同
- `info <id|alias>` - 显示会话统计信息
- `aliases` - 列出所有别名
- `help` - 显示此帮助

## 示例```bash
# List all sessions
/sessions list

# Create an alias for today's session
/sessions alias 2026-02-01 today

# Load session by alias
/sessions load today

# Show session info
/sessions info today

# Remove alias
/sessions alias --remove today

# List all aliases
/sessions aliases
```## 注释

- 会话作为 markdown 文件存储在 `~/.claude/sessions/` 中
- 别名存储在`~/.claude/session-aliases.json`中
- 会话 ID 可以缩短（前 4-8 个字符通常足够唯一）
- 对经常引用的会话使用别名