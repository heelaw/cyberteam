# interfaces - 运营总监

## 核心原则

**所有Agent决策前必须读取项目资料库。所有Agent产出必须存入项目目录。**

```
┌─────────────────────────────────────────────────────────────────┐
│                     项目启动流程                                  │
├─────────────────────────────────────────────────────────────────┤
│  1. 创建项目目录：projects/{project_id}/                         │
│  2. 读取业务数据：context/business_context.md                    │
│  3. 启动专家团队 → 协作产生方案/会议记录                         │
│  4. 产出存入：decisions/ + meetings/                            │
│  5. 归档时沉淀到：shared/knowledge_base/                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 一、项目资料库路径规范

### 1.1 全局路径

```
Output/cyberteam-v4/
├── projects/                      # 所有项目工作目录
│   ├── {project_id}/             # 每个对话/任务 = 一个项目
│   │   ├── metadata.yaml         # 项目元数据
│   │   ├── context/              # 输入：业务数据
│   │   │   ├── business_context.md   # 业务背景（必读）
│   │   │   ├── data_*.md         # 数据文件
│   │   │   ├── user_persona.md   # 用户画像
│   │   │   └── input_files.md    # 输入文件清单
│   │   ├── decisions/            # 输出：决策与方案
│   │   │   ├── diagnosis.md       # 问题诊断
│   │   │   ├── options.md         # 方案选项A/B/C
│   │   │   ├── decision.md        # 最终决策
│   │   │   └── action_plan.md     # 执行计划
│   │   ├── meetings/              # 输出：会议记录
│   │   │   └── meeting_*.md       # 每次会议记录
│   │   └── references/           # 参考资料
│   └── _template/                # 项目模板
│
├── shared/                       # 共享资源库
│   ├── business_data/            # 标准业务数据模板
│   ├── templates/                # 文档模板
│   └── knowledge_base/           # 知识沉淀
```

### 1.2 Agent读取路径优先级

```
优先级1：projects/{current_project}/context/     # 当前项目业务数据
优先级2：shared/business_data/                   # 标准业务数据
优先级3：shared/templates/                      # 文档模板
优先级4：shared/knowledge_base/                 # 历史知识沉淀
```

---

## 二、输入规范 (Input)

### 2.1 必读文件清单

| 文件 | 路径 | 说明 | 读取时机 |
|------|------|------|----------|
| 业务背景 | `{project}/context/business_context.md` | 产品/用户/数据/痛点 | 每次决策前 |
| 项目元数据 | `{project}/metadata.yaml` | 项目类型/阶段/参与者 | 项目启动时 |
| 历史决策 | `{project}/decisions/` | 同项目历史决策参考 | 按需 |

### 2.2 业务数据标准格式

```yaml
# context/business_context.md 必须包含以下字段：

## 基础信息
- 产品名称：
- 核心功能：
- 目标用户：
- 当前阶段：探索期/快速增长期/成熟期/衰退期/危机期

## 核心指标（必须量化）
- DAU：
- MAU：
- 新增/日：
- 留存率(次日/7日/30日)：
- 转化率：
- 客单价：
- LTV：
- CAC：
- LTV/CAC：

## 当前痛点（1-3个）
1. 痛点：[描述]
   影响：[量化]
