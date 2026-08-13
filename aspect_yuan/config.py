"""Small configuration helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except Exception:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping/object")
    return data


def dump_config(data: dict[str, Any], path: Path) -> None:
    try:
        import yaml  # type: ignore

        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    except Exception:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

