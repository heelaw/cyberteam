---
name: 活动复盘三步法
description: 提供系统化的活动复盘方法论，包含回顾目标、分析结果、给出结论三个步骤
trigger: ["活动复盘", "活动总结", "活动效果分析", "活动复盘怎么写"]
difficulty: medium
estimated_time: 15分钟
---

# 活动复盘三步法

## 触发场景

当用户出现以下情况时触发本Skill：
- 活动结束了不知道如何复盘
- 复盘时不知道从哪里开始
- 复盘结论不够深入
- 需要撰写正式的复盘报告

## 输入输出格式

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "activity_info": {
      "type": "object",
      "properties": {
        "activity_name": {
          "type": "string",
          "description": "活动名称"
        },
        "activity_period": {
          "type": "string",
          "description": "活动时间"
        },
        "original_goal": {
          "type": "string",
          "description": "原始目标"
        }
      },
      "required": ["activity_name", "original_goal"]
    },
    "actual_results": {
      "type": "object",
      "properties": {
        "key_metrics": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "metric_name": {"type": "string"},
              "target_value": {"type": "string"},
              "actual_value": {"type": "string"},
              "completion_rate": {"type": "string"}
            }
          }
        },
        "process_data": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "stage": {"type": "string"},
              "data": {"type": "string"}
            }
          },
          "description": "过程数据（可选）"
        }
      }
    },
    "review_context": {
      "type": "object",
      "properties": {
        "review_depth": {
          "type": "string",
          "enum": ["快速复盘", "标准复盘", "深度复盘"],
          "description": "复盘深度"
        },
        "focus_areas": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "重点关注领域"
        },
        "audience": {
          "type": "string",
          "description": "复盘报告的汇报对象"
        }
      }
    },
    "qualitative_feedback": {
      "type": "object",
      "properties": {
        "user_feedback": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "用户反馈（可选）"
        },
        "team_feedback": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "团队反馈（可选）"
        },
        "unexpected_events": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "意外事件（可选）"
        }
      }
    }
  },
  "required": ["activity_info", "actual_results"]
}
```

### 输出格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "review_structure": {
      "type": "object",
      "properties": {
        "step1_goal_review": {
          "type": "object",
          "properties": {
            "original_goal": {"type": "string"},
            "goal_breakdown": {"type": "array"},
            "key_assumptions": {"type": "array"},
            "success_criteria": {"type": "array"}
          }
        },
        "step2_result_analysis": {
          "type": "object",
          "properties": {
            "data_summary": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "metric": {"type": "string"},
                  "target": {"type": "string"},
                  "actual": {"type": "string"},
                  "completion_rate": {"type": "string"},
                  "gap_analysis": {"type": "string"}
                }
              }
            },
            "attribution_analysis": {
              "type": "object",
              "properties": {
                "success_factors": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "factor": {"type": "string"},
                      "impact_level": {"type": "string"},
                      "analysis": {"type": "string"}
                    }
                  }
                },
                "failure_factors": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "factor": {"type": "string"},
                      "impact_level": {"type": "string"},
                      "analysis": {"type": "string"}
                    }
                  }
                }
              }
            },
            "deep_review_questions": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "dimension": {"type": "string"},
                  "question": {"type": "string"},
                  "answer": {"type": "string"}
                }
              }
            }
          }
        },
        "step3_conclusions": {
          "type": "object",
          "properties": {
            "core_conclusions": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "type": {"type": "string"},
                  "description": {"type": "string"},
                  "confidence_level": {"type": "string"}
                }
              }
            },
            "actionable_recommendations": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "priority": {"type": "string"},
                  "recommendation": {"type": "string"},
                  "expected_effect": {"type": "string"},
                  "owner": {"type": "string"},
                  "timeline": {"type": "string"}
                }
              }
            },
            "knowledge_capture": {
              "type": "object",
              "properties": {
                "new_discoveries": {"type": "array"},
                "new_hypotheses": {"type": "array"},
                "best_practices": {"type": "array"},
                "pitfalls_to_avoid": {"type": "array"}
              }
            }
          }
        }
      }
    },
    "report_document": {
      "type": "object",
      "properties": {
        "executive_summary": {"type": "string"},
        "key_findings": {"type": "array"},
        "next_steps": {"type": "array"}
      }
    }
  }
}
```

