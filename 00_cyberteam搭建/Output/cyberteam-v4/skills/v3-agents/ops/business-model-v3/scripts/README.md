# 业务模型梳理 Skill - 辅助脚本

本目录包含业务模型梳理工作流的辅助脚本工具。

## 脚本列表

### 核心脚本

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `workflow_manager.py` | 工作流状态管理 | Stage 0 初始化、状态持久化、进度跟踪 |
| `report_generator.py` | 最终报告生成 | Stage 6 整合各阶段结果、生成完整报告 |
| `validator.py` | 模板验证工具 | 验证各阶段输入完整性、填充模板字段 |

### 分析辅助脚本

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `revenue_calculator.py` | 收入公式计算与敏感度分析 | Stage 2 计算收入变化、变量影响分析 |
| `funnel_analyzer.py` | 转化漏斗分析 | Stage 3 计算转化率、识别流失点 |
| `metrics_validator.py` | 运营指标验证 | Stage 4 验证指标定义完整性 |

### 增强功能脚本

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `status_checker.py` | 工作流状态检查 | `/status` 命令支持、检查工作流进度 |
| `export_tool.py` | 报告导出 | 导出为 HTML/TXT/摘要 |

---

## 快速开始

### 1. 工作流管理

```bash
# 初始化工作流
python3 workflow_manager.py init

# 查看状态
python3 workflow_manager.py status

# 重置工作流
python3 workflow_manager.py reset
```

### 2. 模板验证

```bash
# 查看某阶段的填充指南
python3 validator.py --stage 1 --fill-guide

# 验证输入数据
python3 validator.py --stage 1 --data data.json
```

### 3. 收入计算

```bash
# 基本计算
python3 revenue_calculator.py \
  --formula "流量×转化率×客单价" \
  --variables '{"流量": 10000, "转化率": 0.05, "客单价": 100}'

# 敏感度分析
python3 revenue_calculator.py \
  --variables '{"流量": 10000, "转化率": 0.05, "客单价": 100}' \
  --sensitivity

# 查找优化杠杆
python3 revenue_calculator.py \
  --variables '{"流量": 10000, "转化率": 0.05, "客单价": 100}' \
  --optimize
```

### 4. 转化漏斗分析

```bash
# 分析漏斗
python3 funnel_analyzer.py \
  --nodes '[{"name": "接触", "users": 10000}, {"name": "点击", "users": 5000}]' \
  --visualize

# 与行业基准对比
python3 funnel_analyzer.py \
  --nodes '[...]' \
  --benchmarks '{"点击": 0.05, "浏览": 0.03}'
```

### 5. 指标验证

```bash
# 验证指标定义
python3 metrics_validator.py --metrics metrics.json --report

# 检查目标值合理性
python3 metrics_validator.py --metrics metrics.json --check-target
```

### 6. 状态检查

```bash
# 查看完整状态报告
python3 status_checker.py

# 检查特定阶段
python3 status_checker.py --stage 1

# 仅显示问题
python3 status_checker.py --issues
```

### 7. 报告导出

```bash
# 导出为 HTML
python3 export_tool.py --format html

# 导出所有格式
python3 export_tool.py --format all
```

---

## 脚本详细说明

### workflow_manager.py

管理工作流状态和配置。

**命令：**
- `init` - 初始化新工作流
- `status` - 查看当前状态
- `reset` - 重置工作流

### report_generator.py

生成最终业务模型分析报告。

**参数：**
- `--workflow-dir` - 输出目录（默认：output）
- `--business-name` - 业务/公司名称（必需）
- `--business-type` - 业务类型（toB/toC/toG）
- `--business-stage` - 业务阶段（初创期/成长期/成熟期）

### validator.py

验证各阶段输入数据的完整性。

**命令：**
- `--stage` - 阶段编号（1-5）
- `--data` - 输入数据文件（JSON）
- `--fill-guide` - 显示填充指南
- `--check-template` - 检查模板占位符

### revenue_calculator.py

收入公式计算和敏感度分析。

**参数：**
- `--formula` - 收入公式
- `--variables` - 变量值（JSON，必需）
- `--sensitivity` - 执行敏感度分析
- `--optimize` - 查找优化杠杆
- `--scenarios` - 情景分析（JSON）

### funnel_analyzer.py

转化漏斗分析和流失点识别。

**参数：**
- `--nodes` - 节点数据（JSON，必需）
- `--threshold` - 流失率阈值（默认：0.3）
- `--benchmarks` - 行业基准（JSON）
- `--visualize` - 显示可视化漏斗

### metrics_validator.py

运营指标定义验证。

**参数：**
- `--metrics` - 指标数据（JSON，必需）
- `--report` - 生成完整报告
- `--check-formula` - 检查公式语法
- `--check-target` - 检查目标值合理性

### status_checker.py

检查工作流状态和文件完整性。

**参数：**
- `--workflow-dir` - 输出目录（默认：output）
- `--stage` - 检查特定阶段
- `--issues` - 仅显示问题
- `--json` - 以 JSON 格式输出

### export_tool.py

导出报告为不同格式。

**参数：**
- `--format` - 导出格式（html/txt/summary/all）
- `--report` - 指定报告文件路径
- `--output` - 输出文件路径

---

## Python API 使用

所有脚本都可以作为 Python 模块导入使用。

```python
from scripts.workflow_manager import WorkflowManager
from scripts.revenue_calculator import RevenueCalculator
from scripts.funnel_analyzer import FunnelAnalyzer

# 工作流管理
manager = WorkflowManager()
manager.initialize({"business_name": "示例公司"})
progress = manager.get_progress()

# 收入计算
calculator = RevenueCalculator()
revenue = calculator.calculate_revenue("流量*转化率*客单价", variables)

# 漏斗分析
analyzer = FunnelAnalyzer()
nodes = analyzer.calculate_funnel(nodes_data)
dropoffs = analyzer.identify_dropoffs()
```

---

## 依赖要求

- Python 3.7+
- 标准库（无需额外安装）

---

## 使用示例

### 完整工作流示例

```bash
# 1. 初始化工作流
python3 scripts/workflow_manager.py init

# 2. 执行 Stage 1，验证输入
python3 scripts/validator.py --stage 1 --fill-guide

# 3. 收入公式分析
python3 scripts/revenue_calculator.py \
  --variables '{"流量": 10000, "转化率": 0.05, "客单价": 100}' \
  --sensitivity

# 4. 转化漏斗分析
python3 scripts/funnel_analyzer.py \
  --nodes '[{"name":"接触","users":10000},{"name":"点击","users":5000}]'

# 5. 查看工作流状态
python3 scripts/status_checker.py

# 6. 生成最终报告
python3 scripts/report_generator.py --business-name "示例公司"

# 7. 导出报告
python3 scripts/export_tool.py --format all
```

---

## 注意事项

1. 所有脚本都包含 `--help` 参数，可查看详细用法
2. JSON 输入需要严格的格式，建议使用文件而非命令行字符串
3. 输出目录默认为 `output/`，可通过参数自定义
4. 生成的报告保存在 `output/{项目名称}/06-final-report/` 目录

---

## 更新日志

- 2026-01-13: 初始版本，包含 8 个核心脚本
