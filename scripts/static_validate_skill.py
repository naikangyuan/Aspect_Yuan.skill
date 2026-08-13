#!/usr/bin/env python3
"""Static validation for the geologist-aspect-300 skill.

This script checks local files, paths, script health, and beginner PRM
structure. It does not run ASPECT and does not prove parameter legality.
"""

from __future__ import annotations

import argparse
import compileall
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
ASPECT_ROOT = Path(os.environ["ASPECT_ROOT"]).resolve() if os.environ.get("ASPECT_ROOT") else None
ASPECT_MARKERS = ("cookbooks", "benchmarks", "tests", "doc", "source", "include")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    cwd = cwd or ROOT
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode, proc.stdout


def check_prm_templates() -> list[str]:
    errors: list[str] = []
    lint = ROOT / "scripts" / "aspect_prm_lint.py"
    for prm in sorted((ROOT / "assets" / "prm_templates").glob("*.prm")):
        code, output = run([sys.executable, str(lint), str(prm)])
        if code != 0:
            errors.append(f"PRM lint failed for {rel(prm)}:\n{output}")
        text = prm.read_text(errors="ignore")
        if "Teaching template" not in text or "not a final research model" not in text:
            errors.append(f"{rel(prm)} missing teaching-template header.")
        if "Needs verification with ASPECT 3.0.0" not in text:
            errors.append(f"{rel(prm)} missing ASPECT verification warning.")
        m = re.search(r"^\s*set\s+Output directory\s*=\s*(\S+)", text, re.M)
        if not m:
            errors.append(f"{rel(prm)} missing Output directory.")
        elif not m.group(1).startswith("output-"):
            errors.append(f"{rel(prm)} output directory does not start with output-: {m.group(1)}")
    return errors


def markdown_refs(paths: Iterable[Path]) -> list[tuple[Path, str]]:
    refs: list[tuple[Path, str]] = []
    for path in paths:
        text = path.read_text(errors="ignore")
        for ref in re.findall(r"`([^`]+\.(?:prm|md|py|sh|cc|h|txt|json))`", text):
            ref = ref.split()[0]
            if ref.startswith(("http://", "https://")):
                continue
            refs.append((path, ref))
    return refs


def check_referenced_paths() -> list[str]:
    errors: list[str] = []
    md_files = list((ROOT / "references").glob("*.md")) + list((ROOT / "model_wizards").glob("*.md")) + [ROOT / "SKILL.md"]
    for source, ref in markdown_refs(md_files):
        candidates = []
        if ref.startswith(tuple(f"{marker}/" for marker in ASPECT_MARKERS)):
            if ASPECT_ROOT is None:
                continue
            if (ASPECT_ROOT / ref).exists():
                continue
            if not any((ASPECT_ROOT / marker).exists() for marker in ASPECT_MARKERS):
                continue
            candidates.append(ASPECT_ROOT / ref)
        candidates.append(ROOT / ref)
        candidates.append(source.parent / ref)
        if not any(candidate.exists() for candidate in candidates):
            errors.append(f"{rel(source)} references missing path `{ref}`")
    return errors


def check_scripts() -> list[str]:
    errors: list[str] = []
    scripts = sorted((ROOT / "scripts").glob("*"))
    py_files = [p for p in scripts if p.suffix == ".py"]
    for py in py_files:
        try:
            compile(py.read_text(), str(py), "exec")
        except SyntaxError as exc:
            errors.append(f"Python syntax failed for {rel(py)}: {exc}")
        code, output = run([sys.executable, str(py), "--help"])
        if code != 0:
            errors.append(f"--help failed for {rel(py)}:\n{output}")
    for sh in [p for p in scripts if p.suffix == ".sh"]:
        code, output = run(["bash", str(sh), "--help"])
        if code != 0:
            errors.append(f"--help failed for {rel(sh)}:\n{output}")
    for script in scripts:
        if script.is_file() and script.name not in {"__pycache__"}:
            mode = script.stat().st_mode
            if not (mode & stat.S_IXUSR):
                errors.append(f"{rel(script)} is not executable.")
    return errors


def check_evals() -> list[str]:
    errors: list[str] = []
    test_cases = sorted((ROOT / "evals" / "test_cases").glob("*.md"))
    expected = sorted((ROOT / "evals" / "expected_outputs").glob("*.md"))
    expected_names = {p.name for p in expected}
    if not test_cases:
        errors.append("No eval test cases found.")
    for case in test_cases:
        if case.name not in expected_names:
            errors.append(f"No matching expected output for {rel(case)}")
        text = case.read_text(errors="ignore")
        if "## User Request" not in text or "## Expected Skill Behavior" not in text:
            errors.append(f"{rel(case)} missing required eval headings.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Run static validation for geologist-aspect-300.")
    parser.add_argument("--json", action="store_true", help="Reserved for future machine-readable output.")
    args = parser.parse_args()

    checks = {
        "beginner PRM templates": check_prm_templates(),
        "referenced paths": check_referenced_paths(),
        "scripts": check_scripts(),
        "evals": check_evals(),
    }

    failures = 0
    print(f"Static validation for {ROOT}")
    if ASPECT_ROOT is None:
        print("ASPECT root: not set; ASPECT source-tree references are skipped. Set ASPECT_ROOT=/path/to/aspect to check them.")
    else:
        print(f"ASPECT root: {ASPECT_ROOT}")
    for name, errors in checks.items():
        if errors:
            failures += len(errors)
            print(f"\n[FAIL] {name}")
            for error in errors:
                print(f"- {error}")
        else:
            print(f"[ OK ] {name}")

    if failures:
        print(f"\nStatic validation failed with {failures} issue(s).")
        return 1
    print("\nStatic validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
