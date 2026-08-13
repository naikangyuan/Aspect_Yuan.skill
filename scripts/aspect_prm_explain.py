#!/usr/bin/env python3
"""Explain ASPECT .prm subsection paths in geologist-facing language."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


SUBSECTION_RE = re.compile(r"^\s*subsection\s+(.+?)\s*(?:#.*)?$")
END_RE = re.compile(r"^\s*end\s*(?:#.*)?$")
SET_RE = re.compile(r"^\s*set\s+(.+?)\s*=\s*(.*?)\s*(?:#.*)?$")


MEANINGS = {
    "Geometry model": "Defines the shape and coordinate system of the modeled geological region.",
    "Geometry model > Box": "Sets Cartesian box dimensions and boundary names.",
    "Geometry model > Spherical shell": "Sets shell radii and spherical geometry for mantle or planetary models.",
    "Geometry model > Chunk": "Sets a regional spherical chunk, useful for subduction or regional mantle flow.",
    "Gravity model": "Defines the direction and magnitude of buoyancy forcing.",
    "Boundary velocity model": "Defines imposed plate, wall, basal, or free-slip velocity behavior.",
    "Boundary velocity model > Function": "Uses mathematical expressions for velocity boundary conditions.",
    "Boundary velocity model > Ascii data model": "Uses external gridded velocity data for boundary motion.",
    "Boundary temperature model": "Defines thermal conditions imposed on model boundaries.",
    "Boundary temperature model > Function": "Uses mathematical expressions for thermal boundary values.",
    "Initial temperature model": "Defines the starting geotherm, plume, slab, or mantle thermal state.",
    "Initial temperature model > Function": "Uses mathematical expressions for the initial temperature field.",
    "Initial temperature model > Adiabatic": "Starts from an adiabatic thermal profile.",
    "Initial temperature model > Ascii data model": "Imports initial temperature from data files.",
    "Compositional fields": "Declares tracked geological units or compositional tracers.",
    "Initial composition model": "Places geological units or compositional fields at model start.",
    "Initial composition model > Function": "Uses mathematical expressions to define initial rock domains.",
    "Initial composition model > Ascii data model": "Imports initial composition from data files.",
    "Material model": "Defines density, viscosity, rheology, thermal properties, yielding, melt, or phase behavior.",
    "Material model > Simple model": "Uses simple density, viscosity, and thermal property relationships.",
    "Material model > Visco Plastic": "Defines viscous/plastic rheology, often for lithosphere deformation and weak zones.",
    "Material model > Viscoelastic": "Defines elastic plus viscous behavior for stress relaxation or flexure.",
    "Material model > Multicomponent": "Defines material properties that vary by compositional field.",
    "Material model > Melt global": "Defines material behavior for melt transport models.",
    "Heating model": "Defines heat sources such as shear, adiabatic, radiogenic, latent, or melt-related heating.",
    "Mesh refinement": "Controls where ASPECT adds resolution for geological gradients and interfaces.",
    "Mesh deformation": "Controls moving mesh or free-surface behavior.",
    "Free surface": "Controls free-surface stabilization and surface motion behavior.",
    "Particles": "Configures Lagrangian particles used as markers or property carriers.",
    "Particles > Generator": "Controls initial particle placement.",
    "Postprocess": "Selects diagnostics and outputs used to interpret the geological run.",
    "Postprocess > Visualization": "Selects graphical fields such as temperature, composition, viscosity, stress, and strain rate.",
    "Solver parameters": "Controls nonlinear and linear solver behavior without directly defining the geology.",
    "Solver parameters > Stokes solver parameters": "Controls the Stokes flow solve.",
    "Discretization": "Controls finite-element polynomial degrees and field discretization.",
    "Stabilization parameters": "Controls numerical stabilization for advection and related equations.",
    "Termination criteria": "Defines when the run should stop.",
    "Checkpointing": "Controls restart files.",
    "Melt settings": "Controls whether melt transport and melt-related equations are active.",
}


def load_reference_table(skill_root: Path | None) -> dict[str, str]:
    """Load subsection meanings from the bundled markdown when available.

    The built-in dictionary is authoritative enough for script execution. This
    loader extends it from table rows in references/prm_section_meaning.md when
    the file is present, without inventing meanings for unknown sections.
    """

    meanings = dict(MEANINGS)
    if not skill_root:
        return meanings
    ref = skill_root / "references" / "prm_section_meaning.md"
    if not ref.exists():
        return meanings
    for line in ref.read_text(errors="ignore").splitlines():
        if not line.startswith("|") or "---" in line or "Geological concept" in line:
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 3:
            continue
        concept, subsection = parts[0], parts[1].strip("`")
        if subsection and subsection not in meanings:
            meanings[subsection] = f"Related geological concept: {concept}."
    return meanings


def parse(path: Path) -> list[dict[str, Any]]:
    stack: list[str] = []
    sections: list[dict[str, Any]] = []
    current_by_path: dict[str, dict[str, Any]] = {}
    for line_no, line in enumerate(path.read_text(errors="ignore").splitlines(), start=1):
        subsection = SUBSECTION_RE.match(line)
        if subsection:
            stack.append(subsection.group(1).strip())
            section_path = " > ".join(stack)
            item = {"line": line_no, "path": section_path, "sets": []}
            sections.append(item)
            current_by_path[section_path] = item
            continue
        if END_RE.match(line):
            if stack:
                stack.pop()
            continue
        setting = SET_RE.match(line)
        if setting and stack:
            section_path = " > ".join(stack)
            current_by_path.setdefault(section_path, {"line": line_no, "path": section_path, "sets": []})
            current_by_path[section_path]["sets"].append(
                {"line": line_no, "parameter": setting.group(1).strip(), "value": setting.group(2).strip()}
            )
    return sections


def explain_path(path: str, meanings: dict[str, str]) -> str:
    if path in meanings:
        return meanings[path]
    parts = path.split(" > ")
    for i in range(len(parts) - 1, 0, -1):
        candidate = " > ".join(parts[:i])
        if candidate in meanings:
            return meanings[candidate]
    if parts[-1] in meanings:
        return meanings[parts[-1]]
    return "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explain ASPECT .prm subsections in geological language.")
    parser.add_argument("prm_file", type=Path, help="Path to an ASPECT .prm file")
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to geologist-aspect-300 skill root",
    )
    args = parser.parse_args(argv)

    if not args.prm_file.exists():
        print(f"error: file not found: {args.prm_file}", file=sys.stderr)
        return 2

    meanings = load_reference_table(args.skill_root)
    sections = parse(args.prm_file)

    print(f"ASPECT PRM geological explanation: {args.prm_file}")
    print("Unknown means this script has no bundled geological meaning for that subsection; verify with local ASPECT docs or examples.")
    print()

    for section in sections:
        meaning = explain_path(section["path"], meanings)
        print(f"- line {section['line']}: {section['path']}")
        print(f"  Geological meaning: {meaning}")
        if section["sets"]:
            preview = section["sets"][:6]
            params = ", ".join(f"{item['parameter']} = {item['value']}" for item in preview)
            if len(section["sets"]) > len(preview):
                params += f", ... ({len(section['sets']) - len(preview)} more)"
            print(f"  Parameters here: {params}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
