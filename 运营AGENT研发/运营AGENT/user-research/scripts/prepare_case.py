#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

payload = {
    'problem': '',
    'user': '',
    'scene': '',
    'data': [],
}
if len(sys.argv) > 1:
    payload['problem'] = sys.argv[1]
print(json.dumps(payload, ensure_ascii=False, indent=2))
