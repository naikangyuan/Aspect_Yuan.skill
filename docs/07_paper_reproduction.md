# Paper Reproduction

Paper reproduction remains evidence-first.

Current supported commands:

```bash
scripts/aspect-yuan reproduce catalog
scripts/aspect-yuan reproduce template kaili-rift /tmp/kaili-repro
scripts/aspect-yuan reproduce inspect /path/to/paper-code --project /tmp/kaili-repro --profile auto
scripts/aspect-yuan reproduce status /tmp/kaili-repro
scripts/detect_aspect_reproduction_context.py --path /path/to/paper-code --json
scripts/plan_aspect_version.py "paper title or geological model"
```

Built-in reproduction profiles:

- `kaili-rift`: rifted margin/orogenic inheritance style projects with ASPECT plugins and FastScape evidence.
- `oneill-hadean-mixing`: Hadean lateral mixing / mantle convection style projects.
- `gernon-craton-breakup`: craton margin/interior breakup style projects.

`reproduce inspect` writes:

- `reproduction.yaml`
- `reproduction_profile.yaml` when a profile is detected or selected
- `REPRODUCTION_REPORT.md`
- `parameter_inventory.csv`
- `SMOKE_TEST_PLAN.md`
- `VERSION_PLAN.md`
- `PAPER_REPRODUCTION_CHECKLIST.md`

Do not claim complete paper reproduction after inspection alone. Report the ASPECT version, commit, plugins, PRM paths, Docker evidence, and smoke-test result.
