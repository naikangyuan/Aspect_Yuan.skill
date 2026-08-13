#!/usr/bin/env python3
"""Keyword-based ASPECT plugin type recommender for geologist requests."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class PluginRoute:
    name: str
    score: int
    why: list[str]
    next_steps: list[str]


RULES = {
    "material model": {
        "keywords": ["rheology", "viscosity", "density", "yield", "plastic", "weakening", "cohesion", "friction", "melt law", "phase", "craton strength", "damage"],
        "steps": [
            "Check built-in material models and composition-dependent parameters first.",
            "Start from assets/plugin_templates/material_model_minimal.cc.",
            "Define which material outputs change and which composition/temperature/pressure inputs control them.",
        ],
    },
    "boundary velocity": {
        "keywords": ["plate motion", "boundary velocity", "convergence", "extension rate", "trench migration", "basal flow", "inflow", "outflow", "time dependent velocity"],
        "steps": [
            "Check Boundary velocity model/function and ascii data first.",
            "Start from assets/plugin_templates/boundary_velocity_minimal.cc.",
            "Define boundary names, velocity components, units, and time dependence.",
        ],
    },
    "boundary temperature": {
        "keywords": ["boundary temperature", "surface temperature", "basal temperature", "thermal boundary", "side temperature", "heat boundary"],
        "steps": [
            "Check built-in box, spherical constant, function, and ascii data boundary temperature models first.",
            "Use the boundary temperature interface if temperature must be computed from custom geology.",
            "TODO: create a boundary_temperature template if this becomes a repeated workflow.",
        ],
    },
    "initial temperature": {
        "keywords": ["initial temperature", "geotherm", "thermal anomaly", "slab temperature", "plume temperature", "tomography temperature", "cooling age"],
        "steps": [
            "Check Initial temperature model/function, adiabatic, ascii data, and world builder first.",
            "Start from assets/plugin_templates/initial_temperature_minimal.cc.",
            "Define coordinate convention, units, background geotherm, and anomaly shape.",
        ],
    },
    "initial composition": {
        "keywords": ["initial composition", "rock unit", "weak zone", "fault", "slab geometry", "craton", "lithology", "material domain", "composition field"],
        "steps": [
            "Check Initial composition model/function, ascii data, slab model, and world builder first.",
            "Start from assets/plugin_templates/initial_composition_minimal.cc.",
            "Map every returned field to Compositional fields names in the .prm.",
        ],
    },
    "gravity model": {
        "keywords": ["gravity", "body force", "radial gravity", "variable gravity", "nonvertical gravity"],
        "steps": [
            "Check vertical, radial, function, and ascii data gravity models first.",
            "Use GravityModel::Interface only if built-ins cannot express the body force.",
            "TODO: create a gravity template if this becomes a repeated workflow.",
        ],
    },
    "postprocessor": {
        "keywords": ["diagnostic", "postprocess", "statistics", "measure", "trench position", "retreat rate", "heat flow statistic", "integrated strain", "output metric"],
        "steps": [
            "Check existing postprocessors and visualization outputs first.",
            "Start from assets/plugin_templates/postprocessor_minimal.cc.",
            "Define the statistic, output name, units, and how to validate it from a simple model.",
        ],
    },
}


def classify(text: str) -> list[PluginRoute]:
    lower = text.lower()
    routes: list[PluginRoute] = []
    for name, rule in RULES.items():
        hits = [kw for kw in rule["keywords"] if kw in lower]
        if hits:
            routes.append(PluginRoute(name=name, score=len(hits), why=hits, next_steps=rule["steps"]))
    return sorted(routes, key=lambda route: route.score, reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest an ASPECT plugin route from a natural-language request.")
    parser.add_argument("request", nargs="+", help="User request text")
    args = parser.parse_args()

    text = " ".join(args.request)
    routes = classify(text)

    print("Plugin request interpretation")
    print(f"Request: {text}")
    print()

    if not routes:
      print("No strong plugin type matched.")
      print("Recommended route:")
      print("- First try a .prm-only solution with built-in ASPECT models.")
      print("- If built-ins cannot express the geology, inspect references/aspect300_plugin_interfaces.md.")
      return 0

    best = routes[0]
    print(f"Most likely plugin type: {best.name}")
    print(f"Matched keywords: {', '.join(best.why)}")
    print()
    print("Development route:")
    for step in best.next_steps:
        print(f"- {step}")

    if len(routes) > 1:
        print()
        print("Other possible plugin types:")
        for route in routes[1:]:
            print(f"- {route.name}: matched {', '.join(route.why)}")

    print()
    print("Guardrail: describe the geological behavior first, then implement the ASPECT interface.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
