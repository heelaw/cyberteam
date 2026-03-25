# Cyberwiz Business Model Analyzer - 快速入门指南

## 🎯 这是什么？

一个**智能业务模型分析工具包**，帮助你：
- ✅ 自动提取业务文档中的关键指标
- ✅ 验证数据的逻辑一致性
- ✅ 增量更新指标，自动追踪影响
- ✅ 使用行业最佳实践框架

---

## ⚡ 5分钟上手

### 步骤1：分析现有文档

假设你有一份业务模型文档 `my-business-model.md`：

```bash
cd /Users/cyberwiz/Documents/trae_projects/Claude\ code/skills/skills/cyberwiz-businessmodel

python core/parameter_extractor.py path/to/my-business-model.md
```

**你会看到**：
```
🔍 开始提取参数...
✅ 提取完成，共找到 23 个参数
✅ 参数已导出到: parameters.json

=====================================================================
📊 参数提取摘要

## 共提取 23 个参数

### RATE (8个)
- **completion_rate**: 0.3
- **interest_rate**: 0.08
- **payment_rate**: 0.05

### METRIC (5个)
- **CAC**: 175
  - 公式: 营销总费用 / 新客数
- **LTV**: 3025
- **ROI**: 5.7

### RATIO (2个)
- **LTV_CAC_ratio**: 17.285714285714285
  - 依赖: LTV, CAC
=====================================================================
```

### 步骤2：验证业务模型

```bash
python validators/validation_engine.py path/to/my-business-model.md
```

**你会看到**：
```
=====================================================================
📊 业务模型验证报告
=====================================================================

总检查项: 8
✅ 通过: 6
⚠️  警告: 2
❌ 错误: 0

----------------------------------------------------------------------
详细问题列表:
----------------------------------------------------------------------

⚠️  LTV > CAC (第7.2.1节): LTV ($3025) 显著高于行业基准 ($500-2000)
  - metric: LTV
  - value: 3025
  - industry: o2o-service
  - expected_range: $500 - $2,000

⚠️  CAC一致性 (多处): CAC在不同位置的值有微小差异
  - values: [{'name': 'CAC', 'value': 175}, {'name': 'CAC', 'value': 200}]

=====================================================================
✅ 验证通过但有 2 个警告
=====================================================================
```

### 步骤3：修正错误指标

发现CAC在不同位置的值不一致，修复它：

```bash
python tools/incremental_updater.py path/to/my-business-model.md update_metric "CAC" 175
```

**你会看到**：
```
💾 已备份到: /path/to/.backups/document_20250114_153045.md

📊 更新指标: CAC
   新值: 175

📍 影响范围:
   - 影响指标: CAC, LTV:CAC, ROI
   - 影响章节: 6. 流量渠道, 7. 运营指标, 附录
   - 预估工作量: 中等（需要重新计算比率）

   ✏️  6.3 流量渠道汇总表 (行1234): 200 → 175
   ✏️  7.2.1 顶层指标 (行890): 200 → 175
   ✏️  附录A 核心数据一览 (行1456): 200 → 175

✅ 已更新 3 处
📝 已记录变更到: /path/to/CHANGELOG.md
```

### 步骤4：优化转化漏斗

发现"完播率"偏低，优化后重新验证：

```bash
# 更新漏斗步骤
python tools/incremental_updater.py path/to/my-business-model.md update_funnel "完播" 0.35
```

**输出**：
```
💾 已备份到: /path/to/.backups/document_20250114_153112.md

🔄 更新转化漏斗: 完播
   新转化率: 35.00%
   ✏️  已更新

⚠️  注意：转化率从 30.00% 变为 35.00%
   需要手动更新整体转化率、曝光需求、预算等衍生指标
```

---

## 🎨 从框架开始新项目

### 选择合适的框架

查看可用框架：

```bash
ls frameworks/
# o2o-preorder.yaml       # O2O预定模式
# saas-subscription.yaml  # SaaS订阅模式
# ecommerce-dtc.yaml      # 电商DTC模式
```

### 使用O2O框架

