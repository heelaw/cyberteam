#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Keep the forbidden terms out of the source text itself.
FORBIDDEN = ("课" + "程", "课" + "程" + "引" + "用")
ROOT_MD_FILES = [
    ROOT / "SKILL.md",
    ROOT / "SOUL.md",
    ROOT / "references" / "route-map.md",
    ROOT / "references" / "assessment.md",
    ROOT / "references" / "platform-presets.md",
    ROOT / "references" / "method-matrix.md",
    ROOT / "references" / "workflow-retrospective.md",
]


def iter_files():
    self_path = Path(__file__).resolve()
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py"} and path.resolve() != self_path:
            yield path


def check_forbidden_terms():
    hits = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8")
        for term in FORBIDDEN:
            if term in text:
                hits.append({"file": str(path), "term": term})
    return hits


def check_required_skill_files():
    problems = []
    skills_dir = ROOT / "skills"
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        required = [
            skill_dir / "SKILL.md",
            skill_dir / "references" / "reference.md",
            skill_dir / "assessments" / "assessment.md",
            skill_dir / "scripts" / "run.py",
        ]
        for path in required:
            if not path.exists():
                problems.append(str(path))
    return problems


def check_root_links():
    missing = []
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in ROOT_MD_FILES:
        text = path.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "file:", "#")):
                continue
            if "{" in target or "}" in target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                missing.append({"file": str(path), "target": target})
    return missing


def check_noise_files():
    noise = []
    for path in ROOT.rglob(".DS_Store"):
        if path.is_file():
            noise.append(str(path))
    return noise


def main() -> int:
    report = {
        "forbidden_terms": check_forbidden_terms(),
        "missing_skill_files": check_required_skill_files(),
        "broken_links": check_root_links(),
        "noise_files": check_noise_files(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["forbidden_terms"] or report["missing_skill_files"] or report["broken_links"] or report["noise_files"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
