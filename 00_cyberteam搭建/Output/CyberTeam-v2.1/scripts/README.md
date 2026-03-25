# CyberTeam v2.1 Scripts

CyberTeam v2.1 脚本系统，提供 Agent 定义转换、多工具适配、工作流引擎和配置生成功能。

## 目录结构

```
scripts/
├── install.sh              # 安装脚本 - 安装 Agents 到各工具
├── agent-converter.py       # Agent 定义转换工具
├── multi-tool-adapter.py   # 多工具适配层
├── workflow-engine.py       # 工作流引擎
├── config-generator.py      # 配置生成器
├── cyberteam               # CyberTeam CLI Wrapper (推荐)
└── README.md              # 本文档
```

## 5. cyberteam - CLI Wrapper

CyberTeam 统一品牌 CLI，底层调用 ClawTeam，提供 CyberTeam 品牌体验。

```bash
# 安装
cp scripts/cyberteam ~/.local/bin/cyberteam
chmod +x ~/.local/bin/cyberteam

# 使用 (完全替代 clawteam)
cyberteam team spawn-team my-team -d "我的团队"
cyberteam spawn --team my-team --agent-name worker1 --task "任务"
cyberteam board live my-team --interval 5
cyberteam launch my-team "一句话交代任务"
cyberteam --help
```

### 命令对照表

| CyberTeam 命令 | 底层 ClawTeam |
|---------------|---------------|
| `cyberteam team ...` | `clawteam team ...` |
| `cyberteam spawn ...` | `clawteam spawn ...` |
| `cyberteam task ...` | `clawteam task ...` |
| `cyberteam board ...` | `clawteam board ...` |
| `cyberteam inbox ...` | `clawteam inbox ...` |
| `cyberteam launch <name> [goal]` | 快速启动团队 (CyberTeam 特色) |

## 功能概述

### 1. install.sh - 安装脚本

将 CyberTeam Agents 和 Skills 安装到本地 AI 编程工具中。

**支持的工具:**

| 工具 | 类型 | 安装位置 |
|------|------|----------|
| Claude Code | 全局 | `~/.claude/agents/` |
| GitHub Copilot | 全局 | `~/.github/agents/` |
| Antigravity | 全局 | `~/.gemini/antigravity/skills/` |
| Gemini CLI | 全局 | `~/.gemini/extensions/cyberteam/` |
| OpenCode | 项目级 | `.opencode/agents/` |
| Cursor | 项目级 | `.cursor/rules/` |
| Aider | 项目级 | `CONVENTIONS.md` |
| Windsurf | 项目级 | `.windsurfrules` |
| OpenClaw | 全局 | `~/.openclaw/cyberteam/` |
| Qwen Code | 项目级 | `.qwen/agents/` |

**使用方法:**

```bash
# 安装所有检测到的工具 (交互模式)
./scripts/install.sh

# 安装到特定工具
./scripts/install.sh --tool claude-code

# 非交互模式
./scripts/install.sh --no-interactive

# 并行安装
./scripts/install.sh --parallel --jobs 4
```

### 2. agent-converter.py - Agent 定义转换工具

将通用 Agent 定义转换为特定工具格式。

**支持的工具格式:**

- Claude Code (.md)
- GitHub Copilot (.md)
- Cursor (.mdc)
- Windsurf (.windsurfrules)
- OpenCode (.md)
- OpenClaw (SOUL.md + AGENTS.md + IDENTITY.md)
- Aider (CONVENTIONS.md)
- Antigravity (SKILL.md)
- Gemini CLI (SKILL.md)
- Qwen Code (.md)
- Roo Code
- Continue
- Codestral
- Lovable
- Cline

**使用方法:**

```bash
# 转换为单个工具格式
python3 agent-converter.py --tool claude-code --input ../agents/ --output ./integrations/

# 转换为所有格式
python3 agent-converter.py --all --input ../agents/

# 仅验证 Agent 定义
python3 agent-converter.py --validate --input ../agents/

# 指定输出目录
python3 agent-converter.py --tool cursor --input ../agents/ --output ./cursor-rules/
```

### 3. multi-tool-adapter.py - 多工具适配层

统一接口适配多种 AI 编程工具，提供自动检测、动态路由和状态同步。

**支持的工具:**

- claude (Claude Code)
- cursor (Cursor)
- windsurf (Windsurf)
- copilot (GitHub Copilot)
- aider (Aider)
- codestral (Codestral)
- lovable (Lovable)
- cline (Cline)
- gemini (Gemini CLI)
- continue (Continue)
- opencode (OpenCode)
- qwen (Qwen Code)

**使用方法:**

```bash
# 检测所有可用工具
python3 multi-tool-adapter.py --detect

# 列出工具状态
python3 multi-tool-adapter.py --list

# 获取工具推荐
python3 multi-tool-adapter.py --recommend --task "代码审查"

# 输出 JSON 报告
python3 multi-tool-adapter.py --detect --output report.json
```

### 4. workflow-engine.py - 工作流引擎

定义和执行多步骤工作流，支持并行和串行任务、状态管理和恢复。

**使用方法:**

