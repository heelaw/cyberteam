#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a course research brief")
    parser.add_argument("--course", required=True, help="Course name")
    parser.add_argument("--input", required=True, help="Primary input path")
    parser.add_argument("--direction", required=True, help="Target skill direction")
    parser.add_argument("--batch", default="", help="Batch label")
    parser.add_argument("--notes", default="", help="Extra notes")
    args = parser.parse_args()

    brief = {
        "course_name": args.course,
        "primary_input": args.input,
        "target_skill_direction": args.direction,
        "batch": args.batch or None,
        "notes": args.notes or None,
    }
    print(json.dumps(brief, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
