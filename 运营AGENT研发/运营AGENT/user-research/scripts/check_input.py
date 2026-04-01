#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

required = ['problem', 'user', 'scene']
obj = json.load(sys.stdin)
missing = [k for k in required if not str(obj.get(k, '')).strip()]
print(json.dumps({'ok': not missing, 'missing': missing}, ensure_ascii=False, indent=2))
sys.exit(0 if not missing else 1)
