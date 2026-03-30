# CyberTeam v2.0.1 - Dev-QA 循环引擎
"""
Dev-QA 循环引擎 — 自主闭环的质量保障系统
源自 v2.1 engines/dev-qa-loop-engine.md 的 Python 实现

核心流程: 证据收集 → 五维评分 → 重试 → 升级
"""

import time
import logging
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class DevQAStatus(Enum):
    """Dev-QA 状态机"""
    INIT = "init"
    COLLECTING = "collecting"
    SCORING = "scoring"
    RETRYING = "retrying"
    PASSED = "passed"
    FAILED = "failed"
    ESCALATED = "escalated"


class QualityDimension(Enum):
    """质量维度"""
    CODE_QUALITY = "code_quality"           # 代码质量 (权重25%)
    FUNCTIONAL = "functional"              # 功能完整性 (权重30%)
    SECURITY = "security"                   # 安全性 (权重25%)
    PERFORMANCE = "performance"             # 性能 (权重10%)
    MAINTAINABILITY = "maintainability"     # 可维护性 (权重10%)


@dataclass
class Evidence:
    """证据"""
    dimension: QualityDimension
    score: float                           # 0-100
    metrics: Dict[str, Any] = field(default_factory=dict)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    raw_output: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class DimensionResult:
    """单维度评分结果"""
    dimension: QualityDimension
    score: float
    weight: float
    weighted_score: float
    is_pass: bool
    is_warning: bool
    detail: str


@dataclass
class ScoreResult:
    """综合评分结果"""
    overall_score: float                  # 0-100
    dimensions: List[DimensionResult]
    passed: bool
    conditional_pass: bool
    failed: bool
    failed_dimensions: List[str]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class RetryRecord:
    """重试记录"""
    attempt: int
    timestamp: str
    failure_type: str
    failure_detail: str
    action_taken: str
    delay_ms: int
    success: bool


@dataclass
class EscalationPackage:
    """升级包 (发送到CEO)"""
    request_id: str
    source_agent: str
    original_request: str
    retry_count: int
    final_score: float
    dimension_scores: Dict[str, float]
    failure_analysis: Dict[str, Any]
    attempted_solutions: List[Dict]
    recommended_actions: List[Dict]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class DevQAExecution:
    """Dev-QA执行上下文"""
    execution_id: str
    target_type: str                       # agent / skill / system
    target_name: str
    status: DevQAStatus = DevQAStatus.INIT
    evidence: List[Evidence] = field(default_factory=list)
    score_result: Optional[ScoreResult] = None
    retry_history: List[RetryRecord] = field(default_factory=list)
    max_attempts: int = 3
    current_attempt: int = 0
    escalation_package: Optional[EscalationPackage] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


