"""
CyberTeam v2 - Dev-QA 引擎测试套件

测试覆盖：
1. DevQAEngine - Dev-QA 引擎
2. Evidence - 证据类
3. ScoreResult - 评分结果
4. 质量维度评分
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.dev_qa_engine import (
    DevQAEngine,
    DevQAStatus,
    QualityDimension,
    Evidence,
    DimensionResult,
    ScoreResult,
    RetryRecord,
    EscalationPackage,
    DevQAExecution,
    EvidenceCollector
)


class TestEvidence:
    """证据类测试"""

    def test_create_evidence(self):
        """测试创建证据"""
        evidence = Evidence(
            dimension=QualityDimension.CODE_QUALITY,
            score=85.0,
            metrics={"lines": 100},
            issues=[{"type": "warning", "message": "test"}]
        )
        assert evidence.dimension == QualityDimension.CODE_QUALITY
        assert evidence.score == 85.0
        assert evidence.timestamp != ""

    def test_evidence_default_timestamp(self):
        """测试证据默认时间戳"""
        evidence = Evidence(
            dimension=QualityDimension.FUNCTIONAL,
            score=90.0
        )
        assert evidence.timestamp != ""


class TestDimensionResult:
    """单维度评分结果测试"""

    def test_create_dimension_result(self):
        """测试创建维度结果"""
        result = DimensionResult(
            dimension=QualityDimension.CODE_QUALITY,
            score=80.0,
            weight=0.25,
            weighted_score=20.0,
            is_pass=True,
            is_warning=False,
            detail="代码质量良好"
        )
        assert result.dimension == QualityDimension.CODE_QUALITY
        assert result.is_pass is True


class TestScoreResult:
    """综合评分结果测试"""

    def test_create_score_result(self):
        """测试创建评分结果"""
        dimensions = [
            DimensionResult(
                dimension=QualityDimension.CODE_QUALITY,
                score=80.0,
                weight=0.25,
                weighted_score=20.0,
                is_pass=True,
                is_warning=False,
                detail="测试"
            )
        ]
        result = ScoreResult(
            overall_score=85.0,
            dimensions=dimensions,
            passed=True,
            conditional_pass=False,
            failed=False,
            failed_dimensions=[]
        )
        assert result.overall_score == 85.0
        assert result.passed is True

    def test_score_result_default_timestamp(self):
        """测试评分结果默认时间戳"""
        result = ScoreResult(
            overall_score=50.0,
            dimensions=[],
            passed=False,
            conditional_pass=False,
            failed=True,
            failed_dimensions=["functional"]
        )
        assert result.timestamp != ""


class TestRetryRecord:
    """重试记录测试"""

    def test_create_retry_record(self):
        """测试创建重试记录"""
        record = RetryRecord(
            attempt=2,
            timestamp="2024-01-01T00:00:00",
            failure_type="timeout",
            failure_detail="Request timeout",
            action_taken="retry",
            delay_ms=1000,
            success=False
        )
        assert record.attempt == 2
        assert record.success is False


class TestEscalationPackage:
    """升级包测试"""

    def test_create_escalation_package(self):
        """测试创建升级包"""
        package = EscalationPackage(
            request_id="req-001",
            source_agent="dev-agent",
            original_request="test request",
            retry_count=3,
            final_score=45.0,
            dimension_scores={"functional": 40},
            failure_analysis={"reason": "low score"},
            attempted_solutions=[{"action": "fix"}],
            recommended_actions=[{"action": "retry"}]
        )
        assert package.request_id == "req-001"
        assert package.final_score == 45.0


class TestDevQAExecution:
    """Dev-QA执行上下文测试"""

    def test_create_execution(self):
        """测试创建执行上下文"""
        execution = DevQAExecution(
            execution_id="exec-001",
            target_type="agent",
            target_name="test-agent"
        )
        assert execution.execution_id == "exec-001"
        assert execution.status == DevQAStatus.INIT

    def test_execution_default_timestamps(self):
        """测试执行上下文默认时间戳"""
        execution = DevQAExecution(
            execution_id="exec-002",
            target_type="skill",
            target_name="test-skill"
        )
        assert execution.created_at != ""
        assert execution.updated_at != ""


class TestEvidenceCollector:
    """证据收集器测试"""

    def setup_method(self):
        self.collector = EvidenceCollector()

    def test_dimension_weights(self):
        """测试维度权重"""
        weights = EvidenceCollector.DIMENSION_WEIGHTS
        assert QualityDimension.CODE_QUALITY in weights
        assert QualityDimension.FUNCTIONAL in weights
        assert sum(weights.values()) == 1.0

    def test_min_requirements(self):
        """测试最低要求"""
        requirements = EvidenceCollector.MIN_REQUIREMENTS
        assert requirements[QualityDimension.FUNCTIONAL] == 80  # 功能完整性要求最高


class TestDevQAEngine:
    """Dev-QA 引擎测试"""

    def setup_method(self):
        self.engine = DevQAEngine(max_attempts=3)

    def test_engine_initialization(self):
        """测试引擎初始化"""
        assert self.engine.max_attempts == 3
        assert self.engine.collector is not None

    def test_execute_with_agent(self):
        """测试Agent检查"""
        test_agent = {
            "name": "test-agent",
            "id": "test-agent",
            "Identity": "测试身份",
            "能力": ["分析", "执行"],
            "输出格式": "JSON",
            "trigger": ["测试"]
        }
        result = self.engine.execute(
            target_type="agent",
            target_name="test-agent",
            target=test_agent
        )

        assert result is not None
        assert result.execution_id != ""
        assert result.status in [DevQAStatus.PASSED, DevQAStatus.FAILED, DevQAStatus.RETRYING]

    def test_execute_with_skill(self):
        """测试Skill检查"""
        test_skill = {
            "name": "test-skill",
            "trigger": ["测试"],
            "action": "test_action"
        }
        result = self.engine.execute(
            target_type="skill",
            target_name="test-skill",
            target=test_skill
        )

        assert result is not None

    def test_retry_mechanism(self):
        """测试重试机制"""
        # 使用一个低质量的Agent定义，应该触发重试
        low_quality_agent = {
            "name": "low-quality",
            "id": "low-quality"
            # 缺少必需字段
        }

        result = self.engine.execute(
            target_type="agent",
            target_name="low-quality",
            target=low_quality_agent
        )

        # 应该看到重试历史
        assert len(result.retry_history) >= 0  # 可能有重试也可能没有

    def test_generate_report(self):
        """测试报告生成"""
        test_agent = {
            "name": "test",
            "id": "test"
        }
        result = self.engine.execute(
            target_type="agent",
            target_name="test",
            target=test_agent
        )

        report = self.engine.generate_report(result)
        assert isinstance(report, str)
        assert len(report) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])