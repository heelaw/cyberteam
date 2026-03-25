from __future__ import annotations
from typing import Optional

"""Helpers for making the current cyberteam executable available to spawned agents."""


import os
import shutil
import sys
from pathlib import Path


def _looks_like_cyberteam_entrypoint(value: str) -> bool:
    """Return True when argv0 plausibly points at the cyberteam CLI."""

    name = Path(value).name.lower()
    return name == "cyberteam" or name.startswith("cyberteam.")


def resolve_cyberteam_executable() -> str:
    """Resolve the current cyberteam executable.

    Prefer the current process entrypoint when running from a venv or editable
    install via an absolute path. Fall back to `shutil.which("cyberteam")`, then
    the bare command name.
    """

    argv0 = (sys.argv[0] or "").strip()
    if argv0 and _looks_like_cyberteam_entrypoint(argv0):
        candidate = Path(argv0).expanduser()
        has_explicit_dir = candidate.parent != Path(".")
        if (candidate.is_absolute() or has_explicit_dir) and candidate.is_file():
            return str(candidate.resolve())

    resolved = shutil.which("cyberteam")
    return resolved or "cyberteam"


def build_spawn_path(base_path: Optional[str] = None) -> str:
    """Ensure the current cyberteam executable directory is on PATH."""

    path_value = base_path if base_path is not None else os.environ.get("PATH", "")
    executable = resolve_cyberteam_executable()
    if not os.path.isabs(executable):
        return path_value

    bin_dir = str(Path(executable).resolve().parent)
    path_parts = [part for part in path_value.split(os.pathsep) if part] if path_value else []
    if bin_dir in path_parts:
        return path_value
    if not path_parts:
        return bin_dir
    return os.pathsep.join([bin_dir, *path_parts])
