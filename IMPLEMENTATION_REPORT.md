# Implementation Report

Date: 2026-08-11

This report covers the Aspect_Yuan incremental P0 implementation added to the existing `geologist-aspect-300` skill. The existing architecture was not replaced.

## Added

### Architecture and Planning

- `CURRENT_ARCHITECTURE.md`
- `DEVELOPMENT_PLAN.md`

### Unified CLI

- `scripts/aspect-yuan`
- `aspect_yuan/cli.py`

Implemented commands:

```bash
scripts/aspect-yuan model list
scripts/aspect-yuan model create CONFIG.yaml --output-dir CASE_DIR
scripts/aspect-yuan model validate CASE_DIR/case.prm
scripts/aspect-yuan postprocess scan output/ --json --output output_scan.json
scripts/aspect-yuan plot figure.yaml
```

### Core Python Package

- `aspect_yuan/config.py`: YAML/JSON config loading and writing.
- `aspect_yuan/models.py`: P0 model generator for `mantle_convection`, `subduction`, and `rift`.
- `aspect_yuan/prm.py`: lightweight PRM validation for generated starter cases.
- `aspect_yuan/output_scan.py`: ASPECT output scanner for PVD/PVTU/VTU/statistics/depth-average/particles/log files.
- `aspect_yuan/colormaps.py`: scientific geodynamics colormap presets.
- `aspect_yuan/journals.py`: publication-ready journal presets.
- `aspect_yuan/recipe.py`: reproducible figure recipe writer.
- `aspect_yuan/plotting.py`: publication plotting entry point with PyVista rendering path and metadata-only fallback.

### Model Template Library

- `templates/models/mantle_convection/base.prm`
- `templates/models/mantle_convection/config.yaml`
- `templates/models/mantle_convection/README.md`
- `templates/models/subduction/base.prm`
- `templates/models/subduction/config.yaml`
- `templates/models/subduction/README.md`
- `templates/models/rift/base.prm`
- `templates/models/rift/config.yaml`
- `templates/models/rift/README.md`

The `base.prm` files reuse existing beginner PRM templates instead of inventing new ASPECT syntax.

### Figure Templates and Examples

- `templates/figures/field_temperature.yaml`
- `templates/figures/multipanel_times.yaml`
- `examples/figures/temperature.yaml`
- `examples/models/mantle_convection_basic.yaml`
- `examples/models/subduction_basic.yaml`
- `examples/models/rift_basic.yaml`

### Documentation

- `README.md`
- `docs/01_quick_start.md`
- `docs/02_model_generator.md`
- `docs/03_docker.md`
- `docs/04_running_aspect.md`
- `docs/05_postprocessing.md`
- `docs/06_publication_figures.md`
- `docs/07_paper_reproduction.md`

### Tests

- `tests/test_model_generator.py`
- `tests/test_prm_validator.py`
- `tests/test_output_scanner.py`
- `tests/test_plot_config.py`
- `tests/test_colormap.py`
- `tests/test_figure_recipe.py`
- `tests/test_reproduction.py`

## Modified

- `SKILL.md`: added `scripts/aspect-yuan` routing for model generation, output scanning, publication plotting, and figure recipes.

## Working CLI Examples

List model types:

```bash
scripts/aspect-yuan model list
```

Create starter models:

```bash
scripts/aspect-yuan model create examples/models/mantle_convection_basic.yaml --output-dir /tmp/aspect-yuan-p0-mantle
scripts/aspect-yuan model create examples/models/subduction_basic.yaml --output-dir /tmp/aspect-yuan-p0-subduction
scripts/aspect-yuan model create examples/models/rift_basic.yaml --output-dir /tmp/aspect-yuan-p0-rift
```

Validate generated PRMs:

```bash
scripts/aspect-yuan model validate /tmp/aspect-yuan-p0-mantle/case.prm
scripts/aspect-yuan model validate /tmp/aspect-yuan-p0-subduction/case.prm
scripts/aspect-yuan model validate /tmp/aspect-yuan-p0-rift/case.prm
```

