# 地质问题

普通地质学家通常会这样描述：我想研究厚而强的克拉通岩石圈边缘如何影响地幔流动、边缘驱动对流、岩石圈减薄、热流异常、弱化带或相邻活动带变形。

初学者不要直接模拟真实三维克拉通形状。先用二维 box 或 spherical slice 表示一个厚冷强的 craton keel 和相邻薄弱活动岩石圈，测试边缘流动和热结构。

# 最小可行 ASPECT 模型

Beginner：二维 box，composition fields 区分 craton keel、普通岩石圈和地幔；initial temperature 定义冷厚克拉通和相邻较热岩石圈；material model 赋予 craton 更高黏度或不同密度；边界可先用自由滑移或简单背景流。输出温度、速度、组分、黏度、热流。

Research：加入 spherical shell/chunk、真实边界速度、地震层析或 lithosphere thickness 数据、自由表面、弱带、侵蚀/热流约束、粒子追踪和热化学密度差。

Advanced/plugin：真实克拉通边界、多边形/三维 keel、数据驱动材料属性、层析速度转温度/密度、或复杂 craton erosion 机制通常需要 World Builder、ASCII data 或自定义 material/initial composition 插件。

# 研究级模型

- 用 tomography_based_plate_motions 案例学习 faults/cratons/slabs/topography 数据驱动结构。
- 用 multicomponent Steinberger plume 案例学习球壳、组分和密度/黏度差异。
- 用 mantle_convection_with_continents_in_annulus 学习大陆或强块体对对流的影响。
- 用 continental/free-surface-with-crust 案例学习岩石圈分层、自由表面和热结构。
- 研究级模型要分别测试 craton 厚度、边缘坡度、黏度对比、密度对比、背景流速和热结构。

# 需要的 ASPECT 组件

- `Geometry model`: 初学者二维 `Box`；区域或全球问题用 `Spherical shell` 或 `Chunk`。
- `Compositional fields`: craton keel、mobile belt、crust、mantle lithosphere、asthenosphere。
- `Initial composition model`: function、ASCII data 或 World Builder 定义 craton geometry。
- `Initial temperature model`: cold keel、lithosphere geotherm、adiabatic mantle 或 ASCII data。
- `Material model`: multicomponent、visco plastic、Steinberger 或 tomography-based model。
- `Boundary velocity model`: free slip、background mantle flow、plate motions。
- `Boundary temperature model`: surface/basal or spherical thermal conditions。
- `Mesh refinement`: craton edge、lithosphere-asthenosphere boundary、weak margins。
- `Postprocess` / `Visualization`: temperature、composition、viscosity、velocity、strain rate、heat flux、topography。

# 推荐参考案例

- `cookbooks/tomography_based_plate_motions/2D_slice_with_faults_and_cratons.prm`
- `cookbooks/tomography_based_plate_motions/2D_slice_with_faults_slabs_and_topo.prm`
- `cookbooks/mantle_convection_with_continents_in_annulus/modelR.prm`
- `cookbooks/multicomponent_steinberger/steinberger_thermochemical_plume.prm`
- `cookbooks/continental_extension/continental_extension.prm`
- `cookbooks/free_surface_with_crust/free_surface_with_crust.prm`
- `cookbooks/shell_simple_2d/shell_simple_2d.prm`
- `cookbooks/shell_simple_3d/shell_simple_3d.prm`
- `benchmarks/tosi_et_al_2015_gcubed/Tosi_base.prm`

# 推荐 .prm 结构

```text
set Dimension = 2

subsection Geometry model
  subsection Box / Spherical shell / Chunk
  end
end

subsection Compositional fields
  # craton, mobile lithosphere, crust, mantle fields
end

subsection Initial composition model
  # craton keel geometry
end

subsection Initial temperature model
  # cold craton geotherm and warmer surroundings
end

subsection Boundary velocity model
  # optional background flow or plate motions
end

subsection Boundary temperature model
end

subsection Gravity model
end

subsection Material model
  # composition-dependent viscosity/density
end

subsection Mesh refinement
  # craton edge and LAB refinement
end

subsection Mesh deformation            # optional free surface
end

subsection Postprocess
  subsection Visualization
  end
end
```

# 是否需要插件

内置 function composition、ASCII data, multicomponent material behavior and standard visualization can support a first craton-edge model.

需要插件的情况：真实 craton polygon/3D keel 数据、层析转换、复杂 craton-specific rheology、composition-dependent depletion buoyancy not supported by selected material model、或自定义 edge-driven convection diagnostics。插件前先建立二维简化模型，确认 craton thickness and viscosity contrast 是主要控制。

# 常见错误

- 把 craton 只做成冷温度异常，却没有强黏度或组分差异。
- craton edge 太陡或太窄，网格解析不足。
- density contrast、thermal structure 和 rheology 的地质含义混淆。
- 球壳模型仍使用 box 边界名称。
- 未输出 heat flux、viscosity、composition，无法判断 craton 是否稳定。
- 背景流或板块速度方向没有与研究假设对应。

# 结果应该如何检查

检查 craton composition 是否保持厚 keel；温度场是否显示冷厚岩石圈；黏度是否使 craton 比相邻活动带更强；速度场是否在 craton edge 形成合理绕流或下沉/上升；应变率是否集中在边缘而不是 craton 内部；热流是否在 craton 上低、边缘或活动带较高；自由表面模型还要检查地形和网格质量。
