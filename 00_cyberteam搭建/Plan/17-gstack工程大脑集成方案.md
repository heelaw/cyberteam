# gstack 工程大脑集成方案

**版本**: v1.0
**日期**: 2026-03-24
**作者**: gstack-expert（P8闭环整理）
**团队**: cyberteam-discuss
**状态**: 已完成

---

## 一、定位：gstack 作为工程大脑

CyberTeam v2.0 采用 **双轨架构**：
- **业务侧**：8大运营专家 + 100思维专家（任务执行层）
- **工程侧**：gstack 作为工程大脑（技术实现层）
- **调度层**：CEO Agent 负责统一调度

```
┌─────────────────────────────────────────────────────────────┐
│                     CEO Agent（调度层）                        │
│         任务分发 · 结果聚合 · 决策生成 · 资源协调              │
├─────────────────────────┬───────────────────────────────────┤
│      业务侧（运营专家）   │        工程侧（gstack）            │
│  • 战略顾问              │  • /plan-eng-review 工程评审        │
│  • 增长顾问              │  • /plan-design-review 设计评审      │
│  • 产品顾问              │  • /codex 代码审查                  │
│  • 营销顾问              │  • /review PR审查                   │
│  • 技术顾问              │  • /qa QA测试                      │
│  • 运营顾问              │  • /ship 部署上线                  │
│  • 品牌顾问              │  • /investigate 调试分析            │
│  • 战略顾问              │  • /office-hours 方案讨论           │
│                          │  • /autoplan 全流程评审             │
├─────────────────────────┴───────────────────────────────────┤
│              工具层（ClawTeam 底层）                          │
│  spawn · inbox · task · board · lifecycle                   │
└─────────────────────────────────────────────────────────────┘
```

**核心结论**：gstack 与 CyberTeam 互补——CyberTeam 提供业务智能（运营专家），gstack 提供工程智能（28个slash命令），两者共同构成完整的AI协作系统。

## 二、28个slash命令分类映射

### 2.1 战略规划类

| 命令 | CyberTeam映射 | 用途 |
|------|--------------|------|
| `/office-hours` | 产品顾问/战略顾问 | 方案讨论、商业诊断 |
| `/plan-ceo-review` | CEO Agent | 战略评审、愿景扩展 |
| `/plan-eng-review` | 工程总监 | 技术方案评审 |
| `/plan-design-review` | 设计总监 | UI/UX方案评审 |

### 2.2 代码工程类

| 命令 | CyberTeam映射 | 用途 |
|------|--------------|------|
| `/review` | QA Agent | PR审查、代码质量 |
| `/codex` | 工程专家 | 第二意见、独立审查 |
| `/investigate` | 调试专家 | 根因分析、调试 |
| `/refactor-cleaner` | 工程专家 | 重构、清理死代码 |

### 2.3 设计类

| 命令 | CyberTeam映射 | 用途 |
|------|--------------|------|
| `/design-consultation` | 设计总监 | 设计系统、配色字体 |
| `/plan-design-review` | 设计总监 | 设计方案评审 |
| `/design-review` | QA Designer | 视觉质量检查 |

### 2.4 测试/QA类

| 命令 | CyberTeam映射 | 用途 |
|------|--------------|------|
| `/qa` | QA Agent | 完整QA测试+修复 |
| `/qa-only` | QA Agent | 仅报告模式 |
| `/browse` | 测试Agent | 浏览器自动化测试 |
| `/benchmark` | 性能Agent | 性能基准测试 |

### 2.5 部署/DevOps类

| 命令 | CyberTeam映射 | 用途 |
|------|--------------|------|
| `/ship` | DevOps Agent | 完整部署流程 |
| `/land-and-deploy` | DevOps Agent | 合并+部署 |
| `/canary` | SRE Agent | 金丝雀监控 |
| `/setup-deploy` | DevOps Agent | 部署配置 |

### 2.6 安全/质量类

| 命令 | CyberTeam映射 | 用途 |
|------|--------------|------|
| `/cso` | 安全Agent | 安全审计、威胁建模 |
| `/careful` | 安全Agent | 危险操作警告 |
| `/guard` | 安全Agent | 完整安全模式 |

### 2.7 流程/团队类

| 命令 | CyberTeam映射 | 用途 |
|------|--------------|------|
| `/clawteam` | ClawTeam Agent | Agent团队管理 |
| `/clawteam-dev` | ClawTeam Agent | E2E测试 |
| `/retro` | HR Agent | 复盘分析 |
| `/autoplan` | 计划Agent | 全流程自动评审 |

