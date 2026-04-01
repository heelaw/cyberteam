# CyberTeam 数据库设计草案

## 1. 设计原则

- 本地优先
- SQLite 存储
- 结构清晰
- 支持版本与审核
- 支持聊天与组织
- 为后续市场、模板、PUA 增强预留扩展字段

## 2. 核心表

### companies
- id
- name
- avatar
- description
- theme
- version
- createdAt
- updatedAt

### departments
- id
- companyId
- parentId
- name
- type
- color
- description
- createdAt
- updatedAt

### departments
- id
- companyId
- parentId
- name
- type
- color
- description
- createdAt
- updatedAt

### agents
- id
- companyId
- departmentId
- name
- title
- avatar
- bio
- personality
- status
- isCEO
- isActive
- createdAt
- updatedAt

### skills
- id
- name
- category
- description
- prompt
- tools
- version
- createdAt
- updatedAt

### agent_skills
- agentId
- skillId

### conversations
- id
- companyId
- type
- title
- departmentId
- createdAt
- updatedAt

### conversation_participants
- conversationId
- agentId
- role

### messages
- id
- conversationId
- senderId
- senderType
- content
- mentions
- attachments
- status
- createdAt

### playground_documents
- id
- sourceConversationId
- title
- type
- content
- reviewStatus
- version
- createdAt
- updatedAt

### review_records
- id
- documentId
- reviewerId
- decision
- comments
- createdAt

### templates
- id
- type
- name
- description
- payload
- createdAt
- updatedAt

## 3. 关系说明

- 公司拥有多个部门
- 部门拥有多个 Agent
- Agent 可绑定多个 Skill
- 会话可绑定多个参与者
- 消息属于会话
- Playground 文档来源于会话
- 审核记录属于文档

## 4. 后续扩展

- 任务表
- 事件日志表
- 消息索引表
- 模板版本表
- 用户偏好表
