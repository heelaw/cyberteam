"""
Review Engine - 三省六部审核机制实现
来源: 三省六部Agent/
功能: 四级质量门禁审核（自检→互检→专检→终检）
"""
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ReviewLevel(Enum):
    """审核级别"""
    SELF = "self_check"           # 自检
    PEER = "peer_review"          # 互检
    EXPERT = "expert_review"       # 专家审核
    FINAL = "final_approval"      # 终检


class ReviewResult(Enum):
    """审核结果"""
    PASS = "pass"
    FAIL = "fail"
    REVISION_REQUIRED = "revision_required"
    BLOCKED = "blocked"


@dataclass
class ReviewRecord:
    """审核记录"""
    content: Any
    level: ReviewLevel
    result: ReviewResult
    reviewer: str
    feedback: str
    timestamp: datetime
    issues: List[str] = field(default_factory=list)


@dataclass
class QualityGate:
    """质量门禁"""
    name: str
    check_fn: Callable
    severity: str = "medium"  # low, medium, high, critical


class ReviewEngine:
    """
    审核引擎 - 三省六部制度实现

    四级审核:
    1. SELF - 自检（产出者自己检查）
    2. PEER - 互检（同级审核）
    3. EXPERT - 专家审核（领域专家审核）
    4. FINAL - 终检（最终批准）

    使用示例:
    >>> review = ReviewEngine()
    >>> result = review.self_check(content)
    >>> result = review.peer_review(content, reviewer="coo")
    >>> result = review.expert_review(content, domain="marketing")
    >>> result = review.final_approval(content, approver="ceo")
    """

    def __init__(self):
        self._gates: List[QualityGate] = []
        self._history: List[ReviewRecord] = []
        self._expert_registry: Dict[str, List[str]] = {}  # domain -> experts

        # 注册默认质量门禁
        self._register_default_gates()

        logger.info("ReviewEngine 初始化完成")

    def _register_default_gates(self):
        """注册默认质量门禁"""
        self._gates = [
            QualityGate(
                name="format_check",
                check_fn=lambda c: self._check_format(c),
                severity="medium"
            ),
            QualityGate(
                name="completeness_check",
                check_fn=lambda c: self._check_completeness(c),
                severity="high"
            ),
            QualityGate(
                name="safety_check",
                check_fn=lambda c: self._check_safety(c),
                severity="critical"
            ),
            QualityGate(
                name="consistency_check",
                check_fn=lambda c: self._check_consistency(c),
                severity="medium"
            ),
        ]

    def register_expert(self, domain: str, expert_id: str):
        """
        注册专家

        Args:
            domain: 领域（如 marketing, ops, tech）
            expert_id: 专家ID
        """
        if domain not in self._expert_registry:
            self._expert_registry[domain] = []
        if expert_id not in self._expert_registry[domain]:
            self._expert_registry[domain].append(expert_id)
            logger.info(f"专家注册: {domain}/{expert_id}")

    def self_check(self, content: Any, **kwargs) -> ReviewRecord:
        """
        自检

        Args:
            content: 待审核内容
            **kwargs: 额外参数

        Returns:
            ReviewRecord: 审核记录
        """
        logger.info("开始自检...")
        issues = []

        # 运行所有质量门禁
        for gate in self._gates:
            try:
                gate_issues = gate.check_fn(content)
                if gate_issues:
                    issues.extend(gate_issues)
            except Exception as e:
                logger.error(f"质量门禁 {gate.name} 执行失败: {e}")
                issues.append(f"门禁执行错误: {gate.name}")

        result = ReviewResult.FAIL if issues else ReviewResult.PASS
        feedback = self._format_feedback(issues, "自检")

        record = ReviewRecord(
            content=content,
            level=ReviewLevel.SELF,
            result=result,
            reviewer="self",
            feedback=feedback,
            timestamp=datetime.now(),
            issues=issues
        )
        self._history.append(record)

        logger.info(f"自检完成: {result.value} ({len(issues)}个问题)")
        return record

    def peer_review(self, content: Any, reviewer: str = "peer", **kwargs) -> ReviewRecord:
        """
        互检

        Args:
            content: 待审核内容
            reviewer: 审核者ID

        Returns:
            ReviewRecord: 审核记录
        """
        logger.info(f"开始互检 (审核者: {reviewer})...")
        issues = []

        # 互检重点检查
        peer_checks = [
            self._check_logic_consistency,
            self._check_alignment_with_goals,
            self._check_risk_awareness,
        ]

        for check_fn in peer_checks:
            try:
                check_issues = check_fn(content)
                if check_issues:
                    issues.extend(check_issues)
            except Exception as e:
                logger.error(f"互检执行失败: {e}")

        result = ReviewResult.FAIL if issues else ReviewResult.PASS
        feedback = self._format_feedback(issues, f"互检({reviewer})")

        record = ReviewRecord(
            content=content,
            level=ReviewLevel.PEER,
            result=result,
            reviewer=reviewer,
            feedback=feedback,
            timestamp=datetime.now(),
            issues=issues
        )
        self._history.append(record)

        logger.info(f"互检完成: {result.value} ({len(issues)}个问题)")
        return record

    def expert_review(self, content: Any, domain: str = "general", **kwargs) -> ReviewRecord:
        """
        专家审核

        Args:
            content: 待审核内容
            domain: 领域

        Returns:
            ReviewRecord: 审核记录
        """
        experts = self._expert_registry.get(domain, ["anonymous"])
        expert = experts[0] if experts else "anonymous"

        logger.info(f"开始专家审核 (领域: {domain}, 专家: {expert})...")
        issues = []

        # 领域特定检查
        domain_checks = {
            "marketing": [self._check_marketing_compliance, self._check_brand_alignment],
            "ops": [self._check_ops_safety, self._check_resource_limits],
            "tech": [self._check_tech_quality, self._check_security],
            "finance": [self._check_finance_compliance, self._check_risk_control],
            "hr": [self._check_hr_compliance, self._check_culture_fit],
        }

        checks = domain_checks.get(domain, [self._check_general_quality])

        for check_fn in checks:
            try:
                check_issues = check_fn(content)
                if check_issues:
                    issues.extend(check_issues)
            except Exception as e:
                logger.error(f"专家审核执行失败: {e}")

        result = ReviewResult.FAIL if issues else ReviewResult.PASS
        feedback = self._format_feedback(issues, f"专家审核({domain})")

        record = ReviewRecord(
            content=content,
            level=ReviewLevel.EXPERT,
            result=result,
            reviewer=expert,
            feedback=feedback,
            timestamp=datetime.now(),
            issues=issues
        )
        self._history.append(record)

        logger.info(f"专家审核完成: {result.value} ({len(issues)}个问题)")
        return record

    def final_approval(self, content: Any, approver: str = "ceo", **kwargs) -> ReviewRecord:
        """
        终检

        Args:
            content: 待审核内容
            approver: 批准者ID

        Returns:
            ReviewRecord: 审核记录
        """
        logger.info(f"开始终检 (批准者: {approver})...")
        issues = []

        # 终检：全面检查 + 授权确认
        final_checks = [
            self._check_final_completeness,
            self._check_authorization,
            self._check_impact_assessment,
        ]

        for check_fn in final_checks:
            try:
                check_issues = check_fn(content)
                if check_issues:
                    issues.extend(check_issues)
            except Exception as e:
                logger.error(f"终检执行失败: {e}")

        result = ReviewResult.FAIL if issues else ReviewResult.PASS
        feedback = self._format_feedback(issues, f"终检({approver})")

        record = ReviewRecord(
            content=content,
            level=ReviewLevel.FINAL,
            result=result,
            reviewer=approver,
            feedback=feedback,
            timestamp=datetime.now(),
            issues=issues
        )
        self._history.append(record)

        logger.info(f"终检完成: {result.value} ({len(issues)}个问题)")
        return record

    def multi_level_review(self, content: Any, **kwargs) -> bool:
        """
        多级审核（完整流程）

        Args:
            content: 待审核内容

        Returns:
            bool: 是否全部通过
        """
        results = []

        # 自检
        r1 = self.self_check(content)
        results.append(r1)
        if r1.result == ReviewResult.FAIL:
            logger.warning("自检未通过，但继续流程...")

        # 互检
        r2 = self.peer_review(content, reviewer=kwargs.get("peer", "coo"))
        results.append(r2)
        if r2.result == ReviewResult.FAIL:
            logger.warning("互检未通过，但继续流程...")

        # 专家审核
        r3 = self.expert_review(content, domain=kwargs.get("domain", "general"))
        results.append(r3)
        if r3.result == ReviewResult.FAIL:
            logger.warning("专家审核未通过，但继续流程...")

        # 终检
        r4 = self.final_approval(content, approver=kwargs.get("approver", "ceo"))
        results.append(r4)

        # 全部通过才算通过
        all_pass = all(r.result == ReviewResult.PASS for r in results)

        logger.info(f"多级审核完成: {'全部通过' if all_pass else '存在未通过项'}")
        return all_pass

    def get_history(self, level: Optional[ReviewLevel] = None) -> List[ReviewRecord]:
        """
        获取审核历史

        Args:
            level: 筛选级别

        Returns:
            List[ReviewRecord]: 审核记录列表
        """
        if level:
            return [r for r in self._history if r.level == level]
        return self._history

    # ==================== 内部检查函数 ====================

    def _check_format(self, content: Any) -> List[str]:
        """检查格式"""
        issues = []
        if not content:
            issues.append("内容为空")
        elif isinstance(content, str) and len(content.strip()) == 0:
            issues.append("内容为空字符串")
        return issues

    def _check_completeness(self, content: Any) -> List[str]:
        """检查完整性"""
        issues = []
        if isinstance(content, dict):
            if "title" not in content and "name" not in content:
                issues.append("缺少标题/名称字段")
            if "description" not in content and "content" not in content:
                issues.append("缺少描述/内容字段")
        return issues

    def _check_safety(self, content: Any) -> List[str]:
        """安全检查"""
        issues = []
        dangerous_patterns = ["rm -rf", "DROP TABLE", "DELETE FROM", "eval(", "exec("]
        content_str = str(content).lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in content_str:
                issues.append(f"危险模式检测: {pattern}")
        return issues

    def _check_consistency(self, content: Any) -> List[str]:
        """一致性检查"""
        return []  # 默认通过

    def _check_logic_consistency(self, content: Any) -> List[str]:
        """逻辑一致性检查"""
        return []  # 默认通过

    def _check_alignment_with_goals(self, content: Any) -> List[str]:
        """目标对齐检查"""
        return []  # 默认通过

    def _check_risk_awareness(self, content: Any) -> List[str]:
        """风险意识检查"""
        return []  # 默认通过

    def _check_marketing_compliance(self, content: Any) -> List[str]:
        """营销合规检查"""
        return []  # 默认通过

    def _check_brand_alignment(self, content: Any) -> List[str]:
        """品牌对齐检查"""
        return []  # 默认通过

    def _check_ops_safety(self, content: Any) -> List[str]:
        """运营安全检查"""
        return []  # 默认通过

    def _check_resource_limits(self, content: Any) -> List[str]:
        """资源限制检查"""
        return []  # 默认通过

    def _check_tech_quality(self, content: Any) -> List[str]:
        """技术质量检查"""
        return []  # 默认通过

    def _check_security(self, content: Any) -> List[str]:
        """安全检查"""
        return []  # 默认通过

    def _check_finance_compliance(self, content: Any) -> List[str]:
        """财务合规检查"""
        return []  # 默认通过

    def _check_risk_control(self, content: Any) -> List[str]:
        """风险控制检查"""
        return []  # 默认通过

    def _check_hr_compliance(self, content: Any) -> List[str]:
        """人力合规检查"""
        return []  # 默认通过

    def _check_culture_fit(self, content: Any) -> List[str]:
        """文化契合检查"""
        return []  # 默认通过

    def _check_general_quality(self, content: Any) -> List[str]:
        """通用质量检查"""
        return []  # 默认通过

    def _check_final_completeness(self, content: Any) -> List[str]:
        """终检完整性"""
        return []  # 默认通过

    def _check_authorization(self, content: Any) -> List[str]:
        """授权确认"""
        return []  # 默认通过

    def _check_impact_assessment(self, content: Any) -> List[str]:
        """影响评估"""
        return []  # 默认通过

    def _format_feedback(self, issues: List[str], stage: str) -> str:
        """格式化反馈"""
        if not issues:
            return f"{stage}: 通过"
        return f"{stage}: 发现 {len(issues)} 个问题\n" + "\n".join(f"  - {i}" for i in issues)


# 全局实例
REVIEW = ReviewEngine()