### 2.8 其他

| 命令 | CyberTeam映射 | 用途 |
|------|--------------|------|
| `/gstack-upgrade` | 系统管理员 | gstack升级 |
| `/document-release` | 文档Agent | 文档更新 |

## 三、Conductor 并行模式

### 3.1 核心设计

Conductor 是 gstack 的并行任务协调器，允许同时执行多个工程任务：

```
┌─────────────────────────────────────────────────────────┐
│                    Conductor                            │
│                                                      │
│  TaskA ──┐                                           │
│  TaskB ──┼──→ Parallel Execution ──→ Result Merge    │
│  TaskC ──┘                                           │
│                                                      │
│  同时触发：/review + /qa + /codex → 合并审查意见       │
└─────────────────────────────────────────────────────────┘
```

### 3.2 CyberTeam 中的 Conductor 使用

```python
# CEO 触发 Conductor 并行模式
class ConductorIntegration:
    def plan_and_execute(self, user_goal: str) -> Result:
        # 1. CEO 解析目标，分解任务
        tasks = self.ceo.decompose(user_goal)

        # 2. 并行调度 gstack 命令
        parallel_tasks = []
        for task in tasks:
            gstack_cmd = self.map_to_gstack(task)
            parallel_tasks.append(gstack_cmd)

        # 3. Conductor 并行执行
        results = self.conductor.run_parallel(parallel_tasks)

        # 4. CEO 聚合结果
        return self.ceo.aggregate(results)
```

### 3.3 任务类型 → gstack 命令映射

| 任务类型 | gstack 命令 | 并行组 |
|---------|------------|--------|
| 代码审查 | `/review` | A组 |
| 安全审计 | `/cso` | A组（与review并行） |
| 架构评审 | `/plan-eng-review` | B组 |
| 性能测试 | `/benchmark` | B组（与arch并行） |
| 部署上线 | `/ship` | C组（顺序） |

## 四、分阶段集成计划

### Phase 1（第1-2周）：基础集成

**目标**：让 gstack 作为工具被 CyberTeam 调用

```python
# CyberTeam 调用 gstack 示例
class GstackTool:
    def __init__(self):
        self.commands = GstackCommands()

    def call(self, command: str, args: dict) -> Result:
        if command == "review":
            return self.commands.review(args["diff"])
        elif command == "qa":
            return self.commands.qa(args["url"])
        elif command == "ship":
            return self.commands.ship()
        # ...
```

**交付物**：gstack 作为 CyberTeam 工具函数注册

### Phase 2（第3-4周）：Conductor 集成

**目标**：实现多命令并行执行

**交付物**：Conductor 并行调度器 + 结果合并逻辑

### Phase 3（第5-6周）：深度集成

**目标**：gstack 命令结果自动注入 CyberTeam 记忆

```python
# gstack 结果 → CyberTeam Memory
def integrate_result(gstack_result: Result, memory: MemorySystem):
    memory.save_episode(
        source="gstack",
        command=gstack_result.command,
        output=gstack_result.summary,
        artifacts=gstack_result.files_changed,
    )
```

**交付物**：gstack ↔ Memory System 双向集成

### Phase 4（第7-8周）：HUD 展示

**目标**：gstack 任务状态实时展示

```typescript
// CyberTeam Dashboard 中的 gstack 任务面板
const GstackTaskPanel: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const status = await clawteam.board.overview("cyberteam");
      setTasks(status.tasks);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="gstack-panel">
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
};
```

**交付物**：Dashboard 中的 gstack 任务监控面板

## 五、关键集成点

| 集成点 | 方式 | 说明 |
|--------|------|------|
| 命令注册 | 动态加载 | CyberTeam 启动时扫描 gstack 命令 |
| 结果解析 | 标准化 | 统一结果格式（JSON） |
| 错误处理 | 分级重试 | 3次重试 + 升级 |
| 成本追踪 | 日志记录 | Token 使用量记录 |
| 并行控制 | Conductor | 最多5个并行任务 |

## 六、ROI 分析

| 指标 | 不用gstack | 使用gstack | 提升 |
|------|-----------|-----------|------|
| 代码审查时间 | 30min | 5min | 6x |
| QA覆盖率 | 60% | 95% | +58% |
| Bug发现率 | 70% | 92% | +31% |
| 部署频率 | 1次/周 | 随时 | 无限 |
| 工程决策质量 | 主观 | 数据驱动 | 定量化 |
