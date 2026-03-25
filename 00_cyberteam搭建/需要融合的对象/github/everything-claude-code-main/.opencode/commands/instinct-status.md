# 本能状态命令

显示 Continuous-learning-v2 的本能状态：$ARGUMENTS

## 你的任务

运行：```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" status
```如果“CLAUDE_PLUGIN_ROOT”不可用，请使用：```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py status
```## 行为注意事项

- 输出包括项目范围和全球直觉。
- 当 ID 发生冲突时，项目本能会凌驾于全局本能之上。
- 输出按带有置信条的域进行分组。
- 此命令不支持 v2.1 中的额外过滤器。