1. 查看框架定义：
```bash
cat frameworks/o2o-preorder.yaml
```

2. 关键信息：
```yaml
name: "O2O预定模式"
适用场景:
  - 本地服务（美容、健身、教育）
  - 高客单价定制服务
  - 需要预约的服务业

标准转化路径:
  - 触达 → 完播 → 兴趣 → 预约 → 到店 → 交付 → 复购
    100%   30%    8%     6%    90%   100%   45%/年

核心指标:
  - CAC: $50-500
  - 爽约率: <10%
  - 预收款比例: 80-100%
```

3. 基于框架创建文档（手动复制章节结构）

---

## 🔍 常见使用场景

### 场景1：检查数据一致性

**问题**：文档中CAC出现了多个不同的值

**解决**：
```bash
# 1. 提取参数
python core/parameter_extractor.py document.md

# 2. 查看CAC的所有出现
python tools/incremental_updater.py document.md find "CAC"

# 3. 统一更新为正确值
python tools/incremental_updater.py document.md update_metric "CAC" 175
```

### 场景2：调整业务目标

**问题**：投资人要求提高市场份额，需要调整所有相关指标

**解决**：
```bash
# 1. 更新目标客户数
python tools/incremental_updater.py document.md update_metric "目标客户数" 50000

# 2. 工具会提示影响的指标
# 3. 根据提示更新曝光量、预算等

# 4. 重新验证
python validators/validation_engine.py document.md
```

### 场景3：优化转化路径

**问题**：发现某个转化步骤流失严重

**解决**：
```bash
# 1. 更新该步骤的目标转化率
python tools/incremental_updater.py document.md update_funnel "付款" 0.07

# 2. 重新计算整体转化率
# 3. 根据新的转化率调整曝光需求

# 4. 验证优化后的指标
python validators/validation_engine.py document.md
```

---

## 💡 实用技巧

### 技巧1：定期验证

在每次重大修改后运行验证：
```bash
# 建立工作流
python validators/validation_engine.py document.md
```

### 技巧2：查看变更历史

所有更新都会记录在 `CHANGELOG.md`：
```bash
cat output/{项目名称}/06-final-report/CHANGELOG.md
```

### 技巧3：恢复备份

如果更新出错，从 `.backups/` 目录恢复：
```bash
ls .backups/
# document_20250114_153045.md
# document_20250114_161230.md

cp .backups/document_20250114_153045.md document.md
```

### 技巧4：自定义验证规则

编辑 `config/validator_rules.yaml` 添加项目特定规则：
```yaml
mathematical_consistency:
  - name: "毛利率必须>60%"
    expression: "gross_margin > 0.6"
    severity: "error"
    message: "公司要求毛利率>60%"
```

---

## 🐛 故障排除

### 问题1：找不到指标

**错误**：`未找到指标 'CAC'`

**解决**：
- 检查指标名称拼写
- 使用 `parameter_extractor.py` 查看实际提取的指标名称
- 尝试模糊匹配或部分匹配

### 问题2：更新后验证失败

**错误**：更新指标后验证报错

**解决**：
- 检查是否更新了所有相关位置
- 查看备份文件确认更新内容
- 使用 `incremental_updater.py` 的 `--dry-run` 选项预览

### 问题3：依赖关系未更新

**错误**：更新CAC后，LTV:CAC比率未更新

**解决**：
- 工具会提示需要手动更新的衍生指标
- 使用计算器或Excel重新计算
- 再次使用 `update_metric` 更新衍生指标

---

## 📚 下一步

1. **深入学习框架**
   - 阅读 `frameworks/` 中的框架定义
   - 理解不同商业模式的指标差异

2. **自定义配置**
   - 编辑 `config/validator_rules.yaml`
   - 创建项目特定的验证规则

3. **扩展功能**
   - 创建自定义框架
   - 开发新的验证规则
   - 贡献到开源项目

---

## 🆘 获取帮助

- 📖 查看完整文档：`README.md`
- 🐛 报告问题：GitHub Issues
- 💬 讨论交流：GitHub Discussions

---

**Happy Analyzing! 🚀**
