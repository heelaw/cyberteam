# PM2 初始化

自动分析项目并生成PM2服务命令。

**命令**：`$ARGUMENTS`

---

## 工作流程

1.检查PM2（如果缺少，通过`npm install -g pm2`安装）
2. 扫描项目识别服务（前端/后端/数据库）
3. 生成配置文件和单独的命令文件

---

## 服务检测

|类型 |检测|默认端口 |
|------|------------|--------------|
|维特 | vite.config.* | 5173 | 5173
| Next.js |下一个.config.* | 3000 | 3000
|努克斯特 | nuxt.config。* | 3000 | 3000
|加拿大税务局 | package.json 中的反应脚本 | 3000 | 3000
|快递/节点 | server/backend/api 目录 + package.json | 3000 | 3000
| FastAPI/Flask |需求.txt / pyproject.toml | 8000 |
|去 | go.mod / main.go | 8080|

**端口检测优先级**：用户指定 > .env > 配置文件 > 脚本参数 > 默认端口

---

## 生成的文件```
project/
├── ecosystem.config.cjs              # PM2 config
├── {backend}/start.cjs               # Python wrapper (if applicable)
└── .claude/
    ├── commands/
    │   ├── pm2-all.md                # Start all + monit
    │   ├── pm2-all-stop.md           # Stop all
    │   ├── pm2-all-restart.md        # Restart all
    │   ├── pm2-{port}.md             # Start single + logs
    │   ├── pm2-{port}-stop.md        # Stop single
    │   ├── pm2-{port}-restart.md     # Restart single
    │   ├── pm2-logs.md               # View all logs
    │   └── pm2-status.md             # View status
    └── scripts/
        ├── pm2-logs-{port}.ps1       # Single service logs
        └── pm2-monit.ps1             # PM2 monitor
```---

## Windows 配置（重要）

### 生态系统.config.cjs

**必须使用 `.cjs` 扩展名**```javascript
module.exports = {
  apps: [
    // Node.js (Vite/Next/Nuxt)
    {
      name: 'project-3000',
      cwd: './packages/web',
      script: 'node_modules/vite/bin/vite.js',
      args: '--port 3000',
      interpreter: 'C:/Program Files/nodejs/node.exe',
      env: { NODE_ENV: 'development' }
    },
    // Python
    {
      name: 'project-8000',
      cwd: './backend',
      script: 'start.cjs',
      interpreter: 'C:/Program Files/nodejs/node.exe',
      env: { PYTHONUNBUFFERED: '1' }
    }
  ]
}
```**框架脚本路径：**

|框架|脚本|参数|
|------------|--------|------|
|维特 | `node_modules/vite/bin/vite.js` | `--端口 {端口}` |
| Next.js | `node_modules/next/dist/bin/next` | `dev -p {端口}` |
|努克斯特 | `node_modules/nuxt/bin/nuxt.mjs` | `dev --port {端口}` |
|快递| `src/index.js` 或 `server.js` | - |

### Python 包装脚本 (start.cjs)```javascript
const { spawn } = require('child_process');
const proc = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'], {
  cwd: __dirname, stdio: 'inherit', windowsHide: true
});
proc.on('close', (code) => process.exit(code));
```---

## 命令文件模板（最少内容）

### pm2-all.md（全部启动+监控）````markdown
Start all services and open PM2 monitor.
```巴什
cd "{PROJECT_ROOT}" && pm2 start Ecosystem.config.cjs && start wt.exe -d "{PROJECT_ROOT}" pwsh -NoExit -c "pm2 monit"```
````

### pm2-all-stop.md````markdown
Stop all services.
```巴什
cd "{PROJECT_ROOT}" && pm2 停止全部```
````

### pm2-all-restart.md````markdown
Restart all services.
```巴什
cd "{PROJECT_ROOT}" && pm2 全部重启```
````

### pm2-{port}.md (启动单+日志)````markdown
Start {name} ({port}) and open logs.
```巴什
cd "{PROJECT_ROOT}" && pm2 start Ecosystem.config.cjs --only {name} && start wt.exe -d "{PROJECT_ROOT}" pwsh -NoExit -c "pm2 logs {name}"```
````

### pm2-{端口}-stop.md````markdown
Stop {name} ({port}).
```巴什
cd "{PROJECT_ROOT}" && pm2 停止 {name}```
````

### pm2-{端口}-restart.md````markdown
Restart {name} ({port}).
```巴什
cd "{PROJECT_ROOT}" && pm2 重新启动 {name}```
````

### pm2-logs.md````markdown
View all PM2 logs.
```巴什
cd "{PROJECT_ROOT}" && pm2 日志```
````

### pm2-status.md````markdown
View PM2 status.
```巴什
cd "{PROJECT_ROOT}" && pm2 状态```
````

### PowerShell 脚本 (pm2-logs-{port}.ps1)```powershell
Set-Location "{PROJECT_ROOT}"
pm2 logs {name}
```### PowerShell 脚本 (pm2-monit.ps1)```powershell
Set-Location "{PROJECT_ROOT}"
pm2 monit
```---

## 关键规则

1. **配置文件**：`ecosystem.config.cjs`（不是.js）
2. **Node.js**：直接指定bin路径+解释器
3. **Python**：Node.js 包装脚本 + `windowsHide: true`
4. **打开新窗口**：`start wt.exe -d "{path}" pwsh -NoExit -c "command"`
5. **最少内容**：每个命令文件只有1-2行描述+bash块
6. **直接执行**：无需AI解析，直接运行bash命令即可

---

## 执行

基于`$ARGUMENTS`，执行init：

1. 扫描项目以获取服务
2.生成`ecosystem.config.cjs`
3. 为Python服务生成`{backend}/start.cjs`（如果适用）
4. 在`.claude/commands/`中生成命令文件
5. 在`.claude/scripts/`中生成脚本文件
6. **使用 PM2 信息更新项目 CLAUDE.md**（见下文）
7. **使用终端命令显示完成摘要**

---

## 初始化后：更新 CLAUDE.md

生成文件后，将 PM2 部分附加到项目的“CLAUDE.md”（如果不存在则创建）：````markdown
## PM2 Services

| Port | Name | Type |
|------|------|------|
| {port} | {name} | {type} |

**Terminal Commands:**
```巴什
pm2 start Ecosystem.config.cjs # 第一次
pm2 start all # 第一次之后
pm2 全部停止 / pm2 全部重新启动
pm2 开始 {名称} / pm2 停止 {名称}
pm2 日志 / pm2 状态 / pm2 监控
pm2 save #保存进程列表
pm2reviv #恢复保存的列表```
````

**CLAUDE.md 更新规则：**
- 如果PM2部分存在，则更换它
- 如果不存在，则追加到末尾
- 保持内容最少和必要

---

## 初始化后：显示摘要

所有文件生成后，输出：```
## PM2 Init Complete

**Services:**

| Port | Name | Type |
|------|------|------|
| {port} | {name} | {type} |

**Claude Commands:** /pm2-all, /pm2-all-stop, /pm2-{port}, /pm2-{port}-stop, /pm2-logs, /pm2-status

**Terminal Commands:**
## First time (with config file)
pm2 start ecosystem.config.cjs && pm2 save

## After first time (simplified)
pm2 start all          # Start all
pm2 stop all           # Stop all
pm2 restart all        # Restart all
pm2 start {name}       # Start single
pm2 stop {name}        # Stop single
pm2 logs               # View logs
pm2 monit              # Monitor panel
pm2 resurrect          # Restore saved processes

**Tip:** Run `pm2 save` after first start to enable simplified commands.
```