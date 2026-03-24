"""
Conversation Chain AST - 对话链结构化表示
=========================================

提供对话链的抽象语法树表示，支持：
- 节点类型定义 (用户消息、助手消息、系统消息、工具调用等)
- 链式结构 (前驱/后继关系)
- 序列化/反序列化
- 语义分组和分段

参考: PentAGI Chain Summarization
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class NodeType(str, Enum):
    """对话链节点类型"""
    # 消息类型
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    SYSTEM_MESSAGE = "system_message"
    TOOL_MESSAGE = "tool_message"

    # 结构类型
    SECTION_HEADER = "section_header"
    QA_PAIR = "qa_pair"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

    # 压缩类型
    SUMMARIZED = "summarized"
    COMPRESSED = "compressed"

    # 元数据
    METADATA = "metadata"


class MessageRole(str, Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ChainNode:
    """
    对话链中的单个节点

    Attributes:
        id: 唯一标识符
        type: 节点类型
        content: 原始内容
        summary: 压缩后的摘要 (用于已压缩节点)
        metadata: 附加元数据
        parent_id: 父节点ID (用于嵌套结构)
        prev_id: 前驱节点ID
        next_id: 后继节点ID
        created_at: 创建时间
        token_count: Token 数量
        compressed: 是否已压缩
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: NodeType = NodeType.USER_MESSAGE
    content: str = ""
    summary: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    parent_id: Optional[str] = None
    prev_id: Optional[str] = None
    next_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    token_count: int = 0
    compressed: bool = False

    def __post_init__(self):
        if not self.token_count and self.content:
            # 简单的 token 估算 (中文约 1.5 字符/token, 英文约 4 字符/token)
            self.token_count = self._estimate_tokens()

    def _estimate_tokens(self) -> int:
        """估算 token 数量"""
        # 简化的估算: 中文 * 0.7 + 英文 * 0.25 + 特殊字符
        chinese_chars = sum(1 for c in self.content if '\u4e00' <= c <= '\u9fff')
        english_chars = sum(1 for c in self.content if c.isascii() and c.isalpha())
        other_chars = len(self.content) - chinese_chars - english_chars

        return int(chinese_chars * 0.7 + english_chars * 0.25 + other_chars * 0.5)