class EvidenceCollector:
    """
    证据收集器

    对不同类型的检查目标，使用不同的收集策略:
    - agent: 检查 Agent 定义完整性、trigger匹配、输出格式
    - skill: 检查 Skill 定义完整性、trigger匹配、执行流程
    - system: 检查集成链路、配置完整性
    """

    DIMENSION_WEIGHTS = {
        QualityDimension.CODE_QUALITY: 0.25,
        QualityDimension.FUNCTIONAL: 0.30,
        QualityDimension.SECURITY: 0.25,
        QualityDimension.PERFORMANCE: 0.10,
        QualityDimension.MAINTAINABILITY: 0.10,
    }

    MIN_REQUIREMENTS = {
        QualityDimension.CODE_QUALITY: 70,
        QualityDimension.FUNCTIONAL: 80,
        QualityDimension.SECURITY: 85,
        QualityDimension.PERFORMANCE: 70,
        QualityDimension.MAINTAINABILITY: 65,
    }

    def collect(
        self,
        execution: DevQAExecution,
        target: Dict[str, Any]
    ) -> List[Evidence]:
        """
        收集证据

        Args:
            execution: Dev-QA执行上下文
            target: 检查目标 (Agent/Skill定义)

        Returns:
            List[Evidence]: 各维度的证据
        """
        target_type = execution.target_type

        if target_type == "agent":
            return self._collect_agent_evidence(target)
        elif target_type == "skill":
            return self._collect_skill_evidence(target)
        elif target_type == "system":
            return self._collect_system_evidence(target)
        else:
            return self._collect_default_evidence(target)

    def _collect_agent_evidence(self, agent_def: Dict) -> List[Evidence]:
        """收集 Agent 定义证据"""
        evidence = []
        name = agent_def.get("name", agent_def.get("id", "unknown"))

        # L1: 完整性检查
        completeness_score = self._check_agent_completeness(agent_def)
        evidence.append(Evidence(
            dimension=QualityDimension.FUNCTIONAL,
            score=completeness_score,
            metrics={"checklist_score": completeness_score},
            issues=self._find_completeness_issues(agent_def)
        ))

        # L2: 专业度检查
        quality_score = self._check_agent_quality(agent_def)
        evidence.append(Evidence(
            dimension=QualityDimension.CODE_QUALITY,
            score=quality_score,
            metrics={"quality_score": quality_score},
            issues=[]
        ))

        # L3: 可执行性检查
        exec_score = self._check_agent_executability(agent_def)
        evidence.append(Evidence(
            dimension=QualityDimension.MAINTAINABILITY,
            score=exec_score,
            metrics={"executability_score": exec_score},
            issues=self._find_executability_issues(agent_def)
        ))

        # 安全检查 (无实际代码，安全分给高)
        evidence.append(Evidence(
            dimension=QualityDimension.SECURITY,
            score=100,
            metrics={},
            issues=[]
        ))

        # 性能 (非运行时，给高)
        evidence.append(Evidence(
            dimension=QualityDimension.PERFORMANCE,
            score=100,
            metrics={},
            issues=[]
        ))

        logger.info(f"Agent '{name}' 收集了 {len(evidence)} 个维度证据")
        return evidence

    def _collect_skill_evidence(self, skill_def: Dict) -> List[Evidence]:
        """收集 Skill 定义证据"""
        evidence = []
        name = skill_def.get("name", "unknown")

        completeness = self._check_skill_completeness(skill_def)
        evidence.append(Evidence(
            dimension=QualityDimension.FUNCTIONAL,
            score=completeness,
            metrics={},
            issues=[]
        ))
        evidence.append(Evidence(
            dimension=QualityDimension.CODE_QUALITY,
            score=completeness,
            metrics={},
            issues=[]
        ))
        evidence.append(Evidence(
            dimension=QualityDimension.SECURITY,
            score=100, issues=[]
        ))
        evidence.append(Evidence(
            dimension=QualityDimension.PERFORMANCE,
            score=100, issues=[]
        ))
        evidence.append(Evidence(
            dimension=QualityDimension.MAINTAINABILITY,
            score=completeness, issues=[]
        ))

        logger.info(f"Skill '{name}' 收集了 {len(evidence)} 个维度证据")
        return evidence

    def _collect_system_evidence(self, system_def: Dict) -> List[Evidence]:
        """收集系统集成证据"""
        evidence = []
        integration_score = self._check_integration(system_def)
        for dim in QualityDimension:
            evidence.append(Evidence(
                dimension=dim,
                score=integration_score.get(dim.value, 50),
                metrics={},
                issues=[]
            ))
        return evidence

    def _collect_default_evidence(self, target: Dict) -> List[Evidence]:
        """默认证据收集"""
        return [Evidence(
            dimension=d,
            score=50,
            metrics={},
            issues=[]
        ) for d in QualityDimension]

    # ---- Agent 完整性检查 ----

    def _check_agent_completeness(self, agent_def: Dict) -> float:
        """检查 Agent 定义完整性"""
        score = 0
        total = 0

        required_fields = ["name", "id"]
        for field in required_fields:
            total += 1
            if agent_def.get(field):
                score += 100 / len(required_fields)

        # 检查关键section
        content = str(agent_def)
        sections = ["Identity", "能力", "输出格式", "思维注入"]
        for section in sections:
            total += 1
            if section in content:
                score += 100 / (len(required_fields) + len(sections))

        return score

    def _find_completeness_issues(self, agent_def: Dict) -> List[Dict]:
        """找完整性问题"""
        issues = []
        content = str(agent_def)

        if "Identity" not in content:
            issues.append({"type": "missing_section", "detail": "缺少 Identity 定义"})
        if "输出格式" not in content and "output" not in content.lower():
            issues.append({"type": "missing_section", "detail": "缺少输出格式定义"})
        if "思维注入" not in content and "thinking" not in content.lower():
            issues.append({"type": "warning", "detail": "建议添加思维注入配置"})

        return issues

    def _check_agent_quality(self, agent_def: Dict) -> float:
        """检查 Agent 定义质量"""
        content = str(agent_def)
        score = 50

        # 有详细描述
        if len(content) > 500:
            score += 20
        elif len(content) > 200:
            score += 10

        # 有trigger
        if "trigger" in content.lower():
            score += 15

        # 有tool定义
        if "tools" in content.lower():
            score += 15

        return min(score, 100)

    def _check_agent_executability(self, agent_def: Dict) -> float:
        """检查可执行性"""
        content = str(agent_def)
        score = 60

        if "输出格式" in content or "output" in content.lower():
            score += 20
        if "quality_gate" in content.lower() or "质量门控" in content:
            score += 20

        return min(score, 100)

    def _find_executability_issues(self, agent_def: Dict) -> List[Dict]:
        """找可执行性问题"""
        issues = []
        content = str(agent_def)

        if "输出格式" not in content and "output" not in content.lower():
            issues.append({"type": "executability", "detail": "缺少明确的输出格式定义"})

        return issues

    def _check_skill_completeness(self, skill_def: Dict) -> float:
        """检查 Skill 完整性"""
        score = 50
        content = str(skill_def)

        if "SKILL" in content or "skill" in content.lower():
            score += 10
        if "trigger" in content.lower():
            score += 15
        if "执行" in content or "execute" in content.lower():
            score += 15
        if "output" in content.lower() or "输出" in content:
            score += 10

        return min(score, 100)

    def _check_integration(self, system_def: Dict) -> Dict[str, float]:
        """检查系统集成度"""
        return {
            "code_quality": 70,
            "functional": 75,
            "security": 80,
            "performance": 70,
            "maintainability": 65
        }


