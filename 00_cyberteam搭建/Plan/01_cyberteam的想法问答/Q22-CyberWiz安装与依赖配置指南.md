# Q22: CyberWiz Agent 安装与依赖配置指南

**问题**: 在新的 Claude Code 里安装 CyberWiz Agent 需要哪些依赖和配套工具？

---

## 一、安装架构概览

### 1.1 核心组件

```
CyberWiz Agent 系统
│
├── 基础层 (必须)
│   ├── Claude Code CLI
│   ├── Python 3.10+
│   └── Git
│
├── 核心层 (必须)
│   ├── thinking-team/         # 思考天团主系统
│   ├── config/               # 配置文件
│   └── skills/               # Skill集合
│
├── 增强层 (可选)
│   ├── web-board/           # Web看板
│   ├── pua-system/          # PUA监督
│   └── knowledge-base/       # 知识库
│
└── 工具层 (可选)
    ├── tmux                  # 多会话管理
    └── watchdog              # 文件监控
```

---

## 二、环境要求

### 2.1 基础环境

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| **macOS / Linux** | 12.0+ | 操作系统 |
| **Claude Code** | 最新版 | AI Agent核心 |
| **Python** | 3.10+ | 运行时环境 |
| **Git** | 2.0+ | 版本控制 |
| **Node.js** | 18+ | Web看板(可选) |

### 2.2 检查命令

```bash
# 检查基础环境
claude --version              # Claude Code
python3 --version             # Python
git --version                 # Git
node --version                # Node.js (可选)
tmux -V                       # tmux (可选)
```

---

## 三、快速安装

### 3.1 一键安装脚本

```bash
#!/bin/bash
# install_cyberwiz.sh

set -e

echo "🚀 开始安装 CyberWiz Agent..."

# 1. 检查基础依赖
echo "📋 检查基础依赖..."
command -v claude >/dev/null 2>&1 || { echo "❌ 需要安装 Claude Code"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ 需要安装 Python 3.10+"; exit 1; }

# 2. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p ~/cyberwiz/{config,skills,workspace,knowledge,logs}

# 3. 克隆或创建项目
echo "📦 初始化项目..."
cd ~/cyberwiz

# 4. 安装Python依赖
echo "🐍 安装Python依赖..."
pip3 install -r requirements.txt

# 5. 配置Claude Code
echo "⚙️ 配置Claude Code..."
cat > ~/.claude/settings.json << 'EOF'
{
  "extensions": {
    "cyberwiz": {
      "enabled": true,
      "root": "~/cyberwiz"
    }
  }
}
EOF

# 6. 创建启动命令
echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "  1. 运行: cd ~/cyberwiz && claude"
echo "  2. 输入: @thinking-team help"
```

### 3.2 手动安装步骤

#### 步骤1: 创建项目目录

```bash
# 创建主目录
mkdir -p ~/cyberwiz
cd ~/cyberwiz

# 创建子目录
mkdir -p {config,skills,workspace/{tasks,messages},knowledge/{patterns,experts,learnings},logs}
```

#### 步骤2: 配置文件

```bash
# 创建配置文件
cat > ~/cyberwiz/config/settings.yaml << 'EOF'
# CyberWiz 设置

system:
  name: "思考天团"
  version: "3.0"

execution:
  max_experts: 8
  timeout_minutes: 30
  parallel_mode: true

agents:
  thinking_experts:
    - kahneman
    - first_principle
    - six_hats
    - grow
    - reverse_thinking

  operation_experts:
    - growth_hacker
    - product_manager
    - data_analyst

web:
  host: "localhost"
  port: 8080
  auto_open: true
EOF
```

#### 步骤3: 创建 requirements.txt

```bash
cat > ~/cyberwiz/requirements.txt << 'EOF'
# Core
pydantic>=2.0
pyyaml>=6.0

# Web (可选)
fastapi>=0.100
uvicorn>=0.23
websocket-client>=1.6

# File monitoring (可选)
watchdog>=3.0

# Utils
python-dotenv>=1.0
requests>=2.31
EOF

# 安装依赖
pip3 install -r ~/cyberwiz/requirements.txt
```

