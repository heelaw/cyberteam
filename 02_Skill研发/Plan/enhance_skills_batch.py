#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Enhancement Script
为Skills添加输入输出格式、使用示例、错误处理和独特个性
"""

import os
import json
from pathlib import Path

# 定义所有需要处理的skills及其增强内容
SKILL_ENHANCEMENTS = {
    "精益运营思维": {
        "input_schema": {
            "type": "object",
            "properties": {
                "想法列表": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "用户的所有运营想法"
                },
                "资源约束": {
                    "type": "string",
                    "description": "可用资源限制（预算、人力、时间）"
                },
                "验证偏好": {
                    "type": "string",
                    "enum": ["快速验证", "完整验证", "低成本优先"],
                    "description": "验证方案的选择偏好"
                }
            },
            "required": ["想法列表"]
        },
        "output_schema": {
            "精益验证计划": {
                "想法清单": {"type": "array"},
                "假设拆解": {"type": "object"},
                "验证方案": {"type": "array"},
                "行动计划": {"type": "array"}
            }
        },
        "input_example": "想法列表：[1.增加优惠券 2.优化首页 3.做裂变活动]\n资源约束：预算5万，人力3人，时间1个月",
        "output_example": "优先级排序：\n1. 优惠券A/B测试（低成本高价值）\n2. 首页优化（中成本高价值）\n3. 裂变活动（高成本中价值）",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 想法太多 | 优先识别核心假设，分批次验证 |
| 资源不足 | 优先低成本验证方案 |
| 无法验证 | 明确标注，建议调整假设""",
        "personality": """**精益验证倡导者**
- 快速试错，小步快跑
- 数据驱动，假设验证
- 成本控制，ROI导向
- 拒绝盲目投入

**实验设计专家**
- 设计最小可行验证方案
- 明确成功/失败标准
- 设置止损点"""
    },

    "指标拆解三逻辑": {
        "input_schema": {
            "type": "object",
            "properties": {
                "业务目标": {"type": "string"},
                "业务类型": {
                    "type": "string",
                    "enum": ["电商", "内容", "工具", "社群", "增长"]
                },
                "可用数据": {"type": "array"},
                "团队分工": {"type": "string"}
            },
            "required": ["业务目标", "业务类型"]
        },
        "output_schema": {
            "指标体系": {
                "北极星指标": {"type": "object"},
                "拆解维度": {"type": "array"},
                "指标清单": {"type": "array"},
                "责任矩阵": {"type": "array"}
            }
        },
        "input_example": "业务目标：提升GMV\n业务类型：电商\n团队：运营5人+技术3人",
        "output_example": "北极星指标：GMV\n拆解公式：GMV = 流量 × 转化率 × 客单价\n一级指标：UV、注册转化率、付费转化率、ARPU",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 目标不清晰 | 引导用户量化目标 |
| 业务类型不明确 | 询问核心业务模式 |
| 数据不可得 | 标注数据缺口，给出替代方案 |
| 指标过多 | 合并相似指标，聚焦关键指标""",
        "personality": """**指标拆解专家**
- 目标导向，层层拆解
- 公式推导，逻辑闭环
- 责任到人，可追踪

**数据思维**
- 每个指标都有业务含义
- 每个指标都有数据来源
- 每个指标都有责任人"""
    },

    "同理心地图": {
        "input_schema": {
            "type": "object",
            "properties": {
                "目标用户": {"type": "string"},
                "研究场景": {"type": "string"},
                "用户数据": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "访谈记录、评论、问卷等"
                }
            },
            "required": ["目标用户"]
        },
        "output_schema": {
            "同理心地图": {
                "看到_听到": {"type": "array"},
                "想到_感受到": {"type": "array"},
                "说什么_做什么": {"type": "array"},
                "痛点_期望": {"type": "object"}
            },
            "产品建议": {"type": "array"}
        },
        "input_example": "目标用户：25-35岁职场女性\n研究场景：通勤场景内容消费",
        "output_example": "核心洞察：用户说想要更多内容，实际需要更精准的内容\n痛点：内容重复浪费时间\n建议：优化去重算法",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 用户数据不足 | 基于常识和经验做初步分析，标注需补充数据 |
| 用户群体不明确 | 引导用户聚焦特定用户群体 |
| 象限内容空缺 | 明确标注，提供分析框架 |
| 言行矛盾 | 重点分析，揭示真实需求""",
        "personality": """**用户洞察专家**
- 深度共情，换位思考
- 区分表面言语和真实想法
- 识别情绪，理解动机
- 痛点具体，期望可行

**人性理解者**
- 用户不会直接说出真实需求
- 行为比言语更真实
- 情绪驱动决策"""
    },

    "KANO模型": {
        "input_schema": {
            "type": "object",
            "properties": {
                "需求列表": {"type": "array"},
                "用户群体": {"type": "string"},
                "调研方式": {
                    "type": "string",
                    "enum": ["已有调研数据", "需要设计问卷", "基于经验判断"]
                }
            },
            "required": ["需求列表"]
        },
        "output_schema": {
            "KANO分类": {
                "type": "array",
                "items": {
                    "需求": {"type": "string"},
                    "类型": {"type": "string"},
                    "Better系数": {"type": "string"},
                    "Worse系数": {"type": "string"}
                }
            },
            "优先级矩阵": {"type": "object"},
            "产品建议": {"type": "array"}
        },
        "input_example": "需求列表：[夜间模式, 个性化推荐, 社交分享, 启动速度优化]",
        "output_example": "M类（必备）：启动速度优化 - 优先做\nO类（期望）：个性化推荐 - 努力做\nA类（兴奋）：夜间模式 - 创新做\nI类（无差异）：社交分享 - 暂缓",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 无调研数据 | 基于产品经验判断，明确标注需验证 |
| 需求描述模糊 | 细化需求描述，确保可评估 |
| 样本量不足 | 标注局限性，建议扩大样本 |
| 分类结果不明确 | 使用Better-Worse系数辅助判断""",
        "personality": """**需求分类专家**
- 严格区分M/O/A/I/R五类
- Better-Worse系数量化分析
- 动态审视，兴奋属性会变为必备

**产品战略思维**
- 必备属性不做会死
- 期望属性做好才有竞争力
- 兴奋属性超出预期才有惊喜"""
    },

    "价值努力矩阵": {
        "input_schema": {
            "type": "object",
            "properties": {
                "待评估选项": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "评估维度": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "价值评估的维度"
                },
                "团队资源": {
                    "type": "string",
                    "description": "可用资源限制"
                }
            },
            "required": ["待评估选项"]
        },
        "output_schema": {
            "价值努力矩阵": {
                "做": {"type": "array"},
                "计划": {"type": "array"},
                "委托": {"type": "array"},
                "消除": {"type": "array"}
            },
            "执行建议": {"type": "array"}
        },
        "input_example": "待评估选项：[登录优化, 新手引导, 数据导出, 界面改版]",
        "output_example": "做（高价值低努力）：新手引导\n计划（高价值高努力）：登录优化\n委托（低价值高努力）：数据导出\n消除（低价值低努力）：界面改版",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 价值评估分歧 | 团队讨论达成共识，标注不同观点 |
| 努力估算困难 | 给出区间估算，明确不确定性 |
| 选项过多 | 分批评估，优先聚焦核心选项 |
| 四象限不均衡 | 检查评估标准，避免极端情况""",
        "personality": """**优先级决策专家**
- 价值与努力双维度评估
- 四象限清晰，决策有据
- ROI导向，资源最优配置

**务实高效**
- 高价值低努力立即做
- 避免低价值高努力的陷阱
- 考虑依赖关系和风险"""
    },

    "用户旅程图": {
        "input_schema": {
            "type": "object",
            "properties": {
                "用户目标": {"type": "string"},
                "旅程起点": {"type": "string"},
                "旅程终点": {"type": "string"},
                "分析范围": {"type": "string"}
            },
            "required": ["用户目标"]
        },
        "output_schema": {
            "用户旅程图": {
                "阶段划分": {"type": "array"},
                "各阶段要素": {"type": "object"},
                "情绪曲线": {"type": "array"},
                "痛点排序": {"type": "array"}
            },
            "优化建议": {"type": "array"}
        },
        "input_example": "用户目标：完成在线课程学习\n旅程：发现→评估→购买→学习→完成",
        "output_example": "情绪低点：支付决策（焦虑）\n情绪高点：完成学习（满足）\n核心痛点：支付安全焦虑、试看内容有限\n优化：展示安全认证、开放更多试看",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 阶段划分困难 | 引导用户按目标节点划分 |
| 情绪数据缺失 | 基于行为推断情绪，标注推断依据 |
| 接触点不明确 | 聚焦核心触点，次要触点可简化 |
| 痛点证据不足 | 标注需补充数据，基于经验判断""",
        "personality": """**用户体验专家**
- 完整还原用户旅程
- 情绪曲线可视化
- 痛点精准定位

**体验优化思维**
- 识别情绪低点（挫败时刻）
- 设计惊喜时刻（情感高点）
- 优化关键节点体验"""
    },

    "5W1H分析法": {
        "input_schema": {
            "type": "object",
            "properties": {
                "核心问题": {"type": "string"},
                "问题范围": {"type": "string"},
                "分析深度": {
                    "type": "string",
                    "enum": ["快速诊断", "深度分析", "全面分析"]
                }
            },
            "required": ["核心问题"]
        },
        "output_schema": {
            "六要素分析": {
                "What": {"type": "object"},
                "Why": {"type": "array"},
                "Who": {"type": "object"},
                "When": {"type": "object"},
                "Where": {"type": "object"},
                "How": {"type": "object"}
            },
            "综合结论": {"type": "object"},
            "行动计划": {"type": "array"}
        },
        "input_example": "核心问题：下单转化率下降\n范围：App端渠道\n深度：快速诊断",
        "output_example": "What：转化率从15%降至8%\nWhy：价格敏感+体验下降\nWho：中等消费力用户\nWhen：双十一后\nWhere：商品详情页\nHow：支付环节流失",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 要素信息不足 | 基于现有信息分析，标注待补充项 |
| Why分析困难 | 提出多个假设，标注需验证 |
| 用户群体泛化 | 引导用户细分用户群体 |
| 时间模糊 | 明确具体时间节点""",
        "personality": """**问题诊断专家**
- 六要素全面覆盖
- 因果逻辑清晰
- 数据支撑结论

**系统思维**
- 不遗漏任何要素
- 要素相互印证
- 根因优先级排序"""
    },

    "案例拆解法": {
        "input_schema": {
            "type": "object",
            "properties": {
                "学习目的": {"type": "string"},
                "案例类型": {
                    "type": "string",
                    "enum": ["活动案例", "内容案例", "增长案例", "其他"]
                },
                "案例来源": {"type": "string"}
            },
            "required": ["学习目的"]
        },
        "output_schema": {
            "案例背景": {"type": "object"},
            "四维度分析": {"type": "object"},
            "关键成功因素": {"type": "array"},
            "可应用方法论": {"type": "array"},
            "实践计划": {"type": "array"}
        },
        "input_example": "学习目的：学习如何设计裂变活动\n案例类型：活动案例",
        "output_example": "案例：春节拉新裂变\n成功因素：1.钩子强（终身会员）2.路径简（3步）3.时机准\n方法论：高价值+稀缺感+即时可得钩子设计\n实践：设计XX活动钩子方案",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 案例信息不全 | 基于现有信息分析，明确信息缺口 |
| 数据缺失 | 标注数据来源缺失，基于逻辑推断 |
- 学习目的模糊 | 引导用户明确具体学习目标 |
| 方法论抽象困难 | 提供方法论框架，帮助提炼""",
        "personality": """**案例学习专家**
- 带着问题拆解案例
- 深入原理，不止表面
- 提炼可复用方法论

**实战导向**
- 理论结合实际
- 方法论可迁移
- 学完就能用"""
    },

    "流程化思维法": {
        "input_schema": {
            "type": "object",
            "properties": {
                "流程目标": {"type": "string"},
                "当前痛点": {"type": "array"},
                "团队情况": {"type": "string"}
            },
            "required": ["流程目标"]
        },
        "output_schema": {
            "流程图": {"type": "string"},
            "关键影响因素": {"type": "array"},
            "瓶颈节点": {"type": "array"},
            "放大节点": {"type": "array"},
            "优化建议": {"type": "array"}
        },
        "input_example": "流程目标：新用户注册转化率从15%提升至25%\n痛点：注册流程长、流失率高",
        "output_example": "流程：开始→填手机→验证→填信息→选领域→完成\n关键因素：页面加载速度、表单字段数、验证方式\n瓶颈：验证码失败率20%、表单放弃率60%\n优化：精简字段至6个、优化加载速度",
        "error_handling": """| 错误类型 | 处理方式 |
|---------|---------|
| 目标不清晰 | 引导用户量化目标 |
| 流程过于复杂 | 拆分子流程，每个≤7步 |
| 责任人不明确 | 标注需明确责任人 |
| 关键因素识别困难 | 引导用户分析数据，识别影响点""",
        "personality": """**流程设计专家**
- 目标驱动流程设计
- 五符号标准化表达
- 关键节点可控

**系统思维**
- 单一入口出口
- 步骤不可逆
- 责任明确到人"""
    }
}

# 定义文件路径映射
FILE_MAPPING = {
    "精益运营思维": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/工作管理进阶Agent/配套skill/精益运营思维/SKILL.md",
    "指标拆解三逻辑": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/工作管理进阶Agent/配套skill/指标拆解三逻辑/SKILL.md",
    "同理心地图": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/用户洞察Agent/配套skill/同理心地图/SKILL.md",
    "KANO模型": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/用户洞察Agent/配套skill/KANO模型/SKILL.md",
    "价值努力矩阵": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/用户洞察Agent/配套skill/价值努力矩阵/SKILL.md",
    "用户旅程图": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/用户洞察Agent/配套skill/用户旅程图/SKILL.md",
    "5W1H分析法": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/用户洞察Agent/配套skill/5W1H分析法/SKILL.md",
    "案例拆解法": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/运营方法论Agent/配套skill/案例拆解法/SKILL.md",
    "流程化思维法": "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/【项目组2】/运营方法论Agent/配套skill/流程化思维法/SKILL.md"
}

def create_enhancement_content(skill_name):
    """创建增强内容"""
    if skill_name not in SKILL_ENHANCEMENTS:
        print(f"Warning: {skill_name} not in enhancements")
        return None

    enhancement = SKILL_ENHANCEMENTS[skill_name]

    content = f"""
---

## 输入输出格式

### 输入格式 (JSON Schema)

```json
{json.dumps(enhancement["input_schema"], indent=2, ensure_ascii=False)}
```

### 输出格式 (JSON Schema)

```json
{json.dumps(enhancement["output_schema"], indent=2, ensure_ascii=False)}
```

---

## 使用示例

**输入**：
```
{enhancement["input_example"]}
```

**输出核心内容**：
```
{enhancement["output_example"]}
```

---

## 错误处理

{enhancement["error_handling"]}

---

## 独特个性

{enhancement["personality"]}
"""
    return content

def main():
    """主函数"""
    print("开始处理Skills...")

    for skill_name, file_path in FILE_MAPPING.items():
        try:
            # 读取原文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已经包含增强内容
            if "## 输入输出格式" in content:
                print(f"✓ {skill_name} - 已包含增强内容，跳过")
                continue

            # 生成增强内容
            enhancement = create_enhancement_content(skill_name)
            if not enhancement:
                continue

            # 找到插入位置（在Skill角色定义或核心定义之后）
            if "## Skill角色定义" in content:
                insert_marker = "## Skill角色定义"
            elif "## 核心定义" in content:
                insert_marker = "## 核心定义"
            elif "## Skill功能" in content:
                insert_marker = "## Skill功能"
            else:
                print(f"✗ {skill_name} - 未找到合适的插入位置")
                continue

            # 分割内容并插入
            parts = content.split(insert_marker, 1)
            if len(parts) == 2:
                # 找到insert_marker之后的第一个section结束位置
                after_marker = parts[1]
                # 找到下一个##开头的内容
                lines = after_marker.split('\n')
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('---') or (i > 5 and line.startswith('##')):
                        insert_index = i
                        break

                # 重新组合
                before_insert = '\n'.join(lines[:insert_index])
                after_insert = '\n'.join(lines[insert_index:]) if insert_index > 0 else after_insert

                new_content = parts[0] + insert_marker + after_marker

                # 在第一个section之后插入增强内容
                if insert_index > 0:
                    new_content = parts[0] + insert_marker + before_insert + '\n' + enhancement + '\n' + after_insert
                else:
                    # 如果没找到合适的插入点，在insert_marker后直接插入
                    new_content = parts[0] + insert_marker + after_marker.split('\n\n', 1)[0] + enhancement + '\n\n' + after_insert.split('\n\n', 1)[1] if '\n\n' in after_insert else after_insert

                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print(f"✓ {skill_name} - 处理完成")
            else:
                print(f"✗ {skill_name} - 内容分割失败")

        except Exception as e:
            print(f"✗ {skill_name} - 错误: {str(e)}")

    print("\n处理完成！")

if __name__ == "__main__":
    main()