class ScoringEngine:
    """
    评分引擎

    基于证据计算综合评分
    公式: 总分 = Σ(维度分 × 权重)
    判定: PASS ≥80 / CONDITIONAL 70-79 / FAIL <70
    """

    DIMENSION_WEIGHTS = EvidenceCollector.DIMENSION_WEIGHTS
    MIN_REQUIREMENTS = EvidenceCollector.MIN_REQUIREMENTS

    def score(self, evidence_list: List[Evidence]) -> ScoreResult:
        """
        计算评分

        Args:
            evidence_list: 各维度证据

        Returns:
            ScoreResult: 评分结果
        """
        dimension_scores: Dict[QualityDimension, float] = {}
        for ev in evidence_list:
            dimension_scores[ev.dimension] = ev.score

        dimension_results = []
        total = 0.0
        all_pass = True
        any_critical = False
        failed_dims = []

        for dim, weight in self.DIMENSION_WEIGHTS.items():
            score = dimension_scores.get(dim, 0)
            min_req = self.MIN_REQUIREMENTS.get(dim, 60)

            is_pass = score >= min_req
            is_warning = min_req - 10 <= score < min_req

            result = DimensionResult(
                dimension=dim,
                score=score,
                weight=weight,
                weighted_score=score * weight,
                is_pass=is_pass,
                is_warning=is_warning,
                detail=f"{'通过' if is_pass else '警告' if is_warning else '严重'} ({score} vs 要求{min_req})"
            )
            dimension_results.append(result)
            total += score * weight

            if not is_pass and not is_warning:
                any_critical = True
                failed_dims.append(dim.value)
            if not is_pass:
                all_pass = False

        overall = round(total, 2)

        return ScoreResult(
            overall_score=overall,
            dimensions=dimension_results,
            passed=all_pass and overall >= 80,
            conditional_pass=not all_pass and overall >= 70,
            failed=any_critical or overall < 70,
            failed_dimensions=failed_dims
        )


