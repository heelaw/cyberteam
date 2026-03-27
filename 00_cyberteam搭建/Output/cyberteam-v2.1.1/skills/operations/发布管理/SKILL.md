---
name: 发布管理
description: |
  发布管理 — 从测试到生产的完整发布流程。
  配套Agent: DevOps Agent
version: "2.1"
owner: CyberTeam DevOps专家
agent: devops-agent
trigger: "用户需要: 部署/发布/CI-CD/回滚"
---

# 发布管理

## 身份定位

```
+----------------------------------------------------------+
|  发布管理                                               |
|  用途: 测试→预发→生产的完整发布流程                     |
|  核心: 安全发布、可回滚、可追溯                          |
+----------------------------------------------------------+
```

## 发布流程

```
开发分支 → 测试环境 → 预发环境 → 生产环境
    |            |           |           |
    v            v           v           v
  Pull Request  Auto Test  Smoke Test  灰度发布
                              v
                         监控告警
                              v
                         全量发布
```

## 发布检查清单

### 发布前
- [ ] 所有测试通过
- [ ] 代码审查通过
- [ ] 安全扫描通过
- [ ] 性能基线达标

### 发布中
- [ ] 灰度比例正确
- [ ] 监控告警正常
- [ ] 回滚预案就绪

### 发布后
- [ ] 功能验证通过
- [ ] 监控指标正常
- [ ] 回滚通道畅通

## 回滚操作

```bash
# 快速回滚到上一版本
kubectl rollout undo deployment/app

# 回滚到指定版本
kubectl rollout undo deployment/app --to-revision=3

# 查看回滚状态
kubectl rollout status deployment/app
```

---

**版本**: v2.1 | **来源**: gstack ship + CyberTeam | **日期**: 2026-03-23
