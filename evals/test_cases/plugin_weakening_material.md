# Test Case: Plugin Material Weakening

## User Request

我需要一个材料模型插件，让弱带黏度随累计应变降低，用于测试断层弱化。这个内置参数好像不够表达。

## Expected Skill Behavior

- Explain the geological behavior: strain-dependent weak-zone rheology.
- Read `references/plugins_for_geologists.md` and `references/aspect300_plugin_interfaces.md`.
- Identify likely plugin type as material model plugin.
- Use `assets/plugin_templates/material_model_minimal.cc` as a starting point.
- Recommend `scripts/explain_plugin_request.py` and `scripts/build_aspect_plugin.sh`.
- State TODO/verification points for ASPECT API details and for mapping accumulated strain to model inputs.
- Do not promise the template implements strain weakening without additional code.
