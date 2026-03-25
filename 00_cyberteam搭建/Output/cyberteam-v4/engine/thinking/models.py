"""
思维模型数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class ModelCategory(Enum):
    """思维模型分类"""
    # 分析类
    ANALYSIS = "分析"
    # 决策类
    DECISION = "决策"
    # 创造类
    CREATIVE = "创造"
    # 评估类
    EVALUATION = "评估"
    # 系统类
    SYSTEM = "系统"


@dataclass
class ThinkingModel:
    """思维模型定义"""
    id: str                          # 唯一标识: "first-principle"
    name: str                        # 显示名称: "第一性原理"
    category: ModelCategory          # 分类
    description: str                  # 简短描述
    trigger_keywords: List[str]      # 触发关键词
    input_schema: Dict[str, Any]     # 输入schema
    output_schema: Dict[str, Any]     # 输出schema
    example: Optional[str] = None     # 使用示例
    priority: int = 5                # 优先级 1-10

    @classmethod
    def from_dict(cls, data: Dict) -> "ThinkingModel":
        return cls(
            id=data["id"],
            name=data["name"],
            category=ModelCategory(data.get("category", "ANALYSIS")),
            description=data.get("description", ""),
            trigger_keywords=data.get("trigger_keywords", []),
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            example=data.get("example"),
            priority=data.get("priority", 5)
        )

    def to_prompt(self) -> str:
        """转换为注入给 Agent 的提示词"""
        return f"""【思维模型: {self.name}】
{self.description}

使用方法：
- 当遇到问题时，先用此模型分析
- 按照模型的框架结构进行思考
- 输出符合 output_schema 的结果
"""


@dataclass
class ModelCombination:
    """思维模型组合"""
    models: List[ThinkingModel]
    reasoning: str                    # 为什么选择这个组合

    def to_prompt(self) -> str:
        """生成组合提示词"""
        prompts = [m.to_prompt() for m in self.models]
        header = f"""【思维决策开始】
本次决策需要使用 {len(self.models)} 个思维模型：
"""
        footer = """
【思维决策结束】
请先用以上模型分析问题，然后给出你的决策建议。
"""
        return header + "\n\n".join(prompts) + footer


@dataclass
class TaskContext:
    """任务上下文"""
    task_description: str             # 任务描述
    intent: str                       # 意图类型
    complexity: str                   # 复杂度
    domain: str                       # 领域
    constraints: List[str] = field(default_factory=list)  # 约束条件
    available_time: Optional[str] = None  # 可用时间
    resources: List[str] = field(default_factory=list)   # 可用资源

    def to_analysis_text(self) -> str:
        return f"""任务：{self.task_description}
意图：{self.intent}
复杂度：{self.complexity}
领域：{self.domain}
约束：{', '.join(self.constraints) if self.constraints else '无'}
"""


@dataclass
class ThinkingResult:
    """思维分析结果"""
    model_id: str                     # 使用的模型
    model_name: str                   # 模型名称
    analysis: str                      # 分析内容
    key_findings: List[str] = field(default_factory=list)  # 关键发现
    recommendations: List[str] = field(default_factory=list)  # 建议
    confidence: float = 0.5           # 置信度 0-1
    raw_output: Optional[Dict] = None  # 原始输出

    def to_agent_context(self) -> str:
        """转换为 Agent 可用的上下文"""
        findings = "\n".join([f"- {f}" for f in self.key_findings])
        recs = "\n".join([f"- {r}" for r in self.recommendations])
        return f"""【{self.model_name} 分析结果】
关键发现：
{findings if findings else "（无）"}

建议：
{recs if recs else "（无）"}

置信度：{self.confidence:.0%}
"""
