#!/usr/bin/env python3
"""Map a code project with @wesleysimplicio/llm-project-mapper.

Tota Agent treats project mapping as a core onboarding step. This script is
idempotent: re-running on an already-mapped project is a no-op unless
``--force`` is passed.

Memory lives in ``$TOTA_HOME/mapped_projects.json`` (falling back to
``$HERMES_HOME``, then ``~/.tota``) so mapping survives across sessions and
profiles.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


MAPPER_NPM_PACKAGE = "@wesleysimplicio/llm-project-mapper"
MEMORY_FILENAME = "mapped_projects.json"
DEFAULT_TTL_DAYS = 30


def _tota_home() -> Path:
    for env_var in ("TOTA_HOME", "HERMES_HOME"):
        val = os.environ.get(env_var, "").strip()
        if val:
            return Path(val).expanduser()
    return Path.home() / ".tota"


def _memory_path() -> Path:
    home = _tota_home()
    home.mkdir(parents=True, exist_ok=True)
    return home / MEMORY_FILENAME


def _load_memory() -> dict[str, dict[str, Any]]:
    path = _memory_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_memory(memory: dict[str, dict[str, Any]]) -> None:
    path = _memory_path()
    path.write_text(json.dumps(memory, indent=2, sort_keys=True), encoding="utf-8")


def _git_remote(project_root: Path) -> str | None:
    git_dir = project_root / ".git"
    if not git_dir.exists():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(project_root), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def _is_fresh(entry: dict[str, Any], ttl_days: int) -> bool:
    mapped_at = entry.get("mapped_at")
    if not mapped_at:
        return False
    try:
        ts = _dt.datetime.fromisoformat(mapped_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    now = _dt.datetime.now(_dt.timezone.utc)
    return (now - ts).days < ttl_days


def _agents_md_present(project_root: Path) -> bool:
    return (project_root / "AGENTS.md").exists()


def _ralph_ready(project_root: Path) -> bool:
    if not _agents_md_present(project_root):
        return False
    specs_dir = project_root / ".specs"
    if not specs_dir.is_dir():
        return False
    # at least one spec file (any extension)
    return any(specs_dir.iterdir())


def _run_mapper(project_root: Path) -> tuple[bool, str]:
    npx = shutil.which("npx")
    if not npx:
        return False, "npx is not installed; install Node.js >=16.7 to use the mapper."
    try:
        result = subprocess.run(
            [npx, "--yes", MAPPER_NPM_PACKAGE],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return False, "llm-project-mapper timed out after 600s."
    except OSError as exc:
        return False, f"failed to spawn npx: {exc}"
    if result.returncode != 0:
        msg = (result.stderr or result.stdout or "").strip()[:500]
        return False, f"mapper exited with code {result.returncode}: {msg}"
    return True, (result.stdout or "").strip()[:500]


def _mapper_version() -> str:
    npx = shutil.which("npx")
    if not npx:
        return "unknown"
    try:
        result = subprocess.run(
            [npx, "--yes", MAPPER_NPM_PACKAGE, "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def map_project(project_root: Path, force: bool, ttl_days: int) -> dict[str, Any]:
    project_root = project_root.resolve()
    if not project_root.is_dir():
        return {"ok": False, "error": f"project_root not a directory: {project_root}"}

    memory = _load_memory()
    key = str(project_root)
    existing = memory.get(key)

    if existing and not force and _is_fresh(existing, ttl_days) and _agents_md_present(project_root):
        return {"ok": True, "skipped": True, "reason": "already_mapped_recent", "entry": existing}

    ok, output = _run_mapper(project_root)
    if not ok:
        return {"ok": False, "error": output}

    entry = {
        "project_root": str(project_root),
        "git_remote": _git_remote(project_root),
        "mapped_at": _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "mapper_version": _mapper_version(),
        "agents_md_present": _agents_md_present(project_root),
        "ralph_ready": _ralph_ready(project_root),
    }
    memory[key] = entry
    _save_memory(memory)

    return {"ok": True, "skipped": False, "entry": entry, "mapper_output": output}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Map a code project with llm-project-mapper.")
    parser.add_argument("--project-root", default=os.getcwd(), help="Path to the project root (default: cwd).")
    parser.add_argument("--force", action="store_true", help="Re-map even if a fresh entry exists in memory.")
    parser.add_argument("--ttl-days", type=int, default=DEFAULT_TTL_DAYS, help="Days after which a mapping is considered stale.")
    args = parser.parse_args(argv)

    result = map_project(Path(args.project_root), force=args.force, ttl_days=args.ttl_days)
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
