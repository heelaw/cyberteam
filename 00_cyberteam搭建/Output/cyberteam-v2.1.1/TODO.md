# CyberTeam v2 完整 To-Do List

**整合专家**: CyberTeam 整合专家  
**日期**: 2026-03-24  
**版本**: v2.0.1 (融合版)

---

## 一、问题清单

### 1.1 核心架构问题

| ID | 问题 | 优先级 | 来源 |
|----|------|--------|------|
| **P0-1** | Agent-Engine 断链：v2.1 的 Agent 定义是纯 markdown，v2 有 Python 引擎，谁来触发引擎？ | P0 | 合并报告 |
| **P0-2** | 思维专家-routing 冲突：thinking_injector 和 routing.yaml 选出的专家可能不一致 | P0 | 合并报告 |
| **P0-3** | 上下文压缩缺失：v2.1 有 Context Compression，v2 无 | P0 | 合并报告 |
| **P0-4** | 文档闭环缺失：两边的 README/ARCHITECTURE 没有对齐 | P0 | 合并报告 |

### 1.2 Phase 4 增强模块

| ID | 问题 | 优先级 | 来源 |
|----|------|--------|------|
| **P1-1** | Execution Monitor 缺失 | P1 | v2.1 modules |
| **P1-2** | Memory System 缺失 | P1 | v2.1 modules |
| **P1-3** | Browse Module 缺失 | P1 | v2.1 modules |
| **P1-4** | Web Dashboard 缺失 | P2 | v2.1 modules |

### 1.3 集成与兼容性

| ID | 问题 | 优先级 | 来源 |
|----|------|--------|------|
| **P1-5** | Agent 格式兼容：v2.1 用 markdown，v2 用 Python，ClawTeam 能认哪种？ | P1 | 合并报告 |
| **P1-6** | 安装脚本缺失：v2.1 有 install.sh，v2 没有 | P1 | 合并报告 |
| **P2-1** | Supervisor 层缺失：v2 的 layers 里有 supervisor 定义吗？ | P2 | 合并报告 |
| **P2-2** | 测试覆盖缺失：v2 没有测试，v2.1 也没有 | P2 | 合并报告 |

---

## 二、优先级矩阵

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         优先级矩阵                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   影响 ↓ / 难度 →    简单        中等        复杂                        │
│  ─────────────────────────────────────────────────────────────         │
│   高影响             [P0-1]      [P0-3]      [P0-2]                     │
│   中影响             [P1-6]      [P1-1]      [P1-2]                     │
│   低影响             [P2-2]      [P2-1]      [P1-4]                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

| 优先级 | 问题 | 策略 |
|--------|------|------|
| **P0** | Agent-Engine断链、routing冲突、上下文压缩、文档闭环 | **立即修复** |
| **P1** | 增强模块、格式兼容、安装脚本 | **尽快完成** |
| **P2** | Supervisor层、测试覆盖、Web Dashboard | **计划进行** |

---

## 三、完整 To-Do List

### [P0-必须完成]

```
- [ ] P0-1: Agent-Engine 断链 → 解决方案: 在 Agent 定义中注入 engine 调用指令，让 markdown Agent 能够触发 thinking_injector
- [ ] P0-2: 思维专家-routing 冲突 → 解决方案: 以 thinking_injector 为主，routing.yaml 作为 fallback
- [ ] P0-3: 上下文压缩缺失 → 解决方案: 实现 SessionContextCompressor，参考 v2.1 设计
- [ ] P0-4: 文档闭环缺失 → 解决方案: 统一更新 README.md 和 ARCHITECTURE.md
```

### [P1-建议完成]

```
- [ ] P1-1: Execution Monitor → 解决方案: 从 v2.1 modules 复制 execution_monitor.py
- [ ] P1-2: Memory System → 解决方案: 实现持久化记忆系统，参考 Auto Memory 设计
- [ ] P1-3: Browse Module → 解决方案: 从 v2.1 modules 复制 browse 模块
- [ ] P1-5: Agent 格式兼容 → 解决方案: 使用 agent-converter.py 转换格式
- [ ] P1-6: 安装脚本 → 解决方案: 复制 v2.1 的 install.sh
```

### [P2-可以增强]

```
- [ ] P2-1: Supervisor 层 → 解决方案: 实现三层架构中的 Supervisor 角色
- [ ] P2-2: 测试覆盖 → 解决方案: 补充 E2E 测试
- [ ] P1-4: Web Dashboard → 解决方案: 从 v2.1 modules 复制并适配
```

---

## 四、参照项目清单

| 参照仓库 | 用途 | 集成方式 |
|----------|------|----------|
| **ClawTeam** (`clawteam` CLI) | 多Agent协作底层 | 任务管理、团队创建、Worktree隔离 |
| **everything-claude-code** | Agent性能优化 | 27个专家Agent、114个Skill、Hooks系统 |
| **agency-agents-zh** | 180个专业Agent | 直接复用工程/设计/营销人设 |
| **pua-main** | PUA监督机制 | L1-L4压力升级、三条铁律 |
| **goal-driven** | 目标循环执行 | Master-Agent评估循环 |
| **v2.1/modules/execution_monitor** | Loop检测 | 复制到 v2/modules/ |
| **v2.1/modules/browse** | 网页浏览 | 复制到 v2/modules/ |
| **v2.1/scripts/install.sh** | 安装脚本 | 复制到 v2/scripts/ |
| **v2.1/scripts/agent-converter.py** | 格式转换 | 复制到 v2/scripts/ |

---

## 五、执行计划

### Phase 0 (第1周): PoC验证

- [ ] P0-4: 统一文档闭环（README + ARCHITECTURE）
- [ ] P0-1: 实现 Agent-Engine 断链修复（Agent 定义注入 engine 调用）
- [ ] 验证 v2 引擎可正常触发

### Phase 1 (第2-4周): 核心能力

- [ ] P0-2: 思维专家-routing 冲突解决
- [ ] P0-3: 上下文压缩模块实现
- [ ] P1-5: Agent 格式兼容（agent-converter.py）
- [ ] P1-6: 安装脚本（install.sh）

### Phase 2 (第5-8周): 完整系统

- [ ] P1-1: Execution Monitor 模块
- [ ] P1-2: Memory System 模块
- [ ] P1-3: Browse Module 模块
- [ ] P2-1: Supervisor 层实现

### Phase 3 (第9-12周): 生态扩展

- [ ] P2-2: 测试覆盖（E2E测试）
- [ ] P1-4: Web Dashboard 模块
- [ ] 集成 ClawTeam 完整协作流程
- [ ] 集成 agency-agents-zh 180个专业Agent

---

## 六、技术实现方案

### P0-1: Agent-Engine 断链修复

```python
# 在每个 Agent 定义 markdown 中注入:
---
engine_injection:
  thinking_injector: true
  intent_classifier: true
  max_active_experts: 5
---

# Agent 执行时自动调用:
injector = ThinkingInjector()
context = injector.process(user_input, agent_context)
```

### P0-2: 思维专家-routing 冲突解决

```python
# 主选: thinking_injector
# Fallback: routing.yaml
selected_experts = thinking_injector.select(user_input)
if not selected_experts:
    selected_experts = routing_fallback.select(user_input)
```

### P0-3: 上下文压缩

```python
class SessionContextCompressor:
    def compress(self, context, max_tokens=160000):
        # 按重要性排序
        # 保留关键对话和决策
        # 压缩重复内容
        pass
```

---

**版本历史**:
- v2.0.1 (2026-03-24): 初始版本，整合所有专家分析结果
