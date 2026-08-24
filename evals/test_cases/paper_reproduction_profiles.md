# Test Case: Paper Reproduction Profiles

## User Request

我有 Kaili、ONeill、Gernon 这几类真实 ASPECT 论文代码目录。请不要直接改模型，先把它们整理成标准复现项目模板，告诉我先跑哪个 smoke test、用哪个版本、要记录哪些证据。

## Expected Skill Behavior

- Treat this as paper reproduction, not new model generation.
- Use `scripts/aspect-yuan reproduce catalog`.
- Use `scripts/aspect-yuan reproduce template kaili-rift`.
- Use `scripts/aspect-yuan reproduce template oneill-hadean-mixing`.
- Use `scripts/aspect-yuan reproduce template gernon-craton-breakup`.
- Use `scripts/aspect-yuan reproduce inspect /path/to/paper-code --project PROJECT --profile auto`.
- Mention generated `SMOKE_TEST_PLAN.md`.
- Mention generated `VERSION_PLAN.md`.
- Mention generated `PAPER_REPRODUCTION_CHECKLIST.md`.
- Mention generated `parameter_inventory.csv`.
- Warn not to silently migrate ASPECT versions or modify paper PRMs.
