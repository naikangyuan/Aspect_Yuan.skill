# Paper Reproduction First

Use this reference whenever the user names a paper, DOI, article title, supplement, GitHub repository, Zenodo archive, or says they want to reproduce published ASPECT results.

## Principle

Reproduction starts from the paper's own code and ASPECT version, not from the current local checkout and not from a generic beginner template. Different papers may rely on different ASPECT releases, unreleased commits, plugin APIs, parameter names, solver defaults, mesh formats, World Builder versions, or data files.

## Required Evidence Table

Before running or editing the model, collect:

- Paper title, DOI, year, and target figure/table/result.
- Code source: supplement, GitHub/GitLab, Zenodo, institutional archive, container, or local folder.
- ASPECT version evidence: release tag, git commit, branch, VERSION file, generated parameters file, run log, README, CMake output, Dockerfile, Singularity/Apptainer file, conda/environment file.
- deal.II, Trilinos, p4est, Geodynamic World Builder, FastScape, and other dependency versions if stated.
- Original `.prm` paths, include files, plugin source files, data files, and mesh files.
- Original run command, MPI process count, refinement level, end time, output cadence, and restart behavior.
- Expected outputs: statistics columns, visualization fields, paper figure diagnostics, published benchmark values.

If evidence is missing, label it `unknown` and list how to verify it. Do not infer a precise version from the publication year alone.

## Workflow

1. Build a reproduction folder outside the ASPECT source tree.
2. Download or point to the paper code archive, preserving original filenames.
3. Run `scripts/detect_aspect_reproduction_context.py` on the README, paper notes, and code directory.
4. Decide environment path using `references/aspect_version_strategy.md`.
5. Install/build the exact ASPECT version only in an isolated directory.
6. Run the paper's smallest `.prm` or shortest benchmark first.
7. Use `scripts/check_aspect_log.py`, `scripts/parse_aspect_statistics.py`, and `scripts/make_case_report.py`.
8. Only after a clean smoke run, reproduce the target figure/result.
9. Record every deviation from the paper: version, parameter, mesh, resolution, timestep, plugin, dependency, or data change.

## Geological Guardrail

Do not simplify the published geometry, rheology, boundary velocities, temperature field, composition fields, gravity, or dimensionality unless the user explicitly asks for a teaching approximation. If a simplification is made, write it as a reproduction deviation, not as a successful exact reproduction.
