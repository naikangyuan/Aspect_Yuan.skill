"""Figure recipe metadata."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from . import __version__


def git_commit(root: Path) -> str:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False)
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def write_recipe(data: dict[str, Any], path: Path, root: Path) -> None:
    payload = dict(data)
    payload["aspect_yuan_skill_version"] = __version__
    payload["git_commit"] = git_commit(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

