"""
CyberTeam 上下文压缩系统
=========================

基于 PentAGI Chain Summarization 设计的上下文压缩系统，包含：
- Conversation Chain AST: 对话链结构化表示
- Section Summarization: 分段压缩
- QA Pair Summarization: 问答对压缩
- Token Budget Management: Token 预算管理

版本: v2.1
"""

from .ast import (
    ConversationChain,
    ChainNode,
    NodeType,
    MessageRole,
    ChainSerializer,
    ChainDeserializer,
)
from .section_summarizer import (
    SectionSummarizer,
    SectionType,
    CompressionLevel,
    SummarizationStrategy,
)
from .qa_summarizer import (
    QAPairSummarizer,
    QAPair,
    QAType,
    AbstractionLevel,
)
from .token_budget import (
    TokenBudget,
    BudgetPolicy,
    CompressionTrigger,
    BudgetManager,
)

__version__ = "2.1.0"

__all__ = [
    # AST
    "ConversationChain",
    "ChainNode",
    "NodeType",
    "MessageRole",
    "ChainSerializer",
    "ChainDeserializer",
    # Section
    "SectionSummarizer",
    "SectionType",
    "CompressionLevel",
    "SummarizationStrategy",
    # QA
    "QAPairSummarizer",
    "QAPair",
    "QAType",
    "AbstractionLevel",
    # Token Budget
    "TokenBudget",
    "BudgetPolicy",
    "CompressionTrigger",
    "BudgetManager",
]
