# Aspect_Yuan 0.2 Beta Release Notes

Date: 2026-08-13

## Release Status

Aspect_Yuan 0.2 beta is ready to publish as a teaching beta for geologists learning ASPECT and starting ASPECT paper reproduction.

## Primary User Promise

A geologist can start from:

```text
I want to make a subduction model.
```

and use:

```bash
scripts/aspect-yuan beginner subduction --output-dir /tmp/my_subduction
```

or, when ASPECT is available:

```bash
scripts/aspect-yuan beginner subduction --output-dir /tmp/my_subduction --run --aspect-bin /path/to/aspect
```

to generate a runnable teaching model, run ASPECT, scan output, and create a first composition figure.

## Supported In This Beta

- One-command beginner workflow for `subduction`, `mantle_convection`, and `rift`.
- Runnable beginner subduction smoke path.
- Model generation from config files.
- Starter PRM validation.
- ASPECT run/log/statistics helpers.
- ASPECT output scanner.
- Real VTK/PyVista field plotting to PNG/PDF/SVG/TIFF.
- Figure metadata and recipe files.
- Scientific colormap presets and journal-style presets.
- Paper reproduction version/source/plugin/PRM triage helpers.
- Plugin skeletons and plugin build helper.

## Not Promised

- Automatic full paper reproduction.
- Automatic dependency installation for every ASPECT/deal.II/FastScape environment.
- Research-grade correctness of parameter values.
- Full compatibility with every ASPECT version.
- Complete publication-layout automation.
- Automatic scientific interpretation without geologist review.

## Release Validation

Command without ASPECT smoke:

```bash
scripts/release_validate.sh
```

Result:

- static validation: passed
- rule-based evals: passed for `9` cases
- unit tests: passed, `13` tests
- ASPECT smoke: skipped by design

Command with ASPECT smoke:

```bash
scripts/release_validate.sh --aspect-bin /home/yuan/fem3/aspect/build/aspect-release --smoke-dir /tmp/aspect-yuan-release-smoke-20260813
```

Result:

- static validation: passed
- rule-based evals: passed for `9` cases
- unit tests: passed, `13` tests
- beginner subduction ASPECT smoke: passed
- ASPECT exit status: `0`
- output scan status: `ok`
- generated first teaching figure:
  - `/tmp/aspect-yuan-release-smoke-20260813/beginner_subduction_crust_SP.png`
  - `/tmp/aspect-yuan-release-smoke-20260813/beginner_subduction_crust_SP.pdf`
  - `/tmp/aspect-yuan-release-smoke-20260813/beginner_subduction_crust_SP.svg`
  - `/tmp/aspect-yuan-release-smoke-20260813/beginner_subduction_crust_SP.tiff`

## Scientific Guardrail

Do not silently change the geological model to make a computation pass. Any simplification of dimension, geometry, boundary conditions, rheology, material fields, temperature structure, gravity, timescale, or resolution must be named as a scientific simplification.