---

## 四、Claude Code 集成

### 4.1 项目配置文件

在项目根目录创建 `CLAUDE.md`:

```markdown
<!-- ~/cyberwiz/CLAUDE.md -->
# CyberWiz - 思考天团 AI智囊团

## 项目指令

这是一个AI多专家协作系统，可以帮助你：
- 分析商业问题
- 生成决策建议
- 制定增长策略

## 可用命令

- `@thinking-team ask <问题>` - 提交问题
- `@thinking-team status` - 查看状态
- `@thinking-team board` - 打开看板

## 文件结构

```
cyberwiz/
├── config/          # 配置文件
├── skills/         # Agent/Skill定义
├── workspace/      # 工作区
├── knowledge/      # 知识库
└── logs/          # 日志
```

## 工具权限

允许使用以下工具：
- Read, Write, Edit (文件操作)
- Bash (命令执行)
- Glob, Grep (搜索)
- Task (Agent调用)
```

### 4.2 配置文件位置

```bash
# 方式1: 项目级配置
~/cyberwiz/.claude.json

# 方式2: 用户级配置
~/.claude.json

# 方式3: 环境变量
export CYBERWIZ_ROOT=~/cyberwiz
```

### 4.3 .claude.json 示例

```json
{
  "rules": [
    "CLAUDE.md"
  ],
  "tools": {
    "allowed": [
      "Read",
      "Write",
      "Edit",
      "Bash",
      "Glob",
      "Grep",
      "Task"
    ]
  },
  "extensions": {
    "cyberwiz": {
      "enabled": true,
      "root": "~/cyberwiz",
      "workspace": "~/cyberwiz/workspace",
      "knowledge": "~/cyberwiz/knowledge"
    }
  }
}
```

---

## 五、Skill 集成

### 5.1 核心Skill

```bash
# 创建 skills 目录
mkdir -p ~/cyberwiz/skills/{thinking,operation}

# 创建 thinking-team skill
cat > ~/cyberwiz/skills/thinking-team/SKILL.md << 'EOF'
---
name: thinking-team
description: >
  思考天团 - 多专家AI智囊团系统
  Invoke when: 用户需要分析商业问题、制定策略、寻求决策建议
  触发条件: 如何、策略、方案、增长、提升、优化
---

# 思考天团

## When to Use This Skill
- 需要多角度分析问题
- 需要专家团队协作
- 需要制定商业策略

## Core Workflow
1. **接收问题** — 理解用户需求
2. **意图识别** — 匹配专家
3. **专家分析** — 并行/辩论执行
4. **整合输出** — 生成报告

## Constraints
### MUST DO
- 保持客观中立
- 提供具体可执行的建议

### MUST NOT DO
- 不提供模糊建议
- 不绕过专家直接给结论
EOF
```

### 5.2 Skill 注册

```bash
# 在 config/skills.yaml 注册
cat > ~/cyberwiz/config/skills.yaml << 'EOF'
skills:
  - name: thinking-team
    path: skills/thinking-team
    enabled: true

  - name: growth-strategy
    path: skills/growth-strategy
    enabled: true

  - name: product-analysis
    path: skills/product-analysis
    enabled: true
EOF
```

---

## 六、Web看板安装（可选）

### 6.1 安装Web依赖

```bash
# 进入web目录
cd ~/cyberwiz/web

# 安装Node依赖
npm init -y
npm install express socket.io
```

### 6.2 启动看板服务

```bash
# 方式1: 直接运行
cd ~/cyberwiz/web
python3 app.py

# 方式2: 使用npm
npm start

# 方式3: Docker (可选)
docker-compose up -d
```

### 6.3 访问看板

```
浏览器打开: http://localhost:8080
```

---

## 七、PUA监督系统（可选）

### 7.1 安装PUA Hook

