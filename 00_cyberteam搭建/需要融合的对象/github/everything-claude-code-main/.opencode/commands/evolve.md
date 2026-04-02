# 进化命令

在持续学习 v2 中分析和发展本能：$ARGUMENTS

## 你的任务

运行：```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" evolve $ARGUMENTS
```如果“CLAUDE_PLUGIN_ROOT”不可用，请使用：```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py evolve $ARGUMENTS
```## 支持的参数 (v2.1)

- 无参数：仅分析
- `--generate`：也在`evolved/{skills,commands,agents}`下生成文件

## 行为注意事项

- 使用项目+全局直觉进行分析。
- 显示来自触发器和域集群的技能/命令/代理候选者。
- 显示项目 -> 全球推广候选人。
- 使用“--generate”，输出路径为：
  - 项目上下文：`~/.claude/homunculus/projects/<project-id>/evolved/`
  - 全局后备：`~/.claude/homunculus/evolved/`