# Aspect_Yuan 0.2 Beta Release Boundary

Use this file when describing what the 0.2 beta can and cannot do.

## Release Position

Aspect_Yuan 0.2 beta is a teaching and first-model skill for geologists learning ASPECT. It is also a starting point for ASPECT paper reproduction, but it is not a complete automatic reproduction platform.

## Supported In 0.2 Beta

- Beginner one-command ASPECT lessons for subduction, mantle convection, and rift.
- Runnable beginner subduction smoke path with local ASPECT evidence.
- Configuration-based starter model generation for subduction, mantle convection, and rift.
- Starter PRM validation and geologist-facing risk messages.
- ASPECT log checking.
- ASPECT statistics parsing.
- ASPECT output scanning for PVD, PVTU, VTU, statistics, logs, particles, and depth-average outputs.
- Real VTK/PyVista field plotting with PNG, PDF, SVG, TIFF, metadata, and recipe output.
- Scientific colormap presets and journal-style figure presets.
- Paper reproduction triage: version, commit, Docker, plugin, PRM, and source-code evidence detection.
- Plugin request triage and minimal plugin templates.

## Not Promised In 0.2 Beta

- Automatic complete reproduction of every ASPECT paper.
- Automatic installation of every ASPECT, deal.II, FastScape, Trilinos, or MPI environment.
- Guaranteed research-grade parameter correctness.
- Guaranteed compatibility across all ASPECT versions.
- Full vector-native publication graphics.
- Complete velocity-arrow and contour-overlay rendering for every output type.
- Automatic scientific interpretation without user review.

## Release Principle

Do not silently change the geological model to make a run succeed. Any simplification of dimension, geometry, boundary conditions, rheology, material fields, temperature structure, gravity, timescale, or resolution must be named as a scientific simplification.

## Required Release Validation

Run:

```bash
scripts/release_validate.sh --aspect-bin /path/to/aspect
```

If ASPECT is not available, run:

```bash
scripts/release_validate.sh
```

and mark the ASPECT smoke test as skipped, not passed.
