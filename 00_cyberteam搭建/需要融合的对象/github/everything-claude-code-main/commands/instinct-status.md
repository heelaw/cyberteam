# 本能状态命令

显示当前项目的学习本能以及按领域分组的全局本能。

## 实施

使用插件根路径运行本能 CLI：```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" status
```或者，如果未设置“CLAUDE_PLUGIN_ROOT”（手动安装），请使用：```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py status
```＃＃ 用法```
/instinct-status
```## 做什么

1.检测当前项目上下文（git remote/path hash）
2. 从 `~/.claude/homunculus/projects/<project-id>/instincts/` 读取项目本能
3. 从`~/.claude/homunculus/instincts/`读取全局本能
4. 与优先规则合并（当ID冲突时项目覆盖全局）
5. 按域分组显示，带有置信条和观察统计数据

## 输出格式```
============================================================
  INSTINCT STATUS - 12 total
============================================================

  Project: my-app (a1b2c3d4e5f6)
  Project instincts: 8
  Global instincts:  4

## PROJECT-SCOPED (my-app)
  ### WORKFLOW (3)
    ███████░░░  70%  grep-before-edit [project]
              trigger: when modifying code

## GLOBAL (apply to all projects)
  ### SECURITY (2)
    █████████░  85%  validate-user-input [global]
              trigger: when handling user input
```