## User Request

I want to model deep-shallow coupling, where global mantle flow drives a regional lithosphere model. Which ASPECT version and prm setup should I start from?

## Expected Skill Behavior

The skill should use `references/model_family_version_map.md`, `references/aspect_version_strategy.md`, `references/aspect300_case_map.md`, `cookbooks/global_regional_coupling/global_regional_coupling.prm`, `scripts/plan_aspect_version.py`, `scripts/aspect_prm_lint.py`, and `scripts/run_aspect_case.sh`.

It should classify the request as global-regional or deep-shallow coupling, mark version risk high, and recommend checking data formats and coupling scripts before generating a new model.