Scan output:

```bash
scripts/aspect-yuan postprocess scan /tmp/aspect-yuan-p0-mantle/output --json --output /tmp/aspect-yuan-p0-mantle/output_scan.json
```

Create figure metadata and recipe:

```bash
scripts/aspect-yuan plot examples/figures/temperature.yaml
scripts/aspect-yuan plot templates/figures/multipanel_times.yaml
```

## Test Results

Unit tests:

```bash
PYTHONPATH=/home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300 python3 -m unittest discover -s /home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300/tests
```

Result: `Ran 9 tests`, `OK`.

Existing skill validation:

```bash
python3 scripts/static_validate_skill.py
python3 scripts/run_skill_evals.py
```

Result:

- static validation passed;
- skill eval checks passed for `8` cases.

Syntax check:

- all `aspect_yuan/*.py` files compiled with Python `compile()` without writing `__pycache__`;
- result: `syntax ok`.

CLI smoke results:

- `aspect-yuan --help`: passed.
- `aspect-yuan model list`: passed.
- generated mantle convection, subduction, and rift starter case directories in `/tmp`.
- generated PRM validation returned `PASS` for the three generated cases.
- output scanner correctly reported an empty output directory as `status: empty`.
- single-panel and multipanel figure metadata/recipe files were generated in metadata-only mode.

## Real ASPECT Output Plot Smoke

Date: 2026-08-11

Real ASPECT output used:

```text
/tmp/geologist-aspect-smoke/01_convection/output-beginner-2d-box-convection
```

Scanner command:

```bash
scripts/aspect-yuan postprocess scan /tmp/geologist-aspect-smoke/01_convection/output-beginner-2d-box-convection --json --output /tmp/aspect-yuan-real-plot-scan.json
```

Scanner result:

- status: `ok`
- PVD files: `1`
- PVTU files: `50`
- VTU files: `50`
- statistics files: `1`
- logs: `1`
- detected timesteps: `50`
- detected ASPECT field aliases: `T -> temperature`, `p -> pressure`
- common geodynamics variables: `pressure`, `temperature`, `velocity`

Plot config:

```text
/tmp/aspect-yuan-real-temperature-dir.yaml
```

Plot command:

```bash
scripts/aspect-yuan plot /tmp/aspect-yuan-real-temperature-dir.yaml
```

The config used the whole ASPECT output directory as input and requested `field.variable: temperature`. The plotting engine selected the latest available timestep and resolved ASPECT variable `T` as temperature.

Generated real figure files:

- `/tmp/aspect-yuan-real-temperature-dir.png`
- `/tmp/aspect-yuan-real-temperature-dir.pdf`
- `/tmp/aspect-yuan-real-temperature-dir.svg`
- `/tmp/aspect-yuan-real-temperature-dir.tiff`
- `/tmp/aspect-yuan-real-temperature-dir_metadata.json`
- `/tmp/aspect-yuan-real-temperature-dir_recipe.json`

Image QA:

- PNG size: `1600 x 900`
- grayscale extrema: `0-255`
- grayscale standard deviation: `81.26`
- file checks identify valid PNG, one-page PDF, SVG, and TIFF outputs.

Code changes from this smoke:

- `aspect_yuan/output_scan.py` now recognizes ASPECT aliases `T -> temperature` and `p -> pressure`.
- `aspect_yuan/plotting.py` now resolves user-facing `temperature` to ASPECT field `T` when needed.
- Directory input now selects the latest timestep from the scanned PVD list.
- PDF/TIFF are converted from the rendered PNG; SVG embeds the rendered PNG instead of writing a placeholder.
- `MPLCONFIGDIR` defaults to `/tmp/aspect-yuan-matplotlib` to avoid unwritable home-cache warnings.

Remaining plotting caveat:

- VTK reports a headless offscreen warning about `DISPLAY=:0`, but the rendered image files were created and passed nonblank checks.

## Current Limitations

