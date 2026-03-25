# downstream - 资产库中台

## 直接下游

| 下游Agent/系统 | 关系 | 说明 |
|----------------|------|------|
| gstack Skills | 技能调用 | gstack工程能力 |
| agency Agents | Agent调用 | agency专业能力 |
| baoyu Skills | 创意调用 | baoyu创意能力 |
| 监控中台 | 负载上报 | 资源使用监控 |

## 输出物

| 输出物 | 下游使用方 | 用途 |
|--------|------------|------|
| 资产调度结果 | 调用方Agent | 执行任务 |
| 技能调用指令 | gstack/baoyu | 触发技能 |
| Agent任务分配 | agency | 任务执行 |
| 负载更新 | 监控中台 | 资源监控 |

## 调度报告格式

```yaml
资产调度报告:
  任务类型: {任务类型}
  场景标签: {标签列表}
  调度策略: {策略说明}
  选中资产: {资产ID} ({资产名称})
  备选资产: [{资产ID}, ...]
  当前负载: {当前}/{最大}
  预计等待: {秒数}s
  调度置信度: {分数}
```

## 输出分类

### gstack资产输出

| 输出物 | 格式 | 下游使用 |
|--------|------|----------|
| 代码执行指令 | JSON | gsd-executor |
| 代码审查指令 | JSON | code-reviewer |
| UI设计指令 | JSON | design-ui-designer |
| 架构设计指令 | JSON | engineering-backend-architect |

### agency资产输出

| 输出物 | 格式 | 下游使用 |
|--------|------|----------|
| 运营策略指令 | JSON | 运营Agent |
| 营销方案指令 | JSON | 营销Agent |
| 技术咨询指令 | JSON | 技术Agent |
| 战略规划指令 | JSON | 战略Agent |

### baoyu资产输出

| 输出物 | 格式 | 下游使用 |
|--------|------|----------|
| 图片生成指令 | JSON | baoyu-image-gen |
| 文案创作指令 | JSON | baoyu-post-to-x |
| PPT生成指令 | JSON | baoyu-slide-deck |
| 翻译指令 | JSON | baoyu-translate |

## 下游数据流

```
资产中台调度
    ↓
    ├── gstack → gstack Skills → 工程执行
    ├── agency → agency Agents → 专业执行
    ├── baoyu → baoyu Skills → 创意执行
    └── 监控 → 监控中台 → 负载更新
```