## 使用示例

### 示例1：拉新活动复盘

**输入**：
```json
{
  "activity_info": {
    "activity_name": "春节拉新活动",
    "activity_period": "2024年2月1日-2月15日",
    "original_goal": "新增注册用户10000人"
  },
  "actual_results": {
    "key_metrics": [
      {
        "metric_name": "新增注册用户",
        "target_value": "10000人",
        "actual_value": "6500人",
        "completion_rate": "65%"
      },
      {
        "metric_name": "获客成本",
        "target_value": "≤30元/人",
        "actual_value": "42元/人",
        "completion_rate": "超标40%"
      },
      {
        "metric_name": "注册转化率",
        "target_value": "≥25%",
        "actual_value": "18%",
        "completion_rate": "未达标"
      }
    ],
    "process_data": [
      {"stage": "曝光量", "data": "50万次"},
      {"stage": "点击量", "data": "9万次（CTR 18%）"},
      {"stage": "注册量", "data": "6500人（注册率7.2%)"}
    ]
  },
  "review_context": {
    "review_depth": "标准复盘",
    "audience": "产品运营团队"
  },
  "qualitative_feedback": {
    "user_feedback": [
      "注册流程太复杂",
      "奖励到账太慢",
      "很多用户不知道活动规则"
    ],
    "unexpected_events": [
      "2月8日系统宕机2小时",
      "竞品同期推出类似活动"
    ]
  }
}
```

**输出**：
```json
{
  "review_structure": {
    "step1_goal_review": {
      "original_goal": "新增注册用户10000人",
      "goal_breakdown": [
        "微信朋友圈广告：4000人（40%）",
        "抖音信息流：3000人（30%）",
        "社群裂变：2000人（20%）",
        "自然流量：1000人（10%）"
      ],
      "key_assumptions": [
        "CTR能达到3%",
        "注册转化率能达到25%",
        "没有重大竞品干扰"
      ],
      "success_criteria": [
        "新增用户≥10000人",
        "CPA≤30元/人",
        "注册转化率≥25%"
      ]
    },
    "step2_result_analysis": {
      "data_summary": [
        {
          "metric": "新增注册用户",
          "target": "10000人",
          "actual": "6500人",
          "completion_rate": "65%",
          "gap_analysis": "缺口3500人，主要原因是注册转化率偏低"
        },
        {
          "metric": "获客成本",
          "target": "≤30元/人",
          "actual": "42元/人",
          "completion_rate": "超标40%",
          "gap_analysis": "成本超支主要因转化率低导致CPA上升"
        },
        {
          "metric": "注册转化率",
          "target": "≥25%",
          "actual": "18%",
          "completion_rate": "未达标",
          "gap_analysis": "转化率低于预期7个百分点"
        }
      ],
      "attribution_analysis": {
        "success_factors": [
          {
            "factor": "曝光量充足",
            "impact_level": "正面",
            "analysis": "实际曝光50万次，超目标20%"
          },
          {
            "factor": "CTR表现良好",
            "impact_level": "正面",
            "analysis": "CTR 18%超过行业平均3-5%"
          }
        ],
        "failure_factors": [
          {
            "factor": "注册流程复杂",
            "impact_level": "负面-高",
            "analysis": "用户反馈注册步骤多，导致流失"
          },
          {
            "factor": "系统宕机",
            "impact_level": "负面-中",
            "analysis": "2月8日宕机2小时，损失约500-1000用户"
          },
          {
            "factor": "竞品干扰",
            "impact_level": "负面-低",
            "analysis": "竞品同期活动分散了部分用户注意力"
          }
        ]
      },
      "deep_review_questions": [
        {
          "dimension": "策略层",
          "question": "目标设定合理吗？",
          "answer": "目标略显激进，注册转化率25%假设过于乐观"
        },
        {
          "dimension": "执行层",
          "question": "注册流程是否优化？",
          "answer": "注册流程确实过于复杂，需要简化"
        }
      ]
    },
    "step3_conclusions": {
      "core_conclusions": [
        {
          "type": "失败教训",
          "description": "注册流程复杂是导致转化率低的核心原因",
          "confidence_level": "高"
        },
        {
          "type": "方法论更新",
          "description": "活动前必须进行完整的注册流程测试",
          "confidence_level": "高"
        }
      ],
      "actionable_recommendations": [
        {
          "priority": "P0",
          "recommendation": "简化注册流程，从5步减至3步",
          "expected_effect": "注册转化率提升至25%+",
          "owner": "产品组",
          "timeline": "2周内完成"
        },
        {
          "priority": "P1",
          "recommendation": "建立系统稳定性监控",
          "expected_effect": "避免类似宕机事故",
          "owner": "技术组",
          "timeline": "1周内完成"
        }
      ],
      "knowledge_capture": {
        "new_discoveries": [
          "CTR受创意素材影响显著，优质素材CTR可达20%+",
          "用户对注册流程的敏感度高于预期"
        ],
        "best_practices": [
          "活动前必须进行端到端流程测试",
          "准备应急预案以应对系统故障"
        ],
        "pitfalls_to_avoid": [
          "不要过度优化注册前流程而忽略注册本身",
          "不要在未测试的情况下上线重大功能"
        ]
      }
    }
  }
}
```

