#!/usr/bin/env python3
"""Plot ASPECT statistics time histories with pandas/matplotlib."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from parse_aspect_statistics import read_statistics, safe_float


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot time histories from an ASPECT statistics file.")
    parser.add_argument("statistics_file", type=Path, help="Path to ASPECT statistics file")
    parser.add_argument("--columns", nargs="*", help="Column names to plot. Defaults to common diagnostics.")
    parser.add_argument("--output", type=Path, default=Path("statistics-history.png"), help="Output PNG path")
    args = parser.parse_args()

    try:
        import pandas as pd
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"error: pandas and matplotlib are required for plotting: {exc}", file=sys.stderr)
        print("Install them in your ASPECT analysis environment, or use parse_aspect_statistics.py for CSV output.", file=sys.stderr)
        return 2

    if not args.statistics_file.exists():
        print(f"error: statistics file not found: {args.statistics_file}", file=sys.stderr)
        return 2

    columns, rows = read_statistics(args.statistics_file)
    if not rows:
        print("error: no data rows found in statistics file", file=sys.stderr)
        return 1

    time_col = next((c for c in columns if c.startswith("Time (")), None)
    if time_col is None:
        print("error: no Time column found in statistics file", file=sys.stderr)
        return 1

    default_cols = [c for c in columns if any(k in c for k in ["RMS velocity", "Average temperature", "Max. velocity", "Maximal temperature"])]
    plot_cols = args.columns or default_cols
    if not plot_cols:
        print("error: no plot columns requested and no common diagnostics found", file=sys.stderr)
        return 1

    data = {}
    for col in [time_col] + plot_cols:
        if col not in columns:
            print(f"warning: column not found, skipping: {col}", file=sys.stderr)
            continue
        values = [safe_float(row.get(col, "")) for row in rows]
        if any(v is None for v in values):
            print(f"warning: column is not numeric, skipping: {col}", file=sys.stderr)
            continue
        data[col] = values

    if time_col not in data or len(data) <= 1:
        print("error: no numeric columns available to plot", file=sys.stderr)
        return 1

    df = pd.DataFrame(data)
    ax = df.plot(x=time_col, y=[c for c in data if c != time_col], figsize=(9, 5))
    ax.set_xlabel(time_col)
    ax.set_ylabel("Value")
    ax.grid(True, alpha=0.3)
    ax.figure.tight_layout()
    ax.figure.savefig(args.output, dpi=150)
    print(f"Wrote plot: {args.output}")
    print("Geologist note: use this plot to check whether the run reached a stable or interpretable evolution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
