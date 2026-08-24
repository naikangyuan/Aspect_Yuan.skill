"""Unified aspect-yuan CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .beginner import run_beginner
from .compatibility import assess_compatibility, format_compat_check, format_compat_explain, format_policy_matrix, policy_matrix
from .config import load_config
from .env import discover_aspect, environment_check, format_aspect_candidates, format_environment_check
from .fingerprint import fingerprint_aspect, format_fingerprint
from .geospec import create_case_from_geospec, explain_geospec, format_geospec_validation, geospec_to_model_config, init_geospec, validate_geospec
from .models import create_model, list_models
from .output_scan import format_scan, scan_output, write_scan
from .plotting import plot_from_config
from .prm import validate_prm
from .reproduce import init_project, inspect_code, reproduction_status


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
    fingerprint = env_sub.add_parser("fingerprint", help="Detect and record the active ASPECT version/build profile.")
    fingerprint.add_argument("--aspect-bin", help="Explicit ASPECT executable.")
    fingerprint.add_argument("--search-root", action="append", type=Path, default=[], help="Additional directory to search.")
    fingerprint.add_argument("--output", type=Path, default=Path("aspect_profile.json"), help="JSON profile path. Default: aspect_profile.json")
    fingerprint.add_argument("--json", action="store_true", help="Print JSON instead of the human summary.")
    compat = sub.add_parser("compat", help="Explain ASPECT version support and PRM compatibility risk.")
    compat_sub = compat.add_subparsers(dest="compat_command", required=True)
    compat_matrix = compat_sub.add_parser("matrix", help="Show Aspect_Yuan ASPECT version support policy.")
    compat_matrix.add_argument("--json", action="store_true")
    compat_check = compat_sub.add_parser("check", help="Check a PRM against the detected ASPECT version without rewriting it.")
    compat_check.add_argument("prm", type=Path)
    compat_check.add_argument("--aspect-bin", help="Explicit ASPECT executable.")
    compat_check.add_argument("--search-root", action="append", type=Path, default=[], help="Additional directory to search.")
    compat_check.add_argument("--json", action="store_true")
    compat_explain = compat_sub.add_parser("explain", help="Explain ASPECT version risk for a PRM in geologist-facing language.")
    compat_explain.add_argument("prm", type=Path)
    compat_explain.add_argument("--aspect-bin", help="Explicit ASPECT executable.")
    compat_explain.add_argument("--search-root", action="append", type=Path, default=[], help="Additional directory to search.")
    compat_explain.add_argument("--json", action="store_true")
    geospec = sub.add_parser("geospec", help="Create, validate, and explain geology-first model intent files.")
    geospec_sub = geospec.add_subparsers(dest="geospec_command", required=True)
    geospec_init = geospec_sub.add_parser("init", help="Create a geology.yaml template for a supported model family.")
    geospec_init.add_argument("model_family", choices=["mantle_convection", "subduction", "rift"])
    geospec_init.add_argument("--output", type=Path, default=Path("geology.yaml"))
    geospec_validate = geospec_sub.add_parser("validate", help="Validate geology.yaml without generating or rewriting a PRM.")
    geospec_validate.add_argument("geology_yaml", type=Path)
    geospec_validate.add_argument("--json", action="store_true")
    geospec_explain = geospec_sub.add_parser("explain", help="Explain geology.yaml in geologist-facing language.")
    geospec_explain.add_argument("geology_yaml", type=Path)
    geospec_model_config = geospec_sub.add_parser("model-config", help="Convert geology.yaml to the existing starter model config.")
    geospec_model_config.add_argument("geology_yaml", type=Path)
    geospec_model_config.add_argument("--output", type=Path)
    geospec_create = geospec_sub.add_parser("create-case", help="Generate a starter ASPECT case from geology.yaml.")
    geospec_create.add_argument("geology_yaml", type=Path)
    geospec_create.add_argument("--output-dir", type=Path)
    reproduce = sub.add_parser("reproduce", help="Initialize and inspect ASPECT paper-reproduction projects.")
    reproduce_sub = reproduce.add_subparsers(dest="reproduce_command", required=True)
    reproduce_init = reproduce_sub.add_parser("init", help="Create a paper reproduction project.")
    reproduce_init.add_argument("project", type=Path)
    reproduce_inspect = reproduce_sub.add_parser("inspect", help="Inspect a downloaded paper code directory.")
    reproduce_inspect.add_argument("code_path", type=Path)
    reproduce_inspect.add_argument("--project", type=Path, help="Reproduction project directory. Defaults to current directory.")
    reproduce_inspect.add_argument("--json", action="store_true")
    reproduce_status_cmd = reproduce_sub.add_parser("status", help="Report reproduction level for a project.")
    reproduce_status_cmd.add_argument("project", type=Path, nargs="?", default=Path("."))
    reproduce_status_cmd.add_argument("--json", action="store_true")
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
            if args.env_command == "fingerprint":
                result = fingerprint_aspect(args.aspect_bin, args.search_root)
                args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                print(json.dumps(result, indent=2) if args.json else format_fingerprint(result))
                return 0
        if args.command == "compat":
            if args.compat_command == "matrix":
                print(json.dumps(policy_matrix(), indent=2) if args.json else format_policy_matrix())
                return 0
            if args.compat_command in {"check", "explain"}:
                profile = fingerprint_aspect(args.aspect_bin, args.search_root)
                result = assess_compatibility(args.prm, profile)
                if args.json:
                    print(json.dumps(result, indent=2))
                elif args.compat_command == "check":
                    print(format_compat_check(result))
                else:
                    print(format_compat_explain(result))
                return 1 if result["prm_syntax"] == "fail" else 0
        if args.command == "geospec":
            if args.geospec_command == "init":
                result = init_geospec(args.model_family, args.output)
                print(json.dumps(result, indent=2))
                return 0
            if args.geospec_command == "validate":
                issues = validate_geospec(args.geology_yaml)
                print(json.dumps(issues, indent=2) if args.json else format_geospec_validation(issues))
                return 1 if any(issue["level"] == "ERROR" for issue in issues) else 0
            if args.geospec_command == "explain":
                print(explain_geospec(args.geology_yaml))
                return 0
            if args.geospec_command == "model-config":
                config = geospec_to_model_config(args.geology_yaml)
                if args.output:
                    args.output.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
                    print(f"Wrote model config: {args.output}")
                else:
                    print(json.dumps(config, indent=2))
                return 0
            if args.geospec_command == "create-case":
                case_dir = create_case_from_geospec(args.geology_yaml, args.output_dir)
                print(f"Created ASPECT case from GeoSpec: {case_dir}")
                print(f"Run: cd {case_dir} && ./run.sh")
                return 0
        if args.command == "reproduce":
            if args.reproduce_command == "init":
                result = init_project(args.project)
                print(json.dumps(result, indent=2))
                return 0
            if args.reproduce_command == "inspect":
                result = inspect_code(args.code_path, args.project)
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Project: {result['project']}")
                    print(f"Reproduction YAML: {result['reproduction_yaml']}")
                    print(f"Report: {result['report']}")
                    print(f"Parameter inventory: {result['parameter_inventory']}")
                    print(f"Level: {result['reproduction_level']}")
                return 0
            if args.reproduce_command == "status":
                result = reproduction_status(args.project)
                print(json.dumps(result, indent=2) if args.json else "\n".join(f"{k}: {v}" for k, v in result.items()))
                return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
