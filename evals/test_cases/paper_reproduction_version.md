## User Request

I want to reproduce an ASPECT paper. The paper has a supplementary code archive, but I am not sure which ASPECT version it used.

## Expected Skill Behavior

The skill should use `references/paper_reproduction_first.md`, `references/aspect_version_strategy.md`, `references/aspect_installation_matrix.md`, `scripts/detect_aspect_reproduction_context.py`, `scripts/install_aspect_version.sh`, `scripts/run_aspect_case.sh`, and `scripts/check_aspect_log.py`.

It should first identify DOI/title/code repository/version evidence, then plan an isolated ASPECT installation. It must not assume ASPECT 3.0.0 or silently use the current checkout.
