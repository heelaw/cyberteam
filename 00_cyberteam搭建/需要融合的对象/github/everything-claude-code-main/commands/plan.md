# 计划命令

此命令会在编写任何代码之前调用 **planner** 代理来创建全面的实施计划。

## 该命令的作用

1. **重申要求** - 明确需要构建什么
2. **识别风险** - 暴露潜在问题和阻碍因素
3. **创建步骤计划** - 将实施分解为阶段
4. **等待确认** - 在继续之前必须获得用户批准

## 何时使用

在以下情况下使用“/plan”：
- 开始一项新功能
- 进行重大的架构更改
- 致力于复杂的重构
- 多个文件/组件将受到影响
- 要求不明确或不明确

## 它是如何工作的

规划代理人将：

1. **分析请求**并以明确的措辞重述要求
2. **分为阶段**，并采取具体、可操作的步骤
3. **识别组件之间的依赖关系**
4. **评估风险**和潜在阻碍因素
5. **估计复杂性**（高/中/低）
6. **提出计划**并等待您的明确确认

## 用法示例```
User: /plan I need to add real-time notifications when markets resolve

Agent (planner):
# Implementation Plan: Real-Time Market Resolution Notifications

## Requirements Restatement
- Send notifications to users when markets they're watching resolve
- Support multiple notification channels (in-app, email, webhook)
- Ensure notifications are delivered reliably
- Include market outcome and user's position result

## Implementation Phases

### Phase 1: Database Schema
- Add notifications table with columns: id, user_id, market_id, type, status, created_at
- Add user_notification_preferences table for channel preferences
- Create indexes on user_id and market_id for performance

### Phase 2: Notification Service
- Create notification service in lib/notifications.ts
- Implement notification queue using BullMQ/Redis
- Add retry logic for failed deliveries
- Create notification templates

### Phase 3: Integration Points
- Hook into market resolution logic (when status changes to "resolved")
- Query all users with positions in market
- Enqueue notifications for each user

### Phase 4: Frontend Components
- Create NotificationBell component in header
- Add NotificationList modal
- Implement real-time updates via Supabase subscriptions
- Add notification preferences page

## Dependencies
- Redis (for queue)
- Email service (SendGrid/Resend)
- Supabase real-time subscriptions

## Risks
- HIGH: Email deliverability (SPF/DKIM required)
- MEDIUM: Performance with 1000+ users per market
- MEDIUM: Notification spam if markets resolve frequently
- LOW: Real-time subscription overhead

## Estimated Complexity: MEDIUM
- Backend: 4-6 hours
- Frontend: 3-4 hours
- Testing: 2-3 hours
- Total: 9-13 hours

**WAITING FOR CONFIRMATION**: Proceed with this plan? (yes/no/modify)
```## 重要提示

**关键**：规划代理将**不会**编写任何代码，直到您使用“是”或“继续”或类似的肯定响应明确确认计划。

如果您想要更改，请回复：
- “修改：[您的更改]”
- “不同的方法：[替代]”
- “跳过第 2 阶段并先执行第 3 阶段”

## 与其他命令集成

规划后：
- 使用`/tdd`来实现测试驱动开发
- 如果发生构建错误，请使用“/build-fix”
- 使用“/code-review”来审查已完成的实施

## 相关代理

该命令调用 ECC 提供的“planner”代理。

对于手动安装，源文件位于：
`代理/planner.md`