#!/usr/bin/env python3
"""
产品状态评估 - 计算引擎
输入：JSON格式的产品数据
输出：五维度评分、综合得分、健康等级、投入建议

使用方式：
    python run.py < input.json
    python run.py '{"dau": 1500000, "mau": 8000000, ...}'
"""

from __future__ import annotations

import json
import sys
from typing import Any, Optional


def _load_payload() -> dict[str, Any]:
    """从stdin或命令行参数加载JSON数据"""
    if len(sys.argv) > 1 and sys.argv[1].strip():
        try:
            return json.loads(sys.argv[1])
        except json.JSONDecodeError:
            pass
    raw = sys.stdin.read().strip()
    if raw:
        return json.loads(raw)
    return {}


def _to_float(value: Any, default: float = 0.0) -> float:
    """将值转换为浮点数"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip().replace('%', '')
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _to_pct(value: Any) -> float:
    """将百分比字符串转换为浮点数（0-100）"""
    if isinstance(value, str):
        value = value.strip().replace('%', '')
        try:
            return float(value)
        except ValueError:
            return 0.0
    if isinstance(value, (int, float)):
        # 如果值 > 1，认为是小数形式（如0.3表示30%）
        if value <= 1:
            return value * 100
        return float(value)
    return 0.0


# =============================================================================
# B2C 评分函数
# =============================================================================

def _score_b2c_channel(channels: dict, ltv: float = 0) -> dict:
    """
    评估B2C渠道质量
    输入：渠道数据字典，格式 {渠道名: {流量占比: x%, 转化率: x%, CAC: xxx}}
    返回：{score: float, findings: list, risks: list}
    """
    findings = []
    risks = []

    if not channels:
        return {"score": 0.0, "findings": ["缺少渠道数据"], "risks": []}

    total_score = 0.0
    channel_count = 0
    max_concentration = 0.0
    cac_issues = []

    for name, data in channels.items():
        if not isinstance(data, dict):
            continue

        flow_ratio = _to_pct(data.get("流量占比", 0))
        conversion = _to_pct(data.get("转化率", 0))
        cac = _to_float(data.get("CAC", 0))

        channel_count += 1

        # 计算渠道集中度
        if flow_ratio > max_concentration:
            max_concentration = flow_ratio

        # CAC健康度：CAC <= LTV/3 为健康
        if ltv > 0 and cac > ltv / 3:
            cac_issues.append(name)
        elif ltv > 0 and cac <= ltv / 3:
            total_score += 25  # CAC健康
        elif ltv > 0 and cac <= ltv / 5:
            total_score += 30  # CAC优秀

        # 转化率评分
        if conversion >= 8:
            total_score += 25
        elif conversion >= 5:
            total_score += 20
        elif conversion >= 3:
            total_score += 10
        else:
            total_score += 5

    # 渠道集中度评分
    if max_concentration < 60:
        total_score += 20
    elif max_concentration < 80:
        total_score += 10
        findings.append(f"渠道集中度{max_concentration:.0f}%偏高，建议优化")
    else:
        total_score += 0
        risks.append(f"渠道集中度{max_concentration:.0f}%超80%危险线，结构风险高")

    # 有2个以上高效渠道加成
    if channel_count >= 3:
        total_score += 10

    # CAC问题标记
    if cac_issues:
        risks.append(f"以下渠道CAC过高: {', '.join(cac_issues)}")

    score = min(100.0, total_score)
    return {"score": round(score, 1), "findings": findings, "risks": risks}


def _score_b2c_feature(features: dict) -> dict:
    """
    评估B2C功能使用
    输入：功能数据字典
    返回：{score: float, findings: list, risks: list}
    """
    findings = []
    risks = []

    if not features:
        return {"score": 0.0, "findings": ["缺少功能数据"], "risks": []}

    total_score = 0.0
    core_penetration_sum = 0.0
    core_count = 0
    deep_usage_count = 0

    for name, data in features.items():
        if not isinstance(data, dict):
            continue

        penetration = _to_pct(data.get("渗透率", 0))
        depth = _to_float(data.get("使用次数人均", 0))

        if "核心" in name or "核心功能" in str(data.get("类型", "")):
            core_penetration_sum += penetration
            core_count += 1

        # 使用深度评分
        if depth >= 3:
            deep_usage_count += 1

    # 核心功能渗透率评分
    if core_count > 0:
        avg_core_penetration = core_penetration_sum / core_count
        if avg_core_penetration >= 60:
            total_score += 40
        elif avg_core_penetration >= 40:
            total_score += 30
        elif avg_core_penetration >= 25:
            total_score += 15
            findings.append(f"核心功能渗透率{avg_core_penetration:.0f}%偏低")
        else:
            total_score += 5
            risks.append(f"核心功能渗透率{avg_core_penetration:.0f}%低于40%，产品价值未被用户感知")

    # 功能深度加成
    if deep_usage_count >= 2:
        total_score += 20
    elif deep_usage_count >= 1:
        total_score += 10

    # 有高价值功能激活
    for name, data in features.items():
        if isinstance(data, dict) and data.get("高价值功能"):
            penetration = _to_pct(data.get("渗透率", 0))
            if penetration >= 30:
                total_score += 20
                break

    # 无沉睡功能
    sleep_count = sum(1 for d in features.values() if isinstance(d, dict) and _to_pct(d.get("渗透率", 0)) < 5)
    if sleep_count == 0:
        total_score += 10

    score = min(100.0, total_score)
    return {"score": round(score, 1), "findings": findings, "risks": risks}


def _score_b2c_repurchase(repurchase: dict, ltv: float = 0, cac: float = 0) -> dict:
    """
    评估B2C复购率
    输入：复购数据字典
    返回：{score: float, findings: list, risks: list}
    """
    findings = []
    risks = []

    if not repurchase:
        return {"score": 0.0, "findings": ["缺少复购数据"], "risks": []}

    # 各周期复购率
    repurchase_7 = _to_pct(repurchase.get("7日复购率", 0))
    repurchase_30 = _to_pct(repurchase.get("30日复购率", 0))
    repurchase_90 = _to_pct(repurchase.get("90日复购率", 0))

    # 基础分：加权复购率
    base_score = repurchase_7 * 0.2 + repurchase_30 * 0.35 + repurchase_90 * 0.45
    total_score = base_score

    # LTV/CAC加成
    if ltv > 0 and cac > 0:
        ltv_cac_ratio = ltv / cac
        if ltv_cac_ratio >= 5:
            total_score += 20
        elif ltv_cac_ratio >= 3:
            total_score += 10
        elif ltv_cac_ratio >= 1:
            total_score += 0
        else:
            total_score -= 30
            risks.append(f"LTV/CAC = {ltv_cac_ratio:.1f} < 1，永远无法盈利")
    elif ltv > 0:
        ltv_cac_ratio = ltv / 15  # 假设平均CAC=15
        if ltv_cac_ratio >= 3:
            total_score += 10

    # 复购周期健康度
    cycle = _to_float(repurchase.get("平均复购周期", 0))
    if cycle > 0:
        if cycle <= 14:
            total_score += 10
        elif cycle <= 30:
            total_score += 5
        elif cycle >= 60:
            total_score -= 20
            risks.append("复购周期过长，用户需求在减弱")

    score = min(100.0, max(0.0, total_score))
    return {"score": round(score, 1), "findings": findings, "risks": risks}


def _score_b2c_activity(activity: dict) -> dict:
    """
    评估B2C活跃度
    输入：活跃度数据字典
    返回：{score: float, findings: list, risks: list}
    """
    findings = []
    risks = []

    if not activity:
        return {"score": 0.0, "findings": ["缺少活跃度数据"], "risks": []}

    dau = _to_float(activity.get("DAU", 0))
    mau = _to_float(activity.get("MAU", 0))

    # DAU/MAU评分
    dau_mau_ratio = (dau / mau * 100) if mau > 0 else 0.0
    if isinstance(activity.get("DAU/MAU"), str):
        dau_mau_ratio = _to_pct(activity.get("DAU/MAU"))

    if dau_mau_ratio >= 25:
        dau_mau_score = 50
    elif dau_mau_ratio >= 20:
        dau_mau_score = 40
    elif dau_mau_ratio >= 15:
        dau_mau_score = 30
    elif dau_mau_ratio >= 10:
        dau_mau_score = 20
    else:
        dau_mau_score = 10
        risks.append(f"DAU/MAU {dau_mau_ratio:.1f}% < 10%，粘性危险")

    total_score = dau_mau_score

    # 分层健康度
    high_ratio = _to_pct(activity.get("高活跃占比", 0))
    mid_ratio = _to_pct(activity.get("中活跃占比", 0))
    low_ratio = _to_pct(activity.get("低活跃占比", 0))
    silent_ratio = _to_pct(activity.get("沉默占比", 0))

    if high_ratio >= 20:
        total_score += 20
    elif high_ratio >= 10:
        total_score += 10

    if 30 <= mid_ratio <= 50:
        total_score += 15
    elif mid_ratio > 60:
        total_score += 5

    if low_ratio < 30:
        total_score += 10
    else:
        findings.append(f"低活跃占比{low_ratio:.0f}%偏高")

    if silent_ratio < 15:
        total_score += 15
    elif silent_ratio >= 30:
        total_score -= 20
        risks.append(f"沉默用户占比{silent_ratio:.0f}% > 30%，超1/3用户已放弃")
    elif silent_ratio >= 15:
        total_score += 0
        findings.append(f"沉默用户占比{silent_ratio:.0f}%需关注")

    score = min(100.0, max(0.0, total_score))
    return {"score": round(score, 1), "findings": findings, "risks": risks}


def _score_trend_b2c(trend: dict, activity: dict) -> dict:
    """
    评估B2C数据趋势
    输入：趋势数据字典
    返回：{score: float, findings: list, risks: list, inflection: list}
    """
    findings = []
    risks = []
    inflections = []

    if not trend and not activity:
        return {"score": 0.0, "findings": ["缺少趋势数据"], "risks": [], "inflections": []}

    # 提取趋势数据
    dau_change_30 = _to_float(trend.get("近30天DAU变化", 0))
    dau_change_90 = _to_float(trend.get("近90天DAU变化", 0))
    dau_change_180 = _to_float(trend.get("近180天DAU变化", 0))

    if isinstance(trend.get("近30天DAU趋势"), str):
        trend_str = trend.get("近30天DAU趋势", "")
        if "+" in trend_str or "上升" in trend_str or "增长" in trend_str:
            dau_change_30 = 5
        elif "-" in trend_str or "下降" in trend_str or "下跌" in trend_str:
            dau_change_30 = -5

    # 计算综合趋势
    trend_sum = 0
    trend_count = 0
    if dau_change_30 != 0:
        trend_sum += dau_change_30
        trend_count += 1
    if dau_change_90 != 0:
        trend_sum += dau_change_90
        trend_count += 1
    if dau_change_180 != 0:
        trend_sum += dau_change_180
        trend_count += 1

    avg_trend = trend_sum / trend_count if trend_count > 0 else 0

    # 趋势评分
    if avg_trend > 10:
        total_score = 90
    elif avg_trend > 5:
        total_score = 80
    elif avg_trend >= 0:
        total_score = 70
    elif avg_trend > -5:
        total_score = 55
        findings.append("DAU轻微下滑，需观察")
    elif avg_trend > -10:
        total_score = 40
        risks.append("DAU下滑加速，需警惕")
    else:
        total_score = 25
        risks.append("DAU大幅下滑，存在系统性风险")

    # 识别拐点
    if dau_change_30 < -15 or dau_change_90 < -20:
        inflections.append({
            "time": "近期",
            "phenomenon": "DAU下降加速",
            "severity": "高"
        })

    # 检查是否有止血迹象
    if trend.get("无任何止血迹象"):
        risks.append("连续下滑且无止血迹象")
        total_score = min(20, total_score)

    score = min(100.0, max(0.0, total_score))
    return {"score": round(score, 1), "findings": findings, "risks": risks, "inflections": inflections}


# =============================================================================
# B2B 评分函数
# =============================================================================

def _score_b2b_channel(channels: dict) -> dict:
    """
    评估B2B渠道质量
    输入：渠道数据字典，格式 {渠道名: {占比: x%, 续费率: x%, 企业平均规模: xxx}}
    返回：{score: float, findings: list, risks: list}
    """
    findings = []
    risks = []

    if not channels:
        return {"score": 0.0, "findings": ["缺少渠道数据"], "risks": []}

    total_score = 0.0
    channel_quality_issues = []

    for name, data in channels.items():
        if not isinstance(data, dict):
            continue

        ratio = _to_pct(data.get("占比", 0))
        renewal = _to_pct(data.get("续费率", 0))

        # 渠道质量评分
        if renewal >= 88:
            total_score += 25
        elif renewal >= 80:
            total_score += 20
        elif renewal >= 70:
            total_score += 10
            findings.append(f"{name}渠道续费率{renewal:.0f}%偏低")
        else:
            total_score += 0
            channel_quality_issues.append(f"{name}(续费率{renewal:.0f}%)")

    if channel_quality_issues:
        risks.append(f"以下渠道客户质量差: {', '.join(channel_quality_issues)}")

    # 渠道集中度（直销客户通常质量更高）
    direct_ratio = _to_pct(channels.get("直销", {}).get("占比", 0))
    channel_ratio = _to_pct(channels.get("渠道代理", channels.get("渠道", {})).get("占比", 0))
    online_ratio = _to_pct(channels.get("线上获客", channels.get("线上", {})).get("占比", 0))

    if channel_ratio > 50:
        total_score -= 10
        risks.append("依赖渠道代理客户，质量难控")

    score = min(100.0, max(0.0, total_score))
    return {"score": round(score, 1), "findings": findings, "risks": risks}


def _score_b2b_feature(features: dict) -> dict:
    """
    评估B2B功能使用
    输入：功能数据字典
    返回：{score: float, findings: list, risks: list}
    """
    findings = []
    risks = []

    if not features:
        return {"score": 0.0, "findings": ["缺少功能数据"], "risks": []}

    total_score = 0.0
    core_penetration_sum = 0.0
    core_count = 0
    advanced_sum = 0.0
    advanced_count = 0

    for name, data in features.items():
        if not isinstance(data, dict):
            continue

        usage = _to_pct(data.get("使用率", 0))

        # 判断是否为核心功能
        if any(kw in name for kw in ["IM", "即时通讯", "核心", "主要"]):
            core_penetration_sum += usage
            core_count += 1
        elif any(kw in name for kw in ["高级", "分析", "增值"]):
            advanced_sum += usage
            advanced_count += 1

    # 核心功能渗透率评分
    if core_count > 0:
        avg_core = core_penetration_sum / core_count
        if avg_core >= 80:
            total_score += 40
        elif avg_core >= 60:
            total_score += 30
        elif avg_core >= 40:
            total_score += 15
            findings.append(f"核心功能渗透率{avg_core:.0f}%偏低")
        else:
            total_score += 5
            risks.append(f"核心功能渗透率{avg_core:.0f}%低于40%")

    # 高级功能渗透率
    if advanced_count > 0:
        avg_advanced = advanced_sum / advanced_count
        if avg_advanced >= 30:
            total_score += 20
        elif avg_advanced >= 15:
            total_score += 10
            findings.append(f"高级功能渗透率{avg_advanced:.0f}%偏低")
        else:
            total_score += 0
            risks.append(f"高级功能渗透率{avg_advanced:.0f}%过低，价值未充分实现")

    # 席位利用率（如果有）
    seat_util = _to_float(features.get("席位利用率", features.get("seat_utilization", 0)))
    if seat_util >= 70:
        total_score += 10
    elif seat_util >= 50:
        total_score += 5
    elif seat_util > 0:
        findings.append(f"席位利用率{seat_util:.0f}%偏低")

    score = min(100.0, max(0.0, total_score))
    return {"score": round(score, 1), "findings": findings, "risks": risks}


def _score_b2b_renewal(renewal_data: dict) -> dict:
    """
    评估B2B续费率
    输入：续费/复购数据字典
    返回：{score: float, findings: list, risks: list}
    """
    findings = []
    risks = []

    if not renewal_data:
        return {"score": 0.0, "findings": ["缺少续费数据"], "risks": []}

    renewal_rate = _to_pct(renewal_data.get("续费率", 0))
    nrr = _to_float(renewal_data.get("NRR", 0))
    expansion = _to_pct(renewal_data.get("增购率", 0))

    # 续费率基础分
    if renewal_rate >= 95:
        renewal_score = 60
    elif renewal_rate >= 85:
        renewal_score = 50
    elif renewal_rate >= 75:
        renewal_score = 30
        findings.append(f"续费率{renewal_rate:.0f}%低于健康线85%")
    else:
        renewal_score = 10
        risks.append(f"续费率{renewal_rate:.0f}%低于75%危险线，产品基础价值不被认可")

    total_score = renewal_score

    # NRR加成
    if nrr >= 120:
        total_score += 30
    elif nrr >= 110:
        total_score += 20
    elif nrr >= 100:
        total_score += 10
    elif nrr > 0:
        total_score -= 30
        risks.append(f"NRR {nrr:.0f}% < 100%，存量客户在流失")

    # 增购率加成
    if expansion >= 20:
        total_score += 15
    elif expansion >= 15:
        total_score += 10
    elif expansion >= 10:
        total_score += 5
    elif expansion > 0:
        total_score += 0
    else:
        findings.append("无增购，成长性不足")

    score = min(100.0, max(0.0, total_score))
    return {"score": round(score, 1), "findings": findings, "risks": risks}


def _score_b2b_activity(activity: dict) -> dict:
    """
    评估B2B活跃度
    输入：活跃度数据字典
    返回：{score: float, findings: list, risks: list}
    """
    findings = []
    risks = []

    if not activity:
        return {"score": 0.0, "findings": ["缺少活跃度数据"], "risks": []}

    # 企业活跃率
    enterprise_active = _to_pct(activity.get("企业活跃率", 0))
    if enterprise_active >= 85:
        active_score = 50
    elif enterprise_active >= 75:
        active_score = 40
    elif enterprise_active >= 65:
        active_score = 30
        findings.append(f"企业活跃率{enterprise_active:.0f}%偏低")
    else:
        active_score = 20
        risks.append(f"企业活跃率{enterprise_active:.0f}%低于65%危险线")

    total_score = active_score

    # 健康度分布
    high_health = _to_pct(activity.get("高活跃企业占比", 0))
    mid_health = _to_pct(activity.get("中活跃企业占比", 0))
    low_health = _to_pct(activity.get("低活跃企业占比", 0))
    warning = _to_pct(activity.get("即将流失企业占比", 0))

    if high_health >= 30:
        total_score += 20
    elif high_health >= 20:
        total_score += 10

    if warning < 10:
        total_score += 15
    elif warning >= 20:
        total_score -= 30
        risks.append(f"流失预警率{warning:.0f}% > 20%，存量收入在倒计时")
    elif warning >= 10:
        total_score += 5
        findings.append(f"流失预警率{warning:.0f}%需关注")

    score = min(100.0, max(0.0, total_score))
    return {"score": round(score, 1), "findings": findings, "risks": risks}


def _score_trend_b2b(trend: dict, renewal_data: dict) -> dict:
    """
    评估B2B数据趋势
    输入：趋势数据字典
    返回：{score: float, findings: list, risks: list, inflections: list}
    """
    findings = []
    risks = []
    inflections = []

    if not trend and not renewal_data:
        return {"score": 0.0, "findings": ["缺少趋势数据"], "risks": [], "inflections": []}

    # 检查续费率趋势
    renewal_rate = _to_pct(renewal_data.get("续费率", 0))
    renewal_trend = trend.get("续费率趋势", "")

    if "下降" in str(renewal_trend) or "下滑" in str(renewal_trend):
        risks.append("续费率呈下降趋势")
        inflections.append({
            "time": "近期",
            "phenomenon": "续费率开始下滑",
            "severity": "高"
        })

    # 检查NRR趋势
    nrr = _to_float(renewal_data.get("NRR", 0))
    if nrr < 100:
        risks.append("NRR < 100%，存量客户价值在流失")
        total_score = 30
    elif nrr < 110:
        total_score = 60
        findings.append("NRR低于优秀水平")
    elif nrr >= 115:
        total_score = 85
        findings.append("NRR表现优秀，存量客户价值在增长")
    else:
        total_score = 75

    score = min(100.0, max(0.0, total_score))
    return {"score": round(score, 1), "findings": findings, "risks": risks, "inflections": inflections}


# =============================================================================
# 综合评估函数
# =============================================================================

def _classify_health(
    scores: dict,
    product_type: str,
    structural_risks: list
) -> str:
    """判断健康等级"""
    valid_scores = [v for v in scores.values() if isinstance(v, (int, float)) and v > 0]
    if not valid_scores:
        return "无法评估"

    overall = sum(valid_scores) / len(valid_scores)

    # 结构风险降级检查
    downgrade = False
    downgrade_reasons = []

    for risk in structural_risks:
        risk_lower = risk.lower()
        if "渠道集中度" in risk and ("80%" in risk or ">80%" in risk or "85%" in risk):
            downgrade = True
            downgrade_reasons.append("渠道集中度超80%")
        if "ltv/cac" in risk_lower and "< 1" in risk_lower:
            downgrade = True
            downgrade_reasons.append("LTV/CAC<1")
        if "沉默用户" in risk and "30%" in risk:
            downgrade = True
            downgrade_reasons.append("沉默占比>30%")
        if "续费率" in risk and ("62%" in risk or "75%" in risk):
            downgrade = True
            downgrade_reasons.append("续费率低于危险线")
        if "系统性" in risk or "崩溃" in risk:
            downgrade = True
            downgrade_reasons.append("系统性崩溃")

    if downgrade:
        if overall >= 85:
            overall = overall  # 高分降一级还是亚健康
        elif overall >= 70:
            overall = overall - 10  # 亚健康降为风险
        else:
            overall = max(40, overall - 15)  # 风险/危机降到更低

    # 健康等级判定
    if overall >= 85 and not downgrade:
        return "健康"
    elif overall >= 70:
        return "亚健康"
    elif overall >= 55:
        return "风险"
    else:
        return "危机"


def _generate_investment_advice(health_level: str, scores: dict, structural_risks: list) -> dict:
    """生成投入建议"""
    valid_scores = [v for v in scores.values() if isinstance(v, (int, float)) and v > 0]
    overall = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    advice = {
        "decision": "",
        "priority": [],
        "reason": ""
    }

    if health_level == "健康":
        advice["decision"] = "继续投入"
        advice["priority"] = [
            "加大高效渠道投入",
            "深化高价值用户运营",
            "保持当前产品迭代节奏"
        ]
        advice["reason"] = "产品整体正向，可继续加码"
    elif health_level == "亚健康":
        advice["decision"] = "收缩投入"
        advice["priority"] = [
            "停止低效渠道和功能投入",
            "聚焦核心功能和核心用户",
            "控制成本，提升效率"
        ]
        advice["reason"] = "部分维度弱，需先修短板"
    elif health_level == "风险":
        advice["decision"] = "止损优先"
        advice["priority"] = [
            "立即停止无效投入",
            "诊断根因，明确是市场还是产品问题",
            "止血优先于增长"
        ]
        advice["reason"] = "多个维度下滑，需优先止损"
    else:  # 危机
        advice["decision"] = "放弃/止损"
        advice["priority"] = [
            "立即停止所有新投入",
            "深度调研流失原因",
            "评估是否还有转型空间",
            "如无转型空间，启动有序退出"
        ]
        advice["reason"] = "系统性崩溃，建议管理层介入"

    return advice


def _assess(data: dict) -> dict:
    """执行完整评估"""
    product_type = data.get("产品类型", data.get("product_type", "B2C")).upper()

    if product_type not in ("B2C", "B2B"):
        product_type = "B2C"  # 默认B2C

    channels = data.get("渠道数据", data.get("channels", {}))
    features = data.get("功能数据", data.get("features", {}))
    repurchase = data.get("复购数据", data.get("复购", data.get("repurchase", {})))
    activity = data.get("活跃度数据", data.get("活跃度", data.get("activity", {})))
    trend = data.get("趋势数据", data.get("趋势", data.get("trend", {})))

    # 提取LTV和CAC用于计算
    ltv = _to_float(repurchase.get("LTV", 0))
    cac = _to_float(repurchase.get("平均CAC", repurchase.get("CAC", 0)))

    # B2C评分
    if product_type == "B2C":
        channel_result = _score_b2c_channel(channels, ltv)
        feature_result = _score_b2c_feature(features)
        repurchase_result = _score_b2c_repurchase(repurchase, ltv, cac)
        activity_result = _score_b2c_activity(activity)
        trend_result = _score_trend_b2c(trend, activity)

        dimension_scores = {
            "渠道质量": channel_result["score"],
            "功能使用": feature_result["score"],
            "复购率": repurchase_result["score"],
            "活跃度": activity_result["score"],
            "数据趋势": trend_result["score"]
        }
    else:
        # B2B评分
        channel_result = _score_b2b_channel(channels)
        feature_result = _score_b2b_feature(features)
        repurchase_result = _score_b2b_renewal(repurchase)
        activity_result = _score_b2b_activity(activity)
        trend_result = _score_trend_b2b(trend, repurchase)

        dimension_scores = {
            "渠道质量": channel_result["score"],
            "功能使用": feature_result["score"],
            "复购率": repurchase_result["score"],
            "活跃度": activity_result["score"],
            "数据趋势": trend_result["score"]
        }

    # 收集所有风险
    all_risks = (
        channel_result["risks"] +
        feature_result["risks"] +
        repurchase_result["risks"] +
        activity_result["risks"] +
        trend_result["risks"]
    )

    # 收集所有发现
    all_findings = (
        channel_result["findings"] +
        feature_result["findings"] +
        repurchase_result["findings"] +
        activity_result["findings"] +
        trend_result["findings"]
    )

    # 收集拐点
    inflections = trend_result.get("inflections", [])

    # 计算综合得分
    valid_scores = [v for v in dimension_scores.values() if v > 0]
    overall = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0.0

    # 判断健康等级
    health_level = _classify_health(dimension_scores, product_type, all_risks)

    # 生成投入建议
    investment_advice = _generate_investment_advice(health_level, dimension_scores, all_risks)

    # 生成优先级动作
    priority_actions = {}
    if health_level in ("风险", "危机"):
        priority_actions["P0"] = ["止损：停止低效投入"]
        min_dim = min(dimension_scores, key=dimension_scores.get)
        priority_actions["P0"].append(f"优先修复最弱维度：{min_dim}")
    else:
        priority_actions["P0"] = ["优化核心功能与留存路径"]

    priority_actions["P1"] = ["深化用户/客户运营"]
    priority_actions["P2"] = ["补齐趋势与对标数据"]

    # 构建输出
    output = {
        "skill": "产品状态评估",
        "version": "2.0.0",
        "product_name": data.get("产品名称", "未知产品"),
        "product_type": product_type,
        "assessment_period": data.get("评估周期", data.get("周期", "")),
        "purpose": data.get("评估目的", "常规体检"),

        "dimension_scores": dimension_scores,
        "overall_score": overall,
        "health_level": health_level,

        "key_findings": all_findings[:5],  # 最多5个主要发现
        "key_risks": all_risks[:5],  # 最多5个主要风险
        "inflection_points": inflections,

        "investment_advice": investment_advice,
        "priority_actions": priority_actions,

        "calculation_notes": [
            "五维度等权重计分",
            "综合得分 = 五维度平均",
            "结构风险（渠道集中度>80%、LTV/CAC<1等）会导致降级",
            "详细评估逻辑见 references/五维度评估详解.md"
        ]
    }

    return output


# =============================================================================
# 主函数
# =============================================================================

def main() -> int:
    """主入口"""
    payload = _load_payload()

    if not payload:
        print(json.dumps({
            "error": "缺少输入数据",
            "usage": "python run.py '{\"dau\": 1500000, \"mau\": 8000000, ...}'",
            "required_fields": [
                "产品类型 (B2C/B2B)",
                "渠道数据",
                "功能数据",
                "复购数据（或续费数据）",
                "活跃度数据",
                "趋势数据（可选）"
            ]
        }, ensure_ascii=False, indent=2))
        return 1

    result = _assess(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
