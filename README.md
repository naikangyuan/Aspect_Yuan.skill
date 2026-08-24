# Aspect_Yuan Skill

Aspect_Yuan is a Codex skill for geologists learning ASPECT, starting from beginner runnable models and paper-reproduction workflows.

## Install

```bash
git clone https://github.com/naikangyuan/Aspect_Yuan.skill.git ~/.codex/skills/Aspect_Yuan.skill
cd ~/.codex/skills/Aspect_Yuan.skill
chmod +x scripts/*
scripts/aspect-yuan --help
```

If the Codex GitHub installer is used and `scripts/aspect-yuan` reports `Permission denied`, run `chmod +x scripts/*`.

## Smoke Test

```bash
scripts/install_smoke.sh
```

With a real ASPECT executable:

```bash
scripts/install_smoke.sh --aspect-bin /path/to/aspect
```

## First Model

```bash
scripts/aspect-yuan beginner subduction --output-dir /tmp/my_subduction
ASPECT_BIN=/path/to/aspect scripts/aspect-yuan beginner subduction --output-dir /tmp/my_subduction --run
```

## Useful Commands

```bash
scripts/aspect-yuan env find-aspect
scripts/aspect-yuan model create templates/models/subduction/config.yaml --output-dir /tmp/subduction_case
scripts/aspect-yuan model validate /tmp/subduction_case/case.prm
scripts/aspect-yuan postprocess scan /tmp/subduction_case/output
scripts/aspect-yuan reproduce init /tmp/paper_repro
scripts/aspect-yuan reproduce inspect /path/to/paper-code --project /tmp/paper_repro
scripts/aspect-yuan reproduce status /tmp/paper_repro
```

Optional plotting dependencies:

```bash
python3 -m pip install -r requirements-optional.txt
```

Generated models are teaching starters, not final research models. Scientific interpretation still requires ASPECT validation, log/statistics checks, and comparison with the target geological question or paper.
