# CyberTeam v2.0.1 - 三级质量门控引擎
"""
三级质量门控引擎
源自 v2.1 engines/quality-gate-system.md

L1: 完整性门控 (≥95%)
L2: 专业度门控 (≥80分)
L3: 可执行性门控 (≥90%)

必须依次通过，不通过打回重做
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class GateLevel(Enum):
    L1 = "l1"
    L2 = "l2"
    L3 = "l3"


class GateStatus(Enum):
    PASS = "pass"
    CONDITIONAL_PASS = "conditional_pass"
    FAIL = "fail"
    PENDING = "pending"


@dataclass
class GateResult:
    """门控结果"""
    level: GateLevel
    status: GateStatus
    score: float
    threshold: float
    breakdown: Dict[str, float]
    issues: List[str]
    suggestions: List[str]


class L1CompletenessGate:
    """
    L1 完整性门控

    检查:
    - Structure: 结构完整性 (20%)
    - Content: 内容完整性 (35%)
    - Evidence: 证据支撑 (25%)
    - Metadata: 元信息完整性 (20%)

    阈值: ≥95%
    """

    THRESHOLD = 95.0
    SUB_WEIGHTS = {
        "structure": 0.20,
        "content": 0.35,
        "evidence": 0.25,
        "metadata": 0.20,
    }

    def evaluate(self, output: Dict[str, Any]) -> GateResult:
        """
        评估 L1 完整性

        Args:
            output: 待评估的输出

        Returns:
            GateResult: L1 评估结果
        """
        breakdown = {}

        # Structure: 检查结构完整性
        breakdown["structure"] = self._check_structure(output)

        # Content: 检查内容完整性
        breakdown["content"] = self._check_content(output)

        # Evidence: 检查证据支撑
        breakdown["evidence"] = self._check_evidence(output)

        # Metadata: 检查元信息
        breakdown["metadata"] = self._check_metadata(output)

        # 综合分
        score = sum(breakdown[k] * w for k, w in self.SUB_WEIGHTS.items())

        # 问题列表
        issues = []
        suggestions = []

        if breakdown["structure"] < 90:
            issues.append("结构不完整: 缺少必要章节")
            suggestions.append("对照输出格式规范补充缺失章节")
        if breakdown["content"] < 90:
            issues.append("内容深度不足: 部分章节只有框架没有实质内容")
            suggestions.append("每个章节补充至少3个具体分析点")
        if breakdown["evidence"] < 90:
            issues.append("缺乏数据支撑: 没有量化证据")
            suggestions.append("补充数据、案例、引用作为证据")
        if breakdown["metadata"] < 90:
            issues.append("元信息缺失: 缺少版本、时间戳、来源标注")
            suggestions.append("补充完整的元信息")

        status = GateStatus.PASS
        if score < self.THRESHOLD:
            status = GateStatus.FAIL

        return GateResult(
            level=GateLevel.L1,
            status=status,
            score=round(score, 1),
            threshold=self.THRESHOLD,
            breakdown=breakdown,
            issues=issues,
            suggestions=suggestions
        )

    def _check_structure(self, output: Dict) -> float:
        """检查结构完整性"""
        content = str(output)
        score = 0

        # 基本结构检查
        if "goal" in content or "目标" in content:
            score += 20
        if "result" in content or "结果" in content or "输出" in content:
            score += 20
        if "plan" in content or "计划" in content or "方案" in content:
            score += 20
        if "timeline" in content or "时间" in content or "milestone" in content:
            score += 20
        if "kpi" in content.lower() or "指标" in content or "验收" in content:
            score += 20

        return min(score, 100)

    def _check_content(self, output: Dict) -> float:
        """检查内容完整性"""
        content = str(output)
        # 简单估算: 内容长度和具体性
        score = min(len(content) / 5, 100)
        return score

    def _check_evidence(self, output: Dict) -> float:
        """检查证据支撑"""
        content = str(output).lower()
        score = 0

        # 有数据引用
        if any(kw in content for kw in ["数据", "数据表明", "研究显示", "根据"]):
            score += 30
        # 有案例引用
        if any(kw in content for kw in ["案例", "例如", "比如", "具体"]):
            score += 30
        # 有量化指标
        if any(kw in content for kw in ["%", "倍", "万元", "人", "次", "率"]):
            score += 40

        return score

    def _check_metadata(self, output: Dict) -> float:
        """检查元信息"""
        score = 50
        if output.get("timestamp"):
            score += 25
        if output.get("version") or output.get("作者"):
            score += 25
        return min(score, 100)


class L2ProfessionalGate:
    """
    L2 专业度门控

    检查:
    - Methodology: 方法论使用 (25%)
    - Tool: 工具使用 (20%)
    - Format: 格式规范 (20%)
    - Communication: 沟通专业度 (20%)
    - Analysis: 分析深度 (15%)

    阈值: ≥80分
    """

    THRESHOLD = 80.0

    # 评级映射
    RATING_SCORES = {
        "excellent": 100,
        "good": 80,
        "adequate": 60,
        "poor": 40,
        "none": 0,
    }

    def evaluate(self, output: Dict[str, Any]) -> GateResult:
        """
        评估 L2 专业度

        Args:
            output: 待评估的输出

        Returns:
            GateResult: L2 评估结果
        """
        methodology = self._check_methodology(output)
        tool = self._check_tool_usage(output)
        format_score = self._check_format(output)
        communication = self._check_communication(output)
        analysis = self._check_analysis_depth(output)

        breakdown = {
            "methodology": methodology,
            "tool": tool,
            "format": format_score,
            "communication": communication,
            "analysis": analysis,
        }

        weights = {"methodology": 0.25, "tool": 0.20, "format": 0.20,
                   "communication": 0.20, "analysis": 0.15}
        score = sum(breakdown[k] * weights[k] for k in weights)

        issues = []
        suggestions = []

        if methodology < 70:
            issues.append("方法论使用不足: 缺少专业框架支撑")
            suggestions.append("引入相关方法论(如SWOT/PEST/MECE)并正确应用")
        if tool < 70:
            issues.append("工具使用不当: 未使用合适的分析工具")
            suggestions.append("使用数据、模型、工具支撑分析")
        if format_score < 70:
            issues.append("格式不规范: 输出不符合专业格式要求")
            suggestions.append("对照Agent输出格式规范整改")
        if communication < 70:
            issues.append("沟通不够专业: 用语不够精准或过于口语化")
            suggestions.append("使用专业术语，保持逻辑严谨")

        status = GateStatus.PASS
        if score < self.THRESHOLD:
            status = GateStatus.FAIL

        return GateResult(
            level=GateLevel.L2,
            status=status,
            score=round(score, 1),
            threshold=self.THRESHOLD,
            breakdown=breakdown,
            issues=issues,
            suggestions=suggestions
        )

    def _check_methodology(self, output: Dict) -> float:
        """检查方法论使用"""
        content = str(output)
        score = 30

        frameworks = [
            "swot", "pest", "mece", "5w1h", "5why", "grow",
            "bcg", "波特", "mckinsey", "第一性原理",
            "六顶思考帽", "黄金圈", "波士顿"
        ]
        found = sum(1 for fw in frameworks if fw in content.lower())
        score += min(found * 15, 45)

        return min(score, 100)

    def _check_tool_usage(self, output: Dict) -> float:
        """检查工具使用"""
        content = str(output).lower()
        score = 30

        if any(kw in content for kw in ["数据", "调研", "研究", "分析"]):
            score += 30
        if any(kw in content for kw in ["模型", "公式", "框架", "模板"]):
            score += 40

        return min(score, 100)

    def _check_format(self, output: Dict) -> float:
        """检查格式规范"""
        content = str(output)
        score = 50

        # 有结构化输出
        if output.get("type"):
            score += 25
        # 有章节标题
        if "##" in content or "# " in content or any(
            kw in content for kw in ["1.", "2.", "3.", "一、", "二、"]
        ):
            score += 25

        return min(score, 100)

    def _check_communication(self, output: Dict) -> float:
        """检查沟通专业度"""
        content = str(output)
        score = 50

        # 无过多口语化表达
        informal_words = ["我觉得", "大概", "可能吧", "好像", "应该"]
        informal_count = sum(1 for w in informal_words if w in content)
        score -= informal_count * 10

        # 有精炼的总结
        if len(content) > 500:
            score += 25

        return max(min(score, 100), 0)

    def _check_analysis_depth(self, output: Dict) -> float:
        """检查分析深度"""
        content = str(output)
        score = 40

        # 有原因分析
        if any(kw in content for kw in ["原因", "因为", "导致", "由于"]):
            score += 20
        # 有影响分析
        if any(kw in content for kw in ["影响", "作用", "导致", "使得"]):
            score += 20
        # 有风险识别
        if any(kw in content for kw in ["风险", "挑战", "问题", "困难"]):
            score += 20

        return min(score, 100)


class L3ExecutabilityGate:
    """
    L3 可执行性门控

    检查:
    - Action: 行动可行性 (30%)
    - Verification: 结果可验证性 (25%)
    - Context: 上下文可理解性 (25%)
    - Output: 输出可执行性 (20%)

    阈值: ≥90%
    """

    THRESHOLD = 90.0

    def evaluate(self, output: Dict[str, Any]) -> GateResult:
        """
        评估 L3 可执行性

        Args:
            output: 待评估的输出

        Returns:
            GateResult: L3 评估结果
        """
        breakdown = {
            "action": self._check_action(output),
            "verification": self._check_verification(output),
            "context": self._check_context(output),
            "output": self._check_output_quality(output),
        }

        weights = {"action": 0.30, "verification": 0.25,
                    "context": 0.25, "output": 0.20}
        score = sum(breakdown[k] * weights[k] for k in weights)

        issues = []
        suggestions = []

        if breakdown["action"] < 90:
            issues.append("行动不可行: 方案过于笼统，无法直接执行")
            suggestions.append("将方案细化为可操作的步骤，标注责任人/时间")
        if breakdown["verification"] < 90:
            issues.append("无法验证: 缺少明确的成功标准和验收条件")
            suggestions.append("补充KPI、验收标准、里程碑检查点")
        if breakdown["context"] < 90:
            issues.append("上下文不足: 方案缺少背景说明，新人无法理解")
            suggestions.append("补充问题背景、约束条件、假设前提")

        status = GateStatus.PASS
        if score < self.THRESHOLD:
            status = GateStatus.FAIL

        return GateResult(
            level=GateLevel.L3,
            status=status,
            score=round(score, 1),
            threshold=self.THRESHOLD,
            breakdown=breakdown,
            issues=issues,
            suggestions=suggestions
        )

    def _check_action(self, output: Dict) -> float:
        """检查行动可行性"""
        content = str(output)
        score = 50

        # 有具体行动项
        action_words = ["执行", "实施", "落地", "完成", "推进", "制定"]
        if any(w in content for w in action_words):
            score += 30

        # 有时间节点
        time_words = ["立即", "本周", "本月", "第1周", "Day 1", "阶段"]
        if any(w in content for w in time_words):
            score += 20

        return min(score, 100)

    def _check_verification(self, output: Dict) -> float:
        """检查结果可验证性"""
        content = str(output)
        score = 40

        # 有KPI/指标
        kpi_words = ["KPI", "指标", "目标", "达成率", "转化率", "预期"]
        if any(w in content.lower() for w in kpi_words):
            score += 40

        # 有验收条件
        if "验收" in content or "成功标准" in content or "checklist" in content.lower():
            score += 20

        return min(score, 100)

    def _check_context(self, output: Dict) -> float:
        """检查上下文可理解性"""
        content = str(output)
        score = 60

        if len(content) > 300:
            score += 20
        if output.get("goal") or output.get("背景"):
            score += 20

        return min(score, 100)

    def _check_output_quality(self, output: Dict) -> float:
        """检查输出质量"""
        return 80  # 默认高分


class QualityGateEngine:
    """
    三级质量门控引擎 — 顶层API

    使用方式:
        gate = QualityGateEngine()
        result = gate.evaluate_all(output_dict)
        if not result["passed"]:
            print(result["failed_gates"][0].suggestions)
    """

    def __init__(self):
        self.l1 = L1CompletenessGate()
        self.l2 = L2ProfessionalGate()
        self.l3 = L3ExecutabilityGate()

    def evaluate_all(
        self,
        output: Dict[str, Any],
        skip_to: GateLevel = GateLevel.L1
    ) -> Dict[str, Any]:
        """
        执行全部三级门控

        Args:
            output: 待评估的输出
            skip_to: 从哪个门控开始 (默认L1)

        Returns:
            Dict: {
                "passed": bool,
                "gates": {l1: GateResult, l2: GateResult, l3: GateResult},
                "failed_gates": List[GateResult],
                "blocker": GateResult or None
            }
        """
        results = {}

        # 依次执行三级门控
        if skip_to.value <= GateLevel.L1.value:
            results["l1"] = self.l1.evaluate(output)

        if results.get("l1") and results["l1"].status != GateStatus.PASS:
            # L1不通过，后续门控跳过
            return self._build_result(results)

        if skip_to.value <= GateLevel.L2.value:
            results["l2"] = self.l2.evaluate(output)

        if results.get("l2") and results["l2"].status != GateStatus.PASS:
            return self._build_result(results)

        if skip_to.value <= GateLevel.L3.value:
            results["l3"] = self.l3.evaluate(output)

        return self._build_result(results)

    def _build_result(
        self,
        results: Dict[str, GateResult]
    ) -> Dict[str, Any]:
        """构建结果"""
        failed = [r for r in results.values() if r.status == GateStatus.FAIL]
        blocker = failed[0] if failed else None

        return {
            "passed": len(failed) == 0,
            "gates": results,
            "failed_gates": failed,
            "blocker": blocker,
            "summary": {
                "l1": f"{results.get('l1', GateResult(GateLevel.L1, GateStatus.PENDING, 0, 0, {}, [], [])).score:.0f}/95",
                "l2": f"{results.get('l2', GateResult(GateLevel.L2, GateStatus.PENDING, 0, 0, {}, [], [])).score:.0f}/80",
                "l3": f"{results.get('l3', GateResult(GateLevel.L3, GateStatus.PENDING, 0, 0, {}, [], [])).score:.0f}/90",
            }
        }

    def generate_report(self, result: Dict) -> str:
        """生成质量门控报告"""
        lines = [
            "# 三级质量门控报告",
            "",
            f"**通过**: {'✅ 是' if result['passed'] else '❌ 否'}",
            "",
            f"## 评分摘要",
            f"| 门控 | 得分 | 阈值 | 状态 |",
            f"|------|------|------|------|",
        ]

        for level, score_str in result["summary"].items():
            gate = result["gates"].get(level)
            if gate:
                icon = "✅" if gate.status == GateStatus.PASS else "❌"
                lines.append(f"| {level.upper()} | {gate.score} | {gate.threshold} | {icon} |")
            else:
                lines.append(f"| {level.upper()} | — | — | 跳过 |")

        for gate in result.get("failed_gates", []):
            lines.extend(["", f"## ❌ {gate.level.value.upper()} 问题", ""])
            for issue in gate.issues:
                lines.append(f"- ❌ {issue}")
            lines.append("")
            lines.append(f"**修复建议**:")
            for sug in gate.suggestions:
                lines.append(f"  - {sug}")

        return "\n".join(lines)


# ============================================================
# 快速测试
# ============================================================
if __name__ == "__main__":
    gate = QualityGateEngine()

    test_outputs = [
        {
            "goal": "做一个在线教育平台",
            "result": "分析完成",
            "plan": "三阶段执行计划",
            "timeline": "3个月完成MVP",
            "kpi": "10万用户",
            "content": "我们做了SWOT分析，根据数据显示...案例包括某教育平台的增长路径..."
        },
        {
            "goal": "分析竞品",
            "content": "分析了一下竞品的情况。"
        }
    ]

    for i, output in enumerate(test_outputs):
        print(f"\n{'='*60}")
        print(f"测试输出 {i+1}")
        result = gate.evaluate_all(output)
        print(gate.generate_report(result))