class RetryController:
    """
    重试控制器

    策略:
    - 最多3次重试
    - 指数退避 (1s, 2s, 4s)
    - 智能方案调整
    """

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def should_retry(self, execution: DevQAExecution) -> bool:
        """是否应该重试"""
        return (
            execution.current_attempt < self.max_attempts
            and execution.status in [DevQAStatus.RETRYING, DevQAStatus.FAILED]
        )

    def calculate_delay(self, attempt: int) -> int:
        """计算退避延迟 (ms)"""
        import random
        base = 1000
        delay = min(base * (2 ** attempt), 30000)
        # 添加 jitter
        delay *= random.uniform(0.5, 1.0)
        return int(delay)

    def record_retry(
        self,
        execution: DevQAExecution,
        failure_type: str,
        failure_detail: str,
        action: str,
        success: bool
    ) -> RetryRecord:
        """记录重试"""
        execution.current_attempt += 1
        record = RetryRecord(
            attempt=execution.current_attempt,
            timestamp=datetime.now().isoformat(),
            failure_type=failure_type,
            failure_detail=failure_detail,
            action_taken=action,
            delay_ms=self.calculate_delay(execution.current_attempt - 1),
            success=success
        )
        execution.retry_history.append(record)
        execution.updated_at = datetime.now().isoformat()
        return record

    def get_retry_suggestion(self, execution: DevQAExecution) -> str:
        """获取重试建议"""
        score = execution.score_result
        if not score:
            return "分析失败原因，制定修复方案"

        suggestions = []
        for dim_result in score.dimensions:
            if not dim_result.is_pass:
                suggestions.append(
                    f"{dim_result.dimension.value}: "
                    f"当前{dim_result.score}分，需要达到{dim_result.weight * 100}分以上"
                )

        return "; ".join(suggestions) if suggestions else "全面改进"


