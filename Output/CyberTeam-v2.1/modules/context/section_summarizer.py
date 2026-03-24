"""
Section Summarization - 分段压缩
=================================

提供对话分段压缩功能，包括：
- 分段类型定义
- 压缩级别控制
- 摘要生成策略
- 关键信息提取

参考: PentAGI Chain Summarization
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional


class SectionType(str, Enum):
    """分段类型"""
    TASK = "task"              # 任务描述段
    DISCUSSION = "discussion"  # 讨论段
    CODE = "code"             # 代码段
    TOOL_USE = "tool_use"     # 工具使用段
    RESULT = "result"         # 结果段
    ERROR = "error"           # 错误段
    SYSTEM = "system"         # 系统段
    DEFAULT = "default"        # 默认段


class CompressionLevel(str, Enum):
    """压缩级别"""
    NONE = "none"           # 不压缩
    LIGHT = "light"         # 轻度压缩 (保留 70%)
    MEDIUM = "medium"       # 中度压缩 (保留 40%)
    AGGRESSIVE = "aggressive"  # 激进压缩 (保留 15%)
    ULTIMATE = "ultimate"   # 极限压缩 (保留 5%)


class SummarizationStrategy(str, Enum):
    """摘要生成策略"""
    FIRST_MESSAGE = "first_message"     # 只保留首条消息
    LAST_MESSAGE = "last_message"       # 只保留最后消息
    KEY_POINTS = "key_points"           # 提取关键点
    SEMANTIC_DEDUP = "semantic_dedup"   # 语义去重
    HIERARCHICAL = "hierarchical"       # 层级摘要
    ABSTRACT = "abstract"               # 抽象摘要


@dataclass
class Section:
    """
    对话分段

    Attributes:
        id: 分段唯一ID
        type: 分段类型
        nodes: 节点ID列表
        summary: 生成的摘要
        compression_level: 使用的压缩级别
        key_points: 提取的关键点
        created_at: 创建时间
        token_count: 原始token数
        compressed_token_count: 压缩后token数
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: SectionType = SectionType.DEFAULT
    nodes: list[str] = field(default_factory=list)
    summary: Optional[str] = None
    compression_level: CompressionLevel = CompressionLevel.NONE
    key_points: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    token_count: int = 0
    compressed_token_count: int = 0


# 压缩比率映射
COMPRESSION_RATIOS = {
    CompressionLevel.NONE: 1.0,
    CompressionLevel.LIGHT: 0.7,
    CompressionLevel.MEDIUM: 0.4,
    CompressionLevel.AGGRESSIVE: 0.15,
    CompressionLevel.ULTIMATE: 0.05,
}

# 分段类型对应的推荐压缩级别
TYPE_RECOMMENDED_LEVEL = {
    SectionType.TASK: CompressionLevel.LIGHT,
    SectionType.DISCUSSION: CompressionLevel.MEDIUM,
    SectionType.CODE: CompressionLevel.LIGHT,
    SectionType.TOOL_USE: CompressionLevel.AGGRESSIVE,
    SectionType.RESULT: CompressionLevel.MEDIUM,
    SectionType.ERROR: CompressionLevel.AGGRESSIVE,
    SectionType.SYSTEM: CompressionLevel.ULTIMATE,
    SectionType.DEFAULT: CompressionLevel.MEDIUM,
}


