#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


def main() -> int:
    raw = sys.stdin.read().strip()
    payload = None
    if raw:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw}
    result = {
        "skill": '渠道推广四大避坑点',
        "received_input": payload is not None,
        "next_step": "Read references/reference.md, then apply the SOP.",
        "input_echo": payload,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
