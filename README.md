# Aspect_Yuan Skill

Aspect_Yuan is the working name for the geologist-facing ASPECT skill built in `geologist-aspect-300`.

## Install From GitHub

This repository is published as a Codex skill: the repository root contains `SKILL.md`.

Install by cloning this repository into your Codex skills directory, or install through the Codex skill installer when using a GitHub source. Keep the repository root as the skill root.

Optional plotting dependencies:

```bash
python3 -m pip install -r requirements-optional.txt
```

Primary v0.2 development commands:

```bash
scripts/aspect-yuan model list
scripts/aspect-yuan model create examples/models/mantle_convection_basic.yaml --output-dir /tmp/aspect-yuan-demo
scripts/aspect-yuan model validate /tmp/aspect-yuan-demo/case.prm
scripts/aspect-yuan postprocess scan /tmp/aspect-yuan-demo/output
scripts/aspect-yuan plot examples/figures/temperature.yaml
```

Beginner one-command entry:

```bash
scripts/aspect-yuan beginner subduction --output-dir /tmp/my_subduction
scripts/aspect-yuan beginner subduction --output-dir /tmp/my_subduction --run --aspect-bin /path/to/aspect
```

Release validation:

```bash
scripts/release_validate.sh --aspect-bin /path/to/aspect
```

The generated models are starter cases for learning and smoke testing. Scientific interpretation still requires ASPECT validation, log/statistics checks, and comparison with the target geological question or paper.
