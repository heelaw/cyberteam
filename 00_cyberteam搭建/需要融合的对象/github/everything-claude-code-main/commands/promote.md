# 提升命令

在持续学习 v2 中将本能从项目范围提升到全局范围。

## 实施

使用插件根路径运行本能 CLI：```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" promote [instinct-id] [--force] [--dry-run]
```或者如果未设置“CLAUDE_PLUGIN_ROOT”（手动安装）：```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py promote [instinct-id] [--force] [--dry-run]
```＃＃ 用法```bash
/promote                      # Auto-detect promotion candidates
/promote --dry-run            # Preview auto-promotion candidates
/promote --force              # Promote all qualified candidates without prompt
/promote grep-before-edit     # Promote one specific instinct from current project
```## 做什么

1. 检测当前项目
2. 如果提供了“instinct-id”，则仅提升该本能（如果当前项目中存在）
3. 否则，寻找符合以下条件的跨项目候选人：
   - 出现在至少2个项目中
   - 满足置信度阈值
4. 将提升的本能写入 `~/.claude/homunculus/instincts/personal/` 并使用 `scope: global`