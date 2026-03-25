# 本能导入命令

## 实施

使用插件根路径运行本能 CLI：```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" import <file-or-url> [--dry-run] [--force] [--min-confidence 0.7] [--scope project|global]
```或者如果未设置“CLAUDE_PLUGIN_ROOT”（手动安装）：```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py import <file-or-url>
```从本地文件路径或 HTTP(S) URL 导入本能。

＃＃ 用法```
/instinct-import team-instincts.yaml
/instinct-import https://github.com/org/repo/instincts.yaml
/instinct-import team-instincts.yaml --dry-run
/instinct-import team-instincts.yaml --scope global --force
```## 做什么

1. 获取本能文件（本地路径或URL）
2. 解析并验证格式
3. 用现有的直觉检查重复项
4. 合并或添加新的本能
5. 保存到继承本能目录：
   - 项目范围：`~/.claude/homunculus/projects/<project-id>/instincts/inherited/`
   - 全局范围：`~/.claude/homunculus/instincts/inherited/`

## 导入流程```
📥 Importing instincts from: team-instincts.yaml
================================================

Found 12 instincts to import.

Analyzing conflicts...

## New Instincts (8)
These will be added:
  ✓ use-zod-validation (confidence: 0.7)
  ✓ prefer-named-exports (confidence: 0.65)
  ✓ test-async-functions (confidence: 0.8)
  ...

## Duplicate Instincts (3)
Already have similar instincts:
  ⚠️ prefer-functional-style
     Local: 0.8 confidence, 12 observations
     Import: 0.7 confidence
     → Keep local (higher confidence)

  ⚠️ test-first-workflow
     Local: 0.75 confidence
     Import: 0.9 confidence
     → Update to import (higher confidence)

Import 8 new, update 1?
```## 合并行为

当导入具有现有 ID 的本能时：
- 更高置信度的导入成为更新候选
- 跳过相同/较低置信度导入
- 用户确认，除非使用“--force”

## 来源追踪

导入的本能标记为：```yaml
source: inherited
scope: project
imported_from: "team-instincts.yaml"
project_id: "a1b2c3d4e5f6"
project_name: "my-project"
```## 旗帜

- `--dry-run`：预览而不导入
- `--force`：跳过确认提示
- `--min-confidence <n>`：仅导入高于阈值的本能
- `--scope <project|global>`：选择目标范围（默认：`project`）

## 输出

导入后：```
✅ Import complete!

Added: 8 instincts
Updated: 1 instinct
Skipped: 3 instincts (equal/higher confidence already exists)

New instincts saved to: ~/.claude/homunculus/instincts/inherited/

Run /instinct-status to see all instincts.
```