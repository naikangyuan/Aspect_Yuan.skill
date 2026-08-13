# Expected Output: Log Failure Triage

Must include:

- Use `scripts/check_aspect_log.py`.
- Interpret `parameter not declared` as parameter/subsection/version mismatch.
- Interpret Stokes convergence failure as numerical or rheological risk.
- Recommend `.prm` linting.
- Guardrail: do not silently change geological model to make it converge.
