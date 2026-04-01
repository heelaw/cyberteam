# Cyberwiz Business Model Analyzer v2.0

**通用业务模型分析平台** - 智能化、模块化、可扩展的业务模型分析工具套件。

---

## 🎯 核心特性

### 1. **模块化分析框架**
- 📦 预置常见商业模式框架（O2O、SaaS、电商DTC等）
- 🔧 可组合的分析模块
- 🎨 灵活的模板系统

### 2. **智能参数管理**
- 🔍 自动提取关键指标（CAC、LTV、转化率等）
- 🔄 参数同步和一致性检查
- 📊 依赖关系追踪

### 3. **通用验证引擎**
- ✅ 数学关系验证
- 🏆 行业基准对比
- 🔍 一致性检查
- 📋 完整性验证

### 4. **增量更新工作流**
- ✏️ 单个指标更新
- 🔄 转化漏斗更新
- 📝 自动变更记录
- 💾 智能备份

---

## 📁 目录结构

```
cyberwiz-businessmodel/
├── frameworks/                    # 分析框架库
│   ├── o2o-preorder.yaml          # O2O预定模式
│   ├── saas-subscription.yaml     # SaaS订阅模式
│   └── ecommerce-dtc.yaml        # 电商DTC模式
│
├── modules/                       # 可复用分析模块
│   ├── conversion-funnel/         # 转化漏斗分析
│   │   └── README.md              # 模块说明文档
│   ├── unit-economics/            # 单体经济模型
│   │   └── README.md              # 模块说明文档
│   └── growth-metrics/            # 增长指标
│       └── README.md              # 模块说明文档
│
├── templates/                     # 报告模板
│   ├── investor-pitch/            # 投资人版本模板
│   │   └── final-report-template.md
│   ├── internal-strategy/         # 内部战略版本模板
│   │   └── final-report-template.md
│   └── operational-kpi/           # 运营KPI版本模板
│       └── final-report-template.md
│
├── core/                          # 核心引擎
│   └── parameter_extractor.py     # 参数提取器
│
├── validators/                    # 验证工具
│   └── validation_engine.py      # 验证引擎
│
├── tools/                         # 增量更新工具
│   └── incremental_updater.py     # 增量更新器
│
├── scripts/                       # 辅助脚本
│   ├── workflow_manager.py        # 工作流管理
│   ├── report_generator.py        # 报告生成
│   ├── validator.py               # 模板验证
│   ├── revenue_calculator.py      # 收入计算
│   ├── funnel_analyzer.py         # 漏斗分析
│   ├── metrics_validator.py        # 指标验证
│   ├── status_checker.py          # 状态检查
│   ├── export_tool.py             # 报告导出
│   ├── init_v2.py                 # v2.0初始化
│   └── README.md                  # 脚本说明
│
├── config/                        # 配置文件
│   ├── validator_rules.yaml       # 验证规则
│   └── example_project.yaml       # 示例项目
│
├── assets/                        # 资产文件
│   ├── business-model-template.md
│   ├── revenue-formula-template.md
│   ├── conversion-funnel-template.md
│   ├── operational-metrics-template.md
│   ├── breakthrough-points-template.md
│   ├── final-report-template.md
│   ├── README.md                  # 资产说明
│   ├── metrics-reference.md       # 指标参考
│   └── frameworks-reference.md    # 框架参考
│
├── .workflow/                     # 工作流状态（隐藏目录）
│   ├── state-template.json        # 状态模板
│   ├── state_manager.py           # 状态管理器
│   └── backups/                   # 状态备份
│
├── references/                    # 参考资料
│   ├── business-model-methodology.md
│   ├── business-model-cases.md
│   └── business-model-cases-complete.md
│
├── output/                        # 输出目录
│   └── {项目名称}/                # 各项目输出
│
├── SKILL.md                       # Skill说明
├── README.md                      # 本文档
├── QUICKSTART.md                  # 快速入门
├── CHANGELOG.md                   # 变更日志
├── UPGRADE.md                     # 升级说明
└── OPTIMIZATION_SUMMARY.md        # 优化总结
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install pyyaml
```

### 1. 提取文档参数

```bash
python core/parameter_extractor.py path/to/document.md
```

**输出**：
- `parameters.json` - 提取的参数（JSON格式）
- 控制台打印参数摘要

### 2. 验证业务模型

```bash
python validators/validation_engine.py path/to/document.md [config/validator_rules.yaml]
```

**输出**：
- 完整的验证报告
- 通过/警告/错误统计
- 详细问题列表

### 3. 增量更新指标

