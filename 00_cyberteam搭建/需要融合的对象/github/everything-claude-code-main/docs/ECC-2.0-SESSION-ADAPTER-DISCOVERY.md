# ECC 2.0 会话适配器发现

## 目的

该文档将 3 月 11 日的 ECC 2.0 控制平面方向转变为
基于编排代码的具体适配器和快照设计
已存在于此存储库中。

## 当前实现的底层

该存储库已经拥有真正的首次通过编排基础：

- `scripts/lib/tmux-worktree-orchestrator.js`
  提供 tmux 窗格以及独立的 git 工作树
-`脚本/orchestrate-worktrees.js`
  是当前会话启动器
- `scripts/lib/orchestration-session.js`
  收集机器可读的会话快照
-`脚本/orchestration-status.js`
  从会话名称或计划文件中导出这些快照
- `命令/会话.md`
  已经从 Claude 的本地商店公开了相邻的会话历史概念
- `scripts/lib/session-adapters/canonical-session.js`
  定义规范的“ecc.session.v1”规范化层
- `scripts/lib/session-adapters/dmux-tmux.js`
  将当前编排快照收集器包装为适配器“dmux-tmux”
- `scripts/lib/session-adapters/claude-history.js`
  将 Claude 本地会话历史规范化为第二个适配器
- `scripts/lib/session-adapters/registry.js`
  从显式目标和目标类型中选择适配器
- `脚本/session-inspect.js`
  通过适配器注册表发出规范的只读会话快照

实际上，ECC 已经可以回答：

- tmux 编排的会话中存在哪些工作人员
- 每个工作人员附加到哪个窗格
- 每个工作人员存在哪些任务、状态和移交文件
- 会话是否处于活动状态以及存在多少个窗格/工作人员
- 最近的克劳德本地会议在同一个规范中是什么样子的
  作为编排会话的快照形状

这足以证明底物。还不足以获得资格
通用 ECC 2.0 控制平面。

## 当前快照实际模型是什么

当前快照模型来自“scripts/lib/orchestration-session.js”
有这些有效字段：```json
{
  "sessionName": "workflow-visual-proof",
  "coordinationDir": ".../.claude/orchestration/workflow-visual-proof",
  "repoRoot": "...",
  "targetType": "plan",
  "sessionActive": true,
  "paneCount": 2,
  "workerCount": 2,
  "workerStates": {
    "running": 1,
    "completed": 1
  },
  "panes": [
    {
      "paneId": "%95",
      "windowIndex": 1,
      "paneIndex": 0,
      "title": "seed-check",
      "currentCommand": "codex",
      "currentPath": "/tmp/worktree",
      "active": false,
      "dead": false,
      "pid": 1234
    }
  ],
  "workers": [
    {
      "workerSlug": "seed-check",
      "workerDir": ".../seed-check",
      "status": {
        "state": "running",
        "updated": "...",
        "branch": "...",
        "worktree": "...",
        "taskFile": "...",
        "handoffFile": "..."
      },
      "task": {
        "objective": "...",
        "seedPaths": ["scripts/orchestrate-worktrees.js"]
      },
      "handoff": {
        "summary": [],
        "validation": [],
        "remainingRisks": []
      },
      "files": {
        "status": ".../status.md",
        "task": ".../task.md",
        "handoff": ".../handoff.md"
      },
      "pane": {
        "paneId": "%95",
        "title": "seed-check"
      }
    }
  ]
}
```这已经是一个有用的操作员有效负载。主要的限制是它是
隐式地与一种执行风格相关：

- tmux 窗格标识
-worker slug 等于窗格标题
- Markdown 协调文件
- 计划文件或会话名称查找规则

## ECC 1.x 和 ECC 2.0 之间的差距

ECC 1.x 目前有两个不同的“会话”表面：

1.克劳德本地会话历史
2.编排运行时/会话快照

这些表面相邻但不统一。

缺少的 ECC 2.0 层是一个与线束无关的会话适配器边界，
可以标准化：

- tmux 协调的工作人员
- 简单的克劳德会议
- 法典工作树会议
- 开放代码会议
- 未来的 GitHub/App 或远程控制会话

如果没有该适配器层，任何未来的操作员 UI 将被迫读取
tmux 特定的细节和 markdown 直接协调。

## 适配器边界

ECC 2.0应该引入规范的会话适配器合约。

