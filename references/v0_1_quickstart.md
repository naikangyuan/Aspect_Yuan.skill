# v0.1 Quickstart

Use this short guide first when helping a geologist try `geologist-aspect-300` v0.1.

## Entry 1: I have a paper to reproduce

Goal: identify the exact ASPECT code environment before running or editing models.

Minimum steps:

1. Locate the paper code folder, README, supplement, DOI, or downloaded archive.
2. Run:

```bash
scripts/detect_aspect_reproduction_context.py --path /path/to/paper-code --json
```

3. Read:

- `references/paper_reproduction_first.md`
- `references/aspect_version_strategy.md`
- `references/aspect_installation_matrix.md`

4. Identify ASPECT version/commit, external plugins, data files, original `.prm` files, Docker/container files, and existing logs/statistics.
5. If Docker or a built binary exists, run `aspect --version` first.
6. Run the smallest original `.prm` as a smoke test without changing geological settings.
7. Check outputs:

```bash
scripts/check_aspect_log.py path/to/log.txt
scripts/parse_aspect_statistics.py path/to/statistics --json
scripts/make_case_report.py path/to/case-dir --output /tmp/case_report.md
```

## Entry 2: I have a geology question to model

Goal: choose a model family and a conservative ASPECT starting point.

Minimum steps:

1. Restate the geology: process, geometry, timescale, materials, temperature, rheology, and driving forces.
2. Run:

```bash
scripts/plan_aspect_version.py "user geology question"
```

3. Read:

- `references/model_family_version_map.md`
- the selected model wizard under `model_wizards/`
- `references/prm_section_meaning.md`

4. Start from a local cookbook/benchmark or a beginner template in `assets/prm_templates/`.
5. Lint before running:

```bash
scripts/aspect_prm_lint.py path/to/model.prm
```

6. Run a small smoke test and inspect log/statistics before interpreting science.

## Entry 3: I have a `.prm`, log, or statistics file to understand

Goal: explain what the run represents and whether it is safe to interpret.

Minimum steps:

```bash
scripts/aspect_prm_lint.py path/to/model.prm
scripts/aspect_prm_explain.py path/to/model.prm
scripts/check_aspect_log.py path/to/log.txt
scripts/parse_aspect_statistics.py path/to/statistics --json
scripts/make_case_report.py path/to/case-dir --output /tmp/case_report.md
```

Always explain the geological meaning before ASPECT syntax. Do not interpret results from a dirty log, empty statistics file, missing plugin, or unverified paper version.
