# v0.1 Release Boundary

Use this reference when describing what `geologist-aspect-300` v0.1 supports.

## Supports

- Paper-first ASPECT reproduction triage: identify paper code folders, README evidence, Dockerfiles, ASPECT versions, commits, plugins, `.prm` files, logs, and statistics.
- Geologist-facing `.prm` learning: explain subsection meaning, map geology to ASPECT components, and identify common parameter risks.
- Beginner model generation from local patterns: mantle convection, weak zone, plume, rift, lithosphere shortening, subduction, and related wizards/templates.
- Run triage: lint `.prm`, check ASPECT logs, parse statistics, and generate case reports.
- Plugin pathway guidance: identify common plugin types and provide minimal external plugin templates.
- Isolated version planning: outline paper-specific ASPECT checkout/build paths and container-first reproduction plans.

## Does Not Promise

- Automatic full reproduction of every published ASPECT paper.
- Automatic dependency solving for deal.II, Trilinos, p4est, FastScape, World Builder, MPI, or paper-specific forks.
- Automatic correctness of research-grade rheology, boundary conditions, or parameter values.
- Automatic conversion of a published model into a simplified teaching model.
- Silent changes to geometry, dimension, rheology, material fields, boundary velocities, temperature structure, gravity, or timescale.
- Guaranteed compatibility between ASPECT 3.0.0-style templates and older paper forks.

## Required Warnings

- If a paper version or commit is not verified, say `unknown` and list the evidence needed.
- If a run is externally timed out, classify it as startup smoke only, not normal completion.
- If statistics are empty or missing, do not interpret science.
- If a plugin is required, verify the shared library path and registered plugin names before running.
- If a template has not passed real ASPECT smoke testing, keep `Needs verification with ASPECT 3.0.0 before production use` in the file.

## v0.1 Success Definition

The v0.1 skill is successful when a geologist can:

1. start from a paper code folder and identify the likely ASPECT version path;
2. understand the geology encoded in a `.prm`;
3. run or triage a small ASPECT case;
4. read log/statistics risks before interpreting output;
5. move from reproduction evidence toward a first modifiable model without hidden scientific changes.