```bash
# 复制PUA配置
cp -r pua-system/hooks ~/.pua/

# 配置hooks
cat > ~/.claude/hooks.json << 'EOF'
{
  "PreCompact": [{
    "matcher": "*",
    "hooks": [{
      "type": "prompt",
      "prompt": "检查任务完成状态..."
    }]
  }]
}
EOF
```

### 7.2 启用PUA

```yaml
# config/settings.yaml
pua:
  enabled: true
  max_retries: 5
  pressure_levels:
    - name: "温和失望"
    - name: "灵魂拷问"
    - name: "361考核"
    - name: "毕业警告"
```

---

## 八、完整安装清单

### 8.1 必须项

| 项目 | 安装命令 | 验证方式 |
|------|----------|----------|
| Claude Code | 官网下载 | `claude --version` |
| Python 3.10+ | 系统自带 | `python3 --version` |
| 项目目录 | `mkdir -p ~/cyberwiz` | `ls ~/cyberwiz` |
| CLAUDE.md | 手动创建 | 读取成功 |

### 8.2 推荐项

| 项目 | 安装命令 | 用途 |
|------|----------|------|
| tmux | `brew install tmux` | 多会话管理 |
| Git | `brew install git` | 版本控制 |
| Node.js | `brew install node` | Web看板 |

### 8.3 可选项

| 项目 | 安装命令 | 用途 |
|------|----------|------|
| FastAPI | `pip install fastapi` | Web服务 |
| Socket.IO | `npm i socket.io` | 实时通信 |
| Watchdog | `pip install watchdog` | 文件监控 |

---

## 九、快速验证

### 9.1 环境检查

```bash
# 1. 检查目录
ls -la ~/cyberwiz

# 2. 检查配置文件
cat ~/cyberwiz/config/settings.yaml

# 3. 检查Python
python3 -c "import pydantic; print('OK')"

# 4. 启动测试
cd ~/cyberwiz && python3 -c "from web.app import app; print('Web OK')"
```

### 9.2 功能验证

```bash
# 1. 提交测试问题
cd ~/cyberwiz
echo '如何提升DAU？' | ./bin/thinking-team ask

# 2. 查看状态
./bin/thinking-team status

# 3. 打开看板
./bin/thinking-team board
```

---

## 十、常见问题

### 10.1 权限问题

```bash
# 给脚本添加执行权限
chmod +x ~/cyberwiz/bin/*.sh

# 给工作目录权限
chmod 755 ~/cyberwiz
```

### 10.2 依赖冲突

```bash
# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 10.3 Web看板无法启动

```bash
# 检查端口占用
lsof -i :8080

# 使用其他端口
export PORT=8081
python3 app.py --port 8081
```

---

## 十一、卸载

```bash
# 删除项目目录
rm -rf ~/cyberwiz

# 清理配置
rm ~/.claude.json (如果包含cyberwiz配置)

# 清理日志
rm -rf ~/.cyberwiz/logs/
```

---

## 十二、总结

### 12.1 最小安装（核心功能）

```bash
# 仅需3步
mkdir -p ~/cyberwiz
# 创建 CLAUDE.md
# 创建 config/settings.yaml
```

### 12.2 标准安装（推荐）

```bash
# 1. 安装依赖
brew install python node tmux

# 2. 创建项目
mkdir -p ~/cyberwiz
cd ~/cyberwiz

# 3. 配置文件
# - CLAUDE.md
# - config/settings.yaml
# - requirements.txt

# 4. 安装Python包
pip install -r requirements.txt
```

### 12.3 完整安装（生产环境）

```bash
# 1-4: 同标准安装

# 5. 安装Web看板
cd web && npm install

# 6. 配置PUA
cp -r pua-system/hooks ~/

# 7. 配置hooks
# 编辑 ~/.claude/hooks.json

# 8. 启动服务
./bin/thinking-team start
```

---

**安装日期**: 2026-03-20
**文档编号**: Q22
**版本**: v1.0
