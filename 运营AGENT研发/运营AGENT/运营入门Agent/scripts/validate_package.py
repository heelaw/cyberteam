#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    root / 'SKILL.md',
    root / 'references' / 'curriculum-map.md',
    root / 'references' / 'assessment.md',
]
skills = [
    '运营宏观认知与流量增长框架',
    '运营岗位地图与职责边界',
    '运营人成长路径与职业规划',
]
missing = [str(p.relative_to(root)) for p in required if not p.exists()]
for skill in skills:
    base = root / 'skills' / skill
    for rel in ['SKILL.md', 'references/reference.md', 'assess/assessment.md', 'scripts/run.py']:
        path = base / rel
        if not path.exists():
            missing.append(str(path.relative_to(root)))
if missing:
    print('missing:')
    for item in missing:
        print(item)
    sys.exit(1)
print('ok')
