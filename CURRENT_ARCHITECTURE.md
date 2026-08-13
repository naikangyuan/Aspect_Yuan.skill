# Current Architecture

This file records the state of `geologist-aspect-300` before the Aspect_Yuan incremental development pass.

## Existing Skill Identity

- Skill directory: `.codex-skill-dev/geologist-aspect-300`
- Current user-facing identity: geologist-oriented ASPECT skill for paper reproduction, `.prm` understanding, model templates, plugin guidance, run/log/statistics checks, and version planning.
- `SKILL.md` already defines the core guardrail: explain geological meaning first and never silently change geometry, boundary conditions, rheology, material domains, temperature structure, gravity, dimension, or timescale.

## Existing Directory Structure

- `SKILL.md`: main routing instructions and guardrails.
- `references/`: ASPECT 3.0-style PRM knowledge, plugin interface notes, paper reproduction/version strategy, quickstart, release boundary, and validation report references.
- `model_wizards/`: geologist-facing conceptual model guides for mantle convection, shortening/collision, weak zone, subduction, rift, plume, and craton edge.
- `assets/prm_templates/`: beginner ASPECT `.prm` templates for convection, shortening, weak zone, subduction, rift, and plume.
- `assets/plugin_templates/`: minimal external plugin source templates and CMake template.
- `assets/explanation_templates/`: report/readme templates.
- `scripts/`: deterministic helpers for linting, explaining, running, checking, reporting, paper-code detection, installation planning, plugin builds, and eval/static validation.
- `evals/`: rule-based test cases, expected-output requirements, and validation status.
- `examples/`: exists but is currently empty.

## Existing Implemented Functions

- `.prm` structural lint: `scripts/aspect_prm_lint.py`
- `.prm` subsection explanation: `scripts/aspect_prm_explain.py`
- ASPECT run wrapper: `scripts/run_aspect_case.sh`
- ASPECT log diagnosis: `scripts/check_aspect_log.py`
- ASPECT statistics parser and CSV/plot helpers: `scripts/parse_aspect_statistics.py`, `scripts/plot_statistics.py`
- Case report generation: `scripts/make_case_report.py`
- Paper/code/version clue detection: `scripts/detect_aspect_reproduction_context.py`
- Model-family version planning: `scripts/plan_aspect_version.py`
- External plugin build helper: `scripts/build_aspect_plugin.sh`
- Plugin request triage: `scripts/explain_plugin_request.py`
- Skill validation and evals: `scripts/static_validate_skill.py`, `scripts/run_skill_evals.py`

## Reusable Modules

- PRM parsing and linting logic from `aspect_prm_lint.py`.
- Log/statistics/report logic from `check_aspect_log.py`, `parse_aspect_statistics.py`, and `make_case_report.py`.
- Paper reproduction clue extraction from `detect_aspect_reproduction_context.py`.
- Existing beginner templates can seed the model generator.
- Existing model wizards can guide model-family defaults.
- Existing validation scripts can be extended to include new CLI/tests.

## Missing Functions

- No unified `aspect-yuan` CLI entry point.
- No configuration-driven model generator.
- No interactive model wizard.
- No reusable model template library under `templates/models/`.
- No ASPECT output scanner for PVD/PVTU/VTU/statistics/log/depth-average/particles.
- No publication plotting engine for field figures.
- No scientific colormap preset library.
- No journal-style figure presets.
- No figure recipe capture/reproduction.
- No paper-figure set generator.
- No Docker/environment checker module.
- No structured paper reproduction project commands (`reproduce init/audit/status/figure`).
- No Python unit test directory.
- Empty `examples/`.

## Four Major Module Impact

### Model Generator

Add:

- `aspect_yuan/models.py`
- `aspect_yuan/prm.py`
- `templates/models/{mantle_convection,subduction,rift}/`
- `examples/models/`
- tests for model generation and PRM validation.

Reuse:

- `assets/prm_templates/*.prm`
- `scripts/aspect_prm_lint.py`
- `model_wizards/*.md`

### Paper Reproduction

Add later:

- `aspect_yuan/reproduction.py`
- `templates/reproduction/reproduction.yaml`
- `examples/reproduction/`

Reuse:

- `scripts/detect_aspect_reproduction_context.py`
- `references/paper_reproduction_first.md`
- `references/aspect_version_strategy.md`

### Docker / Beginner Environment

Add later:

- `aspect_yuan/environment.py`
- `templates/docker/`
- `examples/beginner/`

Reuse:

- `scripts/run_aspect_case.sh`
- existing beginner PRM templates and case-report scripts.

### Visualization / Publication Figures

Add now:

- `aspect_yuan/output_scan.py`
- `aspect_yuan/plotting.py`
- `aspect_yuan/colormaps.py`
- `aspect_yuan/journals.py`
- `aspect_yuan/recipe.py`
- `templates/figures/`
- `examples/figures/`
- tests for scanner, plot config, colormap, and recipe.

## New Directories Needed

- `aspect_yuan/`
- `templates/models/`
- `templates/figures/`
- `examples/models/`
- `examples/figures/`
- `docs/`
- `tests/`

## Architecture Conflicts

- The current skill is file-asset and script oriented; adding a Python package and unified CLI is compatible if scripts remain callable.
- Existing beginner `.prm` templates are teaching templates, not all smoke-proven to full completion. The model generator must label generated cases as starter models and keep geological assumptions explicit.
- ASPECT output plotting depends on optional VTK/PyVista availability. P0 must work at least for configuration validation, PVD/VTU discovery, recipe generation, and statistics/log-aware fallbacks. Field rendering should use PyVista when installed and fail clearly when it is missing.
- The local ASPECT checkout reports a different version risk than the skill name implies. Generated docs must say ASPECT compatibility needs local verification.
