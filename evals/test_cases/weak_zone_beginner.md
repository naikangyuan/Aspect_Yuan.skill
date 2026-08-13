# Test Case: Beginner Weak Zone

## User Request

我想在二维模型里放一个简单弱带，测试剪切或局部化是否沿弱带发生。先不要复杂三维断层，也不要自定义插件。

## Expected Skill Behavior

- Explain the weak zone as a geological assumption, not a numerical trick.
- Use `model_wizards/weak_zone_wizard.md`.
- Use `assets/prm_templates/beginner_weak_zone.prm`.
- Mention local sources such as `benchmarks/shear_bands/shear_bands.prm` or `benchmarks/finite_strain/simple_shear.prm`.
- Require checking composition field placement, viscosity/strain-rate output, and mesh resolution.
- Do not silently weaken the whole lithosphere.
