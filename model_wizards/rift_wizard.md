# 地质问题

普通地质学家通常会这样描述：我想研究大陆裂谷如何定位、岩石圈如何变薄、地壳如何伸展、弱带或热异常如何控制 rift 位置，以及是否形成被动大陆边缘或岩浆活动。

初学者不要从三维自然裂谷系统开始。先做二维 lithosphere extension：分层岩石圈、左右边界拉张、合理 geotherm 和可检查的弱化机制。

# 最小可行 ASPECT 模型

Beginner：二维 box，左右边界伸展速度，地壳/岩石圈地幔组分场，function 定义 geotherm，visco plastic 材料模型，输出温度、速度、组分、黏度和应变率。可以加入一个简单弱带或热扰动作为 rift seed，但必须说明它代表什么地质结构。

Research：加入自由表面、侵蚀/扩散地形、应变弱化、粒子、熔融、真实地壳分层、热-机械耦合和网格对颈缩区加密。

Advanced/plugin：当需要三维裂谷分段、真实断层演化、地貌侵蚀沉积、岩浆迁移、或复杂损伤流变时，考虑自定义 material、mesh deformation、melt 或 postprocessor 插件。

# 研究级模型

- 用 continental extension 案例学习完整结构。
- 用 Allken rift interaction 案例学习裂谷相互作用。
- 用 Kaus 2010 extension benchmark 学习黏弹/黏塑 shear band 和拉张局部化。
- 加入 melt 前，先用 global_melt 或 mid_ocean_ridge 案例理解 melt settings 和 material model。
- 研究路线：基础伸展 -> 分层材料 -> 弱带/热扰动 -> 自由表面 -> 熔融或侵蚀。

# 需要的 ASPECT 组件

- `Geometry model`: 二维 `Box` 起步。
- `Boundary velocity model`: prescribed extension on side boundaries。
- `Boundary temperature model`: 地表/底部温度边界。
- `Initial temperature model`: lithosphere geotherm、热扰动或 plume/rift seed。
- `Compositional fields`: upper crust、lower crust、mantle lithosphere、weak seed、melt field 可选。
- `Initial composition model`: 岩性分层和弱带。
- `Material model`: `Visco Plastic` 或 viscoelastic-plastic。
- `Heating model`: radiogenic/compositional heating 可用于地壳。
- `Mesh deformation`: free surface 或地形扩散。
- `Melt settings`: 只有研究熔融/岩浆时才加入。
- `Postprocess` / `Visualization`: strain rate、viscosity、composition、topography、melt、heat flux。

# 推荐参考案例

- `cookbooks/allken_et_al_2012_rift_interaction/allken.prm`
- `cookbooks/continental_extension/continental_extension.prm`
- `cookbooks/continental_extension/doc/continental_extension_boundary_conditions.prm`
- `cookbooks/continental_extension/doc/continental_extension_composition.prm`
- `cookbooks/continental_extension/doc/continental_extension_material_model.prm`
- `cookbooks/free_surface_with_crust/free_surface_with_crust.prm`
- `cookbooks/global_melt/global_melt.prm`
- `cookbooks/mid_ocean_ridge/mid_ocean_ridge.prm`
- `benchmarks/viscoelastic_plastic_shear_bands/kaus_2010/kaus_2010_extension.prm`
- `tests/continental_extension.prm`

# 推荐 .prm 结构

```text
set Dimension = 2

subsection Geometry model
  subsection Box
  end
end

subsection Boundary velocity model
  # side-boundary extension
end

subsection Boundary temperature model
end

subsection Initial temperature model
  # lithosphere geotherm and optional anomaly
end

subsection Compositional fields
  # crust, lithosphere mantle, optional weak seed
end

subsection Initial composition model
end

subsection Material model
  # viscoplastic lithosphere
end

subsection Heating model
end

subsection Mesh refinement
  # necking/weak-zone/free-surface refinement
end

subsection Mesh deformation            # optional free surface
end

subsection Melt settings                # optional melt model
end

subsection Postprocess
  subsection Visualization
  end
end
```

# 是否需要插件

内置 ASPECT 组件通常足够做 beginner 和多数二维研究级裂谷模型。Function-based initial fields、composition-aware rheology、free surface 和 melt examples 可覆盖很多问题。

需要插件的情况：真实三维 rift segmentation、非标准 damage rheology、侵蚀沉积与河流网络、复杂 melt extraction、或用户已有地质数据需要特殊插值。插件前先用二维模型确定伸展速度、热结构和弱带假设。

# 常见错误

- 把速度边界方向设反，模型变成缩短。
- 弱带或热扰动没有写入 initial composition/temperature。
- 未输出 strain rate 和 viscosity，无法判断 necking 机制。
- 自由表面 timestep 太大导致地形噪声。
- 地壳放射性生热、温度边界和 geotherm 不一致。
- melt settings 与 compositional fields/material model 不匹配。

# 结果应该如何检查

检查速度场是否为伸展；应变率是否在 rift axis、弱带或热异常处集中；地壳和岩石圈组分是否随时间变薄；黏度场是否显示热弱化或塑性屈服；地形是否形成裂谷盆地或肩部隆升；热流是否随减薄升高；若有熔融，检查 melt fraction、porosity、melt velocity 和相关统计。
