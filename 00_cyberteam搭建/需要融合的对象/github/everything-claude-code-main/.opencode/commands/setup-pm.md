# 设置包管理器命令

配置您首选的包管理器：$ARGUMENTS

## 你的任务

为项目或全局设置包管理器首选项。

## 检测顺序

1. **环境变量**：`CLAUDE_PACKAGE_MANAGER`
2. **项目配置**：`.claude/package-manager.json`
3. **package.json**：`packageManager`字段
4. **锁定文件**：从锁定文件中自动检测
5. **全局配置**：`~/.claude/package-manager.json`
6. **后备**：首先可用

## 配置选项

### 选项 1：环境变量```bash
export CLAUDE_PACKAGE_MANAGER=pnpm
```### 选项 2：项目配置```bash
# Create .claude/package-manager.json
echo '{"packageManager": "pnpm"}' > .claude/package-manager.json
```### 选项 3：package.json```json
{
  "packageManager": "pnpm@8.0.0"
}
```### 选项 4：全局配置```bash
# Create ~/.claude/package-manager.json
echo '{"packageManager": "yarn"}' > ~/.claude/package-manager.json
```## 支持的包管理器

|经理 |锁定文件|命令 |
|--------|------------|----------|
| npm |包锁.json | `npm install`、`npm run` |
| PNPM | pnpm-lock.yaml | `pnpm 安装`、`pnpm 运行` |
|纱线|纱线锁 | `纱线安装`、`纱线运行` |
|包子|包子.lockb | `bun 安装`、`bun 运行` |

## 验证

检查当前设置：```bash
node scripts/setup-package-manager.js --detect
```---

**TIP**: For consistency across team, add `packageManager` field to package.json.