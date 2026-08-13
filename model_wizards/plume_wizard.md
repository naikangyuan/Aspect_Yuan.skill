# 地质问题

普通地质学家通常会这样描述：我想研究热羽从深部上升、羽头撞击岩石圈、形成高热流或熔融，或者热化学异常如何影响地幔流动和大陆岩石圈。

先区分 thermal plume、thermochemical plume 和 plume-lithosphere interaction。初学者应从二维 box 或 chunk 中的简单热异常开始，不要直接做三维全地幔热化学羽状体。

# 最小可行 ASPECT 模型

Beginner：二维 box 或 chunk，背景地幔温度加一个圆形/高斯热异常，简单材料模型或温度依赖黏度，固定热边界和自由滑移边界。输出温度、速度、黏度和热流，确认热异常会上升。

Research：加入球壳或 chunk 几何、温度依赖黏度、化学组分、密度异常、岩石圈盖层、熔融、粒子和自适应网格。逐步检查 plume radius、excess temperature、source depth 和 viscosity contrast。

Advanced/plugin：当 plume 来自层析、热化学数据库、复杂相变、真实三维 plume conduit、或自定义熔融/密度律时，使用 ASCII data、Steinberger、BurnMan、World Builder 或自定义插件。

# 研究级模型

- 用 `plume_2D_chunk` 案例学习 chunk 几何、温度异常和温度依赖黏度。
- 用 multicomponent Steinberger thermochemical plume 学习热化学和球壳结构。
- 用 global_melt 或 mid_ocean_ridge 案例学习熔融输出，但不要一开始加入 melt。
- 对比 thermal-only 与 thermochemical plume，明确密度、黏度和组分贡献。

# 需要的 ASPECT 组件

- `Geometry model`: `Box`、`Chunk` 或 `Spherical shell`。
- `Gravity model`: 垂直或径向重力，必须与几何一致。
- `Boundary temperature model`: 顶/底或内/外热边界。
- `Initial temperature model`: function、adiabatic plus perturbation、ASCII data。
- `Compositional fields`: thermochemical plume 或密度异常时需要。
- `Initial composition model`: plume material 或富集组分。
- `Material model`: simple、visco plastic、Steinberger、multicomponent、melt global。
- `Heating model`: 可选。
- `Mesh refinement`: plume head、conduit、lithosphere base、melt region。
- `Postprocess` / `Visualization`: temperature、velocity、viscosity、composition、heat flux、melt fields。

# 推荐参考案例

- `cookbooks/plume_2D_chunk/plume2D.prm`
- `cookbooks/plume_2D_chunk/opening_angle_45degrees.prm`
- `cookbooks/plume_2D_chunk/opening_angle_90degrees.prm`
- `cookbooks/plume_2D_chunk/strongly_temperature_dependent.prm`
- `cookbooks/plume_2D_chunk/weakly_temperature_dependent.prm`
- `cookbooks/multicomponent_steinberger/steinberger_thermochemical_plume.prm`
- `cookbooks/heat_flow/heat-flow-plume.prm`
- `cookbooks/global_melt/global_melt.prm`
- `cookbooks/initial-condition-S20RTS/S20RTS.prm`
- `benchmarks/rayleigh_taylor_instability/rayleigh_taylor_instability.prm`

# 推荐 .prm 结构

```text
set Dimension = 2

subsection Geometry model
  subsection Box / Chunk / Spherical shell
  end
end

subsection Gravity model
end

subsection Boundary temperature model
end

subsection Boundary velocity model
end

subsection Initial temperature model
  # plume thermal anomaly
end

subsection Compositional fields         # only for thermochemical plume
end

subsection Initial composition model    # only for thermochemical plume
end

subsection Material model
end

subsection Mesh refinement
  # refine plume head/conduit
end

subsection Melt settings                # optional
end

subsection Postprocess
  subsection Visualization
  end
end
```

# 是否需要插件

内置 function initial temperature and composition fields are enough for simple thermal or thermochemical plume tests.

需要插件的情况：层析模型转换、复杂热化学物性、真实三维羽状体几何、压力/温度依赖熔融或自定义 plume diagnostics。插件必须服务具体科学假设，例如密度-温度转换或 melt extraction，而不是为了隐藏复杂初始条件。

# 常见错误

- plume excess temperature、半径或深度没有说明地质依据。
- 重力方向与 geometry 不一致。
- 初始 plume 太窄而网格无法解析。
- 温度依赖黏度被 viscosity bounds 截断。
- 把热羽和化学羽混在一起但没有 composition output。
- 熔融模型未输出 melt fields，无法判断岩浆产生。

# 结果应该如何检查

检查温度异常是否保持并上升；速度场是否显示浮力驱动上升流和回流；黏度场是否显示热弱化；热流是否在 plume-lithosphere interaction 区域升高；thermochemical plume 要检查 composition 是否与温度异常分离或混合；若有 melt，检查 melt fraction、porosity、melt velocity 和地表热流。
