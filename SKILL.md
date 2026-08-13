---
name: geologist-aspect-300
description: Use this skill to help geologists reproduce ASPECT geodynamics papers and build ASPECT models with explicit version control, including paper reproduction, DOI/code repository/version/commit detection, ASPECT installation planning, downloaded article code, .prm parameter file generation, cookbook and benchmark adaptation, plugin development, material model setup, deep-shallow coupling, subduction, mantle convection, lithosphere deformation, weak zone, rift, plume, craton edge, boundary conditions, initial conditions, mesh refinement, postprocessing, and parameter validation.
---

# Geologist ASPECT 300

This skill is for ordinary geologists using ASPECT, not ASPECT core developers. Its purpose is to reproduce published ASPECT-based geodynamics studies first, then translate a geological science question into a runnable, explainable, and modifiable ASPECT model.

Every answer must start with the geological meaning of the proposed model, then give the ASPECT implementation. Do not silently change the user's geological model to make a computation easier: geometry, boundary conditions, rheology, material domains, gravity direction, temperature structure, composition fields, dimension, and timescales must remain explicit scientific choices.

## Core Capabilities

1. **Paper reproduction system**: identify the target paper, DOI, supplement, code repository, ASPECT version, git tag/commit/branch, external plugins, data files, and build environment before changing any model.
2. **Version and installation system**: choose whether to use the user's existing ASPECT, install a tagged release, build a paper-specific commit, or use a container/environment file. Never overwrite an existing ASPECT checkout; install into an isolated directory.
3. **PRM modeling system**: learn from local ASPECT cookbooks, benchmarks, tests, and documentation; draft `.prm` parameter files; explain existing parameter files; check parameter consistency; propose minimal changes.
4. **Plugin development system**: identify the right ASPECT plugin type; generate small plugin skeletons or edits; explain how the plugin is enabled from `.prm`; outline build and smoke-test steps without modifying ASPECT core files unless explicitly requested.
5. **Aspect_Yuan CLI system**: use `scripts/aspect-yuan` for v0.2-dev beginner one-command lessons, model generation, starter PRM validation, ASPECT output scanning, publication figure recipe creation, scientific colormap presets, and journal-style plot presets.

## Required Workflow

1. Restate the user's target in plain geoscience language.
2. Decide whether this is a **paper reproduction task** or a **new model design task**.
3. For paper reproduction, run the paper-first workflow before model generation:
   - read `references/paper_reproduction_first.md`;
   - run `scripts/detect_aspect_reproduction_context.py` on the paper text, README, downloaded code directory, or user notes when available;
   - read `references/aspect_version_strategy.md` and `references/aspect_installation_matrix.md`;
   - identify the exact ASPECT version/commit, required plugins, external data, and original `.prm` files;
   - if the version cannot be verified, mark it `unknown` and list concrete evidence needed. Do not guess.
4. For new model design from a user description, read `references/model_family_version_map.md` first, then choose a model family, likely ASPECT version strategy, local cookbook/benchmark starting point, and template/wizard.
5. Identify the ASPECT implementation strategy: dimension, geometry model, material model, temperature/composition initialization, boundary conditions, gravity, mesh refinement, solver outputs, and expected diagnostics.
6. Read only the references needed for the task:
   - v0.1/v0.2 onboarding and scope: `references/v0_1_quickstart.md`, `references/v0_1_release_boundary.md`, and `references/v0_2_beta_release_boundary.md`
   - Paper reproduction first: `references/paper_reproduction_first.md`
   - Version/installation selection: `references/aspect_version_strategy.md`, `references/aspect_installation_matrix.md`, and `references/model_family_version_map.md`
   - General problem translation: `references/geological_problem_to_aspect.md`
   - PRM generation or review: `references/prm_for_geologists.md`, `references/prm_section_meaning.md`, `references/aspect300_prm_patterns.md`, `references/aspect300_case_map.md`, and `references/aspect300_local_inventory.md`
   - Plugin work: `references/plugins_for_geologists.md`, `references/aspect300_plugin_interfaces.md`, and templates in `assets/plugin_templates/`
   - PRM error diagnosis: `references/common_prm_mistakes.md`
   - General error diagnosis: `references/common_errors_for_geologists.md`
   - Output interpretation: `references/result_interpretation.md`
   - Scientific safety checks: `references/scientific_guardrails.md`
   - Scenario-specific wizards in `model_wizards/`
   - Beginner `.prm` templates: copy from `assets/prm_templates/`
   - Explanation and run-report templates: copy from `assets/explanation_templates/`
   - Parameter-file linting: when checking a `.prm`, run `scripts/aspect_prm_lint.py path/to/file.prm` before deeper interpretation
   - Unified CLI: use `scripts/aspect-yuan --help` to discover implemented v0.2-dev commands
   - Environment discovery: before running ASPECT, use `scripts/aspect-yuan env find-aspect` or `scripts/aspect-yuan env check`; prefer `ASPECT_BIN`, `ASPECT_ROOT`, `PATH`, and `--search-root /path/to/search` over hard-coded user-specific paths
   - Beginner one-command workflow: for first-time geologists use `scripts/aspect-yuan beginner subduction`, `scripts/aspect-yuan beginner mantle_convection`, or `scripts/aspect-yuan beginner rift`; add `--run --aspect-bin /path/to/aspect` only when the ASPECT executable is known, otherwise run `scripts/aspect-yuan env find-aspect` first
   - Model generator: run `scripts/aspect-yuan model list`, `scripts/aspect-yuan model create examples/models/mantle_convection_basic.yaml --output-dir /tmp/case`, and `scripts/aspect-yuan model validate /tmp/case/case.prm`
   - Output scanner: run `scripts/aspect-yuan postprocess scan output/ --json`
   - Publication plotting: run `scripts/aspect-yuan plot examples/figures/temperature.yaml`; use `output.metadata_only: true` when PyVista/VTK is not installed
   - Parameter-file explanation: run `scripts/aspect_prm_explain.py path/to/file.prm`
   - Case running: run `scripts/run_aspect_case.sh path/to/file.prm --mpi N` and keep the generated log
   - Log checking: when checking a run log, run `scripts/check_aspect_log.py path/to/run.log`
   - Result checking: when checking a case directory, run `scripts/make_case_report.py path/to/case-dir`
   - Statistics parsing/plotting: run `scripts/parse_aspect_statistics.py path/to/statistics` or `scripts/plot_statistics.py path/to/statistics`
   - Plugin build helper: run `scripts/build_aspect_plugin.sh path/to/plugin-dir --aspect-dir path/to/aspect-build`
   - Plugin request triage: run `scripts/explain_plugin_request.py "natural language request"`
   - Paper/version detection: run `scripts/detect_aspect_reproduction_context.py --text path/to/paper_or_readme.txt` or `--path path/to/downloaded/code`
   - Model-family version planning: run `scripts/plan_aspect_version.py "user geological request or paper title"`
   - Isolated ASPECT source checkout/build planning: use `scripts/install_aspect_version.sh --help`; execute only after explaining target version, install directory, dependencies, and approval needs
   - Skill validation: run `scripts/static_validate_skill.py` and `scripts/run_skill_evals.py` before packaging or installing this skill
   - Release validation: before a beta release, run `scripts/release_validate.sh --aspect-bin /path/to/aspect`; if ASPECT is unavailable, run `scripts/release_validate.sh` and report the smoke test as skipped
