#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [root / 'SKILL.md', root / 'references' / 'curriculum-map.md', root / 'references' / 'assessment.md']
skills = ['运营认知与岗位理解', '运营成长与职业规划', '文案写作基础', '活动策划基础', '社区运营基础', '社群运营基础', '新媒体内容运营基础', '渠道推广执行基础']
missing = [str(p.relative_to(root)) for p in required if not p.exists()]
for skill in skills:
    base = root / 'skills' / skill
    for rel in ['SKILL.md', 'references/reference.md', 'assess/assessment.md', 'evals/test案例.md', 'scripts/run.py']:
        path = base / rel
        if not path.exists():
            missing.append(str(path.relative_to(root)))
if missing:
    print('missing:')
    for item in missing:
        print(item)
    sys.exit(1)
print('ok')
