#!/usr/bin/env python3
"""
运营岗位结构化分析脚本

用法:
    python3 analyze_position.py "公司名称" "岗位名称"
    python3 analyze_position.py "美团" "用户增长专家"
"""

import sys
import json
from datetime import datetime

# 四种商业模式识别规则
BUSINESS_MODELS = {
    "流量+广告": {
        "keywords": ["广告", "媒体", "内容", "博主", "自媒体", "流量变现"],
        "description": "C端做大流量，B端卖广告",
        "c_end_metrics": ["DAU", "MAU", "用户时长", "留存率"],
        "b_end_metrics": ["广告主数", "询单数", "成交数", "回款率"]
    },
    "平台+抽佣": {
        "keywords": ["平台", "撮合", "抽佣", "o2o", "美团", "滴滴", "淘宝"],
        "description": "撮合CB两端交易，平台抽成",
        "c_end_metrics": ["新增用户", "付费用户数", "复购率"],
        "b_end_metrics": ["商家数", "SKU数", "活跃率"],
        "transaction_metrics": ["GMV", "抽成率", "客单价"]
    },
    "会员订阅": {
        "keywords": ["会员", "订阅", "saas", "续费", "知识付费"],
        "description": "用户付费会员，持续续费",
        "acquisition": ["注册用户数", "获客成本"],
        "conversion": ["付费转化率", "首单金额"],
        "retention": ["续费率", "LTV", "churn率", "ARPU"]
    },
    "产品销售": {
        "keywords": ["电商", "零售", "销售", "教培", "教育"],
        "description": "直接销售产品获取收入",
        "traffic": ["曝光量", "点击率"],
        "conversion": ["咨询率", "下单率", "成交率"],
        "revenue": ["GMV", "客单价", "复购率"]
    }
}

# 岗位关键词映射
POSITION_KEYWORDS = {
    "前端岗位": {
        "keywords": ["增长", "运营", "销售", "推广", "新媒体", "内容", "社群", "活动"],
        "focus": "直接面对用户/客户"
    },
    "后端岗位": {
        "keywords": ["产品", "技术", "数据", "研发", "设计", "策略"],
        "focus": "用户/客户不可见"
    }
}

def identify_business_model(company_info):
    """识别公司商业模式"""
    company_lower = company_info.lower()

    for model, info in BUSINESS_MODELS.items():
        for keyword in info["keywords"]:
            if keyword in company_lower:
                return model, info

    return "未知模式", None

def identify_position_type(position_name):
    """识别岗位类型"""
    position_lower = position_name.lower()

    for pos_type, info in POSITION_KEYWORDS.items():
        for keyword in info["keywords"]:
            if keyword in position_lower:
                return pos_type, info["focus"]

    return "未知类型", "未知"

def generate_analysis_framework(company_name, position_name, business_model, position_type):
    """生成分析框架"""

    framework = f"""# {company_name} - {position_name} 结构化分析

> 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 一、商业模式识别

**识别模式**：{business_model}

**业务逻辑**：{BUSINESS_MODELS.get(business_model, {}).get('description', '未知')}

## 二、岗位定位

**岗位类型**：{position_type}

**岗位位置**：业务{'前端' if '前端' in position_type else '后端'}

**核心职责**：{POSITION_KEYWORDS.get(position_type.split('（')[0], {}).get('focus', '待分析')}

## 三、关键业务指标

### 核心指标（待确认）

根据商业模式和岗位定位，关键指标可能包括：

"""

    if business_model in BUSINESS_MODELS:
        model_info = BUSINESS_MODELS[business_model]
        for category, metrics in model_info.items():
            if category != "keywords" and category != "description":
                framework += f"\n**{category}**：\n"
                framework += f"- {', '.join(metrics)}\n"

    framework += f"""
## 四、用户路径梳理（待分析）

### 典型路径模板

```
[根据业务类型，画出用户从接触到付费/转化的全流程]
```

### 关键节点

- 节点1：[具体描述]
- 节点2：[具体描述]
- 节点3：[具体描述]

### 数据漏斗

- 曝光 → [转化率%] → 点击 → [转化率%] → [下一步] → [转化率%] → 付费/转化

## 五、信息触达场景

### 主要场景
- [场景1]：[具体说明]
- [场景2]：[具体说明]

### 次要场景
- [场景1]：[具体说明]

## 六、工作手段

### 核心手段
1. [手段1]：[具体说明]
2. [手段2]：[具体说明]

### 辅助手段
- [手段1]：[具体说明]

## 七、用户洞察（待补充）

### 基础属性
- 年龄：
- 性别：
- 地域：
- 收入：

### 核心需求
- 需求1：
- 需求2：

### 痛点
- 痛点1：
- 痛点2：

## 八、产品分析（待补充）

### 产品特点
- [特点1]
- [特点2]

### 核心卖点
- 卖点1：
- 卖点2：

## 九、工作策略建议

### 短期策略（1-3个月）
1. [策略1]
2. [策略2]

### 中期策略（3-6个月）
1. [策略1]
2. [策略2]

### 长期策略（6个月以上）
1. [策略1]
2. [策略2]

---

## 下一步行动

- [ ] 通过网络搜索收集公司详细信息
- [ ] 分析产品特点和用户群体
- [ ] 明确关键业务指标和考核标准
- [ ] 梳理完整用户路径和数据漏斗
- [ ] 制定具体工作计划和发力点

---

**分析方法**：运营六要素框架
**Skill版本**：v1.0
"""

    return framework

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\n错误：请提供公司名称和岗位名称")
        print("用法: python3 analyze_position.py \"公司名称\" \"岗位名称\"")
        sys.exit(1)

    company_name = sys.argv[1]
    position_name = sys.argv[2]

    print("="*60)
    print("运营岗位结构化分析")
    print("="*60)
    print(f"公司：{company_name}")
    print(f"岗位：{position_name}")
    print("="*60)

    # 识别商业模式
    business_model, _ = identify_business_model(company_name)
    print(f"\n✓ 识别商业模式：{business_model}")

    # 识别岗位类型
    position_type, focus = identify_position_type(position_name)
    print(f"✓ 识别岗位类型：{position_type}")
    print(f"  岗位焦点：{focus}")

    # 生成分析框架
    framework = generate_analysis_framework(
        company_name, position_name, business_model, position_type
    )

    # 输出到文件
    output_file = f"{company_name}_{position_name}_分析.md".replace(' ', '_')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(framework)

    print(f"\n✓ 分析框架已生成：{output_file}")
    print("\n下一步：")
    print("1. 使用网络搜索工具收集公司详细信息")
    print("2. 分析产品特点和用户群体")
    print("3. 明确关键业务指标")
    print("4. 梳理用户路径和数据漏斗")
    print("5. 制定具体工作策略")

if __name__ == "__main__":
    main()