7. Prefer existing local ASPECT examples over invented syntax. Search `cookbooks/`, `benchmarks/`, `tests/`, `doc/`, `source/`, and `include/` before asserting a parameter or plugin API.
8. If a parameter name, subsection, plugin name, option, ASPECT version, paper code URL, or commit is uncertain, say: `needs verification with the paper supplement/code repository, local ASPECT examples, aspect --help, or official parameter documentation`.
9. When producing a `.prm`, include comments that explain geological intent, not generic programming narration.
10. When producing plugin code, keep it minimal and scoped to the requested scientific behavior. Explain the compile, enable, and smoke-test path.
11. When explaining plugin needs, first consult `references/plugins_for_geologists.md` and `references/aspect300_plugin_interfaces.md`.

## Guardrails

- Do not fabricate ASPECT parameter names or plugin APIs.
- Do not fabricate paper code versions, repository URLs, git commits, release tags, supplement filenames, or dependencies.
- Do not hard-code a developer's home directory, username, local project name, proxy, or machine-specific ASPECT path in generated instructions. Use portable placeholders such as `$HOME`, `$ASPECT_ROOT`, `$ASPECT_BIN`, `/path/to/aspect`, and `/path/to/project`.
- Do not install or overwrite ASPECT until the target version, source, install directory, and dependency path are explicit.
- Do not hide scientific tradeoffs behind numerical convenience.
- Do not convert a 3-D geological question to 2-D, change compressibility, alter rheology, remove a weak zone, change boundary velocities, or simplify material domains without asking or clearly labeling it as an optional simplification.
- If the local checkout version differs from ASPECT 3.0.0, mention the local `VERSION` and treat differences as compatibility risks.
- Keep generated models small enough to inspect first, then describe how to scale resolution, duration, or physics.

## Output Shape

For model generation:

1. Geological interpretation
2. ASPECT design choices
3. `.prm` draft or patch
4. Validation checklist
5. Expected outputs and interpretation

For Aspect_Yuan generated cases:

1. Geological starter-model meaning
2. Input config path
3. Generated case directory
4. Generated PRM/config/run helper/README files
5. Validation command and result
6. Next ASPECT smoke-test command

For beginner one-command lessons:

1. Geological starter-model meaning
2. `scripts/aspect-yuan beginner MODEL --output-dir CASE`
3. Generated case directory and beginner report
4. Whether ASPECT was run
5. Log/statistics/output scan status
6. First teaching figure path, usually composition for subduction

For publication figures:

1. Geological field being plotted
2. Output scan summary
3. Figure config and journal preset
4. Colormap/scale choice
5. Recipe and metadata paths
6. Rendered file paths, or an explicit PyVista/VTK dependency message

For paper reproduction:

1. Geological meaning of the paper model
2. Evidence table for version/code/data/plugins
3. Reproduction environment plan
4. Original `.prm` and plugin inventory
5. Minimal smoke test, then full reproduction run
6. Differences from the paper and unresolved version risks

For plugin generation:

1. Geological behavior represented by the plugin
2. Plugin type and ASPECT integration point
3. Source/header files or external plugin layout
4. `.prm` activation snippet
5. Build and smoke-test steps
