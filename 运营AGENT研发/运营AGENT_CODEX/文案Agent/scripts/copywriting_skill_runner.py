#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from typing import Any


CHANNEL_HINTS = {
    "海报": {"length": "3-8 秒", "cta": "single"},
    "广告位": {"length": "3-8 秒", "cta": "single"},
    "抖音": {"length": "15-60 秒", "cta": "strong"},
    "小红书": {"length": "20-90 秒", "cta": "medium"},
    "公众号": {"length": "2-6 分钟", "cta": "medium"},
    "详情页": {"length": "5-15 秒首屏 / 30-120 秒中段", "cta": "strong"},
    "私信": {"length": "对话式", "cta": "dynamic"},
    "销售": {"length": "对话式", "cta": "dynamic"},
    "长文": {"length": "3-10 分钟", "cta": "soft"},
}

STRUCTURE_HINTS = {
    "不知道": "4P/故事式",
    "没被打动": "PAS/AIDA",
    "比较": "对比式",
    "接近行动": "直述式",
    "很多信息": "清单式",
}

SKILL_SPECS: dict[str, dict[str, Any]] = {
    "detect-need-type": {
        "next_step": "Read references/reference.md, collect seven-direction evidence, then classify the need.",
        "required_keys": ["request_text"],
        "recommended_keys": ["request_text", "behavior", "search", "feedback", "dialogue", "comparison", "data"],
        "analysis_hint": "先采七向证据，再判需求类型。",
        "red_flags": ["只看一句话下结论", "把情绪词当需求", "把搜索词当最终目标"],
    },
    "segment-users": {
        "next_step": "Read references/reference.md, split decision makers, users, blockers, and helpers.",
        "required_keys": ["product_context"],
        "recommended_keys": ["product_context", "roles", "decision_flow", "user_signals"],
        "analysis_hint": "先按决策权和角色分主次，再补阶段、意愿、认知。",
        "red_flags": ["只按年龄职业分人群", "把所有人当主对象", "忽略拍板者"],
    },
    "research-sellpoint-forward": {
        "next_step": "Read references/reference.md, list seven-direction candidates, then choose the main sellpoint.",
        "required_keys": ["product_facts"],
        "recommended_keys": ["product_facts", "evidence", "competitors", "cases"],
        "analysis_hint": "先列事实和证据，再按七向提炼候选卖点。",
        "red_flags": ["把功能描述当卖点", "把优惠当长期卖点", "把口号当证据"],
    },
    "research-sellpoint-backward": {
        "next_step": "Read references/reference.md, move from pain point to scenario, obstruction, cost, and desired result.",
        "required_keys": ["user_feedback"],
        "recommended_keys": ["user_feedback", "scenario", "cost", "attempts", "competitor_feedback"],
        "analysis_hint": "先痛点、场景、阻碍、代价，再反推结果。",
        "red_flags": ["把痛点本身当卖点", "把愿望句当结果", "忽略场景和代价"],
    },
    "judge-scenario": {
        "next_step": "Read references/reference.md and platform-presets.md, then map the channel to length and CTA strength.",
        "required_keys": ["channel"],
        "recommended_keys": ["channel", "entry_state", "reading_window", "goal"],
        "analysis_hint": "先平台、再接收状态、再阅读窗口，最后定短中长和 CTA。",
        "red_flags": ["在短触点里塞长解释", "忽略平台预设", "把能转化误当适合直接转化"],
    },
    "select-structure": {
        "next_step": "Read references/reference.md, select the main structure and one fallback structure.",
        "required_keys": ["user_state", "goal"],
        "recommended_keys": ["user_state", "goal", "channel", "reading_window", "evidence_depth"],
        "analysis_hint": "先判断用户是否知道问题、是否在比较、是否接近行动，再选结构。",
        "red_flags": ["先喜欢结构再硬套", "结构顺序写反", "用户还没认知问题就上 PAS"],
    },
    "draft-copy": {
        "next_step": "Read references/reference.md, then draft conclusion, reason, evidence, and one CTA.",
        "required_keys": ["user", "sellpoint", "scenario", "structure"],
        "recommended_keys": ["user", "sellpoint", "scenario", "structure", "evidence", "length"],
        "analysis_hint": "先主张，再理由、证据、行动。",
        "red_flags": ["在卖点未定时写成稿", "把多种目标混成一个正文", "CTA 太多"],
    },
    "edit-copy": {
        "next_step": "Read references/reference.md, then remove repetition, emptiness, abstraction, and rebuild the order.",
        "required_keys": ["copy_text"],
        "recommended_keys": ["copy_text", "editing_goal", "channel", "length_limit"],
        "analysis_hint": "先删重复空话抽象，再补证据、强动作、调顺序。",
        "red_flags": ["把删改做成重写", "删掉证据和动作", "只改顺序不改逻辑"],
    },
    "self-check-copy": {
        "next_step": "Read references/reference.md, run the seven-question gate, then return pass/fail with risks.",
        "required_keys": ["copy_text", "user", "sellpoint", "scenario", "structure"],
        "recommended_keys": ["copy_text", "user", "sellpoint", "scenario", "structure", "evidence", "cta"],
        "analysis_hint": "逐项核对对象、卖点、场景、结构、动作、证据和风险。",
        "red_flags": ["只给总评不逐项核对", "把风险藏起来", "把感觉不错当通过"],
    },
}


