# Test Case: Beginner Mantle Convection

## User Request

我是地质学背景，想先做一个最简单的二维地幔热对流模型，看热边界层、上升流、下降流、速度和热流，暂时不考虑复杂流变和三维球壳。

## Expected Skill Behavior

- Start with geological meaning before ASPECT implementation.
- Use `model_wizards/mantle_convection_wizard.md`.
- Use `assets/prm_templates/beginner_2d_box_convection.prm`.
- Mention local source `cookbooks/convection-box/convection-box.prm`.
- Recommend `scripts/aspect_prm_lint.py` before running.
- Recommend `scripts/run_aspect_case.sh`, `scripts/check_aspect_log.py`, and `scripts/make_case_report.py` for validation.
- Warn that the beginner template is a teaching model and needs ASPECT runtime verification.
