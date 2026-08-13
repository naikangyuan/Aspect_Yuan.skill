# Validation Report: 09 Validate Templates And Evals

Date: 2026-08-10

## Scope

This validation pass checks that the first version of `geologist-aspect-300` is no longer only content-complete, but also has repeatable static validation and eval coverage.

## Completed Checks

### Static validation

Command:

```bash
python3 .codex-skill-dev/geologist-aspect-300/scripts/static_validate_skill.py
```

Result: passed.

Checked:

- all beginner `.prm` templates with `scripts/aspect_prm_lint.py`;
- teaching-template and ASPECT-verification warning headers;
- `output-...` output directory convention;
- wizard/reference/SKILL local path references;
- Python syntax;
- script `--help` behavior;
- executable bits;
- eval test cases paired with expected outputs.

### Rule-based skill evals

Command:

```bash
python3 .codex-skill-dev/geologist-aspect-300/scripts/run_skill_evals.py
```

Result: passed for 8 cases.

Eval cases:

- `evals/test_cases/mantle_convection_beginner.md`
- `evals/test_cases/weak_zone_beginner.md`
- `evals/test_cases/subduction_beginner.md`
- `evals/test_cases/rift_beginner.md`
- `evals/test_cases/plugin_weakening_material.md`
- `evals/test_cases/log_failure_triage.md`
- `evals/test_cases/paper_reproduction_version.md`
- `evals/test_cases/deep_shallow_coupling_version.md`

### Run/check/report script loop

Commands tested on local ASPECT sample `tests/blankenbach/statistics` and synthetic log files:

```bash
python3 .codex-skill-dev/geologist-aspect-300/scripts/parse_aspect_statistics.py tests/blankenbach/statistics --csv /tmp/geologist-aspect-validate-case/statistics.summary.csv --json
python3 .codex-skill-dev/geologist-aspect-300/scripts/check_aspect_log.py /tmp/geologist-aspect-validate-case/case.run.log
python3 .codex-skill-dev/geologist-aspect-300/scripts/make_case_report.py /tmp/geologist-aspect-validate-case --output /tmp/geologist-aspect-validate-case/case_report.md
```

Result: passed.

## Real ASPECT Smoke Tests

Executable used:

```bash
/home/yuan/fem3/aspect/build/aspect-release --version
```

Result: available and runnable. The executable reports `ASPECT 3.1.0-pre (main, e3feda6c7)`, so this is a real ASPECT smoke test but not a strict ASPECT 3.0.0 binary test.

Smoke runs were executed in `/tmp/geologist-aspect-smoke` so the ASPECT source tree and original cookbook/benchmark files were not modified.

### Passed

```bash
scripts/run_aspect_case.sh /tmp/geologist-aspect-smoke/01_convection/case.prm --aspect-bin /home/yuan/fem3/aspect/build/aspect-release
scripts/run_aspect_case.sh /tmp/geologist-aspect-smoke/02_weak_zone_updated/case.prm --aspect-bin /home/yuan/fem3/aspect/build/aspect-release
scripts/run_aspect_case.sh /tmp/geologist-aspect-smoke/03_plume_updated/case.prm --aspect-bin /home/yuan/fem3/aspect/build/aspect-release
```

Results:

- `beginner_2d_box_convection.prm`: passed; reached `t=0.5 seconds`, exit status `0`.
- `beginner_weak_zone.prm`: passed after template fix; reached `t=1e6 years`, exit status `0`.
- `beginner_plume.prm`: passed after template fix; reached `t=200e6 years`, exit status `0`.

The run/check/report loop also passed on the real outputs:

```bash
scripts/check_aspect_log.py <run-log>
scripts/parse_aspect_statistics.py <output-dir>/statistics --csv <summary.csv> --json
scripts/make_case_report.py <case-dir> --output <case-dir>/case_report.md
```

### Template fixes from smoke tests

- `beginner_weak_zone.prm`: changed the simple-shear velocity boundary from `top x` / `bottom x` component-only constraints to full top/bottom function constraints with zero vertical velocity, matching local simple-shear benchmark practice. Added `X periodic = true` and comments explaining that this represents a laterally repeated teaching shear zone.
- `beginner_plume.prm`: changed `End time` from `200e9` years to `200e6` years. The original value made the beginner smoke test effectively a 200-billion-year run; the corrected value represents a 200 Myr teaching plume model.

