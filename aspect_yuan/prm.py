"""Small ASPECT PRM helpers for generated starter models."""

from __future__ import annotations

import re
from pathlib import Path


SET_RE = re.compile(r"^\s*set\s+(.+?)\s*=\s*(.*?)\s*(?:#.*)?$")


def read_sets(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(errors="ignore").splitlines():
        match = SET_RE.match(line)
        if match:
            values[match.group(1).strip()] = match.group(2).strip()
    return values


def validate_prm(path: Path) -> list[dict[str, str]]:
    text = path.read_text(errors="ignore")
    sets = read_sets(path)
    issues: list[dict[str, str]] = []
    for name in ["Dimension", "Output directory"]:
        if name not in sets:
            issues.append({"level": "ERROR", "item": name, "message": f"Missing required starter-model parameter: {name}"})
    stack: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("subsection "):
            stack.append(stripped.removeprefix("subsection ").strip())
        elif stripped == "end":
            if not stack:
                issues.append({"level": "ERROR", "item": f"line {lineno}", "message": "Found end without matching subsection."})
            else:
                stack.pop()
    if stack:
        issues.append({"level": "ERROR", "item": "subsection", "message": "Unclosed subsection(s): " + " / ".join(stack)})
    dim = sets.get("Dimension")
    if dim and dim not in {"2", "3"}:
        issues.append({"level": "ERROR", "item": "Dimension", "message": "Dimension should normally be 2 or 3."})
    if "Output directory" in sets and not sets["Output directory"]:
        issues.append({"level": "ERROR", "item": "Output directory", "message": "Output directory is empty."})
    if "set " not in text:
        issues.append({"level": "ERROR", "item": "file", "message": "No ASPECT set parameters found."})
    if not issues:
        issues.append({"level": "PASS", "item": "file", "message": "No structural starter-model issues found. ASPECT parameter legality still requires aspect --help or a real run."})
    return issues

