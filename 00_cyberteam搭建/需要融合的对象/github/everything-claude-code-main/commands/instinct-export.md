# 本能导出命令

将本能导出为可共享的格式。非常适合：
- 与队友分享
- 转移到新机器
- 为项目会议做出贡献

## 用法```
/instinct-export                           # Export all personal instincts
/instinct-export --domain testing          # Export only testing instincts
/instinct-export --min-confidence 0.7      # Only export high-confidence instincts
/instinct-export --output team-instincts.yaml
/instinct-export --scope project --output project-instincts.yaml
```## 做什么

1. 检测当前项目上下文
2. 按选定范围加载本能：
   - `project`：仅限当前项目
   - `global`：仅限全球
   - `all`：项目 + 全局合并（默认）
3. 应用过滤器（`--domain`、`--min-confidence`）
4. 将 YAML 样式导出写入文件（如果未提供输出路径，则写入 stdout）

## 输出格式

创建一个 YAML 文件：```yaml
# Instincts Export
# Generated: 2025-01-22
# Source: personal
# Count: 12 instincts

---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.8
domain: code-style
source: session-observation
scope: project
project_id: a1b2c3d4e5f6
project_name: my-app
---

# Prefer Functional Style

## Action
Use functional patterns over classes.
```## 旗帜

- `--domain <name>`：仅导出指定的域
- `--min-confidence <n>`：最小置信度阈值
- `--output <file>`：输出文件路径（省略时打印到标准输出）
- `--scope <project|global|all>`：导出范围（默认：`all`）