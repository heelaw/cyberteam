#!/usr/bin/env python3
"""
活动效果评估 - 评估计算脚本

功能：
1. 数据完整性校验（P0必须数据）
2. 核心指标计算（ROI、CAC、完成率、转化率）
3. 判断阈值校验（对比行业基准）
4. 产出结构化评估结果

输入格式（JSON）：
{
    "活动名称": "xxx",
    "活动周期": {"开始": "2024-01-01", "结束": "2024-01-07"},
    "活动类型": "拉新|促活|转化|品牌|复购|裂变",
    "活动目标": {
        "新用户注册数": 50000,
        "GMV": 10000000,
        "CAC上限": 45,
        "ROI下限": 2.0
    },
    "实际数据": {
        "产出指标": {
            "新用户注册数": 62000,
            "GMV": 11500000
        },
        "成本指标": {
            "投放成本": 750000,
            "运营成本": 350000,
            "人力成本": 80000,
            "技术成本": 50000,
            "补贴成本": 0
        },
        "传播指标": {
            "曝光量": 50000000,
            "点击量": 1500000,
            "分享数": 32000
        },
        "用户行为指标": {
            "访问UV": 800000,
            "参与用户数": 450000,
            "满意度": 4.2
        }
    },
    "对比基准": {
        "目标基准": true,
        "历史基准": {"上期ROI": 1.5, "上期CAC": 48}
    }
}

输出格式（JSON）：
{
    "skill": "活动效果评估",
    "version": "2.0.0",
    "data_validation": {...},
    "computed_metrics": {...},
    "judgment": {...},
    "output": {...}
}
"""

from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from enum import Enum


# ============ 阈值常量 ============

ROI_THRESHOLDS = {
    "excellent": 2.0,   # ROI >= 2.0
    "good": 1.5,        # ROI >= 1.5
    "acceptable": 1.0,    # ROI >= 1.0
    "fail": 0.0,        # ROI < 0
    "danger": -0.5       # ROI < -0.5
}

CAC_CHANGE_THRESHOLDS = {
    "excellent": 0.05,   # 增幅 <= 5%
    "good": 0.10,        # 增幅 <= 10%
    "warning": 0.30,     # 增幅 > 30%
    "danger": 0.50       # 增幅 > 50%
}

COST_STRUCTURE_THRESHOLDS = {
    "投放占比": {"warning": 0.70, "danger": 0.80},
    "补贴占比": {"warning": 0.20, "danger": 0.30},
    "人力占比": {"warning": 0.35, "danger": 0.40}
}

FUNNEL_THRESHOLDS = {
    "ctr": {"excellent": 0.03, "good": 0.01, "warning": 0.005},
    "participation_rate": {"excellent": 0.50, "good": 0.30, "warning": 0.15},
    "share_rate": {"excellent": 0.10, "good": 0.05, "warning": 0.02}
}

SATISFACTION_THRESHOLDS = {
    "excellent": 4.5,
    "good": 4.0,
    "warning": 3.5,
    "danger": 3.0
}

COMPLETION_RATE_THRESHOLDS = {
    "excellent": 1.10,   # >= 110%
    "good": 1.00,       # >= 100%
    "acceptable": 0.80,  # >= 80%
    "fail": 0.00        # < 80%
}


# ============ 数据结构 ============

class ValidationStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class ValidationResult:
    status: ValidationStatus
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class ComputedMetric:
    name: str
    value: float
    unit: str
    description: str
    status: ValidationStatus = ValidationStatus.PASS
    threshold_comparison: dict = field(default_factory=dict)


@dataclass
class DimensionJudgment:
    dimension: str
    rating: str  # A/B/C/D
    score: float  # 1-5
    key_findings: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