class SectionSummarizer:
    """
    分段压缩器

    提供对话分段的压缩功能，支持多种压缩策略和级别。
    """

    def __init__(
        self,
        llm_provider: Optional[Callable[[str], str]] = None,
        default_level: CompressionLevel = CompressionLevel.MEDIUM,
    ):
        """
        初始化分段压缩器

        Args:
            llm_provider: LLM 提供者函数 (输入文本, 输出摘要)
            default_level: 默认压缩级别
        """
        self.llm_provider = llm_provider
        self.default_level = default_level
        self._patterns = self._init_patterns()

    def _init_patterns(self) -> dict:
        """初始化模式匹配规则"""
        return {
            "code_block": re.compile(r"```[\s\S]*?```"),
            "file_path": re.compile(r"(/[\w.-]+)+|[\w]:\\[\w.-]+"),
            "function_def": re.compile(r"(def|class|function|fn)\s+(\w+)"),
            "error_msg": re.compile(r"(error|exception|failed|failure)[\s:]+", re.IGNORECASE),
            "tool_call": re.compile(r"(invoke|call|execute|run)\s+(\w+)"),
            "number": re.compile(r"\d+(?:\.\d+)?"),
        }

    def detect_section_type(self, content: str) -> SectionType:
        """
        根据内容检测分段类型

        Args:
            content: 分段内容

        Returns:
            检测到的分段类型
        """
        content_lower = content.lower()

        # 代码检测
        if self._patterns["code_block"].search(content):
            return SectionType.CODE

        # 工具调用检测
        if self._patterns["tool_call"].search(content):
            return SectionType.TOOL_USE

        # 错误检测
        if self._patterns["error_msg"].search(content):
            return SectionType.ERROR

        # 结果检测
        if any(kw in content_lower for kw in ["result", "output", "return", "success"]):
            return SectionType.RESULT

        # 任务检测
        if any(kw in content_lower for kw in ["task", "goal", "objective", "需要", "完成"]):
            return SectionType.TASK

        # 系统检测
        if any(kw in content_lower for kw in ["system", "config", "setting", "配置"]):
            return SectionType.SYSTEM

        return SectionType.DISCUSSION

    def compress(
        self,
        section: Section,
        level: Optional[CompressionLevel] = None,
        strategy: SummarizationStrategy = SummarizationStrategy.KEY_POINTS,
    ) -> Section:
        """
        压缩分段

        Args:
            section: 要压缩的分段
            level: 压缩级别 (None 使用默认值)
            strategy: 摘要生成策略

        Returns:
            压缩后的分段
        """
        level = level or self.default_level
        section.compression_level = level

        if level == CompressionLevel.NONE:
            return section

        ratio = COMPRESSION_RATIOS.get(level, 0.4)

        # 如果有 LLM 提供者，使用智能摘要
        if self.llm_provider and strategy in (
            SummarizationStrategy.KEY_POINTS,
            SummarizationStrategy.HIERARCHICAL,
            SummarizationStrategy.ABSTRACT,
        ):
            section.summary = self._llm_summarize(section, strategy)
        else:
            # 使用规则基础压缩
            section.summary = self._rule_based_compress(section, ratio)

        # 提取关键点
        section.key_points = self._extract_key_points(section.summary or section.summary or "")

        # 计算压缩后的 token 数
        section.compressed_token_count = len(section.summary) // 4 if section.summary else 0

        return section

    def _llm_summarize(self, section: Section, strategy: SummarizationStrategy) -> str:
        """使用 LLM 生成摘要"""
        if not self.llm_provider:
            return ""

        prompt = self._build_summarize_prompt(section, strategy)

        try:
            summary = self.llm_provider(prompt)
            return summary.strip()
        except Exception:
            # 回退到规则基础压缩
            return self._rule_based_compress(section, COMPRESSION_RATIOS[section.compression_level])

    def _build_summarize_prompt(self, section: Section, strategy: SummarizationStrategy) -> str:
        """构建摘要提示"""
        if strategy == SummarizationStrategy.KEY_POINTS:
            return f"提取以下对话的关键要点 (3-5条):\n\n{section.summary or ' '.join(n for n in section.nodes)}"
        elif strategy == SummarizationStrategy.ABSTRACT:
            return f"用一句话概括以下对话的核心内容:\n\n{section.summary or ' '.join(n for n in section.nodes)}"
        else:
            return f"生成层级摘要:\n\n{section.summary or ' '.join(n for n in section.nodes)}"

    def _rule_based_compress(self, section: Section, ratio: float) -> str:
        """
        基于规则的压缩

        Args:
            section: 分段
            ratio: 保留比率

        Returns:
            压缩后的文本
        """
        # 获取原始内容
        content = section.summary or " ".join(section.nodes)

        if not content:
            return ""

        lines = content.split("\n")
        keep_count = max(1, int(len(lines) * ratio))

        # 保留开头和结尾，中间部分采样
        if len(lines) <= keep_count:
            return content

        kept_lines = []
        kept_lines.extend(lines[:keep_count // 2])
        kept_lines.append(f"... [{len(lines) - keep_count} 行已压缩] ...")
        kept_lines.extend(lines[-keep_count // 2:])

        return "\n".join(kept_lines)

    def _extract_key_points(self, text: str) -> list[str]:
        """提取关键点"""
        if not text:
            return []

        # 简单的关键点提取: 提取句子
        sentences = re.split(r"[。！？\n]", text)
        key_points = []

        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 10:  # 忽略太短的句子
                key_points.append(sent)

            if len(key_points) >= 5:  # 最多5条
                break

        return key_points

    def create_section_from_content(
        self,
        content: str,
        section_type: Optional[SectionType] = None,
    ) -> Section:
        """
        从内容创建分段

        Args:
            content: 分段内容
            section_type: 分段类型 (None 则自动检测)

        Returns:
            创建的分段
        """
        section_type = section_type or self.detect_section_type(content)

        section = Section(
            type=section_type,
            summary=content,
            token_count=len(content) // 4,
        )

        # 应用推荐的压缩级别
        recommended = TYPE_RECOMMENDED_LEVEL.get(section_type, CompressionLevel.MEDIUM)
        section.compression_level = recommended

        return section

    def merge_sections(self, sections: list[Section]) -> Section:
        """
        合并多个分段

        Args:
            sections: 要合并的分段列表

        Returns:
            合并后的分段
        """
        if not sections:
            return Section()

        merged = Section(
            type=sections[0].type,
            nodes=[],
            summary="\n\n---\n\n".join(s.summary or "" for s in sections if s.summary),
        )

        # 合并节点
        for section in sections:
            merged.nodes.extend(section.nodes)

        # 合并关键点
        all_points = []
        for section in sections:
            all_points.extend(section.key_points)

        # 去重
        seen = set()
        unique_points = []
        for point in all_points:
            if point not in seen:
                seen.add(point)
                unique_points.append(point)

        merged.key_points = unique_points[:10]  # 最多10条

        # 计算token
        merged.token_count = sum(s.token_count for s in sections)
        merged.compressed_token_count = sum(s.compressed_token_count for s in sections)

        return merged

    def get_compression_stats(self, section: Section) -> dict:
        """
        获取压缩统计信息

        Args:
            section: 分段

        Returns:
            统计信息字典
        """
        original = section.token_count or len(section.summary or "") // 4
        compressed = section.compressed_token_count or len(section.summary or "") // 4

        return {
            "original_tokens": original,
            "compressed_tokens": compressed,
            "compression_ratio": compressed / original if original > 0 else 1.0,
            "space_saved": original - compressed,
            "space_saved_percent": (1 - compressed / original) * 100 if original > 0 else 0,
            "compression_level": section.compression_level.value,
            "key_points_count": len(section.key_points),
        }
