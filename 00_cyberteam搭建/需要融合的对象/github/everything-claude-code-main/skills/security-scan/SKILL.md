# 安全扫描技巧

使用 [AgentShield](https://github.com/affaan-m/agentshield) 审核您的 Claude Code 配置是否存在安全问题。

## 何时激活

- 建立一个新的克劳德代码项目
- 修改 `.claude/settings.json`、`CLAUDE.md` 或 MCP 配置后
- 提交配置更改之前
- 使用现有 Claude 代码配置登录新存储库时
- 定期安全卫生检查

## 它扫描什么

|文件 |检查|
|------|--------|
| `克劳德.md` |硬编码秘密、自动运行指令、提示注入模式 |
| `settings.json` |过于宽松的允许列表、缺少拒绝列表、危险的绕过标志 |
| `mcp.json` |有风险的 MCP 服务器、硬编码环境机密、npx 供应链风险 |
| `钩子/` |通过插值、数据泄露、静默错误抑制进行命令注入 |
| `代理/*.md` |不受限制的工具访问、快速注射表面、缺少模型规格 |

## 先决条件

必须安装 AgentShield。如果需要的话检查并安装：```bash
# Check if installed
npx ecc-agentshield --version

# Install globally (recommended)
npm install -g ecc-agentshield

# Or run directly via npx (no install needed)
npx ecc-agentshield scan .
```## 用法

### 基本扫描

针对当前项目的 `.claude/` 目录运行：```bash
# Scan current project
npx ecc-agentshield scan

# Scan a specific path
npx ecc-agentshield scan --path /path/to/.claude

# Scan with minimum severity filter
npx ecc-agentshield scan --min-severity medium
```### 输出格式```bash
# Terminal output (default) — colored report with grade
npx ecc-agentshield scan

# JSON — for CI/CD integration
npx ecc-agentshield scan --format json

# Markdown — for documentation
npx ecc-agentshield scan --format markdown

# HTML — self-contained dark-theme report
npx ecc-agentshield scan --format html > security-report.html
```### 自动修复

自动应用安全修复（仅标记为可自动修复的修复）：```bash
npx ecc-agentshield scan --fix
```这将：
- 用环境变量引用替换硬编码的秘密
- 加强对范围内替代方案的通配符权限
- 切勿修改仅手动建议

### Opus 4.6 深度分析

运行对抗性三代理管道以进行更深入的分析：```bash
# Requires ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=your-key
npx ecc-agentshield scan --opus --stream
```这运行：
1. **攻击者（红队）** — 查找攻击向量
2. **后卫（蓝队）** — 建议强化
3. **审计员（最终裁决）** — 综合两种观点

### 初始化安全配置

从头开始搭建新的安全“.claude/”配置：```bash
npx ecc-agentshield init
```创建：
- `settings.json` 具有范围权限和拒绝列表
- `CLAUDE.md` 具有安全最佳实践
- `mcp.json` 占位符

### GitHub 操作

添加到您的 CI 管道：```yaml
- uses: affaan-m/agentshield@v1
  with:
    path: '.'
    min-severity: 'medium'
    fail-on-findings: true
```## 严重级别

|等级 |分数 |意义|
|--------|--------|---------|
|一个 | 90-100 |安全配置 |
|乙| 75-89 | 75-89小问题 |
| C | 60-74 | 60-74需要注意|
| d | 40-59 | 40-59重大风险|
| F | 0-39 |严重漏洞|

## 解释结果

### 关键发现（立即修复）
- 配置文件中的硬编码 API 密钥或令牌
- 允许列表中的“Bash(*)”（不受限制的 shell 访问）
- 通过 `${file}` 插值将命令注入到钩子中
- Shell 运行的 MCP 服务器

### 高发现（在生产前修复）
- CLAUDE.md 中的自动运行指令（提示注入向量）
- 权限中缺少拒绝列表
- 具有不必要的 Bash 访问权限的代理

### 中等发现（推荐）
- 钩子中的静默错误抑制（`2>/dev/null`、`|| true`）
- 缺少 PreToolUse 安全挂钩
- MCP 服务器配置中自动安装“npx -y”

### 信息调查结果（意识）
- MCP 服务器上缺少描述
- 禁止性指令被正确标记为良好实践

## 链接

- **GitHub**：[github.com/affaan-m/agentshield](https://github.com/affaan-m/agentshield)
- **npm**：[npmjs.com/package/ecc-agentshield](https://www.npmjs.com/package/ecc-agentshield)