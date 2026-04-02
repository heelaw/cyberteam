#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any


def _load_payload() -> dict[str, Any]:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        try:
            return json.loads(sys.argv[1])
        except json.JSONDecodeError:
            pass
    raw = sys.stdin.read().strip()
    if raw:
        return json.loads(raw)
    return {}


def _to_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    digits = ''.join(ch for ch in value if ch.isdigit() or ch in '.-')
    if digits in {'', '-', '.', '-.', '.-'}:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


def _ratio(actual: Any, target: Any) -> float | None:
    a = _to_number(actual)
    t = _to_number(target)
    if a is None or t in (None, 0):
        return None
    return a / t


def _pick_activity_type(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False)
    if any(k in text for k in ['复购', '会员', '留存']):
        return '复购型'
    if any(k in text for k in ['GMV', '下单', '支付', '成交']):
        return '转化型'
    if any(k in text for k in ['拉新', '注册', '新客']):
        return '拉新型'
    if any(k in text for k in ['品牌', '曝光', '话题', '分享']):
        return '品牌型'
    return '混合型'


def main() -> int:
    payload = _load_payload()
    target = payload.get('target') or payload.get('活动目标') or {}
    actual = payload.get('actual') or payload.get('实际数据') or {}
    cost = payload.get('cost') or payload.get('成本指标') or {}
    exposure = payload.get('exposure') or payload.get('传播指标') or {}
    behavior = payload.get('behavior') or payload.get('用户行为指标') or {}

    ratios: dict[str, float] = {}
    for k, v in target.items():
        if k in actual:
            r = _ratio(actual.get(k), v)
            if r is not None:
                ratios[k] = round(r, 4)

    total_cost = sum(filter(None, (_to_number(v) for v in cost.values()))) if cost else 0.0
    actual_sales = _to_number(actual.get('新品销售额') or actual.get('GMV') or actual.get('收入') or actual.get('营收')) or 0.0
    roi = None
    if total_cost > 0:
        roi = round((actual_sales - total_cost) / total_cost, 4)

    shares = _to_number(exposure.get('分享数') or exposure.get('分享'))
    participation = _to_number(behavior.get('参与活动用户数') or behavior.get('参与'))
    share_rate = None
    if shares is not None and participation not in (None, 0):
        share_rate = round(shares / participation, 4)

    rating = '待判断'
    if ratios and all(v >= 1 for v in ratios.values()) and (roi is None or roi >= 0):
        rating = '优秀'
    elif any(v < 0.8 for v in ratios.values()) or (roi is not None and roi < 0):
        rating = '偏弱'
    elif ratios:
        rating = '良好'

    output = {
        'skill': '活动效果评估',
        'activity_type': _pick_activity_type(payload),
        'coverage': {
            'target_keys': sorted(target.keys()),
            'actual_keys': sorted(actual.keys()),
            'ratio_keys': sorted(ratios.keys()),
        },
        'computed': {
            'completion_ratios': ratios,
            'roi': roi,
            'share_rate': share_rate,
            'total_cost': round(total_cost, 2),
        },
        'judgment': {
            'rating': rating,
            'reuse': ['保留高效渠道', '保留高转化钩子'] if rating in {'优秀', '良好'} else ['优先优化承接链路'],
            'stop': ['停止高补贴低回报做法'] if (roi is not None and roi < 1) else [],
        },
        'next_step': 'Use references/评估维度详解.md and compare against target, history, and same-type activity before finalizing.',
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