@dataclass
class ConversationChain:
    """
    对话链 - 完整的对话历史表示

    Attributes:
        id: 链的唯一标识符
        nodes: 节点字典 (id -> node)
        head: 头节点ID
        tail: 尾节点ID
        sections: 分段信息
        metadata: 链级元数据
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nodes: dict[str, ChainNode] = field(default_factory=dict)
    head: Optional[str] = None
    tail: Optional[str] = None
    sections: dict[str, dict] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Token 预算配置
    max_tokens: int = 100000
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95

    def add_node(self, node: ChainNode, after: Optional[str] = None) -> ChainNode:
        """
        添加节点到链中

        Args:
            node: 要添加的节点
            after: 在指定节点之后插入 (None 表示添加到末尾)

        Returns:
            添加的节点
        """
        node_id = node.id

        if not self.nodes:
            # 第一个节点
            self.head = node_id
            self.tail = node_id
            node.prev_id = None
            node.next_id = None
        elif after is None:
            # 添加到末尾
            tail_node = self.nodes[self.tail]
            tail_node.next_id = node_id
            node.prev_id = self.tail
            node.next_id = None
            self.tail = node_id
        else:
            # 插入到指定位置
            after_node = self.nodes[after]
            node.prev_id = after
            node.next_id = after_node.next_id
            node.parent_id = after_node.parent_id

            if after_node.next_id:
                next_node = self.nodes[after_node.next_id]
                next_node.prev_id = node_id

            after_node.next_id = node_id

            if self.tail == after:
                self.tail = node_id

        self.nodes[node_id] = node
        self.updated_at = datetime.now()
        return node

    def remove_node(self, node_id: str) -> Optional[ChainNode]:
        """
        从链中移除节点

        Args:
            node_id: 要移除的节点ID

        Returns:
            被移除的节点，如果不存在则返回 None
        """
        if node_id not in self.nodes:
            return None

        node = self.nodes[node_id]

        # 更新链表指针
        if node.prev_id and node.prev_id in self.nodes:
            self.nodes[node.prev_id].next_id = node.next_id

        if node.next_id and node.next_id in self.nodes:
            self.nodes[node.next_id].prev_id = node.prev_id

        # 更新 head/tail
        if self.head == node_id:
            self.head = node.next_id
        if self.tail == node_id:
            self.tail = node.prev_id

        del self.nodes[node_id]
        self.updated_at = datetime.now()

        return node

    def get_node_sequence(self) -> list[ChainNode]:
        """获取按顺序排列的节点列表"""
        if not self.head:
            return []

        sequence = []
        current_id = self.head

        while current_id:
            node = self.nodes.get(current_id)
            if node:
                sequence.append(node)
                current_id = node.next_id
            else:
                break

        return sequence

    def get_total_tokens(self) -> int:
        """获取链的总 token 数"""
        return sum(node.token_count for node in self.nodes.values())

    def get_message_count(self) -> int:
        """获取消息数量"""
        return sum(1 for node in self.nodes.values()
                   if node.type in (NodeType.USER_MESSAGE,
                                    NodeType.ASSISTANT_MESSAGE,
                                    NodeType.SYSTEM_MESSAGE))

    def create_section(self, section_id: str, start_id: str, end_id: str,
                       section_type: str = "default") -> dict:
        """
        创建分段

        Args:
            section_id: 分段ID
            start_id: 起始节点ID
            end_id: 结束节点ID
            section_type: 分段类型

        Returns:
            分段信息字典
        """
        section = {
            "id": section_id,
            "type": section_type,
            "start_id": start_id,
            "end_id": end_id,
            "created_at": datetime.now().isoformat(),
        }

        self.sections[section_id] = section
        return section

    def get_section_nodes(self, section_id: str) -> list[ChainNode]:
        """获取分段内的节点"""
        if section_id not in self.sections:
            return []

        section = self.sections[section_id]
        start_id = section["start_id"]
        end_id = section["end_id"]

        nodes = []
        current_id = start_id

        while current_id and current_id != end_id:
            node = self.nodes.get(current_id)
            if node:
                nodes.append(node)
                current_id = node.next_id
            else:
                break

        # 添加 end_id 对应的节点
        end_node = self.nodes.get(end_id)
        if end_node:
            nodes.append(end_node)

        return nodes

    def get_compression_ratio(self) -> float:
        """获取当前压缩率"""
        total = self.get_total_tokens()
        if total == 0:
            return 0.0
        return total / self.max_tokens


class ChainSerializer:
    """对话链序列化器"""

    @staticmethod
    def to_json(chain: ConversationChain, include_content: bool = True) -> str:
        """
        序列化为 JSON 字符串

        Args:
            chain: 对话链
            include_content: 是否包含完整内容 (False 则只保留摘要)

        Returns:
            JSON 字符串
        """
        data = {
            "id": chain.id,
            "metadata": chain.metadata,
            "max_tokens": chain.max_tokens,
            "warning_threshold": chain.warning_threshold,
            "critical_threshold": chain.critical_threshold,
            "created_at": chain.created_at.isoformat(),
            "updated_at": chain.updated_at.isoformat(),
            "head": chain.head,
            "tail": chain.tail,
            "sections": chain.sections,
            "nodes": {},
        }

        for node_id, node in chain.nodes.items():
            node_data = {
                "id": node.id,
                "type": node.type.value,
                "summary": node.summary,
                "metadata": node.metadata,
                "parent_id": node.parent_id,
                "prev_id": node.prev_id,
                "next_id": node.next_id,
                "created_at": node.created_at.isoformat(),
                "token_count": node.token_count,
                "compressed": node.compressed,
            }

            if include_content:
                node_data["content"] = node.content
            elif node.summary:
                node_data["content"] = node.summary
            else:
                node_data["content"] = ""

            data["nodes"][node_id] = node_data

        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def to_dict(chain: ConversationChain, include_content: bool = True) -> dict:
        """序列化为字典"""
        data = json.loads(ChainSerializer.to_json(chain, include_content))
        return data


class ChainDeserializer:
    """对话链反序列化器"""

    @staticmethod
    def from_json(json_str: str) -> ConversationChain:
        """
        从 JSON 字符串反序列化

        Args:
            json_str: JSON 字符串

        Returns:
            对话链对象
        """
        data = json.loads(json_str)

        chain = ConversationChain(
            id=data.get("id", str(uuid.uuid4())),
            metadata=data.get("metadata", {}),
            max_tokens=data.get("max_tokens", 100000),
            warning_threshold=data.get("warning_threshold", 0.8),
            critical_threshold=data.get("critical_threshold", 0.95),
        )

        if "created_at" in data:
            chain.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            chain.updated_at = datetime.fromisoformat(data["updated_at"])

        chain.head = data.get("head")
        chain.tail = data.get("tail")
        chain.sections = data.get("sections", {})

        nodes_data = data.get("nodes", {})
        for node_id, node_data in nodes_data.items():
            node = ChainNode(
                id=node_data.get("id", node_id),
                type=NodeType(node_data.get("type", "user_message")),
                content=node_data.get("content", ""),
                summary=node_data.get("summary"),
                metadata=node_data.get("metadata", {}),
                parent_id=node_data.get("parent_id"),
                prev_id=node_data.get("prev_id"),
                next_id=node_data.get("next_id"),
                token_count=node_data.get("token_count", 0),
                compressed=node_data.get("compressed", False),
            )

            if "created_at" in node_data:
                node.created_at = datetime.fromisoformat(node_data["created_at"])

            chain.nodes[node_id] = node

        return chain

    @staticmethod
    def from_dict(data: dict) -> ConversationChain:
        """从字典反序列化"""
        return ChainDeserializer.from_json(json.dumps(data))