### Not yet run

- `beginner_lithosphere_shortening.prm`
- `beginner_rift.prm`
- `beginner_subduction.prm`

## Paper-Reproduction Forward Test

Date: 2026-08-11

This validation used two real local ASPECT paper-code directories provided by the user:

- `/home/yuan/aspect-fast_kaili`
- `/home/yuan/fem3/paper-Gernon-Co-evolution-of-craton-margins-and-interiors-during-continental-breakup-main`

### Version detection

Command:

```bash
scripts/detect_aspect_reproduction_context.py --path <paper-code-dir> --json
```

Results:

- Kaili Li et al., *The impact of orogenic inheritance on rifted margin formation*:
  - detected ASPECT version evidence: `2.4.0-pre`;
  - detected paper ASPECT fork commit: `8eb11069463af55995f81ef5527acc7f3bf40f5c`;
  - detected base ASPECT commit: `84d40e745328f62df1a09e15a9f1bb4fdc86141a`;
  - detected FastScape commit: `511ff22fde57317bbab836b35c3e51fab061f24e`;
  - detected Dockerfile, embedded ASPECT source directory, paper `.prm` files, paper plugin source files, and run log/statistics outputs.
- Gernon et al., *Co-evolution of craton margins and interiors during continental breakup*:
  - detected ASPECT fork branch/commit evidence: `fastscape_update_again`, `a1f0aa5`;
  - detected base ASPECT commit evidence: `84d40e7`;
  - detected deal.II evidence: `10.0.0-pre`;
  - detected 5 paper `.prm` files in `prms/`;
  - detected prebuilt paper plugin libraries `libriftplugin_d10.release.so` and `libriftplugin_d10.debug.so`;
  - separated embedded ASPECT source `.prm` samples from paper model `.prm` files.

### Tool fixes from forward test

- `scripts/detect_aspect_reproduction_context.py` now separates paper `.prm` files, embedded ASPECT source `.prm` files, paper plugin files, embedded source plugin samples, run logs/statistics, and embedded ASPECT source directories.
- `scripts/make_case_report.py` now detects `log.txt` and writes derived CSV artifacts beside the requested report output instead of writing into the original case directory.
- `scripts/install_aspect_version.sh` now accepts `--fastscape-dir` and includes `-DFASTSCAPE_DIR=...` in the ASPECT CMake plan.

### Existing-output report loop

Commands:

```bash
scripts/check_aspect_log.py "/home/yuan/aspect-fast_kaili/The_impact_of_orgenic_inheritance_on_rifted_margin formation/inputfiles_outputs/Model_S5/log.txt"
scripts/parse_aspect_statistics.py "/home/yuan/aspect-fast_kaili/The_impact_of_orgenic_inheritance_on_rifted_margin formation/inputfiles_outputs/Model_S5/statistics" --csv /tmp/kaili-model-s5-statistics-summary.csv --json
scripts/make_case_report.py "/home/yuan/aspect-fast_kaili/The_impact_of_orgenic_inheritance_on_rifted_margin formation/inputfiles_outputs/Model_S5" --output /tmp/kaili-model-s5-case-report.md
```

Result: passed.

Key values from `Model_S5/statistics`:

- rows: `2001`;
- columns: `78`;
- final time: `25e6 years`;
- final time step: `2000`;
- final mesh cells: `238379`;
- final RMS velocity: `2.11377424e-02 m/year`;
- final max velocity: `6.20556347e-02 m/year`.

### Installation dry-run planning

Commands:

```bash
scripts/install_aspect_version.sh --source-url https://github.com/Kaili270/aspect.git --ref 8eb11069463af55995f81ef5527acc7f3bf40f5c --prefix /home/yuan/fem3/aspect-versions/kaili-orogenic-inheritance --deal-ii-dir /path/to/dealii-9.3.0 --fastscape-dir /path/to/fastscape-511ff22-build --dry-run
scripts/install_aspect_version.sh --source-url https://github.com/EstherHeck/aspect.git --ref a1f0aa5 --prefix /home/yuan/fem3/aspect-versions/gernon-craton-breakup --deal-ii-dir /path/to/dealii-10.0.0-pre --dry-run
```