@dataclass
class ActivityAssessment:
    # 基础信息
    activity_name: str
    activity_type: str
    activity_period: str

    # 数据验证
    data_validation: ValidationResult

    # 计算指标
    computed_metrics: dict[str, ComputedMetric]

    # 四维度判断
    dimensions: dict[str, DimensionJudgment]

    # 综合结论
    overall_rating: str
    overall_score: float
    roi: float
    cac: float
    completion_rate: float

    # 问题清单
    key_problems: list[str] = field(default_factory=list)
    reuse_recommendations: list[str] = field(default_factory=list)
    stop_recommendations: list[str] = field(default_factory=list)

    # 行动建议
    next_steps: list[dict] = field(default_factory=list)

    # 置信度
    confidence: str = "高"
    confidence_reasons: list[str] = field(default_factory=list)


# ============ 工具函数 ============

def to_number(value: Any) -> Optional[float]:
    """将任意值转换为数字，支持带单位的字符串"""
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if not isinstance(value, str):
        return None
    # 提取数字
    digits = ''.join(ch for ch in value if ch.isdigit() or ch in '.-')
    if digits in {'', '-', '.', '-.', '.-'}:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


def safe_divide(a: Any, b: Any, default: Optional[float] = None) -> Optional[float]:
    """安全除法，避免除零"""
    a_num = to_number(a)
    b_num = to_number(b)
    if a_num is None or b_num is None or b_num == 0:
        return default
    return a_num / b_num


def percentage(value: float) -> str:
    """格式化百分比"""
    return f"{value * 100:.1f}%"


def yuan(value: float) -> str:
    """格式化金额（元）"""
    if abs(value) >= 100000000:
        return f"{value/100000000:.2f}亿"
    elif abs(value) >= 10000:
        return f"{value/10000:.2f}万"
    else:
        return f"{value:.2f}"


# ============ 核心评估逻辑 ============