- PyVista/VTK field rendering is implemented but was not exercised because the test path used metadata-only mode and no real ASPECT VTK output was supplied.
- PDF/SVG/TIFF export is available through the plotting path after a PyVista PNG render, but journal-perfect vector conversion is not claimed.
- Contours, velocity arrows, domains, and time/panel choices are recorded in recipe metadata; full visual overlay rendering needs real VTK output validation.
- `subduction` generation now uses a runnable low-resolution teaching template based on the local ASPECT kinematically driven subduction test. The template explicitly documents that it simplifies the research cookbook from 7 compositional fields to 3 teaching fields.
- Interactive `aspect-yuan model wizard` is not implemented in P0.
- `continental_collision` and `extension` model types are planned but not implemented in P0.
- Docker environment creation/checking is documented as P1, not implemented.
- `aspect-yuan reproduce init/audit/status/figure` is documented as P2, not implemented.

## Next P1/P2 Work

P1:

- Add `aspect-yuan env check`.
- Add `aspect-yuan env docker-init`, `docker-build`, and `docker-run`.
- Add `aspect-yuan beginner` or `aspect-yuan tutorial start`.
- Add beginner examples for mantle convection, subduction, and rift that call the implemented P0 model/scan/plot commands.

P2:

- Add `aspect-yuan reproduce init`.
- Add `reproduction.yaml` template.
- Add parameter provenance audit and conflict tables.
- Add reproduction Level 0-5 status scoring.
- Add figure-driven reproduction and comparison report generation.

## Subduction Beginner Repair

Date: 2026-08-12

Goal: make the first-layer geologist teaching path work for "I want a subduction model."

Changed files:

- `assets/prm_templates/beginner_subduction.prm`
- `templates/models/subduction/base.prm`
- `aspect_yuan/models.py`
- `evals/validation_report.md`

Reason:

- The previous 7-field beginner subduction template failed local ASPECT smoke at timestep 0 with a Stokes solver convergence failure.
- The local ASPECT repository already contains a low-resolution kinematically driven subduction test that preserves the core teaching model and runs quickly.

Explicit geological simplification:

- Research/cookbook version: 7 compositional fields with detailed plate layers and weak zone.
- Beginner runnable version: 3 compositional fields, `OP`, `ML_SP`, and `crust_SP`.
- Preserved meaning: 3000 x 670 km box, right-boundary kinematic subduction inflow/outflow, density/viscosity contrast, Boussinesq formulation, and prescribed-velocity teaching setup.

Smoke command:

```bash
scripts/aspect-yuan model create examples/models/subduction_basic.yaml --output-dir /tmp/aspect-yuan-subduction-cli-case
scripts/aspect-yuan model validate /tmp/aspect-yuan-subduction-cli-case/case.prm
timeout 180s scripts/run_aspect_case.sh /tmp/aspect-yuan-subduction-cli-case/case.prm --aspect-bin /home/yuan/fem3/aspect/build/aspect-release
```

Smoke result:

- ASPECT exit status: `0`
- Runtime: about `4` seconds
- MPI: `1` process
- Reached timestep `1`
- Final model time: `100000 years`
- Active cells: `1792`
- Final Stokes iterations: `13`
- Output written to `/tmp/aspect-yuan-subduction-cli-case/output`

Post-run checks:

- `check_aspect_log.py`: normal end, no issues.
- `parse_aspect_statistics.py`: `2` rows and `28` columns.
- `aspect-yuan postprocess scan`: detected PVD/PVTU/VTU/statistics/log and field variables.
- `aspect-yuan plot /tmp/aspect-yuan-subduction-viscosity.yaml`: generated PNG/PDF/SVG/TIFF from real subduction output.

## Beginner One-Command Workflow

Date: 2026-08-12

Implemented:

- `scripts/aspect-yuan beginner subduction`
- `scripts/aspect-yuan beginner mantle_convection`
- `scripts/aspect-yuan beginner rift`

The command generates:

- `case.prm`
- `config.yaml`
- `run.sh`
- `output/`
- `README.md`
- `beginner_figure.yaml`
- `beginner_report.md`

