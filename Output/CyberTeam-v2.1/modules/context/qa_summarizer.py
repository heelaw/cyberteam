"""
QA Pair Summarization - 问答对压缩
===================================

提供问答对的压缩功能，包括：
- 问答对结构定义
- 问题抽象
- 答案关键信息提取
- 问答关联压缩

参考: PentAGI Chain Summarization
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional


class QAType(str, Enum):
    """问答类型"""
    EXPLICIT = "explicit"           # 显式问答 (直接提问-直接回答)
    IMPLICIT = "implicit"           # 隐式问答 (上下文暗示)
    SEQUENTIAL = "sequential"       # 顺序问答 (多轮对话)
    TOOL_INTERACTION = "tool_interaction"  # 工具交互问答
    CLARIFICATION = "clarification"  # 澄清问答
    ERROR_RECOVERY = "error_recovery"  # 错误恢复问答


class AbstractionLevel(str, Enum):
    """抽象级别"""
    CONCRETE = "concrete"      # 具象 (保留原始细节)
    SEMANTIC = "semantic"      # 语义 (保留核心语义)
    TEMPLATE = "template"      # 模板 (替换为模式)
    CATEGORICAL = "categorical"  # 类别 (分类而非具体)


# 抽象级别对应的信息保留比率
ABSTRACT_RATIOS = {
    AbstractionLevel.CONCRETE: 1.0,
    AbstractionLevel.SEMANTIC: 0.6,
    AbstractionLevel.TEMPLATE: 0.3,
    AbstractionLevel.CATEGORICAL: 0.15,
}


@dataclass
class QAPair:
    """
    问答对

    Attributes:
        id: 唯一ID
        type: 问答类型
        question: 原始问题
        abstracted_question: 抽象后的问题
        answer: 原始答案
        abstracted_answer: 抽象后的答案
        context: 上下文信息
        key_entities: 提取的实体
        relationships: 关系信息
        parent_id: 父问答对ID (用于顺序问答)
        child_ids: 子问答对ID列表
        created_at: 创建时间
        relevance_score: 相关性评分
        token_count: token数
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: QAType = QAType.EXPLICIT
    question: str = ""
    abstracted_question: Optional[str] = None
    answer: str = ""
    abstracted_answer: Optional[str] = None
    context: dict = field(default_factory=dict)
    key_entities: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    child_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0
    token_count: int = 0

    def __post_init__(self):
        if not self.token_count:
            self.token_count = self._estimate_tokens()

    def _estimate_tokens(self) -> int:
        """估算token数"""
        text = f"{self.question} {self.answer}"
        return len(text) // 4


