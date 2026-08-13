"""Unified aspect-yuan CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .beginner import run_beginner
from .config import load_config
from .env import discover_aspect, environment_check, format_aspect_candidates, format_environment_check
from .models import create_model, list_models
from .output_scan import format_scan, scan_output, write_scan
from .plotting import plot_from_config
from .prm import validate_prm


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aspect-yuan", description="Geologist-facing ASPECT model, output, and figure tools.")
    sub = parser.add_subparsers(dest="command", required=True)
    beginner = sub.add_parser("beginner", help="Run a one-command beginner ASPECT lesson.")
    beginner.add_argument("model", choices=["subduction", "mantle_convection", "rift"], help="Beginner model type.")
    beginner.add_argument("--output-dir", type=Path)
    beginner.add_argument("--run", action="store_true", help="Run ASPECT immediately after generating the case.")
    beginner.add_argument("--aspect-bin", help="ASPECT executable for --run. Defaults to ASPECT_BIN or aspect.")
    model = sub.add_parser("model", help="Create and validate ASPECT starter models.")
    model_sub = model.add_subparsers(dest="model_command", required=True)
    model_sub.add_parser("list", help="List supported model types.")
    create = model_sub.add_parser("create", help="Create a model case from YAML/JSON config.")
    create.add_argument("config", type=Path)
    create.add_argument("--output-dir", type=Path)
    validate = model_sub.add_parser("validate", help="Validate starter-model PRM structure and common geoscience risks.")
    validate.add_argument("prm", type=Path)
    validate.add_argument("--json", action="store_true")
    post = sub.add_parser("postprocess", help="Postprocess ASPECT outputs.")
    post_sub = post.add_subparsers(dest="post_command", required=True)
    scan = post_sub.add_parser("scan", help="Scan ASPECT output directory.")
    scan.add_argument("output_dir", type=Path)
    scan.add_argument("--json", action="store_true")
    scan.add_argument("--output", type=Path)
    plot = sub.add_parser("plot", help="Create publication-oriented figures from YAML/JSON config.")
    plot.add_argument("config", type=Path)
    env = sub.add_parser("env", help="Discover ASPECT and common local runtime tools.")
    env_sub = env.add_subparsers(dest="env_command", required=True)
    find_aspect = env_sub.add_parser("find-aspect", help="Find ASPECT executables without user-specific paths.")
    find_aspect.add_argument("--search-root", action="append", type=Path, default=[], help="Additional directory to search.")
    find_aspect.add_argument("--json", action="store_true")
    check = env_sub.add_parser("check", help="Check ASPECT, Python, MPI, Docker, and plotting-related tools.")
    check.add_argument("--search-root", action="append", type=Path, default=[], help="Additional directory to search.")
    check.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "beginner":
            print(json.dumps(run_beginner(args.model, args.output_dir, args.run, args.aspect_bin), indent=2))
            return 0
        if args.command == "model":
            if args.model_command == "list":
                print(json.dumps(list_models(), indent=2))
                return 0
            if args.model_command == "create":
                cfg = load_config(args.config)
                case_dir = create_model(cfg, args.output_dir)
                print(f"Created ASPECT case: {case_dir}")
                print(f"Run: cd {case_dir} && ./run.sh")
                return 0
            if args.model_command == "validate":
                issues = validate_prm(args.prm)
                print(json.dumps(issues, indent=2) if args.json else "\n".join(f"{i['level']}: {i['item']} - {i['message']}" for i in issues))
                return 1 if any(i["level"] == "ERROR" for i in issues) else 0
        if args.command == "postprocess" and args.post_command == "scan":
            result = scan_output(args.output_dir)
            if args.output:
                write_scan(result, args.output)
            print(json.dumps(result, indent=2) if args.json else format_scan(result))
            return 0
        if args.command == "plot":
            print(json.dumps(plot_from_config(args.config), indent=2))
            return 0
        if args.command == "env":
            if args.env_command == "find-aspect":
                candidates = discover_aspect(extra_roots=args.search_root)
                print(json.dumps([c.to_dict() for c in candidates], indent=2) if args.json else format_aspect_candidates(candidates))
                return 0 if candidates else 1
            if args.env_command == "check":
                result = environment_check(extra_roots=args.search_root)
                print(json.dumps(result, indent=2) if args.json else format_environment_check(result))
                return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
