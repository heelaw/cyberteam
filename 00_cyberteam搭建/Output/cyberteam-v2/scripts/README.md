# CyberTeam Scripts 工具集

## 概述

本目录包含 CyberTeam v2.1 提供的实用脚本工具，用于 Agent 管理、配置生成和工作流编排。

## 脚本列表

### 1. agent-converter.py
Agent 定义转换工具，支持多 IDE/工具格式导出。

**功能**:
- 将通用 Agent 定义转换为特定工具格式
- 支持: Claude Code / Cursor / Windsurf / CoSTAR / Roo Code / Continue / GitHub Copilot / Aider / Codestral / Lovable / Cline / Gemini CLI / VS Code Agent
- 验证 Agent 定义完整性
- 生成部署配置

**使用方法**:
```bash
python3 agent-converter.py --tool claude-code --input agents/
python3 agent-converter.py --all --input agents/ --output integrations/
```

### 2. config-generator.py
配置生成器，根据模板和参数自动生成配置文件。

**功能**:
- 从模板生成配置
- 支持变量替换
- 多格式输出支持

**使用方法**:
```bash
python3 config-generator.py --template templates/ --output config/
```

### 3. multi-tool-adapter.py
多工具适配器，实现跨工具的 Agent 调用。

**功能**:
- 统一接口抽象
- 工具特定适配器
- 请求/响应转换

**使用方法**:
```bash
python3 multi-tool-adapter.py --tool claude-code --agent your-agent
```

### 4. workflow-engine.py
工作流引擎，编排复杂的多 Agent 协作流程。

**功能**:
- 工作流定义和执行
- 条件分支和循环
- 状态管理和持久化
- 错误处理和重试

**使用方法**:
```bash
python3 workflow-engine.py --workflow workflows/example.yaml
```

## 环境要求

- Python 3.9+
- PyYAML
- 其他依赖见各脚本的 import 语句

## 安装

```bash
pip install -r requirements.txt
```

## 版本信息

- **版本**: v2.1
- **来源**: CyberTeam-v2.1
- **融合日期**: 2026-03-24
- **整合到**: cyberteam-v2

---

**创建日期**: 2026-03-23 | **更新日期**: 2026-03-24
