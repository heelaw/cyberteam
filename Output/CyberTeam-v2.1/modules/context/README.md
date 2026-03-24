# CyberTeam Context Compression System

基于 PentAGI Chain Summarization 设计的上下文压缩系统。

## 模块结构

```
modules/context/
├── __init__.py           # 模块入口
├── ast.py                # Conversation Chain AST
├── section_summarizer.py # Section Summarization
├── qa_summarizer.py      # QA Pair Summarization
├── token_budget.py       # Token Budget Management
└── README.md             # 本文件
```

## 快速开始

```python
from modules.context import (
    ConversationChain,
    ChainNode,
    NodeType,
    SectionSummarizer,
    CompressionLevel,
    QAPairSummarizer,
    AbstractionLevel,
    BudgetManager,
    BudgetPolicy,
)

# 1. 创建对话链
chain = ConversationChain(max_tokens=100000)

# 添加节点
user_msg = ChainNode(
    type=NodeType.USER_MESSAGE,
    content="帮我写一个排序算法"
)
chain.add_node(user_msg)

assistant_msg = ChainNode(
    type=NodeType.ASSISTANT_MESSAGE,
    content="我来为你实现一个快速排序算法..."
)
chain.add_node(assistant_msg)

# 2. 分段压缩
summarizer = SectionSummarizer()
section = summarizer.create_section_from_content(
    "这里是讨论内容...",
    SectionType.DISCUSSION
)
summarizer.compress(section, CompressionLevel.MEDIUM)

# 3. QA对压缩
qa_summarizer = QAPairSummarizer()
qa = qa_summarizer.create_qa_pair(
    question="如何实现快速排序?",
    answer="快速排序使用分治法..."
)
qa_summarizer.abstract(qa, AbstractionLevel.SEMANTIC)

# 4. Token预算管理
budget_mgr = BudgetManager(max_tokens=100000)
budget_mgr.register_node("node_1", 5000)
budget_mgr.register_node("node_2", 3000)
budget_mgr.allocate(2000)

print(budget_mgr.get_status())
```

## 核心概念

### Conversation Chain AST

对话链的抽象语法树表示，支持：
- 节点类型定义 (用户/助手/系统/工具消息)
- 链式结构 (前驱/后继关系)
- 语义分段
- 序列化/反序列化

### Section Summarization

分段压缩器，支持：
- 自动检测分段类型
- 多种压缩级别 (none/light/medium/aggressive/ultimate)
- 摘要生成策略 (key_points/hierarchical/abstract)
- 关键信息提取

### QA Pair Summarization

问答对压缩器，支持：
- 问答类型检测
- 多级抽象 (concrete/semantic/template/categorical)
- 实体提取
- 问答聚类

### Token Budget Management

Token预算管理器，支持：
- 预算分配/追踪
- 多级阈值 (warning/critical)
- 压缩策略 (FIFO/LRU/priority/adaptive/conservative)
- 压缩历史记录

## 依赖

- Python 3.8+
- 无外部依赖 (可选: Anthropic SDK 用于智能摘要)

## 参考

- [PentAGI Chain Summarization](https://github.com/vxcontrol/pentagi)
