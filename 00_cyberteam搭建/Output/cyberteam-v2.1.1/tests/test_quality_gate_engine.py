"""
CyberTeam v2 - 质量门控引擎测试套件

测试覆盖：
1. QualityGateEngine - 三级质量门控
2. GateResult - 门控结果
3. L1/L2/L3 门控评估
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.quality_gate_engine import (
    QualityGateEngine,
    GateLevel,
    GateStatus,
    GateResult,
    L1CompletenessGate,
    L2ProfessionalGate,
    L3ExecutabilityGate
)


class TestGateResult:
    """门控结果测试"""

    def test_create_gate_result(self):
        """测试创建门控结果"""
        result = GateResult(
            level=GateLevel.L1,
            status=GateStatus.PASS,
            score=95.0,
            threshold=95.0,
            breakdown={"structure": 100},
            issues=[],
            suggestions=[]
        )
        assert result.level == GateLevel.L1
        assert result.status == GateStatus.PASS
        assert result.score == 95.0

    def test_fail_status(self):
        """测试失败状态"""
        result = GateResult(
            level=GateLevel.L1,
            status=GateStatus.FAIL,
            score=80.0,
            threshold=95.0,
            breakdown={},
            issues=["结构不完整"],
            suggestions=["补充内容"]
        )
        assert result.status == GateStatus.FAIL


class TestL1CompletenessGate:
    """L1 完整性门控测试"""

    def setup_method(self):
        self.gate = L1CompletenessGate()

    def test_gate_threshold(self):
        """测试阈值"""
        assert self.gate.THRESHOLD == 95.0

    def test_sub_weights(self):
        """测试子权重"""
        weights = self.gate.SUB_WEIGHTS
        assert sum(weights.values()) == 1.0

    def test_evaluate_complete_output(self):
        """测试完整输出的评估"""
        output = {
            "goal": "做一个教育平台",
            "result": "完成分析",
            "plan": "三阶段计划",
            "timeline": "6个月",
            "kpi": "10万用户",
            "timestamp": "2024-01-01",
            "version": "1.0"
        }
        result = self.gate.evaluate(output)
        assert isinstance(result, GateResult)
        assert result.level == GateLevel.L1
        assert result.score >= 0

    def test_evaluate_incomplete_output(self):
        """测试不完整输出的评估"""
        output = {"goal": "test"}
        result = self.gate.evaluate(output)
        assert result.score < 95.0  # 应该不通过
        assert result.status == GateStatus.FAIL

    def test_check_structure_with_content(self):
        """测试结构检查"""
        output = {
            "goal": "目标",
            "result": "结果",
            "plan": "计划",
            "timeline": "时间",
            "kpi": "指标"
        }
        score = self.gate._check_structure(output)
        assert score >= 80

    def test_check_evidence_with_data(self):
        """测试证据检查-有数据"""
        output = {
            "content": "根据数据显示，增长率为30%，案例表明效果良好"
        }
        score = self.gate._check_evidence(output)
        assert score > 0


class TestL2ProfessionalGate:
    """L2 专业度门控测试"""

    def setup_method(self):
        self.gate = L2ProfessionalGate()

    def test_gate_threshold(self):
        """测试阈值"""
        assert self.gate.THRESHOLD == 80.0

    def test_rating_scores(self):
        """测试评级分数"""
        scores = self.gate.RATING_SCORES
        assert scores["excellent"] == 100
        assert scores["good"] == 80
        assert scores["poor"] == 40

    def test_evaluate_professional_output(self):
        """测试专业输出评估"""
        output = {
            "content": """
            使用SWOT分析方法进行战略规划。
            优势：品牌优势明显
            劣势：技术储备不足
            机会：市场增长30%
            威胁：竞争加剧

            采用PEST分析宏观环境：
            政治：政策支持
            经济：增长稳定

            结论：通过专业方法论支撑，制定完整战略方案。
            """
        }
        result = self.gate.evaluate(output)
        assert isinstance(result, GateResult)
        assert result.level == GateLevel.L2
        assert result.score >= 0

    def test_evaluate_non_professional_output(self):
        """测试非专业输出评估"""
        output = {"content": "这是一个测试"}
        result = self.gate.evaluate(output)
        assert result.score < 80  # 应该分数较低


class TestL3ExecutabilityGate:
    """L3 可执行性门控测试"""

    def setup_method(self):
        self.gate = L3ExecutabilityGate()

    def test_gate_threshold(self):
        """测试阈值"""
        assert self.gate.THRESHOLD == 90.0


class TestQualityGateEngine:
    """质量门控引擎测试"""

    def setup_method(self):
        self.engine = QualityGateEngine()

    def test_engine_initialization(self):
        """测试引擎初始化"""
        assert self.engine.l1 is not None
        assert self.engine.l2 is not None
        assert self.engine.l3 is not None

    def test_evaluate_all_complete(self):
        """测试完整输出评估"""
        output = {
            "goal": "做一个教育平台",
            "result": "分析完成，包含SWOT分析和具体执行步骤",
            "plan": "三阶段计划：1.基础建设 2.用户增长 3.商业化",
            "timeline": "6个月：第1月产品MVP，第2-4月获客，第5-6月变现",
            "kpi": "10万付费用户，ARR 1000万",
            "version": "1.0",
            "timestamp": "2024-01-01",
            "content": """
            使用SWOT分析：优势（品牌强）、劣势（技术弱）、机会（市场30%增长）、威胁（竞争加剧）。
            数据支撑：据QuestMobile显示，行业DAU年增25%。
            案例参考：某竞品6个月增长10倍。
            具体执行：第一步招聘团队，第二步搭建MVP，第三步投放测试，第四步优化迭代。
            风险提示：技术团队可能成为瓶颈，需提前储备。
            """
        }
        result = self.engine.evaluate_all(output)

        assert "gates" in result
        assert "l1" in result["gates"]
        assert "summary" in result
        assert "passed" in result
        # L1通过时才会继续到L2/L3
        if result["passed"]:
            assert "l2" in result["gates"]
            assert "l3" in result["gates"]

    def test_evaluate_all_incomplete(self):
        """测试不完整输出评估"""
        output = {"content": "test"}
        result = self.engine.evaluate_all(output)

        # 不完整的输出应该不通过
        assert result["passed"] is False

    def test_generate_report(self):
        """测试报告生成"""
        output = {
            "goal": "test",
            "result": "result"
        }
        qa_result = self.engine.evaluate_all(output)
        report = self.engine.generate_report(qa_result)

        assert isinstance(report, str)
        assert len(report) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])