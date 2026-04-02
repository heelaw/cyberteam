# 项目命令

列出持续学习 v2 的项目注册表项和每个项目的本能/观察计数。

## 实施

使用插件根路径运行本能 CLI：```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" projects
```或者如果未设置“CLAUDE_PLUGIN_ROOT”（手动安装）：```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py projects
```＃＃ 用法```bash
/projects
```## 做什么

1. 阅读 `~/.claude/homunculus/projects.json`
2. 对于每个项目，显示：
   - 项目名称、id、根、远程
   - 个人和遗传的本能很重要
   - 观察事件计数
   - 最后看到的时间戳
3.同时显示全局本能总数