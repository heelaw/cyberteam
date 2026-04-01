#!/usr/bin/env python3
"""Normalize marketing inputs into a compact brief."""

from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a marketing brief")
    parser.add_argument("--product", required=True, help="Product or service name")
    parser.add_argument("--user", required=True, help="Target user description")
    parser.add_argument("--goal", required=True, help="Marketing goal")
    parser.add_argument("--budget", default="", help="Budget")
    parser.add_argument("--channel", default="", help="Preferred channel")
    parser.add_argument("--deadline", default="", help="Deadline")
    args = parser.parse_args()

    brief = {
        "product_info": args.product,
        "target_user": args.user,
        "marketing_goal": args.goal,
        "budget": args.budget or None,
        "channel": args.channel or None,
        "deadline": args.deadline or None,
    }
    print(json.dumps(brief, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