Result: both produced isolated source/build plans without modifying the user's existing ASPECT checkout.

### Exact Docker smoke test

Date: 2026-08-11

Image:

```bash
aspect-fastscape:local
```

The local image already existed, so no rebuild was needed for this pass. Container version check:

```bash
docker run --rm aspect-fastscape:local aspect --version
```

Result:

- ASPECT `2.4.0-pre`;
- deal.II `9.3.0`;
- Trilinos `12.14.1`;
- p4est `2.2.0`;
- optimized mode.

The ASPECT and deal.II versions match the paper repository's main version evidence. Trilinos differs from the README's HLRN installation note (`12.18.1`), so this remains an environment-difference risk for exact numerical reproduction.

Exact `.prm` startup smoke:

```bash
timeout 120s docker/run-model.sh --mode opt --np 1 --output /tmp/aspect-fastscape-smoke-output --prm /workspace/inputfiles_outputs/Model_S5/continental_extension.prm
```

Result: externally timed out after 120 seconds with exit code `124`; this is not a complete model run. It is a startup smoke test using the paper-provided `.prm` path without changing geological settings.

Verified startup evidence:

- loaded shared library `/libriftplugin_r9.3.so`;
- initialized ASPECT/FastScape topography messages;
- created output files in `/tmp/aspect-fastscape-smoke-output`;
- reached `Timestep 0`;
- assembled initial model with `22,400` active cells and `1,016,292` degrees of freedom;
- solved the first Stokes system with `174+0` iterations;
- performed initial adaptive refinement to `39,620` active cells and `1,802,459` degrees of freedom before the external timeout.

Generated smoke artifacts:

- `/tmp/aspect-fastscape-smoke-output/log.txt`;
- `/tmp/aspect-fastscape-smoke-output/original.prm`;
- `/tmp/aspect-fastscape-smoke-output/parameters.prm`;
- `/tmp/aspect-fastscape-smoke-output/parameters.json`;
- `/tmp/aspect-fastscape-smoke-output/statistics`;
- `/tmp/aspect-fastscape-smoke-report.md`.

The smoke `statistics` file exists but is empty because the run was stopped before normal postprocessing output. `scripts/make_case_report.py` now flags this as `empty statistics`.

## Remaining Risk

- Three beginner `.prm` templates are proven runnable with the local ASPECT executable: convection, weak zone, and plume.
- The lithosphere shortening and rift templates pass startup/partial smoke with local ASPECT, but they were externally stopped before normal completion.
- The subduction beginner template has been replaced with a lower-resolution runnable teaching model based on the local ASPECT low-resolution kinematically driven subduction test.
- The local checkout reports `VERSION = 3.1.0-pre`, while the skill target is ASPECT 3.0.0-style workflows.
- Paper reproduction now has forward-tested version/code detection on two real ASPECT paper repositories. A Docker startup smoke test has run for Kaili `Model_S5`, but it was externally timed out and is not a complete reproduction run.
- Runtime failures must be fixed without silently changing geometry, boundary conditions, rheology, material fields, temperature structure, gravity, dimension, or timescale.

## v0.1 Beta Release Prep

Date: 2026-08-11

Added release-facing documentation:

- `references/v0_1_quickstart.md`: three entry points for geologists: reproduce a paper, model a geological question, and understand a `.prm`/log/statistics file.
- `references/v0_1_release_boundary.md`: explicit 0.1 support scope, non-promises, and the rule that geological meaning must not be silently changed.
- `SKILL.md`: updated to route first-time users to the v0.1 quickstart and to require release-boundary language for beta claims.

Remaining beginner template smoke tests:

