#!/usr/bin/env python3
"""Parse ASPECT statistics files and produce a compact CSV summary."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


HEADER_RE = re.compile(r"^#\s*(\d+):\s*(.+?)\s*$")


def safe_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def read_statistics(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    headers: dict[int, str] = {}
    rows: list[dict[str, str]] = []
    for line in path.read_text(errors="ignore").splitlines():
        if not line.strip():
            continue
        header = HEADER_RE.match(line)
        if header:
            headers[int(header.group(1))] = header.group(2).strip()
            continue
        if line.lstrip().startswith("#"):
            continue
        parts = line.split()
        if not parts:
            continue
        names = [headers.get(i + 1, f"Column {i + 1}") for i in range(len(parts))]
        rows.append({name: value for name, value in zip(names, parts)})
    column_names = [headers[i] for i in sorted(headers) if any(headers[i] in row for row in rows)]
    if not column_names and rows:
        column_names = list(rows[0].keys())
    return column_names, rows


def choose_common_columns(columns: list[str]) -> list[str]:
    wanted_fragments = [
        "Time step number",
        "Time (",
        "Time step size",
        "Number of mesh cells",
        "Iterations for Stokes solver",
        "Iterations for temperature solver",
        "RMS velocity",
        "Max. velocity",
        "Average temperature",
        "Maximal temperature",
        "Minimal temperature",
        "Visualization file name",
    ]
    selected = []
    for col in columns:
        if any(fragment in col for fragment in wanted_fragments):
            selected.append(col)
    return selected or columns[: min(12, len(columns))]


def summarize(columns: list[str], rows: list[dict[str, str]]) -> dict[str, Any]:
    selected = choose_common_columns(columns)
    last = rows[-1] if rows else {}
    numeric_ranges = {}
    for col in selected:
        values = [safe_float(row.get(col, "")) for row in rows]
        values = [value for value in values if value is not None]
        if values:
            numeric_ranges[col] = {"min": min(values), "max": max(values), "last": values[-1]}
    return {
        "row_count": len(rows),
        "column_count": len(columns),
        "columns": columns,
        "summary_columns": selected,
        "last_row": {col: last.get(col, "") for col in selected},
        "numeric_ranges": numeric_ranges,
    }


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]], selected: list[str]) -> None:
    if not selected:
        selected = ["No columns found"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=selected)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in selected})


def maybe_plot(path: Path, columns: list[str], rows: list[dict[str, str]], output_png: Path) -> str:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - environment dependent
        return f"matplotlib not available; skipped PNG plot ({exc})"

    time_col = next((c for c in columns if c.startswith("Time (")), None)
    if time_col is None:
        return "No Time column found; skipped PNG plot."
    plot_cols = [c for c in columns if any(k in c for k in ["RMS velocity", "Average temperature", "Max. velocity", "Maximal temperature"])]
    if not plot_cols:
        return "No common numeric diagnostic columns found; skipped PNG plot."

    x = [safe_float(row.get(time_col, "")) for row in rows]
    valid_x = [v for v in x if v is not None]
    if len(valid_x) != len(rows):
        return "Time column is not fully numeric; skipped PNG plot."

    plt.figure(figsize=(8, 5))
    plotted = 0
    for col in plot_cols[:4]:
        y = [safe_float(row.get(col, "")) for row in rows]
        if any(v is None for v in y):
            continue
        plt.plot(valid_x, y, label=col)
        plotted += 1
    if plotted == 0:
        return "No fully numeric diagnostics available; skipped PNG plot."
    plt.xlabel(time_col)
    plt.ylabel("Value")
    plt.legend(fontsize="small")
    plt.tight_layout()
    plt.savefig(output_png, dpi=150)
    plt.close()
    return f"Wrote PNG plot: {output_png}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse an ASPECT statistics file into a compact CSV summary.")
    parser.add_argument("statistics_file", type=Path, help="Path to ASPECT statistics file")
    parser.add_argument("--csv", type=Path, help="Output CSV path")
    parser.add_argument("--png", type=Path, help="Optional PNG plot path")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args(argv)

    if not args.statistics_file.exists():
        print(f"error: statistics file not found: {args.statistics_file}", file=sys.stderr)
        return 2

    columns, rows = read_statistics(args.statistics_file)
    report = summarize(columns, rows)
    csv_path = args.csv or args.statistics_file.with_suffix(args.statistics_file.suffix + ".summary.csv")
    write_csv(csv_path, columns, rows, report["summary_columns"])
    report["csv"] = str(csv_path)

    if args.png:
        report["plot"] = maybe_plot(args.statistics_file, columns, rows, args.png)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"ASPECT statistics summary: {args.statistics_file}")
        print(f"Rows: {report['row_count']}, columns: {report['column_count']}")
        print(f"Wrote CSV summary: {csv_path}")
        if "plot" in report:
            print(report["plot"])
        print("Last row, common columns:")
        for key, value in report["last_row"].items():
            print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