@dataclass
class QACluster:
    """
    问答簇 - 相关的问答对分组

    Attributes:
        id: 唯一ID
        qa_pairs: 问答对ID列表
        theme: 主题
        summary: 簇摘要
        created_at: 创建时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    qa_pairs: list[str] = field(default_factory=list)
    theme: str = ""
    summary: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


class QAPairSummarizer:
    """
    问答对压缩器

    提供问答对的抽象、压缩和聚类功能。
    """

    def __init__(
        self,
        llm_provider: Optional[Callable[[str], str]] = None,
        default_abstraction: AbstractionLevel = AbstractionLevel.SEMANTIC,
    ):
        """
        初始化问答对压缩器

        Args:
            llm_provider: LLM 提供者函数
            default_abstraction: 默认抽象级别
        """
        self.llm_provider = llm_provider
        self.default_abstraction = default_abstraction
        self._entity_patterns = self._init_entity_patterns()

    def _init_entity_patterns(self) -> dict:
        """初始化实体识别模式"""
        return {
            "file_path": re.compile(r"(?:/[\w.-]+)+|[\w]:\\[\w.-]+"),
            "url": re.compile(r"https?://[^\s]+"),
            "email": re.compile(r"[\w.-]+@[\w.-]+\.\w+"),
            "number": re.compile(r"\d+(?:\.\d+)?"),
            "code": re.compile(r"`[^`]+`"),
            "function": re.compile(r"(\w+)\s*\([^)]*\)"),
        }

    def create_qa_pair(
        self,
        question: str,
        answer: str,
        qa_type: QAType = QAType.EXPLICIT,
    ) -> QAPair:
        """
        创建问答对

        Args:
            question: 问题
            answer: 答案
            qa_type: 问答类型

        Returns:
            创建的问答对
        """
        qa = QAPair(
            question=question,
            answer=answer,
            type=qa_type,
        )

        # 提取实体
        qa.key_entities = self._extract_entities(f"{question} {answer}")

        # 提取关系
        qa.relationships = self._extract_relationships(question, answer)

        return qa

    def abstract(
        self,
        qa: QAPair,
        level: AbstractionLevel = None,
    ) -> QAPair:
        """
        抽象问答对

        Args:
            qa: 问答对
            level: 抽象级别

        Returns:
            抽象后的问答对
        """
        level = level or self.default_abstraction

        # 抽象问题
        qa.abstracted_question = self._abstract_text(
            qa.question, level, "question"
        )

        # 抽象答案
        qa.abstracted_answer = self._abstract_text(
            qa.answer, level, "answer"
        )

        return qa

    def _abstract_text(
        self,
        text: str,
        level: AbstractionLevel,
        text_type: str,
    ) -> str:
        """
        抽象文本

        Args:
            text: 原始文本
            level: 抽象级别
            text_type: 文本类型 (question/answer)

        Returns:
            抽象后的文本
        """
        if level == AbstractionLevel.CONCRETE:
            return text

        if self.llm_provider and level in (
            AbstractionLevel.SEMANTIC,
            AbstractionLevel.TEMPLATE,
        ):
            return self._llm_abstract(text, level, text_type)

        return self._rule_based_abstract(text, level)

    def _llm_abstract(
        self,
        text: str,
        level: AbstractionLevel,
        text_type: str,
    ) -> str:
        """使用 LLM 进行抽象"""
        if level == AbstractionLevel.SEMANTIC:
            prompt = f"提取以下{text_type}的核心语义，忽略具体细节:\n\n{text}"
        else:  # TEMPLATE
            prompt = f"将以下{text_type}转换为通用模板，替换具体值:\n\n{text}"

        try:
            return self.llm_provider(prompt).strip()
        except Exception:
            return self._rule_based_abstract(text, level)

    def _rule_based_abstract(self, text: str, level: AbstractionLevel) -> str:
        """基于规则的抽象"""
        abstracted = text

        if level == AbstractionLevel.SEMANTIC:
            # 替换文件路径
            abstracted = self._entity_patterns["file_path"].sub("<FILE_PATH>", abstracted)
            # 替换URL
            abstracted = self._entity_patterns["url"].sub("<URL>", abstracted)
            # 替换邮箱
            abstracted = self._entity_patterns["email"].sub("<EMAIL>", abstracted)

        elif level == AbstractionLevel.TEMPLATE:
            # 替换所有实体
            for pattern in self._entity_patterns.values():
                abstracted = pattern.sub(f"<{pattern.pattern[:20]}>", abstracted)
            # 替换数字
            abstracted = self._entity_patterns["number"].sub("<NUMBER>", abstracted)

        elif level == AbstractionLevel.CATEGORICAL:
            # 只保留文本类别信息
            abstracted = abstracted[:100] if len(abstracted) > 100 else abstracted
            abstracted += " [已类别化]"

        return abstracted

    def _extract_entities(self, text: str) -> list[str]:
        """提取实体"""
        entities = []

        for name, pattern in self._entity_patterns.items():
            matches = pattern.findall(text)
            entities.extend(matches)

        return list(set(entities))[:10]  # 最多10个

    def _extract_relationships(self, question: str, answer: str) -> list[str]:
        """提取关系"""
        relationships = []

        # 简单的关系提取: 检查问题中的关键词是否在答案中有对应
        q_words = set(question.split())
        a_words = set(answer.split())

        # 找共同词 (排除停用词)
        stopwords = {"的", "是", "在", "了", "和", "与", "或", "the", "a", "an", "is", "are"}
        common = (q_words & a_words) - stopwords

        if common:
            relationships.append(f"共享关键词: {', '.join(list(common)[:5])}")

        return relationships

    def compress(
        self,
        qa: QAPair,
        keep_entities: bool = True,
        keep_context: bool = False,
    ) -> QAPair:
        """
        压缩问答对

        Args:
            qa: 问答对
            keep_entities: 是否保留实体
            keep_context: 是否保留上下文

        Returns:
            压缩后的问答对
        """
        # 抽象问题
        qa.abstracted_question = self._rule_based_abstract(
            qa.question, AbstractionLevel.TEMPLATE
        )

        # 抽象答案 - 保留关键部分
        if keep_entities:
            qa.abstracted_answer = self._rule_based_abstract(
                qa.answer, AbstractionLevel.SEMANTIC
            )
        else:
            qa.abstracted_answer = self._rule_based_abstract(
                qa.answer, AbstractionLevel.TEMPLATE
            )

        # 可选保留上下文
        if not keep_context:
            qa.context = {}

        # 重新计算 token
        qa.token_count = len(qa.abstracted_question or "") // 4 + \
                        len(qa.abstracted_answer or "") // 4

        return qa

    def create_cluster(
        self,
        qa_pairs: list[QAPair],
        theme: str = "",
    ) -> QACluster:
        """
        创建问答簇

        Args:
            qa_pairs: 问答对列表
            theme: 主题

        Returns:
            问答簇
        """
        cluster = QACluster(
            theme=theme,
            qa_pairs=[qa.id for qa in qa_pairs],
        )

        # 生成簇摘要
        if self.llm_provider:
            cluster.summary = self._generate_cluster_summary(qa_pairs)
        else:
            # 简单摘要
            cluster.summary = f"包含 {len(qa_pairs)} 个问答对"

        return cluster

    def _generate_cluster_summary(self, qa_pairs: list[QAPair]) -> str:
        """生成簇摘要"""
        questions = [qa.question for qa in qa_pairs[:5]]

        prompt = f"用一句话概括以下问答对的主题:\n\n" + "\n".join(questions)

        try:
            return self.llm_provider(prompt).strip()
        except Exception:
            return f"包含 {len(qa_pairs)} 个相关问答对"

    def merge_qa_pairs(
        self,
        qa_pairs: list[QAPair],
    ) -> QAPair:
        """
        合并多个问答对

        Args:
            qa_pairs: 要合并的问答对

        Returns:
            合并后的问答对
        """
        if not qa_pairs:
            return QAPair()

        # 使用第一个的类型
        merged = QAPair(
            type=qa_pairs[0].type,
            parent_id=qa_pairs[0].parent_id if len(qa_pairs) == 1 else None,
        )

        # 合并问题 (保留第一个)
        merged.question = qa_pairs[0].question
        merged.abstracted_question = qa_pairs[0].abstracted_question

        # 合并答案
        answers = [qa.answer for qa in qa_pairs if qa.answer]
        merged.answer = "\n".join(answers)

        abstracted = [qa.abstracted_answer for qa in qa_pairs if qa.abstracted_answer]
        if abstracted:
            merged.abstracted_answer = "\n".join(abstracted)

        # 合并实体
        all_entities = []
        for qa in qa_pairs:
            all_entities.extend(qa.key_entities)

        merged.key_entities = list(set(all_entities))[:10]

        # 建立父子关系
        if len(qa_pairs) > 1:
            for i, qa in enumerate(qa_pairs[1:], 1):
                qa.parent_id = qa_pairs[i-1].id
                qa_pairs[i-1].child_ids.append(qa.id)

        merged.token_count = sum(qa.token_count for qa in qa_pairs)

        return merged

    def get_compression_stats(self, qa: QAPair) -> dict:
        """获取压缩统计"""
        original = len(qa.question) // 4 + len(qa.answer) // 4
        compressed = len(qa.abstracted_question or "") // 4 + \
                    len(qa.abstracted_answer or "") // 4

        return {
            "original_tokens": original,
            "compressed_tokens": compressed,
            "compression_ratio": compressed / original if original > 0 else 1.0,
            "space_saved": original - compressed,
            "space_saved_percent": (1 - compressed / original) * 100 if original > 0 else 0,
            "entities_extracted": len(qa.key_entities),
            "relationships_count": len(qa.relationships),
            "relevance_score": qa.relevance_score,
        }
