# ASPECT Plugin Interfaces

This reference summarizes plugin interfaces from the local ASPECT checkout. The local `VERSION` reports `3.1.0-pre`; verify details against ASPECT 3.0.0 when exact compatibility matters.

## Interface Matrix

| Plugin type | Interface path | Typical source paths | Registration macro | Core function(s) | Geologist-facing meaning |
|---|---|---|---|---|---|
| Material model | `include/aspect/material_model/interface.h` | `source/material_model/simple.cc`, `source/material_model/visco_plastic.cc`, `benchmarks/rigid_shear/plugin/rigid_shear.cc`, `cookbooks/tomography_based_plate_motions/plugins/tomography_based_plate_motions.cc` | `ASPECT_REGISTER_MATERIAL_MODEL` | `evaluate(...)`, `is_compressible()`, `declare_parameters(...)`, `parse_parameters(...)` | Defines how rocks respond: density, viscosity, strength, thermal properties, reactions, melt-related properties. |
| Boundary velocity | `include/aspect/boundary_velocity/interface.h` | `source/boundary_velocity/function.cc`, `source/boundary_velocity/ascii_data.cc`, `source/boundary_velocity/gplates.cc` | `ASPECT_REGISTER_BOUNDARY_VELOCITY_MODEL` | `boundary_velocity(boundary_indicator, position)`, `declare_parameters(...)`, `parse_parameters(...)` | Defines imposed plate or wall motion on selected model boundaries. |
| Boundary temperature | `include/aspect/boundary_temperature/interface.h` | `source/boundary_temperature/function.cc`, `source/boundary_temperature/box.cc`, `source/boundary_temperature/ascii_data.cc`, `source/boundary_temperature/dynamic_core.cc` | `ASPECT_REGISTER_BOUNDARY_TEMPERATURE_MODEL` | `boundary_temperature(...)`, `minimal_temperature(...)`, `maximal_temperature(...)`, `declare_parameters(...)`, `parse_parameters(...)` | Defines surface, basal, side, or data-driven thermal boundary conditions. |
| Initial temperature | `include/aspect/initial_temperature/interface.h` | `source/initial_temperature/function.cc`, `source/initial_temperature/adiabatic.cc`, `source/initial_temperature/ascii_data.cc`, `source/initial_temperature/world_builder.cc` | `ASPECT_REGISTER_INITIAL_TEMPERATURE_MODEL` | `initial_temperature(position)`, `declare_parameters(...)`, `parse_parameters(...)` | Defines the starting thermal structure: geotherm, slab, plume, anomaly, tomography field. |
| Initial composition | `include/aspect/initial_composition/interface.h` | `source/initial_composition/function.cc`, `source/initial_composition/ascii_data.cc`, `source/initial_composition/slab_model.cc`, `source/initial_composition/world_builder.cc` | `ASPECT_REGISTER_INITIAL_COMPOSITION_MODEL` | `initial_composition(position, n_comp)`, `declare_parameters(...)`, `parse_parameters(...)` | Places rock units, weak zones, slabs, cratons, melt fields, or tracers at time zero. |
| Gravity model | `include/aspect/gravity_model/interface.h` | `source/gravity_model/vertical.cc`, `source/gravity_model/radial.cc`, `source/gravity_model/function.cc`, `source/gravity_model/ascii_data.cc`, `benchmarks/rigid_shear/plugin/rigid_shear.cc` | `ASPECT_REGISTER_GRAVITY_MODEL` | `gravity_vector(position)`, `declare_parameters(...)`, `parse_parameters(...)` | Defines body-force direction and magnitude that drive buoyancy. |
| Postprocessor | `include/aspect/postprocess/interface.h` | `source/postprocess/topography.cc`, `source/postprocess/velocity_statistics.cc`, `source/postprocess/heat_flux_statistics.cc`, `benchmarks/rigid_shear/plugin/rigid_shear.cc` | `ASPECT_REGISTER_POSTPROCESSOR` | `execute(TableHandler &statistics)`, optional `declare_parameters(...)`, `parse_parameters(...)` | Computes geological diagnostics and statistics after timesteps. |

## Common Base Classes And Helpers

- Most plugin interfaces derive from `Plugins::InterfaceBase` in `include/aspect/plugins.h`.
- Many runtime plugins also derive from `SimulatorAccess<dim>` when they need model time, geometry, material model, mesh, solution fields, or other simulator state.
- Registration macros instantiate 2-D and 3-D template versions in the local interfaces.
- `declare_parameters(ParameterHandler &prm)` declares `.prm` entries.
- `parse_parameters(ParameterHandler &prm)` reads those entries.
- Local examples often nest parameters under the same subsection that selects the plugin, such as `Material model > Simple model` or `Initial temperature model > Function`.

## External Plugin Build Pattern

Real local files:

- `doc/plugin-CMakeLists.txt`
- `benchmarks/annulus/plugin/CMakeLists.txt`
- `cookbooks/vankeken_subduction/plugin/CMakeLists.txt`

Pattern:

```cmake
cmake_minimum_required(VERSION 3.13.4)
find_package(Aspect 2.4.0 QUIET HINTS ${Aspect_DIR} ../ ../../ $ENV{ASPECT_DIR})
DEAL_II_INITIALIZE_CACHED_VARIABLES()
add_library(my_plugin SHARED my_plugin.cc)
ASPECT_SETUP_PLUGIN(my_plugin)
```

Use `-D Aspect_DIR=<path>` or environment variable `ASPECT_DIR` to point CMake to an ASPECT build or installation.

## Minimal Override Notes

- Material model: `evaluate(...)` must fill material outputs for every evaluation point, and `is_compressible()` must return a boolean. See `source/material_model/simple.cc`.
- Boundary velocity: `boundary_velocity(...)` returns `Tensor<1,dim>`. See `source/boundary_velocity/function.cc`.
- Boundary temperature: `boundary_temperature(...)` returns a scalar and min/max functions are pure virtual in the interface. See `source/boundary_temperature/constant.cc` or `source/boundary_temperature/box.cc`.
- Initial temperature: `initial_temperature(position)` returns a scalar. See `source/initial_temperature/function.cc`.
- Initial composition: `initial_composition(position, n_comp)` returns the value for one compositional field. See `source/initial_composition/function.cc`.
- Gravity model: `gravity_vector(position)` returns `Tensor<1,dim>`. See `source/gravity_model/vertical.cc`.
- Postprocessor: `execute(TableHandler &statistics)` returns a pair of display strings and may add values to `statistics`. See `source/postprocess/topography.cc`.

## `.prm` Activation Cheat Sheet

External plugin:

```text
set Additional shared libraries = ./build/libmy_plugin.so
```

Material model:

```text
subsection Material model
  set Model name = my material model
end
```

Boundary velocity:

```text
subsection Boundary velocity model
  set Prescribed velocity boundary indicators = left x: my boundary velocity
end
```

Boundary temperature:

```text
subsection Boundary temperature model
  set Fixed temperature boundary indicators = top
  set List of model names = my boundary temperature
end
```

Initial temperature:

```text
subsection Initial temperature model
  set Model name = my initial temperature
end
```

Initial composition:

```text
subsection Initial composition model
  set Model name = my initial composition
end
```

Gravity model:

```text
subsection Gravity model
  set Model name = my gravity
end
```

Postprocessor:

```text
subsection Postprocess
  set List of postprocessors = visualization, my postprocessor
end
```

Boundary syntax varies by geometry and ASPECT version. Verify with local examples or generated parameter documentation before giving a final `.prm`.