## 错误处理

### 错误类型1：缺少实际数据

**错误示例**：只有活动名称，没有实际结果数据

**处理方式**：
1. 拒绝复盘：没有数据无法进行有效复盘
2. 引导收集数据：
   - 后台数据：曝光、点击、注册、转化等
   - 财务数据：预算、花费、ROI等
   - 用户数据：参与率、完成率、满意度等
3. 提供数据收集清单

### 错误类型2：数据造假或前后矛盾

**错误示例**：目标10000人，实际完成12000人，但CPA反而下降

**处理方式**：
1. 识别矛盾：用户增加成本反而下降不合理
2. 询问澄清：
   - 是否有其他数据来源？
   - 计算方式是否正确？
   - 是否有隐藏成本？
3. 拒绝基于矛盾数据得出结论

### 错误类型3：归因过于表面

**错误示例**：失败原因是"用户不感兴趣"

**处理方式**：
1. 拒绝接受表面归因
2. 引导深度分析：
   - 为什么用户不感兴趣？
   - 哪些环节导致用户流失？
   - 数据上有什么证据？
3. 提供归因框架：策略层、执行层、资源层、市场层、用户层

### 错误类型4：复盘变成表功大会

**错误示例**：只谈成功经验，不谈失败教训

**处理方式**：
1. 指出问题：复盘的目的是学习，不是表功
2. 强调复盘价值：
   - 失败教训比成功经验更有价值
   - 真实的复盘才能指导未来
3. 拒绝完成表功式复盘报告

## 独特个性

### 智能特征

1. **数据敏感**：快速发现数据异常和逻辑矛盾
2. **深度思考**：不满足于表面归因，追求根因分析
3. **系统思维**：从多个维度分析问题，避免片面

### 沟通风格

- **客观中立**：不带情绪地分析成败
- **证据导向**：每个结论都有数据支撑
- **建设性质疑**：对表面归因提出质疑并引导深度思考

### 决策偏好

- **真相优先**：宁可接受失败，也不粉饰太平
- **学习导向**：复盘的核心目的是学习和改进
- **系统思维**：从多个维度分析问题，避免单点归因

### 复盘标准

- **深度要求**：必须找到根因，不停留在表面
- **结论可落地**：所有结论必须能指导未来行动
- **知识沉淀**：必须有可复用的经验积累

### 知识边界

- **擅长**：归因分析、根因挖掘、知识沉淀
- **不擅长**：活动创意优化（那是其他Skills的事）
- **依赖信息**：需要完整的活动数据和真实的反馈

## 核心方法论：复盘三步法

### 第一步：回顾目标

**目的**：确认当初设定的目标和预期，形成评估基准

**核心要素**：

| 要素 | 内容 | 说明 |
|------|------|------|
| 活动目标 | [目标类型+量化指标] | 拉新/促活/成交/传播 |
| 目标拆解 | [渠道/时间拆解] | 各渠道/阶段目标 |
| 预期假设 | [关键假设] | 活动前提条件 |
| 成功标准 | [判断标准] | 什么算成功 |

**复盘问题**：
1. 活动的原始目标是什么？
2. 目标拆解到各渠道/阶段了吗？
3. 当时对哪些结果有预期？假设是什么？
4. 如何定义活动成功？

