# 更新日志 (CHANGELOG)

本文档记录 Cyberwiz Business Model Analyzer 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 计划中
- [ ] 更多商业模式框架（社交、直播、订阅盒等）
- [ ] AI问答助手功能
- [ ] 可视化报告生成
- [ ] 更多验证规则

---

## [2.1.0] - 2025-01-19

### 新增 (Added)

#### 模板系统
- 新增 `templates/` 目录
  - `investor-pitch/` - 投资人版本报告模板
  - `internal-strategy/` - 内部战略版本报告模板
  - `operational-kpi/` - 运营KPI版本报告模板

#### 模块系统
- 新增 `modules/` 目录
  - `conversion-funnel/` - 转化漏斗分析模块
    - 完整的漏斗分析方法论
    - 流失点识别框架
    - A/B测试指南
  - `unit-economics/` - 单体经济模型模块
    - CAC/LTV计算框架
    - 回本周期分析
    - 健康度评估标准
  - `growth-metrics/` - 增长指标模块
    - AARRR增长模型
    - 北极星指标选择
    - 增长质量评估

### 改进 (Improved)
- 完善文档体系结构
- 统一模板格式和占位符
- 增强最佳实践指导

### 文档 (Documentation)
- 新增 CHANGELOG.md 变更日志
- 更新模块说明文档
- 完善使用指南

---

## [2.0.0] - 2025-01-14

### 重大变更 (Breaking Changes)
- 从特定案例分析工具升级为通用业务模型分析平台
- 重新设计整体架构和目录结构

### 新增 (Added)

#### 核心引擎
- `core/parameter_extractor.py` - 智能参数提取器
  - 自动识别 CAC、LTV、ROI 等关键指标
  - 支持依赖关系分析
  - 生成参数摘要和 JSON 导出

#### 验证工具
- `validators/validation_engine.py` - 业务模型验证引擎
  - 数学关系验证
  - 行业基准对比
  - 一致性检查
  - 完整性验证

#### 增量更新工具
- `tools/incremental_updater.py` - 增量更新器
  - 单个指标更新
  - 转化漏斗更新
  - 影响分析
  - 自动备份和变更记录

#### 商业模式框架
- `frameworks/o2o-preorder.yaml` - O2O预定模式框架
  - 适用场景定义
  - 核心指标和基准
  - 标准转化路径
  - 成本结构模板
  - 风险和增长策略

- `frameworks/saas-subscription.yaml` - SaaS订阅模式框架
  - 适用场景定义
  - 核心指标和基准
  - 标准转化路径
  - 成本结构模板

- `frameworks/ecommerce-dtc.yaml` - 电商DTC模式框架
  - 适用场景定义
  - 核心指标和基准
  - 标准转化路径
  - 成本结构模板

#### 辅助脚本
- `scripts/workflow_manager.py` - 工作流状态管理
- `scripts/report_generator.py` - 最终报告生成
- `scripts/validator.py` - 模板验证工具
- `scripts/revenue_calculator.py` - 收入公式计算
- `scripts/funnel_analyzer.py` - 转化漏斗分析
- `scripts/metrics_validator.py` - 运营指标验证
- `scripts/status_checker.py` - 工作流状态检查
- `scripts/export_tool.py` - 报告导出
- `scripts/init_v2.py` - v2.0 初始化脚本

#### 配置文件
- `config/validator_rules.yaml` - 验证规则配置
- `config/example_project.yaml` - 示例项目配置

#### 文档
- `README.md` - 完整使用文档
- `QUICKSTART.md` - 快速入门指南
- `UPGRADE.md` - 升级说明
- `OPTIMIZATION_SUMMARY.md` - 优化总结
- `scripts/README.md` - 脚本使用说明

### 改进 (Improved)
- 通用化设计，支持任意行业
- 模块化架构，易于扩展
- 完整的文档体系

### 变更 (Changed)
- 重新组织目录结构
- 统一文件命名规范

### 移除 (Removed)
- 移除硬编码的特定案例逻辑

---

## [1.0.0] - 2024

### 新增 (Added)
- 基础业务模型梳理工作流
- Stage 0-6 分析框架
- 模板和参考资料
- 基础文档

---

## 版本说明

### 版本号格式
- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 变更类型
- **新增 (Added)**: 新功能
- **变更 (Changed)**: 现有功能的变更
- **弃用 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: 问题修复
- **安全 (Security)**: 安全相关修复

---

## 如何使用此文件

### 查看特定版本变更
```bash
# 查看最新版本
grep -A 10 "\[Unreleased\]" CHANGELOG.md

# 查看特定版本
grep -A 20 "\[2.0.0\]" CHANGELOG.md
```

### 添加新变更
1. 在 `[Unreleased]` 下添加新的变更条目
2. 使用标准的变更类型标签
3. 清晰描述变更内容
4. 发布新版本时，创建新的版本号部分

---

**维护者**: Cyberwiz Team
**最后更新**: 2025-01-19
