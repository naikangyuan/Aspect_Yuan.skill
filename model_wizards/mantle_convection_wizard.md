# 地质问题

普通地质学家通常会这样描述：我想研究热边界层如何产生地幔对流、上升流和下降流如何组织、黏度和温度差如何控制对流强度，或者球壳中地幔流动如何影响热流和板块尺度运动。

先判断问题是局部箱体、二维球壳剖面、环形模型，还是三维球壳。初学者不要从真实三维全地幔开始；先用二维箱体或二维球壳验证温度、速度、热流和网格设置。

# 最小可行 ASPECT 模型

Beginner：从二维 Cartesian box 热对流开始。使用简单几何、上下温度边界、自由滑移或切向边界速度、简单材料模型、垂直重力和基础可视化输出。目标是看见冷下降流、热上升流、速度场和热流统计。

Research：加入温度依赖黏度、内部加热、黏度分层、球壳几何、可压缩近似、组分场或板块状边界速度。逐步提高分辨率，并用 benchmark 检查 Nusselt number、RMS velocity 或热流。

Advanced/plugin：当需要真实地震层析温度场、复杂径向物性、相变、外部热力学表、或自定义黏度律时，再考虑 Steinberger、BurnMan、World Builder、ASCII data 或自定义 material/initial temperature 插件。

# 研究级模型

- 从 `cookbooks/convection-box/convection-box.prm` 验证基本热对流。
- 用 `benchmarks/blankenbach/base_case1a.prm` 或 `benchmarks/tosi_et_al_2015_gcubed/Tosi_base.prm` 做数值对照。
- 加入三维箱体或球壳后，先保持材料模型简单，再逐步加入温度依赖黏度和内部加热。
- 对全地幔或区域球壳，检查径向重力、内外边界温度和坐标系统是否一致。
- 若研究 thermochemical plume 或大陆影响，用组分场表示大陆、富集组分或密度异常。

# 需要的 ASPECT 组件

- `Geometry model`: `Box`, `Spherical shell`, `Chunk`, 或 annulus 相关案例。
- `Gravity model`: 垂直重力或径向重力。
- `Boundary temperature model`: 顶/底或内/外温度边界。
- `Boundary velocity model`: 初学者多用自由滑移/切向边界；板块驱动时加入 prescribed velocity。
- `Initial temperature model`: function、adiabatic、perturbed box、ASCII data。
- `Material model`: simple、visco plastic、Steinberger、multicomponent 或其他本地案例已有模型。
- `Heating model`: 内部加热、adiabatic heating、radiogenic heating。
- `Mesh refinement`: 热边界层、羽状体、组分界面。
- `Postprocess` / `Visualization`: 速度、温度、热流、黏度、组分、统计量。

# 推荐参考案例

- `cookbooks/convection-box/convection-box.prm`
- `cookbooks/convection-box-particles/convection-box-particles.prm`
- `cookbooks/convection_box_3d/convection_box_3d.prm`
- `cookbooks/bunge_et_al_mantle_convection/bunge_et_al.prm`
- `cookbooks/shell_simple_2d/shell_simple_2d.prm`
- `cookbooks/shell_simple_3d/shell_simple_3d.prm`
- `cookbooks/mantle_convection_with_continents_in_annulus/modelR.prm`
- `cookbooks/multicomponent_steinberger/steinberger_thermochemical_plume.prm`
- `benchmarks/blankenbach/base_case1a.prm`
- `benchmarks/tosi_et_al_2015_gcubed/Tosi_base.prm`

# 推荐 .prm 结构

```text
set Dimension = ...
set End time = ...

subsection Geometry model
  set Model name = ...
  subsection Box / Spherical shell / Chunk
  end
end

subsection Gravity model
end

subsection Boundary temperature model
end

subsection Boundary velocity model
end

subsection Initial temperature model
end

subsection Compositional fields        # only if thermochemical model
end

subsection Initial composition model   # only if using compositions
end

subsection Material model
end

subsection Heating model               # if internal/radiogenic/adiabatic heating matters
end

subsection Mesh refinement
end

subsection Postprocess
  subsection Visualization
  end
end

subsection Solver parameters
end
```

# 是否需要插件

内置模型通常足够完成 beginner 和许多 research 模型：简单热对流、box/shell 几何、温度函数、简单或黏塑性材料、常规输出都可用内置功能。

需要插件的情况：自定义黏度律、复杂相变、地震层析到温度/密度转换、外部物性数据库、特殊初始温度场、或论文中必须复现的自定义诊断。使用插件前先检查本地案例是否已有类似插件，例如 Steinberger、BurnMan、Tosi benchmark 或 tomography-based plate motions。

# 常见错误

- 把 nondimensional benchmark 参数直接当作 SI 地球参数。
- 顶/底温度和初始温度场不一致。
- 选择球壳几何但仍使用箱体边界名称。
- 黏度上下限过窄，导致温度依赖或组分依赖不起作用。
- 分辨率不足，热边界层和羽状体被数值扩散。
- 输出变量只包含温度，没有黏度、速度、热流或组分。
- 从二维结果直接解释三维流动结构。

# 结果应该如何检查

检查温度场是否形成合理边界层；速度场是否与浮力方向一致；黏度场是否体现温度或组分控制；热流统计是否稳定；RMS velocity 或 velocity statistics 是否达到准稳态；可视化中是否输出 temperature、velocity、viscosity、strain rate、heat flux、composition。球壳模型还要检查径向剖面、内外边界热流和是否存在不合理 net rotation。
