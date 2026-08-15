"""Small configuration helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except Exception:
        data = _load_without_pyyaml(text, path)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping/object")
    return data


def dump_config(data: dict[str, Any], path: Path) -> None:
    try:
        import yaml  # type: ignore

        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    except Exception:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_without_pyyaml(text: str, path: Path) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError as json_error:
        if path.suffix.lower() not in {".yaml", ".yml"}:
            raise json_error
    try:
        return _parse_simple_yaml_mapping(text)
    except ValueError as yaml_error:
        raise ValueError(
            f"{path} could not be parsed without PyYAML. Install PyYAML for full YAML support, "
            "or use the simple key/value mapping style used by this skill's examples."
        ) from yaml_error


def _parse_simple_yaml_mapping(text: str) -> dict[str, Any]:
    """Parse the small YAML subset used by bundled model/figure configs.

    Supported syntax is intentionally narrow: indentation-based mappings,
    scalar values, and one-line lists like [png, pdf]. This keeps the core CLI
    usable without PyYAML while still failing clearly for advanced YAML.
    """

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("\t"):
            raise ValueError(f"tabs are not supported at line {line_number}")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent % 2:
            raise ValueError(f"indentation must use multiples of two spaces at line {line_number}")
        line = raw_line.strip()
        if line.startswith("- "):
            raise ValueError(f"block lists require PyYAML at line {line_number}")
        if ":" not in line:
            raise ValueError(f"expected key: value at line {line_number}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"empty key at line {line_number}")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"invalid indentation at line {line_number}")
        parent = stack[-1][1]
        value = value.strip()
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_simple_yaml_scalar(value)
    return root


def _parse_simple_yaml_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "None", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_simple_yaml_scalar(part.strip()) for part in inner.split(",")]
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?|[-+]?\d+[eE][-+]?\d+", value):
        return float(value)
    return value