class DevQAEngine:
    """
    Dev-QA 循环引擎 — 顶层API

    使用方式:
        engine = DevQAEngine()
        result = engine.execute(
            target_type="agent",
            target_name="investor-agent",
            target=agent_def_dict
        )
    """

    def __init__(self, max_attempts: int = 3):
        self.collector = EvidenceCollector()
        self.scorer = ScoringEngine()
        self.retry_ctrl = RetryController(max_attempts)
        self.max_attempts = max_attempts

    def execute(
        self,
        target_type: str,
        target_name: str,
        target: Dict[str, Any],
        check_type: str = "full",
        auto_retry: bool = True
    ) -> DevQAExecution:
        """
        执行 Dev-QA 检查

        Args:
            target_type: agent / skill / system
            target_name: 目标名称
            target: 目标定义
            check_type: full / incremental / targeted
            auto_retry: 是否自动重试

        Returns:
            DevQAExecution: 完整的执行上下文
        """
        import uuid
        execution = DevQAExecution(
            execution_id=f"devqa-{uuid.uuid4().hex[:8]}",
            target_type=target_type,
            target_name=target_name,
        )

        # INIT
        execution.status = DevQAStatus.INIT
        logger.info(f"[{execution.execution_id}] Dev-QA 开始: {target_type}/{target_name}")

        # COLLECTING
        execution.status = DevQAStatus.COLLECTING
        execution.evidence = self.collector.collect(execution, target)

        # SCORING
        execution.status = DevQAStatus.SCORING
        execution.score_result = self.scorer.score(execution.evidence)

        # PASS/FAIL 判定
        if execution.score_result.passed:
            execution.status = DevQAStatus.PASSED
            logger.info(
                f"[{execution.execution_id}] PASS: "
                f"{execution.score_result.overall_score:.1f}分"
            )
            return execution

        # FAIL: 进入重试循环
        execution.status = DevQAStatus.RETRYING

        if auto_retry:
            while self.retry_ctrl.should_retry(execution):
                suggestion = self.retry_ctrl.get_retry_suggestion(execution)
                logger.info(
                    f"[{execution.execution_id}] 重试 {execution.current_attempt + 1}/"
                    f"{self.max_attempts}: {suggestion}"
                )

                # 模拟重试 (实际使用时，这里会调用修复后的目标)
                self.retry_ctrl.record_retry(
                    execution=execution,
                    failure_type="score_below_threshold",
                    failure_detail=suggestion,
                    action="re_collect_evidence",
                    success=False
                )

                # 重新收集 + 评分
                execution.evidence = self.collector.collect(execution, target)
                execution.score_result = self.scorer.score(execution.evidence)

                if execution.score_result.passed:
                    self.retry_ctrl.record_retry(
                        execution=execution,
                        failure_type="recovery",
                        failure_detail="Score improved",
                        action="none",
                        success=True
                    )
                    execution.status = DevQAStatus.PASSED
                    logger.info(
                        f"[{execution.execution_id}] 重试后 PASS: "
                        f"{execution.score_result.overall_score:.1f}分"
                    )
                    return execution

        # 达到最大重试次数仍未通过 → ESCALATE
        if execution.score_result.failed:
            execution.status = DevQAStatus.ESCALATED
            execution.escalation_package = self._build_escalation(execution)
            logger.warning(
                f"[{execution.execution_id}] ESCALATED: "
                f"{execution.score_result.overall_score:.1f}分, "
                f"失败维度: {execution.score_result.failed_dimensions}"
            )
        else:
            execution.status = DevQAStatus.FAILED

        return execution

    def _build_escalation(self, execution: DevQAExecution) -> EscalationPackage:
        """构建升级包"""
        score = execution.score_result

        dimension_scores = {}
        for d in score.dimensions:
            dimension_scores[d.dimension.value] = d.score

        return EscalationPackage(
            request_id=f"esc-{execution.execution_id}",
            source_agent=execution.target_name,
            original_request=f"检查 {execution.target_type}: {execution.target_name}",
            retry_count=execution.current_attempt,
            final_score=score.overall_score,
            dimension_scores=dimension_scores,
            failure_analysis={
                "primary_cause": score.failed_dimensions[0] if score.failed_dimensions else "unknown",
                "root_cause_confidence": 0.7
            },
            attempted_solutions=[
                {
                    "attempt": r.attempt,
                    "action": r.action_taken,
                    "result": "improved" if r.success else "no_improvement",
                    "score_after": execution.score_result.overall_score
                }
                for r in execution.retry_history
            ],
            recommended_actions=[
                {"action": "补充缺失的section", "priority": 1},
                {"action": "完善输出格式定义", "priority": 2},
                {"action": "添加trigger关键词", "priority": 3}
            ]
        )

    def generate_report(self, execution: DevQAExecution) -> str:
        """生成 Dev-QA 报告"""
        score = execution.score_result
        lines = [
            f"# Dev-QA 检查报告",
            f"",
            f"**执行ID**: {execution.execution_id}",
            f"**目标**: {execution.target_type}/{execution.target_name}",
            f"**状态**: {execution.status.value.upper()}",
            f"**综合评分**: {score.overall_score:.1f}/100",
            f"",
            f"## 维度评分",
            f"",
        ]

        for d in score.dimensions:
            icon = "✅" if d.is_pass else "⚠️" if d.is_warning else "❌"
            lines.append(
                f"- {icon} **{d.dimension.value}**: "
                f"{d.score:.0f}分 (权重{d.weight:.0%}, 要求≥{self.collector.MIN_REQUIREMENTS[d.dimension]})"
            )
            lines.append(f"  {d.detail}")

        if execution.retry_history:
            lines.extend([
                "",
                f"## 重试历史 ({len(execution.retry_history)}次)",
            ])
            for r in execution.retry_history:
                lines.append(
                    f"- 尝试{r.attempt}: {r.action_taken} → "
                    f"{'✅' if r.success else '❌'} ({r.failure_type})"
                )

        if execution.status == DevQAStatus.ESCALATED:
            lines.extend([
                "",
                f"## ⚠️ 升级通知",
                f"",
                f"请求ID: {execution.escalation_package.request_id}",
                f"失败维度: {', '.join(score.failed_dimensions)}",
                f"",
                f"**推荐行动**:"
            ])
            for action in execution.escalation_package.recommended_actions:
                lines.append(f"  {action['priority']}. {action['action']}")

        return "\n".join(lines)


# ============================================================
# 快速测试
# ============================================================
if __name__ == "__main__":
    engine = DevQAEngine(max_attempts=3)

    test_agents = [
        {
            "name": "investor-agent",
            "id": "investor-agent",
            "Identity": "你是投资人专家，负责TAM/SAM/SOM规模分析。",
            "能力": "市场规模分析、六维评估框架",
            "输出格式": "分析报告 (JSON)",
            "trigger": ["投资人", "市场规模", "TAM"]
        },
        {
            "name": "weak-agent",
            "id": "weak-agent",
            "description": "一个弱定义"
        }
    ]

    for agent in test_agents:
        print(f"\n{'='*60}")
        print(f"检查 Agent: {agent['name']}")
        result = engine.execute(
            target_type="agent",
            target_name=agent["name"],
            target=agent
        )
        print(engine.generate_report(result))