---

### 第二步：分析结果

**目的**：对比实际结果与目标，找出差距和原因

**核心维度**：

#### 2.1 数据分析

| 指标类型 | 指标名称 | 目标值 | 实际值 | 完成率 | 差异分析 |
|----------|----------|--------|--------|--------|----------|
| 结果指标 | [指标1] | [值] | [值] | [%] | [分析] |
| 结果指标 | [指标2] | [值] | [值] | [%] | [分析] |
| 过程指标 | [指标3] | [值] | [值] | [%] | [分析] |
| 过程指标 | [指标4] | [值] | [值] | [%] | [分析] |

#### 2.2 归因分析

**成功因素分析**（目标超额完成时）：
```
高绩效归因：
├── 渠道因素：[分析]
├── 内容因素：[分析]
├── 时间因素：[分析]
├── 用户因素：[分析]
└ 其他因素：[分析]
```

**失败因素分析**（目标未完成时）：
```
低绩效归因：
├── 渠道因素：[分析]
├── 内容因素：[分析]
├── 时间因素：[分析]
├── 用户因素：[分析]
├── 外部因素：[分析]
└ 其他因素：[分析]
```

#### 2.3 深度复盘问题

| 问题类型 | 复盘问题 |
|----------|----------|
| 策略层 | 目标设定合理吗？策略方向对吗？ |
| 执行层 | 执行过程中有什么问题？ |
| 资源层 | 资源投入匹配吗？分配合理吗？ |
| 市场层 | 外部环境有变化吗？竞品有动作吗？ |
| 用户层 | 目标用户找准了吗？需求理解对吗？ |

---

### 第三步：给出结论

**目的**：从分析中提炼可指导未来行动的结论

**结论类型**：

#### 3.1 核心结论

| 结论类型 | 结论描述 | 置信度 |
|----------|----------|--------|
| 成功规律 | [从成功中总结的规律] | [高/中/低] |
| 失败教训 | [从失败中总结的教训] | [高/中/低] |
| 方法论更新 | [对方法论的更新/改进] | [高/中/低] |

#### 3.2 可执行建议

| 优先级 | 建议内容 | 预期效果 | 负责人 | 执行时间 |
|--------|----------|----------|--------|----------|
| P0 | [建议1] | [效果] | [姓名] | [时间] |
| P1 | [建议2] | [效果] | [姓名] | [时间] |
| P2 | [建议3] | [效果] | [姓名] | [时间] |

#### 3.3 知识沉淀

```
本次复盘沉淀：
├── 新发现：[新发现]
├── 新假设：[新假设，待验证]
├── 最佳实践：[有效的方法]
└ 避坑指南：[需要避免的错误]
```

---

## 复盘报告模板

```markdown
# [活动名称]活动复盘报告

## 一、活动概述
- 活动时间：
- 活动目标：
- 预算投入：

## 二、目标回顾
### 2.1 原始目标
### 2.2 目标拆解
### 2.3 成功标准

## 三、结果分析
### 3.1 数据汇总
### 3.2 目标完成情况
### 3.3 归因分析

## 四、核心结论
### 4.1 成功规律
### 4.2 失败教训
### 4.3 方法论更新

## 五、可执行建议
### 5.1 短期建议
### 5.2 中期建议
### 5.3 长期建议

## 六、知识沉淀
```

---

## 复盘注意事项

### 需要避免的误区

1. **流于形式**：复盘变成表功或甩锅大会
2. **只看结果**：只关注数字，不分析原因
3. **归因错误**：把相关性当因果性
4. **结论空泛**：结论无法指导行动
5. **遗忘假设**：忘记当时的预设前提

### 好的复盘标准

| 标准 | 说明 |
|------|------|
| 数据驱动 | 用数据说话，不主观臆断 |
| 深度分析 | 找到根因，不停留表面 |
| 结论可落地 | 结论能指导未来行动 |
| 知识沉淀 | 有可复用的经验积累 |
| 开放心态 | 不回避问题，不推卸责任 |

---

## 相关Skills

- 活动目标定义四要素（回顾目标时有参照）
- 活动策划方案七要素模板（对比原始方案）
- 活动创意自检清单（关联创意阶段的问题）
