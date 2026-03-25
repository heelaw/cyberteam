# 《内容审核 Skill 体系》

版本：v3.1
更新日期：2026-03-24

---

## 1. 定位

为审核校对角色提供自动化审核支持，确保内容质量、规避合规风险、维护品牌调性一致性。

---

## 2. 三个子技能

### 2.1 content-fact-check（事实核查）

- **功能**：数据溯源验证、逻辑漏洞检测、引用准确性检查
- **输出**：问题列表（位置/类型/建议）
- **调用方式**：`/content-review fact-check`

### 2.2 content-brand-audit（品牌调性审核）

- **功能**：语气检查、用词规范检查、竞品描述检查
- **输出**：调性问题列表及修改建议
- **调用方式**：`/content-review brand-audit`

### 2.3 content-compliance-scan（合规风险扫描）

- **功能**：广告法红线检测、平台规则检测、知识产权检测
- **输出**：风险点列表（按 P0/P1/P2 分类）
- **调用方式**：`/content-review compliance-scan`

---

## 3. 调用方式

### 完整审核（一次性执行三种审核）

```
/content-review full <内容文本>
```

### 单独调用

```
/content-review fact-check <内容文本>
/content-review brand-audit <内容文本>
/content-review compliance-scan <内容文本>
```

### 指定平台规则

```
/content-review compliance-scan --platform xhs <内容文本>
/content-review compliance-scan --platform wechat <内容文本>
/content-review compliance-scan --platform weibo <内容文本>
```

---

## 4. 审核优先级

| 优先级 | 类型 | 说明 |
|--------|------|------|
| P0 | 必须修复 | 严重违规，必须立即修改 |
| P1 | 应该修复 | 合规风险，建议修改 |
| P2 | 建议修复 | 优化项，可选择性修改 |

---

## 5. 支持平台

- **小红书 (xhs)**: 小红书社区规范
- **微信 (wechat)**: 微信公众号规范
- **微博 (weibo)**: 微博社区规范
- **通用 (general)**: 通用广告法及基本规范

---

**文档维护**: CyberTeam v4 架构组
**版本**: v3.1
**更新日期**: 2026-03-24
