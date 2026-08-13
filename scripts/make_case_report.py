#!/usr/bin/env python3
"""Generate a geologist-facing markdown report for an ASPECT case directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from check_aspect_log import analyze_log
from parse_aspect_statistics import read_statistics, summarize, write_csv


def newest(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)


def find_case_files(case_dir: Path) -> dict[str, Path | None]:
    prm_files = sorted(case_dir.glob("*.prm"))
    logs = sorted([*case_dir.glob("*.log"), *case_dir.glob("*run*.txt")])
    log_txt = case_dir / "log.txt"
    if log_txt.exists():
        logs.append(log_txt)
    stats = []
    for name in ["statistics", "statistics.txt"]:
        candidate = case_dir / name
        if candidate.exists():
            stats.append(candidate)
    stats.extend(case_dir.glob("**/statistics"))
    return {
        "prm": prm_files[0] if prm_files else None,
        "log": newest(logs),
        "statistics": newest(list(set(stats))),
    }


def report_markdown(case_dir: Path, files: dict[str, Path | None], artifact_dir: Path | None = None) -> str:
    lines = []
    lines.append("# ASPECT Case Report\n")
    lines.append(f"- Case directory: `{case_dir}`\n")
    for key, path in files.items():
        lines.append(f"- {key}: `{path}`\n" if path else f"- {key}: not found\n")
    lines.append("\n## Run Status\n\n")

    risks = []
    if files["log"]:
        log_report = analyze_log(files["log"])
        if log_report["normal_end"]:
            lines.append("The log appears to show a normal completion.\n")
        else:
            lines.append("The log needs attention before interpreting geological results.\n")
        if log_report["last_time_step"] is not None:
            lines.append(f"- Last time step found: `{log_report['last_time_step']}`\n")
        if log_report["last_time"] is not None:
            lines.append(f"- Last model time found: `{log_report['last_time']}`\n")
        if log_report["issues"]:
            lines.append("\n### Log Risks\n\n")
            for issue in log_report["issues"]:
                risks.append(issue["type"])
                lines.append(f"- **{issue['type']}**: {issue['explanation']}\n")
                first = issue["matches"][0]
                lines.append(f"  First match line {first['line']}: `{first['text']}`\n")
    else:
        lines.append("No log file was found. The model cannot be classified as successful from this report alone.\n")
        risks.append("missing log")

    lines.append("\n## Statistics Summary\n\n")
    if files["statistics"]:
        columns, rows = read_statistics(files["statistics"])
        summary = summarize(columns, rows)
        csv_path = (artifact_dir or case_dir) / "statistics.summary.csv"
        write_csv(csv_path, columns, rows, summary["summary_columns"])
        lines.append(f"- Statistics rows: `{summary['row_count']}`\n")
        lines.append(f"- Statistics columns: `{summary['column_count']}`\n")
        lines.append(f"- CSV summary: `{csv_path}`\n")
        if summary["row_count"] == 0 or summary["column_count"] == 0:
            lines.append("- Warning: statistics file exists but no table rows/columns were parsed.\n")
            risks.append("empty statistics")
        lines.append("\n### Last Common Values\n\n")
        for key, value in summary["last_row"].items():
            lines.append(f"- {key}: `{value}`\n")
    else:
        lines.append("No statistics file was found. Check whether the run started, output directory is correct, or postprocessors were enabled.\n")
        risks.append("missing statistics")

    lines.append("\n## Geological Interpretation Guardrails\n\n")
    lines.append("- Do not interpret the science until the log is clean.\n")
    lines.append("- Confirm the `.prm` geometry, boundary conditions, temperature field, material model, and composition fields still match the intended geology.\n")
    lines.append("- Inspect visualization fields such as temperature, velocity, viscosity, strain rate, composition, topography, and heat flux where available.\n")

    lines.append("\n## Main Risks\n\n")
    if risks:
        for risk in sorted(set(risks)):
            lines.append(f"- {risk}\n")
    else:
        lines.append("- No common log/statistics risks detected by the helper scripts.\n")

    lines.append("\n## Suggested Next Steps\n\n")
    if files["prm"]:
        lines.append(f"- Run `aspect_prm_lint.py {files['prm']}` before changing parameters.\n")
    if files["log"]:
        lines.append(f"- Run `check_aspect_log.py {files['log']}` after each run.\n")
    if files["statistics"]:
        lines.append(f"- Run `parse_aspect_statistics.py {files['statistics']}` and plot important time histories.\n")
    lines.append("- Compare outputs against the geological question, not just against numerical completion.\n")
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a markdown report for an ASPECT case directory.")
    parser.add_argument("case_dir", type=Path, help="Directory containing .prm/log/statistics files")
    parser.add_argument("--output", type=Path, help="Output markdown path. Default: <case_dir>/case_report.md")
    args = parser.parse_args()

    if not args.case_dir.exists() or not args.case_dir.is_dir():
        print(f"error: case directory not found: {args.case_dir}", file=sys.stderr)
        return 2

    case_dir = args.case_dir.resolve()
    files = find_case_files(case_dir)
    output = args.output or (case_dir / "case_report.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report_markdown(case_dir, files, output.parent), encoding="utf-8")
    print(f"Wrote case report: {output}")
    print("Geologist note: use this report as a triage summary, then inspect fields visually before scientific interpretation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
