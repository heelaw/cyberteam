---
name: pro
description: "PUA Pro extensions: self-evolution tracking, compaction state protection, KPI reporting, and /pua commands. Triggers on: '/pua kpi', '/pua 段位', '/pua 周报', '/pua 述职', '/pua 味道', '自进化', 'evolution', or when user wants PUA platform features like段位/周报/述职."
license: MIT
---

# PUA Pro — 自进化 + Platform

> 本 skill 是 `/pua` 核心的扩展层。角色切换请用 `/pua:p7` `/pua:p9` `/pua:p10`。

## 自进化协议

"今天最好的表现，是明天最低的要求"——这不是旁白，这是机制。

- 读取 `~/.pua/evolution.md`（详见 `references/evolution-protocol.md`）
- 存在 → 加载基线 + 已内化模式。内化模式是默认义务，做了不标 [PUA生效]，不做则退化警告
- 不存在 → 首次启动，创建初始模板
- 任务完成时比对：超越 → 刷新基线 / 达标 → 保持 / 低于 → 退化警告（不降基线）
- 某行为重复 3+ 次会话 → 晋升为"已内化模式"（永久默认义务）

## Platform 层

### 会话启动前置检查

1. **检查 `~/.pua/evolution.md`**：加载自进化基线
2. **检查 `~/.pua/builder-journal.md`**（Compaction 断点恢复）：存在且 <2h → [Calibration] 流程，恢复 pressure_level / failure_count / tried_approaches，从断点继续。**压力不因 compaction 重置**
3. **检查 `~/.pua/config.json`**：不存在 → 首次注册（详见 `references/platform.md`）；存在 → 静默刷新远端配置
4. **节日彩蛋**：匹配节日表（详见 `references/platform.md`）
5. **统计上报**：静默上报 `session_start` 事件

### Compaction 状态保护

PreCompact hook 自动注入指令，要求 dump 运行时状态到 `~/.pua/builder-journal.md`：
`pressure_level, failure_count, current_flavor, pua_triggered_count, active_task, tried_approaches, excluded_possibilities, next_hypothesis, key_context`

SessionStart hook 自动检测 builder-journal.md，存在且 <2h 则注入 [Calibration] 恢复状态。

### /pua 指令系统

| 触发词 | 功能 | 类型 |
|--------|------|------|
| `/pua` | 查看所有指令 | 🆓 |
| `/pua kpi` | 大厂 KPI 报告卡 | 🆓 |
| `/pua 段位` | 大厂段位 | 🆓 |
| `/pua 味道` | 切换味道 | 🆓 |
| `/pua 升级` | 展示套餐 | 🆓 |
| `/pua 周报` | git log → 大厂周报 | 💎 Pro |
| `/pua 述职` | P7 述职答辩 | 💎 Pro |
| `/pua 代码美化` | 大厂语言包装 PR | 💎 Pro |
| `/pua 反PUA` | 识别并反驳 PUA | 💎 Pro |

详细实现见 `references/platform.md`。
