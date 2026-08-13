#!/usr/bin/env python3
"""Lightweight structural linting for ASPECT .prm files.

This script does not validate ASPECT parameter legality. It checks structure
and common geologist-facing risks that can be found without running ASPECT.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SUBSECTION_RE = re.compile(r"^\s*subsection\s+(.+?)\s*(?:#.*)?$")
END_RE = re.compile(r"^\s*end\s*(?:#.*)?$")
SET_RE = re.compile(r"^\s*set\s+(.+?)\s*=\s*(.*?)\s*(?:#.*)?$")


def parse_prm(path: Path) -> dict[str, Any]:
    stack: list[tuple[str, int]] = []
    subsection_paths: list[tuple[str, int]] = []
    sets: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for line_no, line in enumerate(path.read_text(errors="ignore").splitlines(), start=1):
        subsection = SUBSECTION_RE.match(line)
        if subsection:
            name = subsection.group(1).strip()
            stack.append((name, line_no))
            subsection_paths.append((" > ".join(name for name, _ in stack), line_no))
            continue

        if END_RE.match(line):
            if not stack:
                issues.append(
                    {
                        "severity": "error",
                        "line": line_no,
                        "message": "Found 'end' without a matching open subsection.",
                        "geologist_hint": "A misplaced end can move boundary, material, or output settings into the wrong part of the model.",
                    }
                )
            else:
                stack.pop()
            continue

        setting = SET_RE.match(line)
        if setting:
            parameter = setting.group(1).strip()
            value = setting.group(2).strip()
            sets.append(
                {
                    "line": line_no,
                    "path": " > ".join(name for name, _ in stack) or "<top level>",
                    "parameter": parameter,
                    "value": value,
                }
            )

    for name, line_no in reversed(stack):
        issues.append(
            {
                "severity": "error",
                "line": line_no,
                "message": f"Subsection '{name}' is not closed.",
                "geologist_hint": "Unclosed sections can cause later geological settings to be interpreted in the wrong context.",
            }
        )

    path_counts = Counter(path for path, _ in subsection_paths)
    duplicate_paths = [
        {"path": path, "count": count, "lines": [line for p, line in subsection_paths if p == path]}
        for path, count in sorted(path_counts.items())
        if count > 1
    ]
    for duplicate in duplicate_paths:
        issues.append(
            {
                "severity": "warning",
                "line": duplicate["lines"][0],
                "message": f"Repeated subsection path: {duplicate['path']} ({duplicate['count']} times).",
                "geologist_hint": "Repeated sections may be intentional, but they can split related geometry, material, or output choices.",
            }
        )

    risk_hints = detect_risks(sets)
    issues.extend(risk_hints)

    return {
        "file": str(path),
        "num_sets": len(sets),
        "num_subsections": len(subsection_paths),
        "sets": sets,
        "duplicate_subsection_paths": duplicate_paths,
        "issues": issues,
        "disclaimer": "This script checks structure and common risks only. It does not prove ASPECT parameter names or values are valid.",
    }


def detect_risks(sets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    by_param: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in sets:
        by_param[item["parameter"]].append(item)

    def warn(item: dict[str, Any], message: str, hint: str) -> None:
        issues.append(
            {
                "severity": "info",
                "line": item["line"],
                "message": message,
                "geologist_hint": hint,
            }
        )

    if "Dimension" not in by_param:
        issues.append(
            {
                "severity": "info",
                "line": None,
                "message": "No top-level 'Dimension' setting was found.",
                "geologist_hint": "ASPECT may use a default, but geologists should make 2-D versus 3-D explicit.",
            }
        )

    if "List of postprocessors" not in by_param:
        issues.append(
            {
                "severity": "info",
                "line": None,
                "message": "No 'List of postprocessors' setting was found.",
                "geologist_hint": "The model may run but not produce the diagnostics needed to interpret the geology.",
            }
        )

    if "Number of fields" in by_param and "Names of fields" not in by_param:
        warn(
            by_param["Number of fields"][0],
            "Compositional field count is set but field names were not found.",
            "Named fields make geological units easier to track and reduce material-list mistakes.",
        )

    if "Names of fields" in by_param:
        names_item = by_param["Names of fields"][-1]
        names = [x.strip() for x in re.split(r"[,;]", names_item["value"]) if x.strip()]
        if "Number of fields" in by_param:
            raw_count = by_param["Number of fields"][-1]["value"]
            try:
                expected = int(float(raw_count))
            except ValueError:
                expected = None
            if expected is not None and names and len(names) != expected:
                warn(
                    names_item,
                    f"Names of fields has {len(names)} names, but Number of fields is {expected}.",
                    "Composition-field mismatches can assign crust, mantle, slab, or weak-zone properties incorrectly.",
                )

    boundary_params = [
        "Tangential velocity boundary indicators",
        "Prescribed velocity boundary indicators",
        "Zero velocity boundary indicators",
        "Fixed temperature boundary indicators",
        "Fixed composition boundary indicators",
        "Mesh deformation boundary indicators",
    ]
    for param in boundary_params:
        for item in by_param.get(param, []):
            warn(
                item,
                f"Boundary indicator setting found: {param}.",
                "Check that boundary names match the selected geometry and the intended tectonic or thermal boundary.",
            )

    if "Additional shared libraries" in by_param:
        for item in by_param["Additional shared libraries"]:
            warn(
                item,
                "Additional shared libraries are required.",
                "Confirm the plugin library is built and that selected model names match registered plugin names.",
            )

    for param in ["Minimum viscosity", "Maximum viscosity"]:
        for item in by_param.get(param, []):
            warn(
                item,
                f"Viscosity bound found: {param}.",
                "Viscosity bounds can dominate weak-zone, slab, or lithosphere behavior if they clip the intended rheology.",
            )

    for param in ["Maximum time step", "CFL number", "End time"]:
        for item in by_param.get(param, []):
            warn(
                item,
                f"Time-control parameter found: {param}.",
                "Check units and ensure output cadence resolves the geological process.",
            )

    return issues


def print_text(report: dict[str, Any]) -> None:
    print(f"ASPECT PRM lint report: {report['file']}")
    print(f"- Subsections: {report['num_subsections']}")
    print(f"- Set parameters: {report['num_sets']}")
    print(f"- Duplicate subsection paths: {len(report['duplicate_subsection_paths'])}")
    print()
    print("Important note: this script does not validate all ASPECT parameter names or legal values.")
    print()

    if report["issues"]:
        print("Issues and risk hints:")
        for issue in report["issues"]:
            line = issue["line"] if issue["line"] is not None else "-"
            print(f"- [{issue['severity']}] line {line}: {issue['message']}")
            print(f"  Geologist hint: {issue['geologist_hint']}")
    else:
        print("No structural issues or common risk hints found.")

    print()
    print("Extracted set parameters:")
    for item in report["sets"]:
        print(f"- line {item['line']}: {item['path']} > {item['parameter']} = {item['value']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lightweight structural linting for ASPECT .prm files.")
    parser.add_argument("prm_file", type=Path, help="Path to an ASPECT .prm file")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args(argv)

    if not args.prm_file.exists():
        print(f"error: file not found: {args.prm_file}", file=sys.stderr)
        return 2

    report = parse_prm(args.prm_file)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)

    return 1 if any(issue["severity"] == "error" for issue in report["issues"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
