# CyberTeam V4 多 Agent 协作工作流

## 标准协作流程

CyberTeam V4 采用 **CEO→COO→专家** 的标准协作流程，确保每个任务都经过充分的讨论和审核。

### 完整流程概览

```
┌─────────────────────────────────────────────────────────────┐
│                     1. CEO→COO 战略对齐                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • 5W1H1Y 问题拆解                                   │    │
│  │ • 明确北极星指标                                     │    │
│  │ • 确认约束条件                                       │    │
│  │ • 资源分配                                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                     2. COO→专家 策略讨论                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • 卖点方向讨论                                       │    │
│  │ • 用户场景分析                                       │    │
│  │ • 渠道策略分工                                       │    │
│  │ • 转化路径设计                                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                     3. 专家内部分歧讨论                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • 风险预案制定                                       │    │
│  │ • 保底措施三层                                       │    │
│  │ • 预警机制设计                                       │    │
│  │ • 效果预测（保守/正常/乐观）                         │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                     4. COO→CEO 汇报                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • 策略摘要                                           │    │
│  │ • 预期效果                                           │    │
│  │ • 风险预案                                           │    │
│  │ • 请求授权                                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                     5. CEO 审核批准                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • 审核策略                                           │    │
│  │ • 修改/打回/批准                                     │    │
│  │ • 明确授权范围                                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                     6. 执行阶段                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • 设计联动                                           │    │
│  │ • 文案产出                                           │    │
│  │ • 投放执行                                           │    │
│  │ • 效果监控                                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 工作流示例

### 示例：制定清明节营销方案

#### Step 1: 创建团队

```bash
# CEO 创建专项团队
cyberteam team spawn-team ehomewei-qingming -d "清明节全渠道拉新方案"

# 创建核心任务
cyberteam task create ehomewei-qingming "CEO-COO战略对齐" -o ceo --priority high
cyberteam task create ehomewei-qingming "策略讨论" -o coo --priority high
cyberteam task create ehomewei-qingming "风险预案" -o coo --priority high
```

#### Step 2: Spawn 专家 Agents

```bash
# Spawn 各渠道专家
cyberteam spawn --team ehomewei-qingming --agent-name douyin-strategist --task "制定抖音渠道拉新策略"
cyberteam spawn --team ehomewei-qingming --agent-name xhs-strategist --task "制定小红书种草策略"
cyberteam spawn --team ehomewei-qingming --agent-name wechat-strategist --task "制定微信私域策略"
cyberteam spawn --team ehomewei-qingming --agent-name ecommerce-strategist --task "制定电商平台策略"
cyberteam spawn --team ehomewei-qingming --agent-name growth-expert --task "制定增长和ROI策略"

# 标记 CEO 任务进行中
cyberteam task update ehomewei-qingming <ceo-task-id> --status in_progress
```

#### Step 3: CEO→COO 战略对齐

```bash
# CEO 发送任务给 COO
cyberteam inbox send ehomewei-qingming coo "任务：为 ehomewei 便携屏制定清明节全渠道拉新方案，目标618前销量提升5%。请先进行战略对齐。"

# COO 接收并处理
cyberteam inbox receive ehomewei-qingming

# COO 识别到需要获取更多信息，向 CEO 请求确认
cyberteam inbox send ehomewei-qingming ceo "战略对齐清单：
1. 北极星指标：销量提升5%，对应绝对GMV是多少？
2. 约束条件：预算范围？渠道限制？
3. 风险偏好：保守/平衡/激进？
4. 资源配置：各渠道预算分配？
请确认以上信息。"
```

#### Step 4: CEO 响应 COO

```bash
# CEO 响应（通过 MailboxManager 或直接）
# 假设用户提供了信息：
# - 月销量：2000台，5%增量 = 100台
# - 预算：50万
# - 主渠道：抖音+小红书

cyberteam inbox send ehomewei-qingming coo "战略对齐确认：
1. 北极星指标：销量+100台，GMV约85万
2. 预算：50万
3. 主渠道：抖音（40%）、小红书（30%）、微信（20%）、电商（10%）
4. 时间窗口：4月1日-5月31日
5. 风险偏好：平衡型

请开始策略讨论，组织各专家讨论。"
```

#### Step 5: COO 组织策略讨论

```bash
# COO 发送策略讨论任务给各专家
cyberteam inbox send ehomewei-qingming douyin-strategist "策略讨论议题：
1. 卖点方向：便携屏的哪些卖点最吸引目标用户？
2. 用户场景：用户在什么场景下会想到买便携屏？
3. 渠道分工：清明节期间抖音重点做什么内容？
4. 转化策略：如何把流量转化为购买？

请给出你的策略建议。"

cyberteam inbox send ehomewei-qingming xhs-strategist "策略讨论议题：
1. 卖点方向：便携屏在小红书适合什么样的种草内容？
2. 用户场景：什么场景下用户会主动搜索便携屏？
3. 渠道分工：小红书在整体策略中的定位是什么？
4. 转化策略：如何通过种草带动转化？

请给出你的策略建议。"

