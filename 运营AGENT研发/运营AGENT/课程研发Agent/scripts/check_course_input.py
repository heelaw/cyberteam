#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = ("course_name", "primary_input", "target_skill_direction")


def load_payload(path: str | None) -> dict:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check course input completeness")
    parser.add_argument("path", nargs="?", help="JSON task file; if omitted, read stdin")
    args = parser.parse_args()

    try:
        payload = load_payload(args.path)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"invalid_json: {exc}"}, ensure_ascii=False, indent=2))
        return 2

    missing = [key for key in REQUIRED_KEYS if not str(payload.get(key, "")).strip()]
    if missing:
        print(json.dumps({"ok": False, "missing": missing}, ensure_ascii=False, indent=2))
        return 1

    optional = [k for k in ("secondary_inputs", "batch", "notes", "owner") if payload.get(k)]
    print(json.dumps({"ok": True, "required": list(REQUIRED_KEYS), "provided_optional": optional}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
