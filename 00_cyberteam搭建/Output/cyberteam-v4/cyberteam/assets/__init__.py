"""
CyberTeam Assets Module - 资产库中台

## 基本信息

| 属性 | 内容 |
|------|------|
| **中台名称** | 资产库中台 (Asset Hub) |
| **定位** | gstack/agency-agents/baoyu-skills的统一调度中心 |
| **类型** | 中台能力中心 |
| **版本** | v4.0 |
| **创建日期** | 2026-03-25 |
| **所属系统** | CyberTeam v4 核心中台 |

---

## 核心定位

资产库中台是CyberTeam v4的"能力资源池"，统一管理和调度三大资产来源：
- gstack工程能力 (40+ Agents)
- agency专业能力 (100+ Agents)
- baoyu创意能力 (20+ Skills)

### 核心能力

1. **资产注册**: 三方资产的统一注册和分类
2. **智能调度**: 基于任务类型匹配合适的资产
3. **负载均衡**: 避免单点过载，优化资源分配
4. **效果追踪**: 评估资产使用效果，持续优化

---

## 资产分类

### A类: gstack工程能力 (40+)

| 类别 | Agent数量 | 核心能力 |
|------|-----------|----------|
| 规划类 | 5 | roadmapper, planner, phase-researcher |
| 执行类 | 8 | executor, frontend-dev, backend-architect |
| 验证类 | 4 | verifier, ui-checker, integration-checker |
| 审查类 | 6 | code-reviewer, security-reviewer, database-reviewer |
| 调试类 | 3 | debugger, build-error-resolver |
| 设计类 | 7 | ui-designer, ux-architect, ux-researcher |
| DevOps类 | 5 | devops-automator, sre, deployer |
| 移动类 | 3 | mobile-app-builder, flutter-reviewer |

### B类: agency专业能力 (15类/100+)

| 类别 | Agent数量 | 核心能力 |
|------|-----------|----------|
| 运营类 | 20+ | 操盘手、增长、内容、用户、活动 |
| 营销类 | 15+ | 品牌、投放、SEO、KOL、事件 |
| 战略类 | 10+ | 战略规划、竞争分析、商业模式 |
| 产品类 | 12+ | 需求分析、用户体验、数据分析 |
| 技术类 | 15+ | 架构、安全、性能、AI、区块链 |

### C类: baoyu创意能力 (20+)

| 类别 | Skill数量 | 核心能力 |
|------|-----------|----------|
| 图像生成 | 5 | 图片生成、漫画、信息图 |
| 内容发布 | 8 | X、微信、微博、YouTube |
| 文档处理 | 5 | 翻译、网页转Markdown、PPT |
| 营销工具 | 5 | SEO优化、KOL匹配、投放分析 |

---

## 架构说明

本模块负责：
- 统一管理gstack、agency、baoyu三大资产来源
- 基于任务类型智能匹配最合适的Agent/Skill
- 追踪资产使用效果，持续优化调度策略
- 提供负载均衡，避免单点过载

---

## 模块结构

- assets/registry.py - 资产注册表
- assets/scheduler.py - 智能调度器
- assets/tracker.py - 效果追踪器
"""

from __future__ import annotations

__all__ = []
