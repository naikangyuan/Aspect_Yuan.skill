# Development Plan

This plan extends the current skill incrementally. It does not replace the existing `.prm`, plugin, paper-version, run, log, statistics, or eval helpers.

## P0

### Purpose

Make the skill useful as a runnable 0.2 development build for model creation and publication-oriented postprocessing.

### Tasks

- Add unified CLI: `scripts/aspect-yuan`
- Add Python package: `aspect_yuan/`
- Implement `aspect-yuan postprocess scan`
- Implement `aspect-yuan plot`
- Implement scientific colormap presets.
- Implement journal presets.
- Implement figure recipes and deterministic plot reproduction.
- Implement `aspect-yuan model create` for `mantle_convection`, `subduction`, and `rift`.
- Implement `aspect-yuan model validate`.
- Add templates, examples, docs, and tests for the implemented P0 features.

### Involved Files

- `aspect_yuan/cli.py`
- `aspect_yuan/output_scan.py`
- `aspect_yuan/plotting.py`
- `aspect_yuan/colormaps.py`
- `aspect_yuan/journals.py`
- `aspect_yuan/recipe.py`
- `aspect_yuan/models.py`
- `aspect_yuan/prm.py`
- `scripts/aspect-yuan`
- `templates/models/*`
- `templates/figures/*`
- `examples/models/*`
- `examples/figures/*`
- `docs/01_quick_start.md`
- `docs/02_model_generator.md`
- `docs/05_postprocessing.md`
- `docs/06_publication_figures.md`
- `tests/test_*.py`

### Implementation Method

- Keep the Python package dependency-light.
- Use standard library YAML fallback only when PyYAML is unavailable; prefer JSON-compatible YAML syntax for examples.
- Use PyVista if installed for VTK field plots.
- If PyVista is unavailable, generate a clear recipe/config report and fail field rendering with an actionable message.
- Reuse existing beginner PRM templates and only apply controlled placeholder replacements.

### Test Method

- Run Python unit tests with `python3 -m unittest discover -s tests`.
- Run CLI help and dry commands.
- Generate sample model cases into `/tmp`.
- Scan synthetic ASPECT-like output directories.
- Validate figure config and recipe creation.

### Completion Standard

- `aspect-yuan postprocess scan` returns JSON and text summaries for an output directory.
- `aspect-yuan plot` can create at least recipe/metadata and can render with PyVista when VTK support is installed.
- `aspect-yuan model create examples/models/mantle_convection_basic.yaml` creates a full case directory with `case.prm`, `config.yaml`, `run.sh`, `output/`, and `README.md`.
- Tests pass without requiring a real ASPECT run.

## P1

### Purpose

Make first-time user environment setup and beginner workflow smoother.

### Involved Files

- `aspect_yuan/environment.py`
- `templates/docker/`
- `examples/beginner/`
- `docs/03_docker.md`
- `docs/04_running_aspect.md`

### Implementation Method

- Add `aspect-yuan env check`.
- Add `aspect-yuan env docker-init`.
- Add beginner workflow commands that compose existing model/run/scan/plot tools.

### Test Method

- Unit-test environment check parsing.
- Docker build should be optional and explicitly reported if not run.

### Completion Standard

- A user can run environment diagnostics and generate Docker starter files without modifying ASPECT source.

## P2

### Purpose

Make paper reproduction a first-class workflow.

### Involved Files

- `aspect_yuan/reproduction.py`
- `templates/reproduction/reproduction.yaml`
- `docs/07_paper_reproduction.md`
- `tests/test_reproduction.py`

### Implementation Method

- Add `aspect-yuan reproduce init`.
- Add `aspect-yuan reproduce audit`.
- Add parameter provenance extraction from paper notes, PRM files, and plugin text.
- Add reproduction level scoring.

### Test Method

- Use synthetic paper projects with controlled conflicts.
- Use existing Kaili/Gernon detection outputs as manual validation targets when available.

### Completion Standard

- A paper project can be initialized, audited, and assigned a Level 0-5 reproduction status with evidence.

## P3

### Purpose

Improve advanced reproducibility and publication figure automation.

### Involved Files

- `aspect_yuan/paper_figures.py`
- `aspect_yuan/reproduction.py`
- `examples/reproduction/`
- `examples/paper_figures/`

### Implementation Method

- Add figure-driven reproduction commands.
- Add side-by-side comparison reports.
- Add batch paper-figure generation.

### Test Method

- Use synthetic images/metadata and small VTK fixtures.
- Run optional real ASPECT/PyVista tests when dependencies exist.

### Completion Standard

- `aspect-yuan paper-figures paper_figures.yaml` generates figure outputs, recipes, and captions for available outputs.
