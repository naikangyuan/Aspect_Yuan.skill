"""Scientific colormap presets for geodynamics figures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPreset:
    name: str
    matplotlib: str
    scale: str
    kind: str
    robust_lower: float = 2.0
    robust_upper: float = 98.0


PRESETS: dict[str, ColorPreset] = {
    "geodynamics_temperature": ColorPreset("geodynamics_temperature", "inferno", "linear", "sequential"),
    "temperature": ColorPreset("temperature", "inferno", "linear", "sequential"),
    "geodynamics_viscosity": ColorPreset("geodynamics_viscosity", "viridis", "log10", "sequential"),
    "viscosity": ColorPreset("viscosity", "viridis", "log10", "sequential"),
    "geodynamics_strain_rate": ColorPreset("geodynamics_strain_rate", "magma", "log10", "sequential"),
    "strain_rate": ColorPreset("strain_rate", "magma", "log10", "sequential"),
    "geodynamics_stress": ColorPreset("geodynamics_stress", "coolwarm", "auto", "diverging"),
    "stress": ColorPreset("stress", "coolwarm", "auto", "diverging"),
    "pressure": ColorPreset("pressure", "cividis", "linear", "sequential"),
    "density": ColorPreset("density", "cividis", "linear", "sequential"),
    "composition": ColorPreset("composition", "tab10", "linear", "categorical"),
    "velocity": ColorPreset("velocity", "plasma", "linear", "sequential"),
    "topography": ColorPreset("topography", "terrain", "auto", "diverging"),
    "seismic_velocity": ColorPreset("seismic_velocity", "cividis", "linear", "sequential"),
    "geodynamics_diverging": ColorPreset("geodynamics_diverging", "coolwarm", "auto", "diverging"),
}


def get_preset(name: str | None, variable: str | None = None) -> ColorPreset:
    key = (name or variable or "temperature").lower()
    if key in PRESETS:
        return PRESETS[key]
    if variable and variable.lower() in PRESETS:
        return PRESETS[variable.lower()]
    return PRESETS["temperature"]

