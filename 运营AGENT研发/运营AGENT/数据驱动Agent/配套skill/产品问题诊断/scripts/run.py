#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from typing import Any


REQUIRED_FIELDS = [
    '异常指标',
    '开始时间',
    '影响范围',
]

KEYWORD_SEVERITY = [
    ('P0', ['支付失败', '下单失败', '提交失败', '核心链路', '大面积', '全量']),
    ('P1', ['明显下滑', '连续下跌', '核心体验', '转化骤降', '严重异常']),
    ('P2', ['局部异常', '单渠道', '单功能', '局部下滑', '部分用户']),
]

CAUSE_RULES = [
    ('数据口径或埋点问题', ['埋点', '口径', '漏数', '延迟', '重复统计', '新旧口径']),
    ('版本变更或发布异常', ['版本', '发版', '上线', '更新', '灰度', '回滚']),
    ('支付或订单链路异常', ['支付', '订单', '库存', '退款', '结算']),
    ('运营触达或活动影响', ['活动', '触达', '推送', '短信', '投放', '活动页']),
    ('渠道或流量结构变化', ['渠道', '来源', '投放', '自然流量', '搜索流量']),
    ('用户分层或使用习惯变化', ['新用户', '老用户', '高价值用户', '沉默', '活跃', '留存']),
]


def _load_payload() -> dict[str, Any]:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        try:
            return json.loads(sys.argv[1])
        except json.JSONDecodeError:
            pass
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {'_raw_input': raw}


def _flatten_text(obj: Any) -> str:
    if isinstance(obj, dict):
        return ' '.join(f'{k} { _flatten_text(v) }' for k, v in obj.items())
    if isinstance(obj, list):
        return ' '.join(_flatten_text(item) for item in obj)
    return str(obj)


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


def _collect_numbers(obj: Any) -> list[float]:
    numbers: list[float] = []
    if isinstance(obj, dict):
        for value in obj.values():
            numbers.extend(_collect_numbers(value))
    elif isinstance(obj, list):
        for item in obj:
            numbers.extend(_collect_numbers(item))
    else:
        num = _to_number(obj)
        if num is not None:
            numbers.append(num)
    return numbers


def _severity(text: str, payload: dict[str, Any]) -> str:
    explicit = str(payload.get('severity') or payload.get('级别') or '').upper().strip()
    if explicit in {'P0', 'P1', 'P2', 'P3'}:
        return explicit
    for level, keywords in KEYWORD_SEVERITY:
        if any(keyword in text for keyword in keywords):
            return level
    return 'P3'


def _diagnosis_signals(text: str, payload: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    if any(keyword in text for keyword in ['今日', '昨天', '单日', '突发', '骤降']):
        signals.append('突发型')
    if any(keyword in text for keyword in ['连续', '7天', '30天', '趋势', '持续']):
        signals.append('趋势型')
    if any(keyword in text for keyword in ['全量', '大面积', '核心链路']):
        signals.append('高影响范围')
    if any(keyword in text for keyword in ['单渠道', '单功能', '单端']):
        signals.append('局部异常')
    if payload.get('版本') or payload.get('发版记录'):
        signals.append('版本变更信号')
    if payload.get('活动') or payload.get('活动记录'):
        signals.append('运营动作信号')
    return signals or ['待补充信号']


def _likely_causes(text: str) -> list[str]:
    causes: list[str] = []
    for cause, keywords in CAUSE_RULES:
        if any(keyword in text for keyword in keywords):
            causes.append(cause)
    if not causes:
        causes = ['需要先排口径，再按维度下钻，再验证业务假设']
    return causes[:3]


def _missing_fields(payload: dict[str, Any]) -> list[str]:
    text = _flatten_text(payload)
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in text:
            missing.append(field)
    if not any(key in payload for key in ['指标序列', 'metrics', '数据背景']) and not any(word in text for word in ['时间', '渠道', '用户', '功能']):
        missing.append('时间/渠道/用户/功能维度数据')
    return missing


def _drop_rate(payload: dict[str, Any]) -> float | None:
    source = payload.get('指标序列') or payload.get('metrics') or payload.get('数据背景') or {}
    numbers = _collect_numbers(source)
    if len(numbers) >= 2 and numbers[0] != 0:
        return round((numbers[0] - numbers[-1]) / numbers[0], 4)
    return None


def main() -> int:
    payload = _load_payload()
    text = _flatten_text(payload)
    severity = _severity(text, payload)
    missing = _missing_fields(payload)
    drop_rate = _drop_rate(payload)
    signals = _diagnosis_signals(text, payload)
    causes = _likely_causes(text)

    if missing:
        output = {
            'skill': '产品问题诊断',
            'status': 'blocked',
            'severity': severity,
            'missing': missing,
            'signals': signals,
            'root_cause_hypotheses': causes,
            'verification_order': [
                '先确认指标口径与埋点',
                '再确认版本、活动和配置变更',
                '再按时间、渠道、用户、功能下钻',
                '最后确认外部事件或竞品扰动',
            ],
            'immediate_actions': [
                '补齐缺失字段后再进入归因',
                '先冻结当前口径，避免混算',
            ],
            'fallback': '如果只能输出当前判断，先标明不确定性，不要假装已完成归因。',
            'next_step': '补齐缺失输入后，重新运行并输出完整诊断。',
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    output = {
        'skill': '产品问题诊断',
        'status': 'ready',
        'severity': severity,
        'signals': signals,
        'observed_drop_rate': drop_rate,
        'root_cause_hypotheses': causes,
        'verification_order': [
            '先确认指标口径与埋点',
            '再确认版本、活动和配置变更',
            '再按时间、渠道、用户、功能下钻',
            '最后确认外部事件或竞品扰动',
        ],
        'immediate_actions': [
            '按最可能假设先止损',
            '把验证动作拆成可执行检查项',
            '复盘同口径数据变化并记录恢复时间点',
        ],
        'fallback': '如果证据不足，先输出当前最优判断并标注置信度，不要强行收口。',
        'confidence': '中' if severity in {'P2', 'P3'} else '低',
        'next_step': 'Use references/五步诊断详解.md and references/诊断检查清单.md to expand the hypothesis tree, then verify in order.',
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
