# 地质问题

普通地质学家通常会这样描述：我想模拟一个海洋板片进入地幔，研究俯冲角度、板片年龄、汇聚速度、地幔楔流动、板片脱离、俯冲启动或含水/熔融过程。

先区分 kinematic subduction、dynamic subduction、subduction initiation 和 slab detachment。初学者不要从三维自然俯冲系统开始；先用二维剖面、固定板片几何或运动边界建立可检查模型。

# 最小可行 ASPECT 模型

Beginner：二维 box，板片和上覆板块用 composition fields 表示，初始温度用 function 定义冷板片，边界速度施加汇聚或角点流，材料模型先使用本地案例中的 multicomponent 或 visco plastic 模式。输出温度、速度、组分、黏度和应变率。

Research：加入自由表面、弱带、温度依赖黏度、板片年龄、地幔楔低黏度、相变、粒子、熔体/流体、或动态板片下沉。分阶段验证：几何、温度、速度、材料、网格。

Advanced/plugin：真实三维板片、复杂板块边界、随时间变化板块运动、相变动力学、含水熔融或外部 slab geometry 通常需要 ASCII data、World Builder、或自定义 initial composition/material/postprocessor 插件。

# 研究级模型

- 从 kinematically driven subduction 案例学习板片、边界速度、温度和后处理组织。
- 用 subduction initiation 案例学习弱带或粒子方案。
- 用 slab_detachment benchmark 学习板片断离过程。
- 对含水/熔体问题，先阅读 two-phase Tian parameterization 或 mid-ocean-ridge/global melt 相关结构，再决定是否加入 melt。
- 研究级模型必须报告板片几何、年龄、汇聚速度、弱带强度和材料参数如何控制结果。

# 需要的 ASPECT 组件

- `Geometry model`: 初学者用二维 `Box`；区域模型可用 `Chunk` 或 spherical slice。
- `Boundary velocity model`: prescribed convergence、corner flow、inflow/outflow 或自由滑移组合。
- `Boundary temperature model`: 地表冷边界、底部或侧边界热条件。
- `Initial temperature model`: 冷板片、地幔 geotherm、adiabatic 或 function。
- `Compositional fields`: slab、overriding plate、crust、mantle、weak zone、hydrated/melt fields。
- `Initial composition model`: 板片和弱带几何。
- `Material model`: multicomponent、visco plastic、phase-transition 或 melt 相关模型。
- `Mesh refinement`: 板片界面、板片尖端、地幔楔、弱带。
- `Postprocess` / `Visualization`: trench location、composition velocity statistics、temperature、viscosity、strain rate、melt、particles。

# 推荐参考案例

- `cookbooks/kinematically_driven_subduction_2d/kinematically_driven_subduction_2d_case1.prm`
- `cookbooks/kinematically_driven_subduction_2d/kinematically_driven_subduction_2d_case2a.prm`
- `cookbooks/kinematically_driven_subduction_2d/kinematically_driven_subduction_2d_case2b.prm`
- `cookbooks/subduction_initiation/subduction_initiation_compositional_fields.prm`
- `cookbooks/subduction_initiation/subduction_initiation_particle_in_cell.prm`
- `cookbooks/vankeken_subduction/vankeken_corner_flow.prm`
- `cookbooks/phase_transition_kinetics/simple-subduction.prm`
- `cookbooks/tian_parameterization_kinematic_slab/coupled-two-phase-tian-parameterization-kinematic-slab.prm`
- `benchmarks/slab_detachment/slab_detachment.prm`
- `benchmarks/buiter_et_al_2016_jsg/exp_1.prm`

# 推荐 .prm 结构

```text
set Dimension = 2
set End time = ...

subsection Geometry model
  subsection Box
  end
end

subsection Boundary velocity model
  # prescribed convergence or corner flow
end

subsection Boundary temperature model
end

subsection Compositional fields
  # slab, crust, mantle, weak zone, optional hydrated/melt fields
end

subsection Initial composition model
  # slab and plate geometry
end

subsection Initial temperature model
  # cold slab and mantle geotherm
end

subsection Material model
end

subsection Mesh refinement
  # refine slab, wedge, trench, weak zone
end

subsection Heating model                # optional
end

subsection Melt settings                # only for melt/two-phase models
end

subsection Postprocess
  subsection Visualization
  end
end

subsection Termination criteria
end
```

# 是否需要插件

内置模型足够做二维运动学俯冲、简单板片热结构、组分场板片和基础黏塑性模型。

需要插件的情况：自定义 corner-flow/velocity 边界、真实板片几何导入、复杂相变动力学、特殊地幔楔流变、含水熔融、或自定义 trench/slab diagnostics。`cookbooks/vankeken_subduction/vankeken_corner_flow.prm` 是本地外部插件示例，使用前必须确认共享库已构建。

# 常见错误

- 板片温度场和 composition 几何不重合。
- 汇聚速度方向或边界名称错误。
- 网格没有加密板片尖端和弱带。
- 把 slab age、thickness、dip 改成数值方便值而不说明。
- 没有输出 composition、viscosity、strain rate，无法判断板片是否保持。
- 打开 melt 或 phase transition 后没有检查额外 fields 和材料参数列表。
- 用二维模型解释沿走向三维变化。

# 结果应该如何检查

检查冷板片温度异常、slab composition、地幔楔速度、黏度结构、应变率集中、trench location 或 slab-tip 位置随时间变化。若有自由表面，检查地形和网格质量。若有熔体/流体，检查 porosity/melt velocity/melt fraction 输出。统计文件中 velocity、temperature、composition 和 heat flux 应与板片演化一致。