With `--run --aspect-bin /path/to/aspect`, it also runs ASPECT, scans output, creates the first teaching figure, and records the result in `beginner_report.md`.

Subduction one-command smoke:

```bash
scripts/aspect-yuan beginner subduction --output-dir /tmp/aspect-yuan-beginner-subduction-run --run --aspect-bin /home/yuan/fem3/aspect/build/aspect-release
```

Result:

- generated full beginner case;
- ASPECT exit status `0`;
- output scan status `ok`;
- detected `solution.pvd`, `vtu`, `statistics`, and `log.txt`;
- generated composition teaching figure using `crust_SP`;
- rendered PNG/PDF/SVG/TIFF;
- PNG size `1600 x 900`, grayscale standard deviation `58.14`.

Added beginner documentation:

- `docs/00_我是地质新手_5分钟跑通第一个_ASPECT_模型.md`

Added beginner eval:

- `evals/test_cases/beginner_one_command_subduction.md`
- `evals/expected_outputs/beginner_one_command_subduction.md`

Final P0.3 validation:

- `scripts/aspect-yuan beginner subduction --output-dir /tmp/aspect-yuan-beginner-subduction-run --run --aspect-bin /home/yuan/fem3/aspect/build/aspect-release`: passed.
- `scripts/aspect-yuan beginner mantle_convection --output-dir /tmp/aspect-yuan-beginner-mantle-norun`: generated complete beginner directory.
- `scripts/aspect-yuan beginner rift --output-dir /tmp/aspect-yuan-beginner-rift-norun`: generated complete beginner directory.
- `python3 scripts/static_validate_skill.py`: passed.
- `python3 scripts/run_skill_evals.py`: passed for `9` cases.
- `python3 -m unittest discover -s tests`: passed, `13` tests.

Subduction one-command output:

- case directory: `/tmp/aspect-yuan-beginner-subduction-run`
- report: `/tmp/aspect-yuan-beginner-subduction-run/beginner_report.md`
- generated first teaching figure: `/tmp/aspect-yuan-beginner-subduction-run/beginner_subduction_crust_SP.png`
- PNG QA: `1600 x 900`, grayscale standard deviation `58.14`.

## 0.2 Beta Release Readiness

Date: 2026-08-13

Added release artifacts:

- `references/v0_2_beta_release_boundary.md`
- `scripts/release_validate.sh`
- `RELEASE_0_2_BETA.md`

Release validation without ASPECT:

```bash
scripts/release_validate.sh
```

Result: passed static validation, `9` eval cases, and `13` unit tests. Beginner ASPECT smoke was explicitly skipped because no `--aspect-bin` was provided.

Release validation with ASPECT:

```bash
scripts/release_validate.sh --aspect-bin /home/yuan/fem3/aspect/build/aspect-release --smoke-dir /tmp/aspect-yuan-release-smoke-20260813
```

Result: passed static validation, `9` eval cases, `13` unit tests, and the beginner subduction ASPECT smoke.

Smoke output:

- `/tmp/aspect-yuan-release-smoke-20260813/case.prm`
- `/tmp/aspect-yuan-release-smoke-20260813/run.log`
- `/tmp/aspect-yuan-release-smoke-20260813/output/solution.pvd`
- `/tmp/aspect-yuan-release-smoke-20260813/output/statistics`
- `/tmp/aspect-yuan-release-smoke-20260813/beginner_report.md`
- `/tmp/aspect-yuan-release-smoke-20260813/beginner_subduction_crust_SP.png`

## Key Paths

- Skill root: `/home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300`
- CLI: `/home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300/scripts/aspect-yuan`
- Package: `/home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300/aspect_yuan`
- Tests: `/home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300/tests`
- Architecture report: `/home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300/CURRENT_ARCHITECTURE.md`
- Plan: `/home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300/DEVELOPMENT_PLAN.md`
- Implementation report: `/home/yuan/fem3/aspect/.codex-skill-dev/geologist-aspect-300/IMPLEMENTATION_REPORT.md`
