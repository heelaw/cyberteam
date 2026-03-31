"""
Context Manager - 分层Context管理系统
来源: OpenViking/
功能: 分层Context压缩，Token优化，避免上下文膨胀
"""
import logging
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ContextLayer(Enum):
    """Context层级"""
    CORE = "core"           # 核心层：当前任务关键信息
    HISTORY = "history"    # 历史层：之前的分析结论
    TEMP = "temp"          # 临时层：临时缓存
    ARCHIVE = "archive"    # 归档层：已完成任务


@dataclass
class ContextChunk:
    """Context块"""
    layer: ContextLayer
    content: str
    tokens: int
    priority: int = 0  # 0-100, 越高越重要
    created_at: datetime = field(default_factory=datetime.now)
    compressed: bool = False


@dataclass
class ContextStats:
    """Context统计"""
    total_tokens: int
    total_chunks: int
    layer_distribution: Dict[ContextLayer, int]
    compression_ratio: float


class ContextManager:
    """
    分层Context管理器 - OpenViking架构实现

    功能:
    1. 分层存储不同类型的Context
    2. Token计数和限制
    3. 智能压缩
    4. 动态切换

    使用示例:
    >>> ctx = ContextManager(max_tokens=100000)
    >>> ctx.add(ContextLayer.CORE, "当前任务关键信息")
    >>> ctx.add(ContextLayer.HISTORY, "之前的分析结论")
    >>> ctx.compress()  # 压缩到限制内
    >>> full = ctx.expand()  # 解压展示
    """

    # Token估算（简单实现，实际应使用tiktoken等）
    TOKENS_PER_CHAR = 0.25

    def __init__(self, max_tokens: int = 100000):
        """
        初始化ContextManager

        Args:
            max_tokens: 最大Token限制
        """
        self._max_tokens = max_tokens
        self._chunks: Dict[ContextLayer, List[ContextChunk]] = {
            layer: [] for layer in ContextLayer
        }
        self._total_tokens = 0
        self._compression_count = 0

        logger.info(f"ContextManager 初始化完成 (max_tokens={max_tokens})")

    def add(
        self,
        layer: ContextLayer,
        content: str,
        priority: int = 50,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        添加Context

        Args:
            layer: 层级（接受ContextLayer枚举或字符串如"core", "history", "temp"）
            content: 内容
            priority: 优先级 (0-100)
            metadata: 元数据

        Returns:
            bool: 是否添加成功
        """
        # 自动转换字符串到枚举
        if isinstance(layer, str):
            layer = ContextLayer(layer)

        tokens = self._estimate_tokens(content)

        chunk = ContextChunk(
            layer=layer,
            content=content,
            tokens=tokens,
            priority=priority
        )

        self._chunks[layer].append(chunk)
        self._total_tokens += tokens

        logger.debug(f"Context添加: {layer.value}, {tokens} tokens, priority={priority}")

        # 检查是否需要压缩
        if self._total_tokens > self._max_tokens:
            self.compress()

        return True

    def get(self, layer: Optional[ContextLayer] = None) -> List[ContextChunk]:
        """
        获取Context

        Args:
            layer: 层级过滤，None表示全部

        Returns:
            List[ContextChunk]: Context块列表
        """
        if layer:
            return self._chunks.get(layer, [])
        # 按优先级排序返回所有
        all_chunks = []
        for chunks in self._chunks.values():
            all_chunks.extend(chunks)
        return sorted(all_chunks, key=lambda c: c.priority, reverse=True)

    def get_text(self, layer: Optional[ContextLayer] = None) -> str:
        """
        获取文本形式

        Args:
            layer: 层级过滤

        Returns:
            str: 拼接的文本
        """
        chunks = self.get(layer)
        return "\n\n".join(c.content for c in chunks if not c.compressed)

    def compress(self, target_tokens: Optional[int] = None) -> int:
        """
        压缩Context到限制内

        Args:
            target_tokens: 目标Token数，None表示_max_tokens

        Returns:
            int: 压缩的Token数
        """
        if target_tokens is None:
            target_tokens = int(self._max_tokens * 0.8)  # 默认压缩到80%

        initial_tokens = self._total_tokens
        removed_tokens = 0

        # 按优先级从低到高删除
        all_chunks = self.get()
        all_chunks.sort(key=lambda c: c.priority)

        for chunk in all_chunks:
            if self._total_tokens - removed_tokens <= target_tokens:
                break

            # 归档而非删除
            chunk.layer = ContextLayer.ARCHIVE
            chunk.compressed = True
            removed_tokens += chunk.tokens
            self._compression_count += 1

        self._total_tokens -= removed_tokens

        logger.info(f"Context压缩: {initial_tokens} -> {self._total_tokens} tokens (移除{removed_tokens})")
        return removed_tokens

    def expand(self) -> str:
        """
        解压展示完整Context

        Returns:
            str: 完整Context文本
        """
        # 按层级组织输出
        result_parts = []

        for layer in [ContextLayer.CORE, ContextLayer.HISTORY, ContextLayer.TEMP]:
            chunks = self._chunks[layer]
            if chunks:
                layer_chunks = [c.content for c in chunks if not c.compressed]
                if layer_chunks:
                    result_parts.append(f"=== {layer.value.upper()} ===")
                    result_parts.append("\n\n".join(layer_chunks))

        return "\n\n".join(result_parts)

    def clear(self, layer: Optional[ContextLayer] = None):
        """
        清除Context

        Args:
            layer: 层级过滤，None表示全部
        """
        if layer:
            tokens = sum(c.tokens for c in self._chunks[layer])
            self._chunks[layer] = []
            self._total_tokens -= tokens
            logger.info(f"Context清除: {layer.value}, {tokens} tokens")
        else:
            self._chunks = {layer: [] for layer in ContextLayer}
            self._total_tokens = 0
            logger.info("Context全部清除")

    def stats(self) -> ContextStats:
        """
        获取统计信息

        Returns:
            ContextStats: 统计信息
        """
        layer_dist = {
            layer: len(chunks)
            for layer, chunks in self._chunks.items()
        }

        return ContextStats(
            total_tokens=self._total_tokens,
            total_chunks=sum(layer_dist.values()),
            layer_distribution=layer_dist,
            compression_ratio=self._compression_count / max(1, self._total_tokens)
        )

    def _estimate_tokens(self, text: str) -> int:
        """
        估算Token数

        Args:
            text: 文本

        Returns:
            int: 估算的Token数
        """
        return max(1, int(len(text) * self.TOKENS_PER_CHAR))

    def to_dict(self) -> Dict:
        """
        导出为Dict

        Returns:
            Dict: 导出数据
        """
        return {
            "max_tokens": self._max_tokens,
            "total_tokens": self._total_tokens,
            "chunks": {
                layer.value: [
                    {
                        "content": c.content,
                        "tokens": c.tokens,
                        "priority": c.priority,
                        "compressed": c.compressed
                    }
                    for c in chunks
                ]
                for layer, chunks in self._chunks.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ContextManager":
        """
        从Dict恢复

        Args:
            data: 导出数据

        Returns:
            ContextManager: 恢复的实例
        """
        manager = cls(max_tokens=data.get("max_tokens", 100000))

        for layer_str, chunks_data in data.get("chunks", {}).items():
            layer = ContextLayer(layer_str)
            for chunk_data in chunks_data:
                chunk = ContextChunk(
                    layer=layer,
                    content=chunk_data["content"],
                    tokens=chunk_data["tokens"],
                    priority=chunk_data.get("priority", 50),
                    compressed=chunk_data.get("compressed", False)
                )
                manager._chunks[layer].append(chunk)
                manager._total_tokens += chunk.tokens

        return manager


# 全局实例
CONTEXT = ContextManager()
