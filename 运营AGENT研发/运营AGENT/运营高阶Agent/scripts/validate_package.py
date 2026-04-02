#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    root / 'SKILL.md',
    root / 'references' / 'curriculum-map.md',
    root / 'references' / 'assessment.md',
    root / 'references' / 'upstream.md',
    root / 'references' / 'downstream.md',
    root / 'references' / 'interfaces.md',
    root / 'Agent文档' / '运营高阶agent.md',
]
skills = [
    'skill-1-框架式思维与问题拆解',
    'skill-2-产品运营规划',
    'skill-3-用户留存与激励体系',
    'skill-4-运营框架理解与指标拆解',
    'skill-5-行动指导型框架',
    'skill-6-策略执行',
    'skill-7-数据驱动运营',
]
missing = [str(p.relative_to(root)) for p in required if not p.exists()]
for skill in skills:
    base = root / '配套skill' / skill
    for rel in ['SKILL.md', 'references/reference.md', 'assess/评估清单.md', 'evals/test案例.md', 'scripts/run.py']:
        p = base / rel
        if not p.exists():
            missing.append(str(p.relative_to(root)))
if missing:
    print('missing:')
    print('\n'.join(missing))
    sys.exit(1)
print('ok')
