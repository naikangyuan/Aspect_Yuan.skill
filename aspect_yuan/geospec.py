"""Geology-first model intent specifications."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import dump_config, load_config
from .models import create_model


SUPPORTED_FAMILIES = {"mantle_convection", "subduction", "rift"}


def default_geospec(model_family: str) -> dict[str, Any]:
    if model_family not in SUPPORTED_FAMILIES:
        raise ValueError(f"Unsupported GeoSpec model family: {model_family}. Supported: {', '.join(sorted(SUPPORTED_FAMILIES))}")
    common = {
        "schema_version": "1",
        "project": {"name": f"{model_family}_geospec_case"},
        "scientific_question": "Describe the geological question in one or two sentences.",
        "model_family": model_family,
        "aspect": {
            "version_policy": "fingerprint-local-first",
            "paper_version": None,
            "local_version": None,
            "migration_policy": "do-not-migrate-automatically",
        },
        "geometry": {"dimension": 2, "width_km": 3000, "depth_km": 660},
        "mesh": {"starter_resolution": "coarse-teaching", "global_refinement": None, "adaptive_refinement": None},
        "thermal": {"surface_temperature_K": 273, "mantle_temperature_K": 1573},
        "rheology": {"intent": "teaching starter rheology; verify before research use", "uses_plasticity": False},
        "materials": {"composition_fields": "minimal fields needed for the selected teaching model"},
        "boundary_conditions": {"velocity_intent": "state geological motion explicitly", "temperature_intent": "surface cold, mantle hot"},
        "outputs": {"first_fields_to_check": "temperature, velocity, viscosity, composition when present"},
        "scientific_guardrails": {
            "do_not_silently_change": "geometry, boundary velocities, rheology, composition fields, temperature, gravity, dimension, or timescale"
        },
    }
    if model_family == "subduction":
        common.update({
            "project": {"name": "subduction_geospec_case"},
            "scientific_question": "How does a cold oceanic plate descend into the mantle in a simple teaching-scale subduction setup?",
            "geometry": {"dimension": 2, "width_km": 3000, "depth_km": 670},
            "plate": {"age_Ma": 80, "incoming_plate_thickness_km": 100},
            "subduction": {"style": "kinematically_driven", "slab_dip_deg": 30, "convergence_rate_cm_per_yr": 5.0},
            "materials": {"composition_fields": "slab crust and mantle markers used for teaching visualization"},
            "outputs": {"first_fields_to_check": "composition, temperature, velocity, viscosity, strain_rate"},
        })
    elif model_family == "mantle_convection":
        common.update({
            "project": {"name": "mantle_convection_geospec_case"},
            "scientific_question": "How does a hot mantle layer convect beneath a cold surface in a simple 2-D box?",
            "geometry": {"dimension": 2, "width_km": 2900, "depth_km": 660},
            "convection": {"style": "thermal_bottom_heated", "rayleigh_number_intent": "teaching scale; verify dimensional parameters before research use"},
            "outputs": {"first_fields_to_check": "temperature, velocity, viscosity"},
        })
    elif model_family == "rift":
        common.update({
            "project": {"name": "rift_geospec_case"},
            "scientific_question": "How does continental lithosphere thin and localize deformation during extension?",
            "geometry": {"dimension": 2, "width_km": 2000, "depth_km": 660},
            "extension": {"style": "continental_extension", "extension_rate_cm_per_yr": 2.0},
            "rheology": {"intent": "viscous starter rheology; plastic weakening requires explicit research design", "uses_plasticity": False},
            "outputs": {"first_fields_to_check": "viscosity, strain_rate, temperature, velocity"},
        })
    return common


def init_geospec(model_family: str, output: Path) -> dict[str, Any]:
    spec = default_geospec(model_family)
    output.parent.mkdir(parents=True, exist_ok=True)
    dump_config(spec, output)
    return {"geology_yaml": str(output.resolve()), "model_family": model_family}


def validate_geospec(path: Path) -> list[dict[str, str]]:
    spec = load_config(path)
    issues: list[dict[str, str]] = []
    family = str(spec.get("model_family", "")).strip()
    if not family:
        issues.append(_issue("ERROR", "model_family", "Missing model_family. Use one of: " + ", ".join(sorted(SUPPORTED_FAMILIES))))
    elif family not in SUPPORTED_FAMILIES:
        issues.append(_issue("ERROR", "model_family", f"Unsupported model_family `{family}`. Supported: {', '.join(sorted(SUPPORTED_FAMILIES))}"))
    if not str(spec.get("scientific_question", "")).strip():
        issues.append(_issue("ERROR", "scientific_question", "State the geological question before generating a model."))
    _check_geometry(spec, issues)
    _check_thermal(spec, issues)
    _check_family_specific(spec, family, issues)
    aspect = spec.get("aspect", {}) if isinstance(spec.get("aspect"), dict) else {}
    if aspect.get("migration_policy") not in {None, "do-not-migrate-automatically"}:
        issues.append(_issue("WARNING", "aspect.migration_policy", "GeoSpec should not request automatic ASPECT version migration in v0.4.2."))
    if not issues:
        issues.append(_issue("PASS", "geology.yaml", "GeoSpec has the minimum geological intent needed for a starter model."))
    return issues


def explain_geospec(path: Path) -> str:
    spec = load_config(path)
    family = str(spec.get("model_family", "unknown"))
    question = spec.get("scientific_question") or "not stated"
    geometry = spec.get("geometry", {}) if isinstance(spec.get("geometry"), dict) else {}
    thermal = spec.get("thermal", {}) if isinstance(spec.get("thermal"), dict) else {}
    outputs = spec.get("outputs", {}) if isinstance(spec.get("outputs"), dict) else {}
    lines = [
        "GeoSpec geological interpretation",
        "",
        f"- Geological question: {question}",
        f"- Model family: {family}",
        f"- Geometry: {geometry.get('dimension', 'unknown')}-D, width {geometry.get('width_km', 'unknown')} km, depth {geometry.get('depth_km', 'unknown')} km.",
        f"- Thermal intent: surface {thermal.get('surface_temperature_K', 'unknown')} K, mantle {thermal.get('mantle_temperature_K', 'unknown')} K.",
    ]
    if family == "subduction":
        subduction = spec.get("subduction", {}) if isinstance(spec.get("subduction"), dict) else {}
        lines.append(f"- Subduction intent: {subduction.get('style', 'unknown')} with convergence {subduction.get('convergence_rate_cm_per_yr', 'unknown')} cm/yr and slab dip {subduction.get('slab_dip_deg', 'unknown')} degrees.")
    elif family == "rift":
        extension = spec.get("extension", {}) if isinstance(spec.get("extension"), dict) else {}
        lines.append(f"- Rift intent: {extension.get('style', 'unknown')} with extension rate {extension.get('extension_rate_cm_per_yr', 'unknown')} cm/yr.")
    elif family == "mantle_convection":
        convection = spec.get("convection", {}) if isinstance(spec.get("convection"), dict) else {}
        lines.append(f"- Convection intent: {convection.get('style', 'thermal convection starter')}.")
    lines.extend([
        f"- First outputs to check: {outputs.get('first_fields_to_check', 'temperature, velocity, viscosity, composition when present')}.",
        "",
        "ASPECT implementation path",
        "",
        "1. Fingerprint the ASPECT binary before running or comparing versions.",
        "2. Convert this GeoSpec to the existing starter model config only for a teaching case.",
        "3. Validate the generated PRM and run a short smoke test.",
        "4. Do not silently change geometry, boundary conditions, rheology, temperature, composition, dimension, or timescale.",
    ])
    return "\n".join(lines)


def geospec_to_model_config(path: Path) -> dict[str, Any]:
    spec = load_config(path)
    errors = [issue for issue in validate_geospec(path) if issue["level"] == "ERROR"]
    if errors:
        raise ValueError("GeoSpec has errors: " + "; ".join(issue["message"] for issue in errors))
    family = str(spec["model_family"])
    project = spec.get("project", {}) if isinstance(spec.get("project"), dict) else {}
    geometry = spec.get("geometry", {}) if isinstance(spec.get("geometry"), dict) else {}
    thermal = spec.get("thermal", {}) if isinstance(spec.get("thermal"), dict) else {}
    config: dict[str, Any] = {
        "model": {"type": family, "case_name": project.get("name") or f"{family}_geospec_case"},
        "geometry": {"width_km": geometry.get("width_km"), "depth_km": geometry.get("depth_km")},
        "thermal": {
            "surface_temperature": thermal.get("surface_temperature_K"),
            "mantle_temperature": thermal.get("mantle_temperature_K"),
        },
        "geospec": {"source": str(path), "scientific_question": spec.get("scientific_question")},
    }
    if family == "subduction":
        subduction = spec.get("subduction", {}) if isinstance(spec.get("subduction"), dict) else {}
        config["subduction"] = {
            "style": subduction.get("style", "kinematically_driven"),
            "convergence_rate_cm_per_yr": subduction.get("convergence_rate_cm_per_yr"),
            "slab_dip_deg": subduction.get("slab_dip_deg"),
        }
    elif family == "rift":
        extension = spec.get("extension", {}) if isinstance(spec.get("extension"), dict) else {}
        config["extension"] = {
            "style": extension.get("style", "continental_extension"),
            "extension_rate_cm_per_yr": extension.get("extension_rate_cm_per_yr"),
        }
    return _drop_none(config)


def create_case_from_geospec(path: Path, output_dir: Path | None = None) -> Path:
    config = geospec_to_model_config(path)
    case_dir = create_model(config, output_dir)
    explanation = explain_geospec(path)
    (case_dir / "GEOSPEC_EXPLANATION.md").write_text(explanation + "\n", encoding="utf-8")
    return case_dir


def format_geospec_validation(issues: list[dict[str, str]]) -> str:
    return "\n".join(f"{issue['level']}: {issue['item']} - {issue['message']}" for issue in issues)


def _check_geometry(spec: dict[str, Any], issues: list[dict[str, str]]) -> None:
    geometry = spec.get("geometry")
    if not isinstance(geometry, dict):
        issues.append(_issue("ERROR", "geometry", "Missing geometry block."))
        return
    dimension = geometry.get("dimension")
    if dimension not in {2, 3, "2", "3"}:
        issues.append(_issue("ERROR", "geometry.dimension", "Dimension should be 2 or 3 and must be a deliberate geological simplification."))
    for key in ("width_km", "depth_km"):
        value = geometry.get(key)
        if not isinstance(value, (int, float)) or value <= 0:
            issues.append(_issue("ERROR", f"geometry.{key}", "Use a positive number in km."))
    if isinstance(geometry.get("depth_km"), (int, float)) and geometry["depth_km"] > 3000:
        issues.append(_issue("WARNING", "geometry.depth_km", "Depth exceeds whole-mantle scale; check whether the geometry is intended."))


def _check_thermal(spec: dict[str, Any], issues: list[dict[str, str]]) -> None:
    thermal = spec.get("thermal")
    if not isinstance(thermal, dict):
        issues.append(_issue("ERROR", "thermal", "Missing thermal intent."))
        return
    surface = thermal.get("surface_temperature_K")
    mantle = thermal.get("mantle_temperature_K")
    if not isinstance(surface, (int, float)) or not isinstance(mantle, (int, float)):
        issues.append(_issue("ERROR", "thermal", "surface_temperature_K and mantle_temperature_K must be numeric Kelvin values."))
        return
    if surface < 150 or surface > 400:
        issues.append(_issue("WARNING", "thermal.surface_temperature_K", "Surface temperature is unusual for a starter lithosphere/mantle model."))
    if mantle < 1000 or mantle > 2200:
        issues.append(_issue("WARNING", "thermal.mantle_temperature_K", "Mantle temperature is unusual; verify units and geological intent."))
    if mantle <= surface:
        issues.append(_issue("ERROR", "thermal", "Mantle temperature should be hotter than surface temperature for these starter models."))


def _check_family_specific(spec: dict[str, Any], family: str, issues: list[dict[str, str]]) -> None:
    if family == "subduction":
        subduction = spec.get("subduction")
        if not isinstance(subduction, dict):
            issues.append(_issue("ERROR", "subduction", "Missing subduction block."))
            return
        rate = subduction.get("convergence_rate_cm_per_yr")
        dip = subduction.get("slab_dip_deg")
        if not isinstance(rate, (int, float)) or rate <= 0:
            issues.append(_issue("ERROR", "subduction.convergence_rate_cm_per_yr", "Use a positive convergence rate."))
        if not isinstance(dip, (int, float)) or not 5 <= dip <= 80:
            issues.append(_issue("WARNING", "subduction.slab_dip_deg", "Slab dip is outside a typical teaching range; verify geological intent."))
    elif family == "rift":
        extension = spec.get("extension")
        if not isinstance(extension, dict):
            issues.append(_issue("ERROR", "extension", "Missing extension block."))
            return
        rate = extension.get("extension_rate_cm_per_yr")
        if not isinstance(rate, (int, float)) or rate <= 0:
            issues.append(_issue("ERROR", "extension.extension_rate_cm_per_yr", "Use a positive extension rate."))


def _issue(level: str, item: str, message: str) -> dict[str, str]:
    return {"level": level, "item": item, "message": message}


def _drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _drop_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [_drop_none(item) for item in value if item is not None]
    return value
