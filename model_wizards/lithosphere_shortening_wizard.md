# 地质问题

普通地质学家通常会这样描述：我想模拟陆壳或岩石圈在汇聚挤压下如何增厚、形成剪切带、发生地形隆升、下地壳流动或岩石圈根部变形。

先明确这是缩短问题，不是伸展问题。初学者第一步应使用二维剖面、分层岩石圈、左右边界汇聚速度和简单黏塑性材料，不要一开始加入真实三维地形、侵蚀、复杂断层网和全热-力-化学耦合。

# 最小可行 ASPECT 模型

Beginner：二维 box，分层 crust/mantle lithosphere 组分场，左右边界向内运动，顶部自由表面可先关闭或简化，材料模型使用本地案例中的黏塑性结构。输出温度、速度、黏度、应变率和组分。

Research：加入自由表面、上/下地壳分层、摩擦角/黏聚力差异、放射性生热、网格对剪切带和 Moho 附近加密、有限应变或粒子追踪。

Advanced/plugin：当需要非标准破裂准则、损伤弱化、复杂地形演化、侵蚀沉积耦合、或真实三维构造边界时，考虑自定义 material model、mesh deformation、postprocessor 或外部数据插件。

# 研究级模型

- 从 continental extension 或 crustal deformation 案例借用分层岩石圈、温度结构和黏塑性材料，但把边界速度改为挤压时必须明确地质含义。
- 用 shear-band benchmarks 检查局部化机制。
- 加入自由表面前先确认无自由表面的缩短模式是否合理。
- 对研究级模型，逐步测试：材料分层、屈服参数、热结构、网格分辨率、边界速度、自由表面。

# 需要的 ASPECT 组件

- `Geometry model`: 通常二维 `Box`，研究级可扩展到三维 box。
- `Boundary velocity model`: 左右边界汇聚或一侧固定一侧推动；底边界处理要明确。
- `Boundary temperature model`: 地表冷、底部热或岩石圈 geotherm 一致的边界。
- `Initial temperature model`: 分层岩石圈 geotherm。
- `Compositional fields`: 上地壳、下地壳、岩石圈地幔、弱层或 inherited zone。
- `Initial composition model`: 用 function 或 ASCII data 放置岩性分区。
- `Material model`: `Visco Plastic` 或本地黏弹/黏塑 benchmark 模式。
- `Heating model`: compositional heating 或 radiogenic heating 可用于地壳。
- `Mesh deformation` / `Free surface`: 研究地形时需要。
- `Postprocess` / `Visualization`: topography、strain rate、viscosity、composition、stress、heat flux。

# 推荐参考案例

- `cookbooks/continental_extension/continental_extension.prm`
- `cookbooks/continental_extension/doc/continental_extension_composition.prm`
- `cookbooks/continental_extension/doc/continental_extension_material_model.prm`
- `cookbooks/crustal_deformation/crustal_model_2D.prm`
- `cookbooks/crustal_deformation/crustal_model_3D.prm`
- `cookbooks/free_surface_with_crust/free_surface_with_crust.prm`
- `cookbooks/lower_crustal_flow/lower_crustal_flow_obstacle.prm`
- `benchmarks/shear_bands/shear_bands.prm`
- `benchmarks/viscoelastic_plastic_simple_shear/viscoelastic_plastic_simple_shear.prm`
- `benchmarks/viscoelastic_plastic_shear_bands/gerya_2019/gerya_2019_vep.prm`

# 推荐 .prm 结构

```text
set Dimension = 2
set End time = ...

subsection Geometry model
  subsection Box
  end
end

subsection Mesh refinement
  # refine crust, weak zone, Moho, or expected shear bands
end

subsection Boundary velocity model
  subsection Function
  end
end

subsection Boundary temperature model
end

subsection Compositional fields
end

subsection Initial composition model
end

subsection Initial temperature model
end

subsection Heating model
end

subsection Material model
  # viscoplastic or viscoelastic-plastic structure
end

subsection Mesh deformation            # optional free surface
end

subsection Gravity model
end

subsection Postprocess
  subsection Visualization
  end
end
```

# 是否需要插件

内置模型通常足够做第一版缩短模型：box、function 边界速度、composition fields、visco plastic、free surface 和常规输出都可直接使用。

需要插件的情况：自定义应变弱化律、断层愈合、各向异性、复杂黏弹塑性组合、侵蚀沉积反馈、或特殊地形/构造载荷。插件不应作为修复收敛问题的第一步；先确认基础模型物理合理。

# 常见错误

- 把伸展案例改成缩短时只改速度符号，却忘记检查弱带、温度结构和输出解释。
- 左右边界速度不平衡，产生非预期整体平移或体积变化。
- 组分场数量和材料参数列表不匹配。
- 黏度上限过低，强岩石圈无法形成。
- 未输出 strain rate、stress 或 viscosity，无法判断局部化。
- 自由表面打开后 timestep 太大，地形震荡被误解为构造信号。

# 结果应该如何检查

检查组分场是否保持上/下地壳和岩石圈分区；速度场是否为汇聚；应变率是否在预期弱层或剪切带集中；黏度是否体现强岩石圈和弱层；地形是否与缩短增厚一致；温度场是否没有被边界设置破坏；统计文件中 velocity、topography、composition 和 heat flux 是否稳定。
