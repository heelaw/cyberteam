# 更新文档

将文档与代码库同步，从真实来源文件生成。

## 步骤 1：确定事实来源

|来源 |生成 |
|--------|------------|
| `package.json` 脚本 |可用命令参考|
| `.env.example` |环境变量文档|
| `openapi.yaml` / 路由文件 | API端点参考|
|源代码导出|公共API文档|
| `Dockerfile` / `docker-compose.yml` |基础设施设置文档 |

## 步骤 2：生成脚本参考

1. 读取`package.json`（或`Makefile`、`Cargo.toml`、`pyproject.toml`）
2. 提取所有脚本/命令及其描述
3.生成参考表：```markdown
| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Production build with type checking |
| `npm test` | Run test suite with coverage |
```## 步骤3：生成环境文档

1. 读取`.env.example`（或`.env.template`、`.env.sample`）
2. 提取所有变量及其用途
3. 按必需与可选分类
4. 记录预期格式和有效值```markdown
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgres://user:pass@host:5432/db` |
| `LOG_LEVEL` | No | Logging verbosity (default: info) | `debug`, `info`, `warn`, `error` |
```## 步骤 4：更新贡献指南

使用以下命令生成或更新“docs/CONTRIBUTING.md”：
- 开发环境设置（先决条件、安装步骤）
- 可用的脚本及其用途
- 测试程序（如何运行，如何编写新测试）
- 代码风格强制（linter、格式化程序、预提交挂钩）
- 公关提交清单

## 步骤 5：更新 Runbook

使用以下命令生成或更新“docs/RUNBOOK.md”：
- 部署过程（分步）
- 健康检查端点和监控
- 常见问题及其修复
- 回滚程序
- 警报和升级路径

## 步骤 6：陈旧性检查

1.查找90+天内未修改的文档文件
2. 与最近源代码更改的交叉引用
3. 标记可能过时的文档以供人工审核

## 步骤 7：显示摘要```
Documentation Update
──────────────────────────────
Updated:  docs/CONTRIBUTING.md (scripts table)
Updated:  docs/ENV.md (3 new variables)
Flagged:  docs/DEPLOY.md (142 days stale)
Skipped:  docs/API.md (no changes detected)
──────────────────────────────
```## 规则

- **单一事实来源**：始终从代码生成，从不手动编辑生成的部分
- **保留手动部分**：仅更新生成的部分；保持手写散文完好无损
- **标记生成的内容**：在生成的部分周围使用 `<!-- AUTO-GENERATED -->` 标记
- **不要在无提示的情况下创建文档**：仅在命令明确请求时创建新的文档文件