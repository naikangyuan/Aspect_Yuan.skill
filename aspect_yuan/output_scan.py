"""Discover ASPECT output files and variables."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


COMMON_FIELDS = ["temperature", "velocity", "pressure", "viscosity", "strain_rate", "strain rate", "composition", "density", "stress"]
FIELD_ALIASES = {
    "T": "temperature",
    "p": "pressure",
}


def _parse_pvd(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    try:
        root = ET.fromstring(path.read_text(errors="ignore"))
    except Exception:
        return entries
    for node in root.iter():
        if node.tag.endswith("DataSet"):
            entries.append({"time": node.attrib.get("timestep"), "file": str((path.parent / node.attrib.get("file", "")).resolve())})
    return entries


def _parse_vtu_fields(path: Path) -> list[str]:
    try:
        text = path.read_text(errors="ignore")[:300000]
    except Exception:
        return []
    return sorted(set(re.findall(r'<DataArray[^>]+Name="([^"]+)"', text)))


def scan_output(path: Path) -> dict[str, Any]:
    path = path.resolve()
    files = {
        "pvd": sorted(path.rglob("*.pvd")),
        "pvtu": sorted(path.rglob("*.pvtu")),
        "vtu": sorted(path.rglob("*.vtu")),
        "statistics": sorted([p for p in path.rglob("statistics") if p.is_file()]),
        "depth_average": sorted(path.rglob("*depth_average*")),
        "particles": sorted(path.rglob("*particle*")),
        "logs": sorted(path.rglob("*.log")) + sorted(path.rglob("log.txt")),
    }
    timesteps: list[dict[str, Any]] = []
    for pvd in files["pvd"]:
        timesteps.extend(_parse_pvd(pvd))
    fields: set[str] = set()
    for candidate in files["vtu"][:5] + files["pvtu"][:5]:
        fields.update(_parse_vtu_fields(candidate))
    common = sorted({FIELD_ALIASES.get(f, f) for f in fields if FIELD_ALIASES.get(f, f).lower() in COMMON_FIELDS or any(k in f.lower() for k in COMMON_FIELDS)})
    return {
        "output_dir": str(path),
        "counts": {k: len(v) for k, v in files.items()},
        "files": {k: [str(p) for p in v[:50]] for k, v in files.items()},
        "timesteps": timesteps,
        "num_timesteps": len(timesteps),
        "variables": sorted(fields),
        "common_geodynamics_variables": common,
        "variable_aliases": {k: v for k, v in FIELD_ALIASES.items() if k in fields},
        "status": "ok" if any(files.values()) else "empty",
    }


def format_scan(result: dict[str, Any]) -> str:
    lines = [f"ASPECT output scan: {result['output_dir']}", f"Status: {result['status']}"]
    for key, count in result["counts"].items():
        lines.append(f"- {key}: {count}")
    lines.append(f"- timesteps from PVD: {result['num_timesteps']}")
    if result["common_geodynamics_variables"]:
        lines.append("- common variables: " + ", ".join(result["common_geodynamics_variables"]))
    elif result["variables"]:
        lines.append("- variables: " + ", ".join(result["variables"][:20]))
    else:
        lines.append("- variables: none detected from VTU/PVTU headers")
    return "\n".join(lines)


def write_scan(result: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