class ActivityEvaluator:
    """活动效果评估器"""

    def __init__(self, payload: dict):
        self.payload = payload
        self.activity_name = payload.get("活动名称", "未知活动")
        self.activity_type = payload.get("活动类型", "未知")
        period = payload.get("活动周期", {})
        if isinstance(period, dict):
            self.activity_period = f"{period.get('开始', '')} ~ {period.get('结束', '')}"
        else:
            self.activity_period = str(period)
        self.target = payload.get("活动目标", {})
        self.actual = payload.get("实际数据", {})
        self.baseline = payload.get("对比基准", {})

    def validate_p0_data(self) -> ValidationResult:
        """校验P0必须数据是否完整"""
        missing = []
        warnings = []

        # 活动基础信息
        if not self.activity_name or self.activity_name == "未知活动":
            missing.append("活动名称")
        if not self.activity_type or self.activity_type == "未知":
            missing.append("活动类型")

        # 活动目标
        if not self.target:
            missing.append("活动目标")
        else:
            if "新用户注册数" not in self.target and "GMV" not in self.target:
                missing.append("活动目标（无量化指标）")

        # 产出数据
        产出 = self.actual.get("产出指标", {})
        if not 产出:
            missing.append("产出指标")
        elif "新用户注册数" not in 产出 and "GMV" not in 产出:
            missing.append("产出指标（无核心产出）")

        # 成本数据
        成本 = self.actual.get("成本指标", {})
        if not 成本:
            missing.append("成本指标")
        else:
            total_cost = sum(filter(None, (to_number(v) for v in 成本.values())), 0.0)
            if total_cost == 0:
                warnings.append("总成本为0，请确认数据")

        if missing:
            return ValidationResult(
                status=ValidationStatus.FAIL,
                message=f"P0数据缺失：{', '.join(missing)}",
                details={"missing_p0": missing, "warnings": warnings}
            )

        if warnings:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"数据警告：{', '.join(warnings)}",
                details={"missing_p0": [], "warnings": warnings}
            )

        return ValidationResult(
            status=ValidationStatus.PASS,
            message="P0数据完整",
            details={"missing_p0": [], "warnings": []}
        )

    def compute_metrics(self) -> dict[str, ComputedMetric]:
        """计算核心评估指标"""
        metrics = {}
        产出 = self.actual.get("产出指标", {})
        成本 = self.actual.get("成本指标", {})
        传播 = self.actual.get("传播指标", {})
        行为 = self.actual.get("用户行为指标", {})

        # ===== 成本相关 =====
        total_cost = sum(filter(None, (to_number(v) for v in 成本.values())), 0.0)

        # 总成本
        metrics["总成本"] = ComputedMetric(
            name="总成本",
            value=total_cost,
            unit="元",
            description="活动总投入",
            status=ValidationStatus.PASS if total_cost > 0 else ValidationStatus.FAIL
        )

        # ===== 产出相关 =====
        gmv = to_number(产出.get("GMV") or 产出.get("新品销售额") or 产出.get("收入") or 产出.get("营收") or 0)
        new_users = to_number(产出.get("新用户注册数") or 产出.get("新增用户") or 0)
        first_order = to_number(产出.get("新用户首单转化数") or 产出.get("首单转化数") or 0)

        # GMV
        metrics["GMV"] = ComputedMetric(
            name="GMV",
            value=gmv or 0,
            unit="元",
            description="活动带来的成交金额"
        )

        # 新用户数
        metrics["新用户注册数"] = ComputedMetric(
            name="新用户注册数",
            value=new_users or 0,
            unit="人",
            description="新增注册用户数"
        )

        # ===== ROI =====
        roi = None
        if total_cost > 0 and gmv:
            roi = (gmv - total_cost) / total_cost

        roi_status = ValidationStatus.PASS
        if roi is not None:
            if roi >= ROI_THRESHOLDS["excellent"]:
                roi_status = ValidationStatus.PASS
            elif roi >= ROI_THRESHOLDS["good"]:
                roi_status = ValidationStatus.PASS
            elif roi >= ROI_THRESHOLDS["acceptable"]:
                roi_status = ValidationStatus.WARNING
            else:
                roi_status = ValidationStatus.FAIL

        metrics["ROI"] = ComputedMetric(
            name="ROI",
            value=roi if roi is not None else 0,
            unit="",
            description="投资回报率 (GMV-成本)/成本",
            status=roi_status,
            threshold_comparison={
                "优秀标准": f">={ROI_THRESHOLDS['excellent']}",
                "实际值": f"{roi:.2%}" if roi is not None else "无法计算"
            }
        )

        # ===== CAC =====
        effective_users = new_users or 0
        if first_order and first_order > 0:
            effective_users = first_order  # 用首单用户作为有效用户

        cac = None
        if total_cost > 0 and effective_users > 0:
            cac = total_cost / effective_users

        cac_status = ValidationStatus.PASS
        if cac is not None:
            cac_limit = to_number(self.target.get("CAC上限"))
            if cac_limit:
                if cac <= cac_limit:
                    cac_status = ValidationStatus.PASS
                elif cac <= cac_limit * 1.3:
                    cac_status = ValidationStatus.WARNING
                else:
                    cac_status = ValidationStatus.FAIL

        metrics["CAC"] = ComputedMetric(
            name="CAC",
            value=cac if cac is not None else 0,
            unit="元/人",
            description=f"获客成本 总成本/{effective_users}人",
            status=cac_status,
            threshold_comparison={
                "目标上限": f"{to_number(self.target.get('CAC上限'))}元" if self.target.get("CAC上限") else "未设",
                "实际值": f"{cac:.2f}元" if cac is not None else "无法计算"
            }
        )

        # ===== 完成率 =====
        completion_rates = {}

        # GMV完成率
        gmv_target = to_number(self.target.get("GMV"))
        if gmv_target and gmv:
            cr = gmv / gmv_target
            completion_rates["GMV"] = cr

        # 注册完成率
        reg_target = to_number(self.target.get("新用户注册数"))
        if reg_target and new_users:
            cr = new_users / reg_target
            completion_rates["注册数"] = cr

        # 整体完成率
        overall_completion = sum(completion_rates.values()) / len(completion_rates) if completion_rates else 0

        completion_status = ValidationStatus.PASS
        if overall_completion >= COMPLETION_RATE_THRESHOLDS["excellent"]:
            completion_status = ValidationStatus.PASS
        elif overall_completion >= COMPLETION_RATE_THRESHOLDS["good"]:
            completion_status = ValidationStatus.PASS
        elif overall_completion >= COMPLETION_RATE_THRESHOLDS["acceptable"]:
            completion_status = ValidationStatus.WARNING
        else:
            completion_status = ValidationStatus.FAIL

        metrics["完成率"] = ComputedMetric(
            name="目标完成率",
            value=overall_completion,
            unit="",
            description="实际/目标的加权平均",
            status=completion_status,
            threshold_comparison={
                "优秀": f">={COMPLETION_RATE_THRESHOLDS['excellent']}",
                "达标": f">={COMPLETION_RATE_THRESHOLDS['good']}",
                "实际": f"{overall_completion:.1%}"
            }
        )

        # ===== 成本结构 =====
        cost_structure = {}
        for cost_type, amount in 成本.items():
            amt = to_number(amount) or 0
            if total_cost > 0:
                ratio = amt / total_cost
                cost_structure[cost_type] = {
                    "金额": amt,
                    "占比": ratio
                }

                # 检查异常
                thresholds = COST_STRUCTURE_THRESHOLDS.get(cost_type, {})
                if thresholds:
                    if ratio >= thresholds.get("danger", 1.0):
                        metrics[f"成本异常_{cost_type}"] = ComputedMetric(
                            name=f"{cost_type}占比异常",
                            value=ratio,
                            unit="",
                            description=f"{cost_type}占总成本{ratio:.1%}，超过danger阈值{thresholds['danger']:.0%}",
                            status=ValidationStatus.FAIL
                        )

        # ===== 传播漏斗 =====
        exposure = to_number(传播.get("曝光量") or 传播.get("曝光") or 0)
        clicks = to_number(传播.get("点击量") or 传播.get("点击") or 0)
        shares = to_number(传播.get("分享数") or 传播.get("分享") or 0)

        # CTR
        ctr = safe_divide(clicks, exposure)
        if ctr is not None:
            ctr_status = ValidationStatus.PASS
            if ctr >= FUNNEL_THRESHOLDS["ctr"]["excellent"]:
                ctr_status = ValidationStatus.PASS
            elif ctr >= FUNNEL_THRESHOLDS["ctr"]["good"]:
                ctr_status = ValidationStatus.WARNING
            else:
                ctr_status = ValidationStatus.FAIL

            metrics["CTR"] = ComputedMetric(
                name="点击率",
                value=ctr,
                unit="",
                description=f"点击/曝光 {clicks}/{exposure}",
                status=ctr_status,
                threshold_comparison={
                    "优秀": f">={FUNNEL_THRESHOLDS['ctr']['excellent']:.1%}",
                    "良好": f">={FUNNEL_THRESHOLDS['ctr']['good']:.1%}",
                    "实际": f"{ctr:.2%}"
                }
            )

        # 分享率
        visits = to_number(行为.get("访问UV") or 行为.get("访问") or 0)
        participants = to_number(行为.get("参与用户数") or 行为.get("参与") or 0)

        share_rate = safe_divide(shares, participants)
        if share_rate is not None:
            sr_status = ValidationStatus.PASS
            if share_rate >= FUNNEL_THRESHOLDS["share_rate"]["excellent"]:
                sr_status = ValidationStatus.PASS
            elif share_rate >= FUNNEL_THRESHOLDS["share_rate"]["good"]:
                sr_status = ValidationStatus.WARNING
            else:
                sr_status = ValidationStatus.FAIL

            metrics["分享率"] = ComputedMetric(
                name="分享率",
                value=share_rate,
                unit="",
                description=f"分享/参与 {shares}/{participants}",
                status=sr_status,
                threshold_comparison={
                    "优秀": f">={FUNNEL_THRESHOLDS['share_rate']['excellent']:.1%}",
                    "良好": f">={FUNNEL_THRESHOLDS['share_rate']['good']:.1%}",
                    "实际": f"{share_rate:.2%}"
                }
            )

        # ===== 用户行为 =====
        satisfaction = to_number(行为.get("满意度") or 行为.get("用户满意度") or 行为.get("满意度评分") or 0)

        if satisfaction:
            sat_status = ValidationStatus.PASS
            if satisfaction >= SATISFACTION_THRESHOLDS["excellent"]:
                sat_status = ValidationStatus.PASS
            elif satisfaction >= SATISFACTION_THRESHOLDS["good"]:
                sat_status = ValidationStatus.WARNING
            else:
                sat_status = ValidationStatus.FAIL

            metrics["满意度"] = ComputedMetric(
                name="用户满意度",
                value=satisfaction,
                unit="分",
                description=f"满分5分",
                status=sat_status,
                threshold_comparison={
                    "优秀": f">={SATISFACTION_THRESHOLDS['excellent']}",
                    "良好": f">={SATISFACTION_THRESHOLDS['good']}",
                    "实际": f"{satisfaction}/5"
                }
            )

        # 参与率
        participation_rate = safe_divide(participants, visits)
        if participation_rate is not None:
            pr_status = ValidationStatus.PASS
            if participation_rate >= FUNNEL_THRESHOLDS["participation_rate"]["excellent"]:
                pr_status = ValidationStatus.PASS
            elif participation_rate >= FUNNEL_THRESHOLDS["participation_rate"]["good"]:
                pr_status = ValidationStatus.WARNING
            else:
                pr_status = ValidationStatus.FAIL

            metrics["参与率"] = ComputedMetric(
                name="参与率",
                value=participation_rate,
                unit="",
                description=f"参与/访问 {participants}/{visits}",
                status=pr_status,
                threshold_comparison={
                    "优秀": f">={FUNNEL_THRESHOLDS['participation_rate']['excellent']:.1%}",
                    "良好": f">={FUNNEL_THRESHOLDS['participation_rate']['good']:.1%}",
                    "实际": f"{participation_rate:.2%}"
                }
            )

        return metrics

    def judge_dimensions(self, metrics: dict[str, ComputedMetric]) -> dict[str, DimensionJudgment]:
        """四维度判断"""
        dimensions = {}

        # 1. 产出指标
        产出_dimension = DimensionJudgment(
            dimension="产出指标",
            rating="B",
            score=3.0
        )

        roi_metric = metrics.get("ROI")
        completion_metric = metrics.get("完成率")
        gmv_metric = metrics.get("GMV")

        if roi_metric and completion_metric:
            if completion_metric.value >= 1.10 and roi_metric.value >= 2.0:
                产出_dimension.rating = "A"
                产出_dimension.score = 5.0
                产出_dimension.key_findings.append(f"目标完成率{completion_metric.value:.1%}，超越目标")
                产出_dimension.key_findings.append(f"ROI {roi_metric.value:.2%}，投资回报优秀")
            elif completion_metric.value >= 1.0 and roi_metric.value >= 1.5:
                产出_dimension.rating = "B"
                产出_dimension.score = 4.0
                产出_dimension.key_findings.append(f"目标完成率{completion_metric.value:.1%}，达标")
                产出_dimension.key_findings.append(f"ROI {roi_metric.value:.2%}，回报良好")
            elif completion_metric.value >= 0.8:
                产出_dimension.rating = "C"
                产出_dimension.score = 3.0
                产出_dimension.key_findings.append(f"目标完成率{completion_metric.value:.1%}，基本达标")
                产出_dimension.problems.append("ROI未达优秀水平")

        dimensions["产出"] = 产出_dimension

        # 2. 成本指标
        成本_dimension = DimensionJudgment(
            dimension="成本指标",
            rating="B",
            score=3.0
        )

        # 检查是否有成本异常
        cost_anomalies = [k for k in metrics if k.startswith("成本异常_")]
        if cost_anomalies:
            成本_dimension.rating = "D"
            成本_dimension.score = 1.0
            成本_dimension.problems.append(f"发现{len(cost_anomalies)}项成本结构异常")
        else:
            成本_dimension.rating = "B"
            成本_dimension.score = 4.0
            成本_dimension.key_findings.append("成本结构正常，无明显异常")

        dimensions["成本"] = 成本_dimension

        # 3. 传播指标
        传播_dimension = DimensionJudgment(
            dimension="传播指标",
            rating="B",
            score=3.0
        )

        ctr_metric = metrics.get("CTR")
        share_metric = metrics.get("分享率")

        if ctr_metric and share_metric:
            if ctr_metric.status == ValidationStatus.PASS and share_metric.status == ValidationStatus.PASS:
                传播_dimension.rating = "A"
                传播_dimension.score = 5.0
                传播_dimension.key_findings.append(f"CTR {ctr_metric.value:.2%}，点击效率优秀")
                传播_dimension.key_findings.append(f"分享率 {share_metric.value:.2%}，传播价值高")
            elif ctr_metric.status == ValidationStatus.WARNING or share_metric.status == ValidationStatus.WARNING:
                传播_dimension.rating = "C"
                传播_dimension.score = 3.0
                传播_dimension.problems.append("传播效率有提升空间")

        dimensions["传播"] = 传播_dimension

        # 4. 用户行为
        行为_dimension = DimensionJudgment(
            dimension="用户行为",
            rating="B",
            score=3.0
        )

        sat_metric = metrics.get("满意度")
        pr_metric = metrics.get("参与率")

        if sat_metric and pr_metric:
            if sat_metric.value >= 4.0 and pr_metric.value >= 0.30:
                行为_dimension.rating = "A"
                行为_dimension.score = 5.0
                行为_dimension.key_findings.append(f"满意度 {sat_metric.value}/5，用户体验优秀")
                行为_dimension.key_findings.append(f"参与率 {pr_metric.value:.1%}，用户活跃度高")
            elif sat_metric.value >= 3.5:
                行为_dimension.rating = "B"
                行为_dimension.score = 4.0
                行为_dimension.key_findings.append(f"满意度 {sat_metric.value}/5，体验良好")

        dimensions["行为"] = 行为_dimension

        return dimensions

    def generate_judgment(self, metrics: dict[str, ComputedMetric], dimensions: dict[str, DimensionJudgment]) -> dict:
        """生成综合判断"""

        # 计算综合得分
        weights = {"产出": 0.30, "成本": 0.25, "传播": 0.20, "行为": 0.25}
        total_score = sum(dimensions[k].score * weights[k] for k in weights)

        # 综合评级
        if total_score >= 4.5:
            overall_rating = "优秀"
        elif total_score >= 3.5:
            overall_rating = "良好"
        elif total_score >= 2.5:
            overall_rating = "及格"
        elif total_score >= 1.5:
            overall_rating = "偏弱"
        else:
            overall_rating = "失败"

        # ROI修正
        roi_metric = metrics.get("ROI")
        if roi_metric and roi_metric.value < 0:
            # 亏损活动降级
            if overall_rating == "优秀":
                overall_rating = "偏弱"
            elif overall_rating == "良好":
                overall_rating = "及格"
            elif overall_rating == "及格":
                overall_rating = "偏弱"
            elif overall_rating == "偏弱":
                overall_rating = "失败"

        # 问题清单
        key_problems = []
        reuse_recommendations = []
        stop_recommendations = []

        # 从维度提取
        for dim_name, dim in dimensions.items():
            key_problems.extend(dim.problems)

        # 从指标提取
        for metric_name, metric in metrics.items():
            if metric_name.startswith("成本异常_"):
                stop_recommendations.append(f"停止{metric_name.replace('成本异常_', '')}占比过高的打法")
            if metric.status == ValidationStatus.FAIL:
                key_problems.append(f"{metric.name}未达标：{metric.description}")

        # ROI-based判断
        if roi_metric:
            if roi_metric.value < 0:
                stop_recommendations.append("ROI为负，停止当前打法")
                key_problems.append(f"亏损严重，ROI={roi_metric.value:.2%}")
            elif roi_metric.value >= 2.0:
                reuse_recommendations.append("ROI优秀，可复用当前打法")

        # 成本结构判断
        cost_anomalies = [k for k in metrics if k.startswith("成本异常_")]
        if cost_anomalies:
            key_problems.append(f"成本结构失衡，{len(cost_anomalies)}项占比异常")

        # 行动建议
        next_steps = []
        if key_problems:
            next_steps.append({
                "priority": "P0",
                "action": "解决关键问题",
                "details": "; ".join(key_problems[:2]),
                "expected": "指标改善"
            })

        if overall_rating in ["优秀", "良好"]:
            next_steps.append({
                "priority": "P1",
                "action": "复用成功经验",
                "details": "; ".join(reuse_recommendations[:2]) if reuse_recommendations else "复用当前打法",
                "expected": "维持效率"
            })

        return {
            "overall_rating": overall_rating,
            "overall_score": round(total_score, 2),
            "key_problems": key_problems[:5],  # 最多5个
            "reuse_recommendations": reuse_recommendations[:3],  # 最多3个
            "stop_recommendations": stop_recommendations[:3],  # 最多3个
            "next_steps": next_steps
        }

    def run(self) -> dict:
        """执行完整评估流程"""

        # Step 1: 数据验证
        validation = self.validate_p0_data()

        # Step 2: 计算指标
        metrics = self.compute_metrics()

        # Step 3: 四维度判断
        dimensions = self.judge_dimensions(metrics)

        # Step 4: 综合判断
        judgment = self.generate_judgment(metrics, dimensions)

        # 组装结果
        roi_metric = metrics.get("ROI")
        cac_metric = metrics.get("CAC")
        completion_metric = metrics.get("完成率")

        return {
            "skill": "活动效果评估",
            "version": "2.0.0",
            "data_validation": {
                "status": validation.status.value,
                "message": validation.message,
                "details": validation.details
            },
            "computed_metrics": {
                k: {
                    "name": v.name,
                    "value": v.value,
                    "unit": v.unit,
                    "status": v.status.value,
                    "threshold_comparison": v.threshold_comparison
                }
                for k, v in metrics.items()
            },
            "dimensions": {
                k: {
                    "dimension": v.dimension,
                    "rating": v.rating,
                    "score": v.score,
                    "key_findings": v.key_findings,
                    "problems": v.problems
                }
                for k, v in dimensions.items()
            },
            "judgment": judgment,
            "summary": {
                "activity_name": self.activity_name,
                "activity_type": self.activity_type,
                "period": self.activity_period,
                "overall_rating": judgment["overall_rating"],
                "overall_score": judgment["overall_score"],
                "roi": f"{roi_metric.value:.2%}" if roi_metric else "N/A",
                "cac": f"{cac_metric.value:.2f}元" if cac_metric else "N/A",
                "completion_rate": f"{completion_metric.value:.1%}" if completion_metric else "N/A"
            },
            "note": "如需完整报告，请参照 references/四维度评估模板.md 填充数据"
        }


def _load_payload() -> dict:
    """加载输入数据"""
    if len(sys.argv) > 1 and sys.argv[1].strip():
        try:
            return json.loads(sys.argv[1])
        except json.JSONDecodeError:
            pass
    raw = sys.stdin.read().strip()
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    return {}


def main() -> int:
    """主入口"""
    payload = _load_payload()

    if not payload:
        print(json.dumps({
            "error": "未提供输入数据",
            "usage": "python run.py '<JSON数据>' 或通过stdin传入JSON"
        }, ensure_ascii=False, indent=2))
        return 1

    try:
        evaluator = ActivityEvaluator(payload)
        result = evaluator.run()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as e:
        print(json.dumps({
            "error": f"评估失败: {str(e)}",
            "detail": str(e)
        }, ensure_ascii=False, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
