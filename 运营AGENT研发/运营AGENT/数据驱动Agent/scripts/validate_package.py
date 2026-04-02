#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX_ROOT = ROOT.parents[1] / '运营AGENT_CODEX'
SKILL_ROOT = ROOT / '配套skill'
TERM_A = ''.join(['课', '程'])
TERM_B = ''.join(['课', '程', '引', '用'])
FORBIDDEN = [TERM_A, TERM_B]
REQUIRED_TOP = [
    ROOT / 'SKILL.md',
    ROOT / 'Agent文档' / '数据驱动agent.md',
    ROOT / 'references' / 'theory.json',
    ROOT / 'references' / 'source-map.md',
    ROOT / 'references' / 'workflow-retrospective.md',
    ROOT / 'scripts' / 'validate_package.py',
    CODEX_ROOT / '文件包映射.md',
]
REQUIRED_SKILLS = {
    '活动效果评估': [
        'SKILL.md',
        'references/评估维度详解.md',
        'references/四维度评估模板.md',
        'references/效果对比分析表.md',
        'assess/质量评估清单.json',
        'evals/evals.json',
        'scripts/run.py',
    ],
    '产品问题诊断': [
        'SKILL.md',
        'references/五步诊断详解.md',
        'references/问题分类指南.md',
        'references/诊断检查清单.md',
        'assess/质量评估清单.json',
        'evals/evals.json',
        'scripts/run.py',
    ],
    '产品状态评估': [
        'SKILL.md',
        'references/状态分层与案例库.md',
        'references/五维度评估详解.md',
        'references/产品健康度指标.md',
        'references/评估报告模板.md',
        'assess/质量评估清单.json',
        'evals/evals.json',
        'scripts/run.py',
    ],
}
REQUIRED_ROOT_PHRASES = ['goal-driven-main', '输入 / 输出 对照', '新窗口必读', '当前进度']
REQUIRED_AGENT_PHRASES = ['goal-driven-main', '主循环', '任务归类', '路由', '岗位边界']
REQUIRED_SKILL_PHRASES = ['SOP', '绝对不能', '输出骨架', '参考文件', '状态分层与案例库']


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def iter_text_files() -> list[Path]:
    paths: list[Path] = []
    for suffix in ('*.md', '*.json', '*.py'):
        paths.extend(ROOT.rglob(suffix))
    return paths


def has_all(text: str, phrases: list[str]) -> bool:
    return all(p in text for p in phrases)


def count_nonempty_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def main() -> int:
    problems = []

    for path in REQUIRED_TOP:
        if not path.exists():
            problems.append(f'missing: {path}')

    root_skill_path = ROOT / 'SKILL.md'
    agent_doc_path = ROOT / 'Agent文档' / '数据驱动agent.md'
    source_map_path = ROOT / 'references' / 'source-map.md'
    retro_path = ROOT / 'references' / 'workflow-retrospective.md'

    root_text = read_text(root_skill_path) if root_skill_path.exists() else ''
    agent_text = read_text(agent_doc_path) if agent_doc_path.exists() else ''
    source_map_text = read_text(source_map_path) if source_map_path.exists() else ''
    retro_text = read_text(retro_path) if retro_path.exists() else ''

    if root_text and not has_all(root_text, REQUIRED_ROOT_PHRASES):
        problems.append('root SKILL.md missing required handoff phrases')
    if agent_text and not has_all(agent_text, REQUIRED_AGENT_PHRASES):
        problems.append('agent doc missing required loop / routing phrases')
    if source_map_text and '数据驱动Agent' not in source_map_text:
        problems.append('source-map missing agent linkage')
    if retro_text and 'QA' not in retro_text:
        problems.append('workflow-retrospective missing QA section')

    for skill, rels in REQUIRED_SKILLS.items():
        skill_root = SKILL_ROOT / skill
        for rel in rels:
            path = skill_root / rel
            if not path.exists():
                problems.append(f'missing: {path}')
                continue
            if path.suffix in {'.md', '.py'}:
                text = read_text(path)
                if path.name == 'SKILL.md' and count_nonempty_lines(text) < 24:
                    problems.append(f'too thin skill doc: {path}')
                if path.name == 'SKILL.md' and not has_all(text, REQUIRED_SKILL_PHRASES):
                    problems.append(f'skill doc missing required framing: {path}')
                if path.suffix == '.py':
                    if 'json.dumps' not in text or 'next_step' not in text:
                        problems.append(f'script not obviously executable: {path}')
            elif path.suffix == '.json':
                try:
                    data = json.loads(read_text(path))
                except Exception as exc:
                    problems.append(f'invalid json in {path}: {exc}')
                    continue
                if path.name == '质量评估清单.json':
                    dimensions = data.get('quality_dimension') or data.get('quality_dimensions') or []
                    if len(dimensions) < 5:
                        problems.append(f'quality gate too small in {path}')
                    if 'critical_rules_check' not in data:
                        problems.append(f'missing critical rules in {path}')
                if path.name == 'evals.json':
                    if len(data.get('test_cases', [])) < 3:
                        problems.append(f'too few eval cases in {path}')
                    if not data.get('test_cases'):
                        problems.append(f'missing eval cases in {path}')

    for path in iter_text_files():
        if not path.exists():
            continue
        text = read_text(path)
        for term in FORBIDDEN:
            if term in text:
                problems.append(f'forbidden term {term!r} found in {path}')

    try:
        json.loads((ROOT / 'references' / 'theory.json').read_text(encoding='utf-8'))
    except Exception as exc:
        problems.append(f'invalid json in theory.json: {exc}')

    if problems:
        print(json.dumps({'ok': False, 'problems': problems}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({'ok': True, 'checked': len(REQUIRED_TOP) + sum(len(v) for v in REQUIRED_SKILLS.values())}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
