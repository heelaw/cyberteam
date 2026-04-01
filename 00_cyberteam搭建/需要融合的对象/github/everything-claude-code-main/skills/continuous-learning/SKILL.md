# 持续学习技能

自动评估 Claude 代码会话，以提取可重用的模式，并将其保存为学到的技能。

## 何时激活

- 设置从克劳德代码会话中自动提取模式
- 配置用于会话评估的 Stop 挂钩
- 在`~/.claude/skills/learned/`中审查或管理学到的技能
- 调整提取阈值或模式类别
- 比较 v1（本）与 v2（基于本能）方法

## 它是如何工作的

此技能在每个会话结束时作为 **Stop hook** 运行：

1. **会话评估**：检查会话是否有足够的消息（默认：10+）
2. **模式检测**：识别会话中可提取的模式
3. **技能提取**：将有用的模式保存到`~/.claude/skills/learned/`

## 配置

编辑 `config.json` 进行自定义：```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "learned_skills_path": "~/.claude/skills/learned/",
  "patterns_to_detect": [
    "error_resolution",
    "user_corrections",
    "workarounds",
    "debugging_techniques",
    "project_specific"
  ],
  "ignore_patterns": [
    "simple_typos",
    "one_time_fixes",
    "external_api_issues"
  ]
}
```## 模式类型

|图案|描述 |
|---------|-------------|
| `错误解决方案` |具体错误是如何解决的 |
| `用户更正` |来自用户修正的模式|
| `解决方法` |框架/库怪癖的解决方案|
| `调试技术` |有效的调试方法|
| `项目特定` |特定于项目的约定 |

## 挂钩设置

添加到您的“~/.claude/settings.json”：```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning/evaluate-session.sh"
      }]
    }]
  }
}
```## 为什么要停止 Hook？

- **轻量级**：在会话结束时运行一次
- **非阻塞**：不会给每条消息增加延迟
- **完整的上下文**：可以访问完整的会话记录

## 相关

- [长篇指南](https://x.com/affaanmustafa/status/2014040193557471352) - 关于持续学习的部分
- `/learn` 命令 - 会话中手动模式提取

---

## 比较说明（研究：2025 年 1 月）

### vs 侏儒

Homunculus v2 采用了更复杂的方法：

|特色 |我们的方法|侏儒 v2 |
|--------|--------------|----------------|
|观察|停止钩子（会话结束）| PreToolUse/PostToolUse 挂钩（100% 可靠）|
|分析|主要背景|背景特工（俳句）|
|粒度|技能全 |原子“本能”|
|信心|无 | 0.3-0.9 加权 |
|进化|直接技能 |本能→集群→技能/命令/代理|
|分享|无 |出口/进口本能 |

**来自侏儒的关键见解：**
> “v1 依赖于观察技能。技能是概率性的 — 它们在大约 50-80% 的时间内触发。v2 使用钩子进行观察（100% 可靠），并使用本能作为学习行为的原子单位。”

### 潜在的 v2 增强功能

1. **基于本能的学习** - 具有置信度评分的更小的原子行为
2. **后台观察者** - Haiku Agent 并行分析
3. **信心衰退** - 如果本能受到矛盾，就会失去信心
4. **域标记** - 代码风格、测试、git、调试等。
5. **进化路径** - 将相关本能聚集成技能/命令

请参阅：“docs/continuous-learning-v2-spec.md”了解完整规范。