def _read_payload() -> tuple[Any | None, str]:
    raw = sys.stdin.read().strip()
    if not raw:
        return None, "empty"
    try:
        return json.loads(raw), "json"
    except json.JSONDecodeError:
        return {"request_text": raw}, "text"


def _normalize_payload(payload: Any | None) -> dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, dict):
        return dict(payload)
    return {"request_text": payload}


def _first_text(payload: dict[str, Any]) -> str:
    for key in ("request_text", "copy_text", "text", "raw", "user_input"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _field_blob(payload: dict[str, Any], keys: tuple[str, ...]) -> str:
    parts: list[str] = []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
        elif isinstance(value, (int, float)):
            parts.append(str(value))
    return " ".join(parts)


def _contains_any(text: str, words: list[str]) -> list[str]:
    return [word for word in words if word and word in text]


def _score_keywords(text: str, groups: dict[str, list[str]]) -> dict[str, list[str]]:
    lowered = text.lower()
    return {label: _contains_any(lowered, words) for label, words in groups.items()}


def _detect_need_quick_judgment(text: str) -> dict[str, Any]:
    lowered = text.lower()
    markers = {
        "明确需求": ["我要", "我想", "请直接", "帮我写", "帮我改", "直接给"],
        "模糊需求": ["不太对", "不知道", "有点乱", "说不清", "怎么", "为什么"],
        "潜在需求": ["有没有", "值不值", "要不要", "适不适合", "值得吗"],
    }
    hits = {label: sum(1 for marker in words if marker in lowered) for label, words in markers.items()}
    active = [label for label, count in hits.items() if count > 0]
    if not active:
        best = "无法判断"
    elif len(active) > 1:
        best = "混合信号"
    else:
        best = active[0]
    if best == "明确需求":
        confidence = "high" if hits[best] >= 2 else "medium"
    elif best in {"模糊需求", "潜在需求"}:
        confidence = "medium"
    elif best == "混合信号":
        confidence = "low"
    else:
        confidence = "low"
    question_bank = {
        "明确需求": ["要给谁写", "要放在哪个场景", "有什么证据不能缺"],
        "模糊需求": ["现在最想先解决什么", "最卡在哪一步", "最不能接受什么结果"],
        "潜在需求": ["有没有具体痛点原话", "用户什么时候会意识到问题", "现在先唤醒还是先解释"],
        "混合信号": ["先确认是不是同一句话里同时有明确和模糊信号", "补一个行为或数据", "补一个比较对象"],
        "无法判断": ["补一段原话", "补一个行为或数据", "补一个比较对象"],
    }
    return {
        "label": best,
        "confidence": confidence,
        "hits": hits,
        "signal_balance": sum(hits.values()),
        "next_questions": question_bank[best],
    }


def run_skill(skill_name: str) -> int:
    spec = SKILL_SPECS[skill_name]
    payload, input_kind = _read_payload()
    normalized = _normalize_payload(payload)
    provided_keys = sorted(normalized.keys())
    missing_keys = [key for key in spec["required_keys"] if key not in normalized or normalized.get(key) in (None, "", [], {})]
    text = _first_text(normalized)

    result: dict[str, Any] = {
        "skill": skill_name,
        "received_input": payload is not None,
        "input_kind": input_kind,
        "provided_keys": provided_keys,
        "required_keys": spec["required_keys"],
        "recommended_keys": spec["recommended_keys"],
        "missing_required_keys": missing_keys,
        "analysis_hint": spec["analysis_hint"],
        "red_flags": spec["red_flags"],
        "next_step": spec["next_step"],
    }

    if skill_name == "detect-need-type" and text:
        result["quick_judgment"] = _detect_need_quick_judgment(text)
        result["evidence_types"] = _score_keywords(text, {
            "原话": ["我想", "我需要", "我觉得", "我想要"],
            "行为": ["点击", "停留", "放弃", "回退", "反复", "退回"],
            "搜索": ["怎么", "哪个好", "值不值", "适不适合", "比较"],
            "反馈": ["太", "不行", "差评", "投诉", "麻烦"],
        })
        result["next_questions"] = _detect_need_quick_judgment(text)["next_questions"]
        result["need_state_hint"] = "先补证据再下结论" if result["quick_judgment"]["label"] in {"混合信号", "无法判断"} else "可以进入下一步"

    elif skill_name == "segment-users" and text:
        result["role_signals"] = _score_keywords(text, {
            "购买者": ["出钱", "预算", "采购", "买单"],
            "使用者": ["使用", "每天", "操作", "执行"],
            "拍板者": ["决定", "拍板", "批准", "同意"],
            "阻拦者": ["卡", "否决", "阻止", "审批"],
            "影响者": ["影响", "建议", "技术", "老板", "同事"],
        })
        result["decision_hints"] = ["先找拍板者", "再找使用者", "再补阻拦者和影响者"]

    elif skill_name in {"research-sellpoint-forward", "research-sellpoint-backward"} and text:
        if skill_name == "research-sellpoint-forward":
            result["direction_signals"] = _score_keywords(text, {
                "功能独特性": ["功能", "支持", "自动", "独特", "不同"],
                "效果承诺": ["提升", "减少", "节省", "提高", "缩短"],
                "解决问题": ["解决", "麻烦", "痛点", "卡住", "不会"],
                "用户身份": ["负责人", "新手", "老板", "专家", "团队"],
                "价格优势": ["便宜", "成本", "预算", "划算", "优惠"],
                "服务保障": ["服务", "保证", "支持", "退", "陪跑"],
                "情感价值": ["安心", "体面", "松弛", "掌控", "认可"],
            })
            result["recommendation_order"] = ["用户最在意", "证据最完整", "最容易在目标场景说清楚"]
        else:
            result["pain_signals"] = _score_keywords(text, {
                "功能痛点": ["麻烦", "太慢", "太乱", "漏", "不会"],
                "业务痛点": ["流失", "转化", "延期", "复购", "协作"],
                "心理痛点": ["怕", "担心", "焦虑", "不专业", "丢脸"],
            })
            result["reverse_chain"] = ["痛点", "场景", "阻碍", "代价", "结果", "卖点"]

    elif skill_name == "judge-scenario" and text:
        matched = {k: v for k, v in CHANNEL_HINTS.items() if k in text}
        result["platform_hint"] = matched or None
        result["decision_mode_hint"] = "细细琢磨" if any(word in text for word in ["详情页", "公众号", "长文", "比较", "解释"]) else "不假思索"
        result["platform_keywords"] = _score_keywords(text, {
            "短触点": ["海报", "广告位", "短视频", "首屏"],
            "中触点": ["小红书", "公众号", "详情页"],
            "长触点": ["长文", "教育", "深度"],
        })
        result["length_hint"] = matched

    elif skill_name == "select-structure" and text:
        result["likely_structure"] = next((label for key, label in STRUCTURE_HINTS.items() if key in text), None)
        result["structure_signals"] = _score_keywords(text, {
            "AIDA": ["注意", "兴趣", "欲望", "行动", "钩子"],
            "4P": ["场景", "承诺", "证明", "敦促", "解释"],
            "PAS": ["痛点", "放大", "解决", "麻烦"],
            "对比式": ["比较", "对比", "更好", "区别"],
            "直述式": ["直接", "结果", "行动", "立刻"],
            "清单式": ["清单", "列表", "条", "步骤"],
            "故事式": ["故事", "经历", "变化", "过程"],
        })
        result["selection_rule"] = ["用户状态", "说服目标", "证据深度", "主结构", "备用结构"]

    elif skill_name == "draft-copy" and text:
        result["writing_order"] = ["结论/主张", "理由/解释", "证据/案例", "行动/CTA"]
        result["clarity_checks"] = {
            "是否有陌生概念": bool(_score_keywords(text, {"陌生概念": ["GD", "CPM", "CPA", "术语", "内部", "专业"]})["陌生概念"]),
            "是否有场景": bool(_score_keywords(text, {"场景": ["场景", "时候", "当", "在"]})["场景"]),
        }
        result["length_rules"] = ["短文案先主张后动作", "中长文案先解释后证据", "只保留一个主动作"]

    elif skill_name == "edit-copy" and text:
        result["edit_order"] = ["删重复", "删空话", "删抽象", "补证据", "强动作", "调顺序"]
        result["likely_issue_type"] = next((label for label, words in {
            "太长": ["很多", "太长", "冗余", "重复"],
            "太虚": ["专业", "高效", "极致", "很棒"],
            "太乱": ["但是", "然后", "同时", "另外"],
            "太软": ["欢迎", "了解", "看看", "试试"],
        }.items() if any(word in text for word in words)), None)
        result["keep_order"] = ["主卖点", "证据", "动作", "边界", "修辞"]

    elif skill_name == "self-check-copy":
        judge_text = _field_blob(normalized, ("copy_text", "user", "sellpoint", "scenario", "structure", "evidence", "cta", "risk_notes")) or text
        gate = {
            "对象": bool(_score_keywords(_field_blob(normalized, ("user", "copy_text")) or judge_text, {"对象": ["谁", "用户", "负责人", "执行者", "老板"]})["对象"]),
            "卖点": bool(_score_keywords(_field_blob(normalized, ("sellpoint", "copy_text")) or judge_text, {"卖点": ["结果", "省", "快", "更", "避免", "自动", "待办", "减少", "漏项"]})["卖点"]),
            "场景": bool(_score_keywords(_field_blob(normalized, ("scenario", "copy_text")) or judge_text, {"场景": ["场景", "详情页", "海报", "小红书", "公众号", "抖音", "首屏"]})["场景"]),
            "结构": bool(_score_keywords(_field_blob(normalized, ("structure", "copy_text")) or judge_text, {"结构": ["AIDA", "4P", "PAS", "对比", "清单", "故事", "直述"]})["结构"]),
            "动作": bool(_score_keywords(_field_blob(normalized, ("cta", "copy_text")) or judge_text, {"动作": ["去", "试用", "咨询", "预约", "购买", "点击", "查看", "了解"]})["动作"]),
            "证据": bool(_score_keywords(_field_blob(normalized, ("evidence", "copy_text")) or judge_text, {"证据": ["数据", "案例", "事实", "结果", "对比", "转写", "待办", "同步"]})["证据"]),
            "风险": bool(_score_keywords(_field_blob(normalized, ("risk_notes", "copy_text")) or judge_text, {"风险": ["限制", "边界", "不保证", "可能", "条件", "适用"]})["风险"]),
        }
        hard_promises = _score_keywords(judge_text, {"硬承诺": ["保证", "一定", "绝对", "百分百", "立刻生效", "无条件"]})["硬承诺"]
        passed = sum(gate.values()) == 7 and not hard_promises
        failures = [name for name, ok in gate.items() if not ok]
        severity = "blocker" if (not all(gate.values()) or hard_promises) else "note"
        result["seven_question_gate"] = gate
        result["hard_promises"] = hard_promises
        result["verdict"] = "pass" if passed else "fail"
        result["failure_reasons"] = failures + (["硬承诺或绝对化表达"] if hard_promises else [])
        result["severity"] = severity
        result["pass_rule"] = "7问必须7项全部为真，且无硬承诺或绝对化表达"

    if not payload:
        result["status"] = "needs_input"
    elif missing_keys:
        result["status"] = "needs_more_context"
    else:
        result["status"] = "ready"

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise SystemExit(run_skill(sys.argv[1]))
    raise SystemExit(0)
