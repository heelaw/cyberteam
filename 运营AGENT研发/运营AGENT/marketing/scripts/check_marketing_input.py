#!/usr/bin/env python3
"""Validate a marketing brief.

Usage:
  python3 check_marketing_input.py brief.json
  cat brief.json | python3 check_marketing_input.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = ("product_info", "target_user", "marketing_goal")


def load_payload(path: str | None) -> dict:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check marketing input completeness")
    parser.add_argument("path", nargs="?", help="JSON brief path; if omitted, read stdin")
    args = parser.parse_args()

    try:
        payload = load_payload(args.path)
    except Exception as exc:  # noqa: BLE001
        print(f"invalid_json: {exc}", file=sys.stderr)
        return 2

    missing = [key for key in REQUIRED_KEYS if not payload.get(key)]
    if missing:
        print(json.dumps({"ok": False, "missing": missing}, ensure_ascii=False, indent=2))
        return 1

    optional = [k for k in ("budget", "channel", "deadline", "assets") if payload.get(k)]
    print(json.dumps({"ok": True, "required": list(REQUIRED_KEYS), "provided_optional": optional}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