```bash
# 更新单个指标
python tools/incremental_updater.py path/to/document.md update_metric "CAC" 175

# 更新转化漏斗
python tools/incremental_updater.py path/to/document.md update_funnel "完播" 0.35
```

**功能**：
- 自动备份原文档
- 查找并更新所有相关位置
- 分析影响范围
- 生成变更记录

---

## 📖 使用场景

### 场景1：启动新项目分析

```bash
# 1. 选择框架
# 查看可用框架
ls frameworks/

# 2. 基于框架创建文档
# (手动复制框架中的章节结构)

# 3. 填写内容后验证
python validators/validation_engine.py your-document.md
```

### 场景2：发现数据错误并修正

```bash
# 1. 提取参数查看当前值
python core/parameter_extractor.py document.md

# 2. 增量更新错误指标
python tools/incremental_updater.py document.md update_metric "LTV" 3025

# 3. 重新验证
python validators/validation_engine.py document.md
```

### 场景3：优化转化路径

```bash
# 1. 更新漏斗步骤
python tools/incremental_updater.py document.md update_funnel "完播" 0.35

# 2. 根据影响提示更新相关指标
# (工具会提示需要更新整体转化率、曝光需求等)

# 3. 验证一致性
python validators/validation_engine.py document.md
```

---

## 🎨 框架使用指南

### O2O预定模式框架

**适用场景**：
- 本地服务（美容、健身、教育）
- 高客单价定制服务
- 需要预约的服务业

**核心指标**：
- CAC: $50-500
- 爽约率: <10%
- 预收款比例: 80-100%

**标准转化路径**：
```
触达 → 完播 → 兴趣 → 预约 → 到店 → 交付 → 复购
100%   30%    8%     6%    90%   100%   45%/年
```

### SaaS订阅模式框架

**适用场景**：
- 企业级软件服务
- 云平台服务
- 生产力工具

**核心指标**：
- MRR/ARR增长率
- Churn Rate: <5%（月度）
- LTV:CAC > 3:1

**标准转化路径**：
```
网站访问 → 注册 → 激活 → 试用 → 付费转化
100%      5%    40%   30%    20%
```

### 电商DTC模式框架

**适用场景**：
- 垂直品类电商
- 自有品牌电商
- 订阅制电商

**核心指标**：
- AOV: $50-200
- 复购率: 30-50%
- 购买频率: 2-6次/年

**标准转化路径**：
```
曝光 → 点击 → 访问 → 加购 → 结账 → 购买
100%  3%    90%   10%   30%   70%
```

---

## 🔧 高级功能

### 自定义验证规则

编辑 `config/validator_rules.yaml`：

```yaml
mathematical_consistency:
  - name: "自定义规则"
    expression: "your_expression"
    severity: "warning"
    message: "你的验证消息"
```

### 创建自定义框架

1. 复制现有框架：
```bash
cp frameworks/o2o-preorder.yaml frameworks/your-framework.yaml
```

2. 编辑框架定义

3. 在分析中使用

### Python API

```python
from core.parameter_extractor import ParameterExtractor
from validators.validation_engine import ValidationEngine

# 提取参数
extractor = ParameterExtractor('document.md')
params = extractor.extract_all()

# 验证
engine = ValidationEngine()
report = engine.validate(params, document_content)
report.print_report()
```

---

## 📝 最佳实践

### 1. 参数命名规范
- 使用全大写缩写词：CAC、LTV、ARPU、ROI
- 使用下划线分隔复合词：conversion_rate、retention_rate_90d

### 2. 文档结构
- 使用一致的标题层级
- 关键指标使用表格呈现
- 转化漏斗使用 ASCII 图形

### 3. 版本管理
- 每次重大更新前自动备份
- 维护 CHANGELOG.md
- 使用语义化版本号

### 4. 验证优先级
- 先验证数学关系
- 再检查行业基准
- 最后确认完整性

---

## 🤝 贡献指南

### 添加新框架

1. 在 `frameworks/` 创建新 YAML 文件
2. 定义适用场景、核心指标、标准路径
3. 提交 PR

### 添加新模块

1. 在 `modules/` 创建模块目录
2. 实现模块逻辑
3. 更新文档

### 报告问题

- 使用 Issues 提交 bug
- 附上复现步骤和文档样本

---

## 📄 License

MIT License

---

## 🙏 致谢

感谢所有贡献者和使用者！

---

## 📞 联系方式

- 项目主页：[GitHub](https://github.com/your-repo)
- 问题反馈：[Issues](https://github.com/your-repo/issues)

---

**版本**: 2.0
**更新日期**: 2025-01-14
**维护者**: Cyberwiz Team