```bash
# 列出所有工作流
python3 workflow-engine.py --list

# 执行工作流
python3 workflow-engine.py --define my-workflow.json --execute

# 查看执行状态
python3 workflow-engine.py --status <execution-id>

# 暂停/恢复/取消
python3 workflow-engine.py --pause
python3 workflow-engine.py --resume
python3 workflow-engine.py --cancel
```

**工作流定义示例 (workflow.json):**

```json
{
  "id": "dev-workflow",
  "name": "开发工作流",
  "description": "标准的代码开发流程",
  "tasks": [
    {
      "id": "task-1",
      "name": "代码审查",
      "action": "echo",
      "params": {"message": "开始代码审查"}
    },
    {
      "id": "task-2",
      "name": "运行测试",
      "action": "run",
      "params": {"command": "pytest tests/"},
      "depends_on": ["task-1"]
    }
  ]
}
```

### 5. config-generator.py - 配置生成器

从模板生成配置文件，支持多工具配置和环境变量处理。

**支持的配置模板:**

- claude-code
- cursor
- windsurf
- copilot
- gemini-cli
- aider
- opencode
- qwen

**使用方法:**

```bash
# 列出所有模板
python3 config-generator.py --list

# 生成单个配置
python3 config-generator.py --template claude-code --output ./config/settings.json

# 生成所有配置
python3 config-generator.py --all --output ./config/

# 使用覆盖值
python3 config-generator.py --template claude-code --overrides '{"model": "claude-3-5-sonnet"}'

# 验证配置
python3 config-generator.py --validate ./config/settings.json

# 创建项目配置
python3 config-generator.py --project "MyApp" --tools claude-code cursor --output project.json
```

## 工具兼容性列表

### AI 编程工具支持矩阵

| 工具 | Agent 定义 | Skills | 工作流 | 配置 |
|------|------------|--------|--------|------|
| Claude Code | Yes | Yes | Yes | Yes |
| Cursor | Yes | Yes | Yes | Yes |
| Windsurf | Yes | Yes | Yes | Yes |
| GitHub Copilot | Yes | Partial | Yes | Yes |
| Aider | Yes | Yes | Yes | Yes |
| Gemini CLI | Yes | Yes | Yes | Yes |
| OpenCode | Yes | Yes | Yes | Yes |
| OpenClaw | Yes | Yes | Yes | Yes |
| Qwen Code | Yes | Yes | Yes | Yes |
| Cline | Yes | Yes | Yes | Yes |
| Continue | Yes | Yes | Yes | Yes |
| Codestral | Yes | Yes | Yes | Yes |
| Lovable | Yes | Yes | Yes | Yes |
| Antigravity | Yes | Yes | Yes | Yes |

## 安装说明

### 前置依赖

- Python 3.8+
- Bash 3.2+ (用于 install.sh)

### 快速安装

```bash
# 克隆 CyberTeam
git clone <repository-url>
cd CyberTeam-v2.1

# 安装到所有检测到的工具
./scripts/install.sh

# 或指定工具
./scripts/install.sh --tool claude-code
```

### 验证安装

```bash
# 检测已安装的工具
python3 scripts/multi-tool-adapter.py --detect
```

## 使用示例

### 场景 1: 为新项目设置开发环境

```bash
# 1. 检测可用工具
python3 scripts/multi-tool-adapter.py --detect

# 2. 生成项目配置
python3 scripts/config-generator.py --project "MyProject" --tools claude-code cursor --output myproject.json

# 3. 安装 Agents
./scripts/install.sh --tool claude-code
./scripts/install.sh --tool cursor --no-interactive

# 4. 转换为项目级格式
cd my-project
./scripts/install.sh --tool cursor
```

### 场景 2: 自定义 Agent 转换

```bash
# 1. 编辑 Agent 定义
vim agents/custom-agent.md

# 2. 验证定义
python3 scripts/agent-converter.py --validate --input agents/

# 3. 转换到目标格式
python3 scripts/agent-converter.py --tool cursor --input agents/ --output integrations/

# 4. 安装
./scripts/install.sh --tool cursor
```

### 场景 3: 使用工作流自动化

```bash
# 1. 创建工作流定义
cat > my-workflow.json << 'EOF'
{
  "name": "代码审查流程",
  "tasks": [
    {"name": "静态分析", "action": "run", "params": {"command": "pylint src/"}},
    {"name": "单元测试", "action": "run", "params": {"command": "pytest tests/"}, "depends_on": ["task-1"]}
  ]
}
EOF

# 2. 执行工作流
python3 scripts/workflow-engine.py --define my-workflow.json --execute
```

## 故障排除

### 工具未检测到

```bash
# 检查工具是否安装
which claude
claude --version

# 手动指定安装
./scripts/install.sh --tool claude-code --no-interactive
```

### 转换失败

```bash
# 验证 Agent 定义
python3 scripts/agent-converter.py --validate --input agents/

# 检查文件格式
head -20 agents/my-agent.md
```

### 工作流执行问题

```bash
# 查看执行状态
python3 scripts/workflow-engine.py --status <execution-id>

# 查看详细日志
ls -la .cyberteam/workflows/
```

## 许可证

MIT License
