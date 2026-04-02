# shared - 共享资源库

> 全局共享的业务数据、模板、知识沉淀。所有Agent可读取。

---

## 目录结构

```
shared/
├── business_data/           # 标准业务数据模板
│   └── standard_metrics.md   # 核心指标定义
│
├── templates/                # 文档模板
│   ├── standard_metrics.md  # 指标模板
│   └── decision_framework.md # 决策框架
│
└── knowledge_base/          # 知识沉淀（归档后）
    ├── diagnoses/           # 问题诊断库
    ├── strategies/          # 策略方案库
    └── playbooks/          # SOP playbook库
```

---

## business_data/ - 标准业务数据

### standard_metrics.md
核心指标的统一定义、计算公式、数据格式。

所有业务数据文件必须遵循此模板格式。

---

## templates/ - 文档模板

| 模板 | 用途 |
|------|------|
| standard_metrics.md | 业务数据模板 |
| decision_framework.md | 决策框架模板 |

---

## knowledge_base/ - 知识沉淀

> 项目归档时，重要决策/方案复制到此目录

| 目录 | 内容 |
|------|------|
| diagnoses/ | 问题诊断报告 |
| strategies/ | 策略方案 |
| playbooks/ | SOP playbook |
| cases/ | 案例分析 |
