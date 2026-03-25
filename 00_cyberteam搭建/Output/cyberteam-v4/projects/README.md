# projects - 项目工作目录

> 每个对话/任务 = 一个项目。所有Agent产出必须集中存放。

---

## 目录结构

```
projects/
├── _template/               # 项目模板（新项目从此复制）
│   ├── metadata.yaml        # 项目元数据模板
│   ├── context/             # 输入模板
│   │   └── business_context.md
│   ├── decisions/           # 决策产出模板
│   │   └── options.md
│   └── meetings/            # 会议记录模板
│       └── meeting_template.md
│
└── {project_id}/           # 具体项目（每次对话创建）
    ├── metadata.yaml        # 项目信息
    ├── context/             # 输入：业务数据
    ├── decisions/           # 输出：决策文档
    └── meetings/            # 输出：会议记录
```

---

## 使用流程

### 1. 创建新项目

```bash
cp -r projects/_template projects/{project_id}
```

### 2. 初始化项目元数据

编辑 `projects/{project_id}/metadata.yaml`：
- project_id: proj_YYYYMMDD_XXX
- project_name: 项目名称
- project_type: 类型
- participants: 参与Agent

### 3. 引导用户提供业务数据

使用模板 `context/business_context.md` 引导用户提供：
- 产品信息
- 当前业务数据
- 痛点问题
- 约束条件

### 4. Agent读取后开始工作

Agent必须读取以下文件后才开始决策：
- `metadata.yaml`
- `context/business_context.md`

### 5. 产出存入规范位置

| 产出类型 | 存入位置 |
|----------|----------|
| 问题诊断 | `decisions/diagnosis.md` |
| 方案选项 | `decisions/options.md` |
| 最终决策 | `decisions/decision.md` |
| 执行计划 | `decisions/action_plan.md` |
| 专家讨论 | `meetings/meeting_*.md` |
| 对话记录 | `meetings/conversation_log.md` |

### 6. 项目归档

重要决策和方案 → 复制到 `shared/knowledge_base/`

---

## 项目命名规范

```
proj_{日期}_{序号}
示例：proj_20260325_001, proj_20260325_002
```

---

## 类型分类

| 类型 | 说明 | 示例 |
|------|------|------|
| case_analysis | 案例分析 | "在下辉子账号分析" |
| strategy | 策略制定 | "Q3增长策略" |
| crisis | 危机处理 | "重大事故处理" |
| routine | 常规运营 | "日常运营优化" |
| review | 复盘总结 | "618大促复盘" |
