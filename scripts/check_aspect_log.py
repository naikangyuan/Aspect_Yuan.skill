#!/usr/bin/env python3
"""Check an ASPECT run log and explain common failures for geologists."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PATTERNS = [
    ("exception", re.compile(r"\b(exception|ExcMessage|terminate called|Traceback)\b", re.I),
     "ASPECT reported an exception. This often means an invalid parameter, plugin problem, or numerical failure."),
    ("nan", re.compile(r"\b(nan|inf)\b", re.I),
     "A NaN/Inf appeared. This usually indicates unstable numerics, bad material values, or an invalid expression."),
    ("convergence failure", re.compile(r"(convergence.*fail|failed to converge|no convergence|solver.*fail)", re.I),
     "A solver failed to converge. Check viscosity contrasts, timestep size, mesh resolution, and boundary conditions before changing geology."),
    ("out of memory", re.compile(r"(out of memory|std::bad_alloc|cannot allocate|killed)", re.I),
     "The run likely exceeded available memory. Reduce refinement, output load, or MPI layout."),
    ("plugin not found", re.compile(r"(plugin.*not found|could not find.*plugin|shared librar.*not|cannot open shared object|Additional shared libraries)", re.I),
     "A plugin or shared library may be missing. Check Additional shared libraries and registered model names."),
    ("parameter not declared", re.compile(r"(parameter.*not.*declared|No such entry|does not exist in subsection|not a valid parameter)", re.I),
     "A parameter or subsection name may be wrong for this ASPECT version."),
]

SUCCESS_PATTERNS = [
    re.compile(r"Total wallclock time", re.I),
    re.compile(r"Termination criteria", re.I),
    re.compile(r"ASPECT.*finished", re.I),
    re.compile(r"Exit status:\s*0", re.I),
]


def analyze_log(path: Path) -> dict[str, Any]:
    text = path.read_text(errors="ignore")
    lines = text.splitlines()
    issues = []
    for key, regex, explanation in PATTERNS:
        matches = []
        for i, line in enumerate(lines, start=1):
            if regex.search(line):
                matches.append({"line": i, "text": line.strip()[:300]})
                if len(matches) >= 5:
                    break
        if matches:
            issues.append({"type": key, "explanation": explanation, "matches": matches})

    success_signals = [p.pattern for p in SUCCESS_PATTERNS if p.search(text)]
    exit_status = None
    m = re.search(r"Exit status:\s*(\d+)", text)
    if m:
        exit_status = int(m.group(1))

    step_patterns = [
        re.compile(r"Time step\s+(\d+).*?t\s*=\s*([0-9eE+\-.]+)", re.I),
        re.compile(r"Time step\s+(\d+)", re.I),
    ]
    last_step = None
    last_time = None
    for line in lines:
        for regex in step_patterns:
            m = regex.search(line)
            if m:
                last_step = int(m.group(1))
                if len(m.groups()) > 1:
                    try:
                        last_time = float(m.group(2))
                    except ValueError:
                        pass
                break

    nonlinear_iterations = None
    stokes_iterations = None
    for line in reversed(lines):
        if nonlinear_iterations is None:
            m = re.search(r"nonlinear.*?(\d+)\s+iteration", line, re.I)
            if m:
                nonlinear_iterations = int(m.group(1))
        if stokes_iterations is None:
            m = re.search(r"stokes.*?(\d+)\s+iteration", line, re.I)
            if m:
                stokes_iterations = int(m.group(1))
        if nonlinear_iterations is not None and stokes_iterations is not None:
            break

    normal_end = bool(success_signals) and not issues and (exit_status in (None, 0))
    if exit_status not in (None, 0):
        normal_end = False

    return {
        "file": str(path),
        "normal_end": normal_end,
        "exit_status": exit_status,
        "success_signals": success_signals,
        "issues": issues,
        "last_time_step": last_step,
        "last_time": last_time,
        "last_nonlinear_iterations": nonlinear_iterations,
        "last_stokes_iterations": stokes_iterations,
        "line_count": len(lines),
    }


def print_text(report: dict[str, Any]) -> None:
    print(f"ASPECT log check: {report['file']}")
    if report["normal_end"]:
        print("Status: likely completed normally.")
    else:
        print("Status: needs attention.")

    if report["exit_status"] is not None:
        print(f"Exit status: {report['exit_status']}")
    if report["last_time_step"] is not None:
        print(f"Last time step found: {report['last_time_step']}")
    if report["last_time"] is not None:
        print(f"Last model time found: {report['last_time']}")
    if report["last_nonlinear_iterations"] is not None:
        print(f"Last nonlinear iteration count found: {report['last_nonlinear_iterations']}")
    if report["last_stokes_iterations"] is not None:
        print(f"Last Stokes iteration count found: {report['last_stokes_iterations']}")

    print()
    if report["issues"]:
        print("Problems or risk signals:")
        for issue in report["issues"]:
            print(f"- {issue['type']}: {issue['explanation']}")
            for match in issue["matches"]:
                print(f"  line {match['line']}: {match['text']}")
    else:
        print("No common fatal patterns were found.")
        if not report["success_signals"]:
            print("However, no strong normal-completion signal was found either. Check the end of the log manually.")

    print()
    print("Geologist next step: if the log is clean, inspect statistics and visualization fields before interpreting the science.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check an ASPECT log for common run failures.")
    parser.add_argument("log_file", type=Path, help="Path to an ASPECT run log")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args(argv)

    if not args.log_file.exists():
        print(f"error: log file not found: {args.log_file}", file=sys.stderr)
        return 2

    report = analyze_log(args.log_file)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 1 if report["issues"] or not report["normal_end"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
