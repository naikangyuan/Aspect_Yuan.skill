"""One-command beginner workflows for geologist-facing ASPECT lessons."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from .config import dump_config
from .models import MODEL_SPECS, create_model
from .output_scan import scan_output, write_scan
from .plotting import plot_from_config
from .prm import validate_prm


BEGINNER_DEFAULTS: dict[str, dict[str, Any]] = {
    "subduction": {
        "model": {"type": "subduction", "case_name": "beginner_subduction"},
        "geometry": {"width_km": 3000, "depth_km": 670},
        "subduction": {"style": "kinematically_driven", "convergence_rate_cm_per_yr": 5.0},
        "output": {"first_plot": "composition"},
    },
    "mantle_convection": {
        "model": {"type": "mantle_convection", "case_name": "beginner_mantle_convection"},
        "geometry": {"width_km": 2900, "depth_km": 660},
        "thermal": {"surface_temperature": 273, "mantle_temperature": 1573},
        "output": {"first_plot": "temperature"},
    },
    "rift": {
        "model": {"type": "rift", "case_name": "beginner_rift"},
        "geometry": {"width_km": 2000, "depth_km": 660},
        "extension": {"style": "continental_extension", "extension_rate_cm_per_yr": 2.0},
        "output": {"first_plot": "viscosity"},
    },
}


PLOT_VARIABLES = {
    "subduction": "crust_SP",
    "mantle_convection": "temperature",
    "rift": "viscosity",
}


def run_beginner(model_type: str, output_dir: Path | None, run: bool, aspect_bin: str | None) -> dict[str, Any]:
    if model_type not in BEGINNER_DEFAULTS:
        raise ValueError(f"Unsupported beginner model: {model_type}. Supported: {', '.join(sorted(BEGINNER_DEFAULTS))}")
    case_dir = (output_dir or Path(BEGINNER_DEFAULTS[model_type]["model"]["case_name"])).resolve()
    config = json.loads(json.dumps(BEGINNER_DEFAULTS[model_type]))
    case_dir = create_model(config, case_dir)
    validation = validate_prm(case_dir / "case.prm")
    result: dict[str, Any] = {
        "model": model_type,
        "case_dir": str(case_dir),
        "case_prm": str(case_dir / "case.prm"),
        "run_script": str(case_dir / "run.sh"),
        "readme": str(case_dir / "README.md"),
        "validation": validation,
        "ran_aspect": False,
        "run_log": None,
        "scan": None,
        "plot": None,
        "beginner_report": str(case_dir / "beginner_report.md"),
    }
    plot_config_path = _write_plot_config(case_dir, model_type)
    result["plot_config"] = str(plot_config_path)
    if run:
        result.update(_run_aspect(case_dir, aspect_bin))
        output_dir_path = case_dir / "output"
        if output_dir_path.exists():
            scan = scan_output(output_dir_path)
            write_scan(scan, case_dir / "output_scan.json")
            result["scan"] = scan
            if scan["status"] == "ok":
                try:
                    result["plot"] = plot_from_config(plot_config_path)
                except Exception as exc:
                    result["plot_error"] = str(exc)
    _write_beginner_report(case_dir, model_type, result)
    return result


def _run_aspect(case_dir: Path, aspect_bin: str | None) -> dict[str, Any]:
    binary = aspect_bin or os.environ.get("ASPECT_BIN", "aspect")
    log = case_dir / "run.log"
    with log.open("w", encoding="utf-8") as handle:
        proc = subprocess.run([binary, str(case_dir / "case.prm")], cwd=case_dir, stdout=handle, stderr=subprocess.STDOUT, text=True, check=False)
    return {"ran_aspect": True, "aspect_bin": binary, "run_log": str(log), "exit_status": proc.returncode}


def _write_plot_config(case_dir: Path, model_type: str) -> Path:
    variable = PLOT_VARIABLES[model_type]
    preset = "geodynamics_temperature" if variable == "temperature" else "geodynamics_viscosity"
    if model_type == "subduction":
        preset = "composition"
    config = {
        "input": str(case_dir / "output"),
        "figure": {"type": "field"},
        "field": {"variable": variable},
        "colormap": {"preset": preset},
        "journal": {"preset": "GRL"},
        "output": {"prefix": str(case_dir / f"beginner_{model_type}_{variable}"), "formats": ["png", "pdf", "svg", "tiff"]},
    }
    path = case_dir / "beginner_figure.yaml"
    dump_config(config, path)
    return path


def _write_beginner_report(case_dir: Path, model_type: str, result: dict[str, Any]) -> None:
    spec = MODEL_SPECS[model_type]
    lines = [
        f"# Beginner ASPECT Report: {model_type}",
        "",
        "## Geological Meaning",
        "",
        spec.description + ".",
        "",
        "This is a teaching starter model. Do not treat it as a research result until the geological assumptions, ASPECT version, resolution, log, statistics, and output fields have been checked.",
        "",
        "## Files",
        "",
        f"- case PRM: `{Path(result['case_prm']).name}`",
        f"- run helper: `{Path(result['run_script']).name}`",
        "- output directory: `output/`",
        "- first figure config: `beginner_figure.yaml`",
        "",
        "## Validation",
        "",
    ]
    for issue in result["validation"]:
        lines.append(f"- {issue['level']}: {issue['item']} - {issue['message']}")
    lines.extend(["", "## Run Status", ""])
    if result.get("ran_aspect"):
        lines.append(f"- ASPECT was run with exit status `{result.get('exit_status')}`.")
        lines.append(f"- Run log: `{Path(str(result.get('run_log'))).name}`")
    else:
        lines.append("- ASPECT was not run. Use `./run.sh` or rerun with `--run`.")
    if result.get("scan"):
        scan = result["scan"]
        lines.extend([
            "",
            "## Output Scan",
            "",
            f"- status: `{scan['status']}`",
            f"- timesteps: `{scan['num_timesteps']}`",
            f"- common variables: `{', '.join(scan['common_geodynamics_variables'])}`",
        ])
    if result.get("plot"):
        plot = result["plot"]
        rendered = ", ".join(Path(p).name for p in plot.get("rendered_files", []))
        lines.extend(["", "## First Figure", "", f"- rendered files: `{rendered}`"])
    elif result.get("plot_error"):
        lines.extend(["", "## First Figure", "", f"- plot error: `{result['plot_error']}`"])
    lines.extend([
        "",
        "## Do Not Silently Change",
        "",
        "- geometry and dimension",
        "- boundary velocity and boundary names",
        "- material fields and rheology",
        "- temperature structure",
        "- gravity direction",
        "- model duration and output cadence",
    ])
    (case_dir / "beginner_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