建议的最小界面：```ts
type SessionAdapter = {
  id: string;
  canOpen(target: SessionTarget): boolean;
  open(target: SessionTarget): Promise<AdapterHandle>;
};

type AdapterHandle = {
  getSnapshot(): Promise<CanonicalSessionSnapshot>;
  streamEvents?(onEvent: (event: SessionEvent) => void): Promise<() => void>;
  runAction?(action: SessionAction): Promise<ActionResult>;
};
```### 规范快照形状

建议的首次通过规范有效负载：```json
{
  "schemaVersion": "ecc.session.v1",
  "adapterId": "dmux-tmux",
  "session": {
    "id": "workflow-visual-proof",
    "kind": "orchestrated",
    "state": "active",
    "repoRoot": "...",
    "sourceTarget": {
      "type": "plan",
      "value": ".claude/plan/workflow-visual-proof.json"
    }
  },
  "workers": [
    {
      "id": "seed-check",
      "label": "seed-check",
      "state": "running",
      "branch": "...",
      "worktree": "...",
      "runtime": {
        "kind": "tmux-pane",
        "command": "codex",
        "pid": 1234,
        "active": false,
        "dead": false
      },
      "intent": {
        "objective": "...",
        "seedPaths": ["scripts/orchestrate-worktrees.js"]
      },
      "outputs": {
        "summary": [],
        "validation": [],
        "remainingRisks": []
      },
      "artifacts": {
        "statusFile": "...",
        "taskFile": "...",
        "handoffFile": "..."
      }
    }
  ],
  "aggregates": {
    "workerCount": 2,
    "states": {
      "running": 1,
      "completed": 1
    }
  }
}
```这保留了已经存在的有用信号，同时删除了 tmux 特定的信号
控制平面合同的详细信息。

## 第一个支持的适配器

### 1. `dmux-tmux`

包装已经存在的逻辑
`scripts/lib/orchestration-session.js`。

这是最简单的第一个适配器，因为基材已经是真实的。

### 2.`克劳德历史`

标准化数据
`命令/会话.md`
并且现有的会话管理器实用程序已经公开：

- 会话 ID / 别名
- 分支机构
- 工作树
- 项目路径
- 新近度/文件大小/项目计数

这为 ECC 2.0 提供了非编排的基线。

### 3. `codex-worktree`

使用相同的规范形状，但使用 Codex 原生执行元数据进行支持
而不是可用的 tmux 假设。

### 4.`开放代码`

一旦 OpenCode 会话元数据足够稳定，就可以使用相同的适配器边界
正常化。

## 适配器层中应该保留哪些内容

适配器层不应该拥有：

- 合并排序的业务逻辑
- 操作员用户界面布局
- 定价或货币化决策
- 安装配置文件选择
- tmux 生命周期编排本身

它的工作范围更窄：

- 检测会话目标
- 加载标准化快照
- 可选择流式传输运行时事件
- 可选择公开安全操作

## 当前文件布局

适配器层现在位于：```text
scripts/lib/session-adapters/
  canonical-session.js
  dmux-tmux.js
  claude-history.js
  registry.js
scripts/session-inspect.js
tests/lib/session-adapters.test.js
tests/scripts/session-inspect.test.js
```当前的编排快照解析器现在被用作适配器
实施而不是保留唯一的产品合同。

## 立即采取的后续步骤

1. 添加第三个适配器，可能是“codex-worktree”，因此抽象发生了变化
   超越 tmux 和 Claude 历史。
2. 决定规范快照是否需要单独的“state”和“health”
   UI 工作开始之前的字段。
3. 决定事件流是属于 v1 还是保留到 v1 之后
   快照层证明了自己。
4. 仅在适配器注册表之上构建面向操作员的面板，而不是通过
   直接读取编排内部结构。

## 开放问题

1. 工作人员身份应该由工作人员 slug、分支还是稳定的 UUID 来作为密钥？
2. 在规范层我们需要单独的“state”和“health”字段吗？
3.事件流应该成为 v1 的一部分，还是 ECC 2.0 应该仅提供快照
   首先？
4、快照离开本地之前需要编辑多少路径信息
   机器？
5. 适配器注册表是否应该长期存在于该存储库中，或者移至
   一旦接口稳定，最终的 ECC 2.0 控制平面应用程序会出现吗？

## 推荐

将当前 tmux/worktree 实现视为适配器“0”，而不是最终的
产品表面。

通往 ECC 2.0 的最短路径是：

1. 保留当前的编排底层
2. 将其包装在规范的会话适配器合约中
3.添加1个非tmux适配器
4.然后才开始在顶部构建操作面板