# 其他专家类似...
```

#### Step 6: 专家回复 COO

```bash
# 假设 douyin-strategist 回复：
# （在实际运行中，这是通过 Agent 消息机制实现的）

# douyin-strategist inbox:
# "抖音策略建议：
# 1. 卖点：便携性、多屏办公、电竞副屏
# 2. 场景：办公场景（笔记本副屏）、游戏场景（switch外接）
# 3. 内容：场景化短视频、对比测评
# 4. 转化：直播间+短视频挂车"

# COO 收集所有专家回复后，识别分歧点并组织深度讨论
```

#### Step 7: COO→CEO 汇报

```bash
# COO 汇总所有专家意见，向 CEO 汇报
cyberteam inbox send ehomewei-qingming ceo "COO汇报：

【策略摘要】
- 主打卖点：便携+多场景（办公/游戏）
- 渠道分工：
  * 抖音（40%/20万）：短视频+直播带货
  * 小红书（30%/15万）：场景种草+口碑
  * 微信（20%/10万）：私域沉淀+裂变
  * 电商（10%/5万）：站内流量+大促坑位

【预期效果】
- 保守：GMV 50万，ROI 2.5x
- 正常：GMV 85万，ROI 4.25x
- 乐观：GMV 140万，ROI 7x

【风险预案】
- 主要风险：清明节流量分散、竞品抢先
- 保底措施：加大信息流投放、私域限时优惠

【需要授权】
- 追加预算权限（是否可以在效果好的情况下追加20%）？

请 CEO 审核批准。"
```

#### Step 8: CEO 审核批准

```bash
# CEO 审核并响应
cyberteam inbox send ehomewei-qingming coo "CEO审核：

批准策略方案。

授权范围：
1. 预算：50万，按方案分配
2. 追加预算：效果好的情况下，可追加不超过10%（5万）
3. 时间：4月1日启动，5月31日前完成主要投放

请开始执行，定期汇报进展。"
```

#### Step 9: 执行阶段

```bash
# COO 通知各专家开始执行
cyberteam inbox broadcast ehomewei-qingming "CEO已批准，开始执行。请各专家产出具体执行方案。"

# 专家产出文案和执行计划
# ...

# COO 汇总执行成果，向 CEO 汇报
cyberteam inbox send ehomewei-qingming ceo "执行进展汇报：
1. 抖音：3条场景短视频已产出，1场直播已完成
2. 小红书：5篇种草笔记已发布
3. 微信：私域社群已建立
4. 电商：618预热页面已上线

当前GMV：XX万，完成度XX%。"
```

## 消息模板

### CEO→COO 消息模板

```
【任务】{任务名称}
【背景】{业务背景}
【约束】{预算/时间/渠道限制}
【目标】{北极星指标}
【风险偏好】{保守/平衡/激进}
【请确认】{需要COO确认的问题}
```

### COO→CEO 消息模板

```
【策略摘要】
- 卖点：{卖点方向}
- 渠道：{渠道分工}
- 用户：{目标用户}
- 转化：{转化路径}

【预期效果】
- 保守：{GMV/ROI}
- 正常：{GMV/ROI}
- 乐观：{GMV/ROI}

【风险预案】
- 主要风险：{风险列表}
- 保底措施：{保底方案}

【需要授权】{需要CEO拍板的事项}
```

### 专家策略回复模板

```
【专家】{专家名称}
【议题】{讨论的议题}
【分析】{详细分析}
【建议】{具体建议}
【支持】{需要的资源/支持}
```

## 常见问题

### Q: 专家没有自动回复消息怎么办？

A: tmux agents 需要主动检查 inbox。使用以下方式唤醒：

```bash
# 直接发送消息
cyberteam inbox send <team> <agent> <message>

# 或使用 broadcast
cyberteam inbox broadcast <team> <message>

# 检查 agents 是否在工作
cyberteam board attach <team>
```

### Q: 如何处理分歧？

A: COO 应该识别分歧点，组织专题讨论：

```bash
# COO 识别分歧后，发送专题讨论邀请
cyberteam inbox send <team> <agent1> "请就{分歧点}发表你的观点"
cyberteam inbox send <team> <agent2> "请就{分歧点}发表你的观点"

# 收集后汇总给 CEO
```

### Q: 任务卡住了怎么办？

A: 检查任务状态和 agents 状态：

```bash
# 查看任务
cyberteam task list <team>

# 查看团队状态
cyberteam board show <team>

# 附加到 tmux 会话
cyberteam board attach <team>
```

## Worker Loop Protocol

Agents 应该遵循以下循环协议：

```bash
# 1. 检查分配给自己的任务
clawteam task list <team> --owner <agent>

# 2. 完成工作后，检查 inbox 是否有新指令
clawteam inbox receive <team>

# 3. 如果空闲，通知 leader
clawteam lifecycle idle <team>

# 重复直到被明确关闭
```

## 优雅关闭

```bash
# CEO 请求关闭
cyberteam lifecycle request-shutdown <team> <agent>

# Agent 响应
cyberteam lifecycle approve-shutdown <team> <agent>

# 或者强制关闭
cyberteam team cleanup <team>
```