| Template | Smoke command | Result | Evidence |
|---|---|---|---|
| `assets/prm_templates/beginner_lithosphere_shortening.prm` | `timeout 180s scripts/run_aspect_case.sh /tmp/geologist-aspect-v01-smoke/shortening/case.prm --aspect-bin /home/yuan/fem3/aspect/build/aspect-release` | Partial startup smoke passed; externally timed out, no internal fatal pattern. | Reached statistics timestep 7, model time `1.4e5 years`, `6080` cells; report: `/tmp/geologist-aspect-v01-smoke/shortening/case_report.md`. |
| `assets/prm_templates/beginner_rift.prm` | `timeout 180s scripts/run_aspect_case.sh /tmp/geologist-aspect-v01-smoke/rift/case.prm --aspect-bin /home/yuan/fem3/aspect/build/aspect-release` | Partial startup smoke passed; externally timed out, no internal fatal pattern. | Reached statistics timestep 12, model time `2.4e5 years`, `6080` cells; report: `/tmp/geologist-aspect-v01-smoke/rift/case_report.md`. |
| `assets/prm_templates/beginner_subduction.prm` | `timeout 180s scripts/run_aspect_case.sh /tmp/aspect-yuan-subduction-cli-case/case.prm --aspect-bin /home/yuan/fem3/aspect/build/aspect-release` | Passed local ASPECT smoke from the `aspect-yuan model create` entry point. | Exit status `0`; reached timestep `1` at `1.0e5 years`; `1792` cells; final Stokes iterations `13`; report: `/tmp/aspect-yuan-subduction-cli-case/case_report.md`. |

### Subduction beginner template repair

Date: 2026-08-12

The old 7-field beginner subduction template failed local ASPECT startup smoke at timestep 0 after the mesh coarsened from 1024 cells to 256 cells. The replacement template follows the runnable local ASPECT low-resolution test `tests/kinematically_driven_subduction_2d_case1.prm`.

Scientific change is explicit: the beginner model simplifies the research cookbook's 7 compositional fields to 3 teaching fields (`OP`, `ML_SP`, `crust_SP`). It keeps the same core box size, right-boundary kinematic subduction forcing, density/viscosity contrast, and prescribed-velocity subduction concept.

Validation evidence:

- Generated through `scripts/aspect-yuan model create examples/models/subduction_basic.yaml --output-dir /tmp/aspect-yuan-subduction-cli-case`.
- `scripts/aspect-yuan model validate /tmp/aspect-yuan-subduction-cli-case/case.prm`: `PASS`.
- ASPECT run with `/home/yuan/fem3/aspect/build/aspect-release`: exit status `0` in about 4 seconds.
- `scripts/check_aspect_log.py`: normal end, no issues.
- `scripts/parse_aspect_statistics.py`: `2` rows, `28` columns; final model time `1.0e5 years`.
- `scripts/aspect-yuan postprocess scan`: detected `solution.pvd`, `pvtu`, `vtu`, `statistics`, `log.txt`, and variables `temperature`, `pressure`, `velocity`, `viscosity`, `strain_rate`, `density`.
- `scripts/aspect-yuan plot /tmp/aspect-yuan-subduction-viscosity.yaml`: generated PNG/PDF/SVG/TIFF; PNG size `1600 x 900`, grayscale standard deviation `70.45`.

Release validation commands:

```bash
python3 scripts/static_validate_skill.py
python3 scripts/run_skill_evals.py
```

Release validation result:

- `python3 scripts/static_validate_skill.py`: passed on 2026-08-11 after fixing the Quickstart wildcard path reference.
- `python3 scripts/run_skill_evals.py`: passed on 2026-08-11 for `8` eval cases.

v0.1 beta status:

- Ready for geologist-facing beta use as a learning, paper-reproduction triage, model-planning, and output-checking skill.
- Not a guarantee of complete paper reproduction, dependency installation, or research-grade parameter correctness.
- Release notes must state that exact reproduction starts from version identification and isolated install planning, not from rewriting paper `.prm` files.

## Next Step

For exact reproduction, run the Kaili Docker `Model_S5` case to normal completion or add a separate paper-author-approved smoke `.prm` that shortens only numerical duration/output for startup testing while documenting that it is not the published geological run. Separately continue the beginner smoke-test sequence with `beginner_lithosphere_shortening.prm`, `beginner_rift.prm`, and `beginner_subduction.prm`.
