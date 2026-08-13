# Test Case: Log Failure Triage

## User Request

我的 ASPECT 运行失败了，log 里有 parameter not declared 和 Stokes solver failed to converge。帮我判断问题，不要直接改地质模型。

## Expected Skill Behavior

- Run or recommend `scripts/check_aspect_log.py`.
- Explain parameter-not-declared as likely parameter/subsection/version mismatch.
- Explain Stokes convergence failure as numerical risk tied to viscosity contrasts, timestep, mesh, and boundary conditions.
- Recommend `scripts/aspect_prm_lint.py` on the `.prm`.
- State that geological changes such as rheology, boundary velocities, or geometry must not be changed silently.
