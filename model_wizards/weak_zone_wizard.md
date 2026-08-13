# 地质问题

普通地质学家通常会这样描述：我想在模型中加入一个已有断层、缝合带、弱化剪切带、板块边界或局部低强度区域，看看它是否控制变形集中、俯冲启动、裂谷定位或走滑变形。

弱带不是数值小技巧，而是地质假设。必须明确它的位置、宽度、深度范围、强度降低方式和代表的岩石或构造含义。

# 最小可行 ASPECT 模型

Beginner：二维 box 中放置一个简单倾斜或垂直弱带，用 compositional field 标记弱带区域，再通过材料模型给弱带较低黏度、摩擦角或黏聚力。先不加入复杂三维曲面断层或多条断裂网络。

Research：加入温度依赖、应变弱化、有限应变、粒子追踪、自由表面、弱带网格加密和不同弱化机制对比。

Advanced/plugin：当弱带强度需要随累计应变、流体压力、损伤、愈合、矿物反应或真实断层几何演化时，考虑自定义 material model、initial composition、particle property 或 postprocessor 插件。

# 研究级模型

- 用 shear-band benchmark 测试局部化和应变率输出。
- 用 finite strain 案例学习简单剪切/纯剪切下材料标记。
- 在 continental/subduction/rift 模型中把弱带作为 compositional field，而不是在所有材料中统一降低黏度。
- 对比无弱带、有弱带、不同弱带宽度和强度，避免把数值分辨率误判为地质控制。

# 需要的 ASPECT 组件

- `Geometry model`: 常用二维 `Box`；区域球壳模型需要先验证边界名称。
- `Compositional fields`: 至少一个弱带 field，也可有 crust/slab/lithosphere fields。
- `Initial composition model`: function 或 ASCII data 定义弱带形状。
- `Material model`: `Visco Plastic`、multicomponent、viscoelastic-plastic 或其他支持 composition 依赖的材料模型。
- `Boundary velocity model`: 剪切、挤压、伸展或俯冲启动的驱动。
- `Mesh refinement`: 弱带内部和边界必须有足够分辨率。
- `Particles`: 可选，用于有限应变或追踪材料历史。
- `Postprocess` / `Visualization`: strain rate、viscosity、stress、composition、plastic strain。

# 推荐参考案例

- `benchmarks/shear_bands/shear_bands.prm`
- `benchmarks/shear_bands/magmatic_shear_bands.prm`
- `benchmarks/finite_strain/simple_shear.prm`
- `benchmarks/finite_strain/pure_shear.prm`
- `benchmarks/viscoelastic_plastic_simple_shear/viscoelastic_plastic_simple_shear.prm`
- `benchmarks/viscoelastic_plastic_shear_bands/gerya_2019/gerya_2019_vep.prm`
- `cookbooks/transform_fault_behn_2007/transform_fault_behn_2007.prm`
- `cookbooks/transform_fault_behn_2007/temperature_dependent.prm`
- `cookbooks/subduction_initiation/subduction_initiation_compositional_fields.prm`

# 推荐 .prm 结构

```text
set Dimension = 2

subsection Geometry model
end

subsection Boundary velocity model
end

subsection Compositional fields
  # include weak-zone field name
end

subsection Initial composition model
  # define weak-zone geometry
end

subsection Material model
  # assign weak-zone rheology through composition-aware parameters
end

subsection Mesh refinement
  # refine the weak zone and expected shear band
end

subsection Particles                    # optional finite strain/material tracking
end

subsection Postprocess
  subsection Visualization
  end
end
```

# 是否需要插件

内置 function-based composition 和 composition-dependent material parameters 通常足够定义简单弱带。

需要插件的情况：弱带形状不能用 function 或 ASCII data 表达；强度随历史变量演化；弱化依赖孔隙压、反应、损伤或有限应变；需要自定义输出断层滑移量或弱带积分量。插件前必须先用最小模型证明弱带位置和强度对结果有可解释影响。

# 常见错误

- 弱带宽度小于网格分辨率，导致弱带不存在或被数值扩散。
- 只定义了 `Compositional fields`，但没有在 `Initial composition model` 中放置弱带。
- 组分场名字、数量和材料参数列表不一致。
- 为了收敛把整个岩石圈都弱化，失去局部弱带假设。
- 未输出 viscosity、strain rate、plastic strain 或 composition。
- 弱带位置与边界驱动不匹配，导致没有剪切集中。

# 结果应该如何检查

检查 composition field 是否准确显示弱带位置；strain rate 是否集中在弱带或其端部；viscosity 是否在弱带降低；plastic strain 或有限应变是否随时间累积；速度场是否体现预期剪切、俯冲启动或裂谷定位；网格是否在弱带足够细；对比无弱带模型确认弱带改变了结果。
