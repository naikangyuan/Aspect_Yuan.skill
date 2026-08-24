#!/usr/bin/env python3
"""Rule-based eval checker for geologist-aspect-300.

This does not evaluate an LLM response. It checks that each eval case and
expected-output file names the wizard/reference/template/script assets that a
future agent should use.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_BY_CASE = {
    "mantle_convection_beginner.md": [
        "model_wizards/mantle_convection_wizard.md",
        "assets/prm_templates/beginner_2d_box_convection.prm",
        "cookbooks/convection-box/convection-box.prm",
        "scripts/aspect_prm_lint.py",
        "scripts/run_aspect_case.sh",
        "scripts/check_aspect_log.py",
        "scripts/make_case_report.py",
    ],
    "weak_zone_beginner.md": [
        "model_wizards/weak_zone_wizard.md",
        "assets/prm_templates/beginner_weak_zone.prm",
        "scripts/aspect_prm_lint.py",
    ],
    "subduction_beginner.md": [
        "model_wizards/subduction_wizard.md",
        "assets/prm_templates/beginner_subduction.prm",
        "cookbooks/kinematically_driven_subduction_2d/kinematically_driven_subduction_2d_case1.prm",
    ],
    "beginner_one_command_subduction.md": [
        "scripts/aspect-yuan beginner subduction",
        "model_wizards/subduction_wizard.md",
        "assets/prm_templates/beginner_subduction.prm",
        "scripts/run_aspect_case.sh",
        "scripts/check_aspect_log.py",
        "scripts/parse_aspect_statistics.py",
        "scripts/aspect-yuan postprocess scan",
        "scripts/aspect-yuan plot",
    ],
    "geospec_subduction.md": [
        "scripts/aspect-yuan geospec init subduction",
        "scripts/aspect-yuan geospec validate",
        "scripts/aspect-yuan geospec explain",
        "scripts/aspect-yuan geospec create-case",
        "examples/geospec/subduction_geology.yaml",
        "scripts/aspect-yuan env fingerprint",
        "scripts/aspect-yuan compat check",
    ],
    "rift_beginner.md": [
        "model_wizards/rift_wizard.md",
        "assets/prm_templates/beginner_rift.prm",
        "cookbooks/continental_extension/continental_extension.prm",
    ],
    "plugin_weakening_material.md": [
        "references/plugins_for_geologists.md",
        "references/aspect300_plugin_interfaces.md",
        "assets/plugin_templates/material_model_minimal.cc",
        "scripts/build_aspect_plugin.sh",
        "scripts/explain_plugin_request.py",
    ],
    "log_failure_triage.md": [
        "scripts/check_aspect_log.py",
        "scripts/aspect_prm_lint.py",
    ],
    "paper_reproduction_version.md": [
        "references/paper_reproduction_first.md",
        "references/aspect_version_strategy.md",
        "references/aspect_installation_matrix.md",
        "scripts/detect_aspect_reproduction_context.py",
        "scripts/install_aspect_version.sh",
        "scripts/run_aspect_case.sh",
        "scripts/check_aspect_log.py",
    ],
    "deep_shallow_coupling_version.md": [
        "references/model_family_version_map.md",
        "references/aspect_version_strategy.md",
        "references/aspect300_case_map.md",
        "cookbooks/global_regional_coupling/global_regional_coupling.prm",
        "scripts/plan_aspect_version.py",
        "scripts/aspect_prm_lint.py",
        "scripts/run_aspect_case.sh",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run rule-based skill eval file checks.")
    parser.add_argument("--list", action="store_true", help="List eval cases and exit")
    args = parser.parse_args()

    cases_dir = ROOT / "evals" / "test_cases"
    expected_dir = ROOT / "evals" / "expected_outputs"
    cases = sorted(cases_dir.glob("*.md"))

    if args.list:
        for case in cases:
            print(case.name)
        return 0

    failures: list[str] = []
    for case in cases:
        expected = expected_dir / case.name
        if not expected.exists():
            failures.append(f"{case.name}: missing expected output file")
            continue
        text = case.read_text(errors="ignore") + "\n" + expected.read_text(errors="ignore")
        for required in REQUIRED_BY_CASE.get(case.name, []):
            if required not in text:
                failures.append(f"{case.name}: missing required asset mention `{required}`")

    unknown = [case.name for case in cases if case.name not in REQUIRED_BY_CASE]
    for name in unknown:
        failures.append(f"{name}: no REQUIRED_BY_CASE rule defined")

    if failures:
        print("Skill eval checks failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Skill eval checks passed for {len(cases)} case(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
