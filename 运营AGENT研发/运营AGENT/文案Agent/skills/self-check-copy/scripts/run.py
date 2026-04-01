#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3] / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from copywriting_skill_runner import run_skill


if __name__ == "__main__":
    raise SystemExit(run_skill("self-check-copy"))
