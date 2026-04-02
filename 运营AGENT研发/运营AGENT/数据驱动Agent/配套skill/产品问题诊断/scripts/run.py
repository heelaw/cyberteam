#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
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


def _severity(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False)
    if any(k in text for k in ['P0', '支付失败', '核心链路', '大面积', '全渠道']):
        return 'P0'
    if any(k in text for k in ['连续', '7天', '明显下滑', '核心体验']):
        return 'P1'
    if any(k in text for k in ['局部', '单渠道', '单功能']):
        return 'P2'
    return 'P3'


def _likely_root_cause(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False)
    if '支付' in text or '订单' in text:
        return '支付或订单链路异常'
    if '版本' in text or '发版' in text or '更新' in text:
        return '版本变更引发的体验或兼容问题'
    if '埋点' in text or '口径' in text or '漏数' in text:
        return '数据口径或埋点异常'
    if '投放' in text or '活动' in text or '触达' in text:
        return '运营触达或活动策略变化'
    return '需要继续分维度验证'


def main() -> int:
    payload = _load_payload()
    metrics = payload.get('metrics') or payload.get('数据背景') or {}
    text = json.dumps(payload, ensure_ascii=False)

    drop = None
    numbers = []
    for value in metrics.values() if isinstance(metrics, dict) else []:
        if isinstance(value, dict):
            for nested in value.values():
                num = _to_number(nested)
                if num is not None:
                    numbers.append(num)
        else:
            num = _to_number(value)
            if num is not None:
                numbers.append(num)
    if len(numbers) >= 2 and numbers[0] != 0:
        drop = round((numbers[0] - numbers[-1]) / numbers[0], 4)

    output = {
        'skill': '产品问题诊断',
        'severity': _severity(payload),
        'time_signal': '单日突发' if any(k in text for k in ['今日', '昨天', '单日']) else '趋势性',
        'dimension_focus': [k for k in ['时间', '渠道', '用户', '功能'] if k in text] or ['时间', '渠道', '用户', '功能'],
        'computed': {
            'observed_drop_rate': drop,
        },
        'root_cause_hypothesis': _likely_root_cause(payload),
        'actions': {
            'stop_loss': ['先恢复核心链路'] if '支付' in text or '订单' in text else ['先排除口径问题'],
            'verify': ['按时间、渠道、用户、功能四维拆解验证'],
            'recover': ['修复后回看同口径指标']
        },
        'next_step': 'Use references/五步诊断详解.md to write the hypothesis list, then verify in the order of口径->版本->分层->漏斗->外部事件.',
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
