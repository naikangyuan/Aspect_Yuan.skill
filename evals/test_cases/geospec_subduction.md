# Test Case: GeoSpec Subduction

## User Request

我是地质新手。我不想一开始就写 ASPECT 参数文件。我想先用地质语言描述一个二维俯冲模型，再生成一个可以学习和测试的 ASPECT 入门 case。

## Expected Skill Behavior

- Treat this as a GeoSpec geology-first workflow, not direct PRM editing.
- Use `scripts/aspect-yuan geospec init subduction`.
- Validate with `scripts/aspect-yuan geospec validate`.
- Explain with `scripts/aspect-yuan geospec explain`.
- Generate a starter case with `scripts/aspect-yuan geospec create-case`.
- Mention example `examples/geospec/subduction_geology.yaml`.
- Fingerprint ASPECT with `scripts/aspect-yuan env fingerprint` before running.
- Check the generated PRM with `scripts/aspect-yuan compat check`.
- State that GeoSpec does not silently change geometry, boundary velocities, rheology, temperature, composition fields, dimension, or timescale.
