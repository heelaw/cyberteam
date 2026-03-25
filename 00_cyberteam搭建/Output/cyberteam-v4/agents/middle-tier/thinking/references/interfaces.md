# interfaces - 思维注入中台

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `scene` | string | 场景类型（战略规划/产品设计/技术架构等） |
| `query` | string | 用户Query/问题描述 |
| `intensity` | enum | 注入强度（高/中/低）（可选，默认自动判断） |
| `expert_ids` | string[] | 指定专家ID列表（可选，不指定则自动匹配） |
| `context` | object | 附加上下文（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `experts` | Expert[] | 匹配到的专家列表 |
| `injected_analysis` | Analysis | 专家思维注入后的分析结果 |
| `confidence` | float | 综合置信度（0-1） |
| `report` | InjectionReport | 详细的思维注入报告 |

## Expert 结构

```yaml
Expert:
  id: string              # 专家ID (e.g., ST-001, PD-002)
  name: string            # 专家名称
  category: string        # 专家类别 (战略类/产品类/技术类等)
  core_thinking: string   # 核心思维
  relevance_score: float  # 相关度评分 (0-1)
```

## InjectionReport 结构

```yaml
InjectionReport:
  scene_recognition: SceneType    # 识别的场景类型
  injected_experts: string[]      # 注入的专家ID列表
  expert_count: int              # 注入专家数量
  injection_intensity: float     # 注入强度百分比
  synergy_score: float          # 协同度评分
  confidence: float             # 综合置信度
  reasoning: string            # 匹配推理过程
```

## 场景类型映射

| 场景类型 | 触发关键词 | 推荐专家数量 | 注入强度 |
|----------|------------|--------------|----------|
| 战略规划 | 战略、规划、方向、长期 | 3-5 | 高 |
| 产品设计 | 产品、功能、需求、体验 | 2-4 | 中高 |
| 技术架构 | 架构、技术、系统、性能 | 2-4 | 中高 |
| 运营规划 | 运营、增长、用户、活动 | 2-3 | 中 |
| 营销推广 | 营销、品牌、推广、渠道 | 2-3 | 中 |
| 数据分析 | 数据、分析、指标、报表 | 2-4 | 中 |
| 团队管理 | 团队、管理、组织、绩效 | 2-3 | 中低 |
| 风险评估 | 风险、危机、合规、安全 | 3-4 | 高 |
| 创新突破 | 创新、颠覆、破局、变革 | 3-5 | 高 |
| 财务决策 | 财务、投资、预算、成本 | 2-3 | 中 |

## 调用示例

```python
from agents.middle-tier.thinking import ThinkingHub

thinking = ThinkingHub()
result = thinking.inject(scene="战略规划", query="进入智能家居市场应该怎么做")

# 返回示例
{
    "experts": [
        {"id": "ST-001", "name": "战略之父", "category": "战略类", "core_thinking": "5W1H1Y分析", "relevance_score": 0.95},
        {"id": "ST-002", "name": "MECE大师", "category": "战略类", "core_thinking": "分类分层", "relevance_score": 0.88},
        {"id": "DC-001", "name": "决策科学家", "category": "决策类", "core_thinking": "决策分析", "relevance_score": 0.82}
    ],
    "confidence": 0.88,
    "report": {
        "scene_recognition": "战略规划",
        "injected_experts": ["ST-001", "ST-002", "DC-001"],
        "expert_count": 3,
        "injection_intensity": 0.8,
        "synergy_score": 0.75,
        "confidence": 0.88,
        "reasoning": "基于关键词'进入'、'市场'、'怎么做'识别为战略规划场景..."
    }
}
```