2. ...
```

### 2.3 外部输入（跨Agent）

| 来源 | 内容 | 格式 |
|------|------|------|
| 增长总监 | 战略目标/KPI/预算 | metadata.yaml 或 business_context.md |
| 数据团队 | 分析报告/指标 | context/data_*.md |
| 营销总监 | 渠道反馈/用户画像 | context/channel_*.md |

---

## 三、输出规范 (Output)

### 3.1 输出文件必须存放位置

```
{project}/decisions/          # 决策类产出
{project}/meetings/           # 会议记录类产出
```

### 3.2 决策产出模板

| 产出 | 模板路径 | 必填内容 |
|------|----------|----------|
| 问题诊断 | `{project}/decisions/diagnosis.md` | 问题/根因/影响 |
| 方案选项 | `{project}/decisions/options.md` | A/B/C方案及推荐 |
| 执行计划 | `{project}/decisions/action_plan.md` | 负责人/时间/指标 |

### 3.3 会议记录模板

| 产出 | 模板路径 | 必填内容 |
|------|----------|----------|
| 专家讨论 | `{project}/meetings/meeting_*.md` | 议题/结论/待办 |
| 方案评审 | `{project}/meetings/meeting_*.md` | 方案/意见/决策 |
| 跨部门协调 | `{project}/meetings/meeting_*.md` | 议题/决议/协作事项 |

### 3.4 禁止日报/周报形式

**替代方案**：
- 日常进度 → `{project}/meetings/conversation_log.md`（对话记录）
- 周期性汇报 → `{project}/decisions/status_update.md`（状态更新）
- 正式报告 → `{project}/decisions/decision.md`（决策文档）

---

## 四、协作接口

### 4.1 向下调度（给专家Agent）

```json
{
  "type": "task_dispatch",
  "project_id": "proj_20260325_001",
  "task": "用户分层方案设计",
  "input_files": [
    "context/business_context.md",
    "context/user_persona.md"
  ],
  "expected_output": "decisions/user_stratification.md",
  "deadline": "2026-03-26T18:00:00Z",
  "callback_meeting": "mtg_20260326_001"
}
```

### 4.2 专家回报（专家Agent→运营总监）

```json
{
  "type": "task_completion",
  "project_id": "proj_20260325_001",
  "agent": "用户运营专家",
  "task": "用户分层方案设计",
  "output_file": "decisions/user_stratification.md",
  "summary": "完成四层用户分层，核心发现：...",
  "next_steps": ["需要产品部提供功能支持", "建议增加AB测试"]
}
```

### 4.3 横向协作（与营销总监）

```json
{
  "type": "collaboration_request",
  "project_id": "proj_20260325_001",
  "from": "运营总监",
  "to": "营销总监",
  "topic": "变现方案评审",
  "meeting_id": "mtg_20260326_002",
  "materials": ["decisions/options.md"],
  "expected_decision": "选择变现方案A/B/C"
}
```

### 4.4 接力区接口（用户交接）

```json
{
  "type": "user_handoff",
  "trigger": "first_key_action_completed",
  "user_id": "xxx",
  "action": "first_purchase",
  "timestamp": "2026-03-25T10:00:00Z",
  "user_profile": {
    "acquisition_channel": "douyin",
    "first_session_duration": 120,
    "features_used": ["search", "cart"]
  }
}
```

---

## 五、协作节奏

| 协作方 | 节奏 | 形式 | 产出位置 |
|--------|------|------|----------|
| 增长总监 | 按项目 | 决策会 | `{project}/decisions/` |
| 各运营专家 | 按任务 | 专家讨论 | `{project}/meetings/` |
| 营销总监 | 按项目 | 方案评审 | `{project}/decisions/` |
| 产品部 | 按需求 | 需求评审 | `{project}/meetings/` |
| 数据团队 | 按需求 | 数据分析 | `{project}/context/` |

---

## 六、项目生命周期

```
┌─────────────────────────────────────────────────────────────────┐
│                      项目启动                                     │
│  1. 创建项目目录 cp -r projects/_template projects/{project_id}  │
│  2. 填写 metadata.yaml                                          │
│  3. 引导用户提供 business_context.md                            │
│  4. Agent读取后开始工作                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      项目执行                                     │
│  1. 每次专家讨论 → 存入 meetings/meeting_*.md                   │
│  2. 每次决策产出 → 存入 decisions/*.md                           │
│  3. 对话记录 → 存入 meetings/conversation_log.md                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      项目归档                                     │
│  1. 重要决策/方案 → 复制到 shared/knowledge_base/               │
│  2. 更新 metadata.yaml status = archived                         │
│  3. 保留原始文件在 projects/{project_id}/                       │
└─────────────────────────────────────────────────────────────────┘
```

---

*版本: v3.0 | 更新日期: 2026-03-25*

*核心更新：*
- *v3.0：新增项目资料库路径规范、输入/输出标准化、会议记录替代日报周报*
