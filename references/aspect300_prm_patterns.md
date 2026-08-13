# ASPECT PRM Patterns

This summary is derived from local `.prm` files under `cookbooks/`, `benchmarks/`, and `tests/` in the ASPECT checkout. The local `VERSION` file reports `3.1.0-pre`; the skill target remains ASPECT 3.0.0-style workflows, so syntax differences should be checked against the user's installed ASPECT.

## Corpus Scale

- Files found by the generated inventory: 1,653 `.prm` files.
- Files found by `rg --files cookbooks benchmarks tests -g '*.prm'`: 1,652 `.prm` files.
- The small count difference is likely from filesystem traversal state. Treat the inventory as approximate and use direct path checks for exact tasks.

## Most Common Subsections

The most common subsection names in the local corpus are:

| Subsection | Count | Geological meaning |
|---|---:|---|
| `Function` | 1911 | mathematical expressions for boundary values, initial fields, or material functions |
| `Material model` | 1323 | rheology, density, thermal properties, phase or melt behavior |
| `Postprocess` | 1298 | diagnostics and output selection |
| `Mesh refinement` | 1261 | spatial resolution strategy |
| `Box` | 1232 | Cartesian box geometry details |
| `Geometry model` | 1216 | model domain shape |
| `Gravity model` | 1174 | body force direction and magnitude |
| `Initial temperature model` | 1168 | starting thermal state |
| `Boundary velocity model` | 1146 | plate/wall velocity conditions |
| `Boundary temperature model` | 859 | thermal boundary conditions |
| `Visualization` | 839 | graphical output fields |
| `Compositional fields` | 576 | named geological units or tracked fields |
| `Initial composition model` | 557 | initial placement of geological units |
| `Solver parameters` | 486 | nonlinear/linear solver controls |
| `Particles` | 345 | Lagrangian particle setup |
| `Heating model` | 194 | heat production or conversion terms |
| `Spherical shell` | 192 | spherical shell geometry details |
| `Visco Plastic` | 138 | plastic/viscous rheology controls |
| `Ascii data model` | 132 | imported gridded data |
| `Termination criteria` | 111 | stopping conditions |
| `Mesh deformation` | 86 | free-surface or moving-mesh behavior |
| `Melt settings` | 81 | melt transport controls |

## Most Common Set Parameters

Frequent top-level or subsection parameters include:

- `Model name`
- `Function expression`
- `List of model names`
- `Variable names`
- `End time`
- `List of postprocessors`
- `Dimension`
- `Initial global refinement`
- `Initial adaptive refinement`
- `Use years in output instead of seconds`
- `X extent`, `Y extent`, `Z extent`
- `Magnitude`
- `Tangential velocity boundary indicators`
- `Fixed temperature boundary indicators`
- `Time steps between mesh refinement`
- `Time between graphical output`
- `Nonlinear solver scheme`
- `Viscosity`
- `Number of fields`
- `Reference density`
- `Output directory`
- `Prescribed velocity boundary indicators`
- `Zero velocity boundary indicators`
- `Names of fields`
- `Top temperature`, `Bottom temperature`, `Inner temperature`, `Outer temperature`
- `Additional shared libraries`
- `Minimum viscosity`, `Maximum viscosity`
- `Angles of internal friction`, `Cohesions`
- `Include melt transport`

## Common Model Types And Representative Files

- **Cartesian mantle convection**: `cookbooks/convection-box/convection-box.prm`, `cookbooks/convection_box_3d/convection_box_3d.prm`, `benchmarks/blankenbach/base_case1a.prm`
- **Spherical or annulus convection**: `cookbooks/shell_simple_2d/shell_simple_2d.prm`, `cookbooks/shell_simple_3d/shell_simple_3d.prm`, `cookbooks/2d_annulus_visualization/2d_annulus_example.prm`
- **Thermochemical or composition-aware flow**: `cookbooks/composition_active/composition_active.prm`, `cookbooks/composition_passive/composition_passive.prm`, `cookbooks/multicomponent_steinberger/steinberger_thermochemical_plume.prm`
- **Lithosphere deformation**: `cookbooks/continental_extension/continental_extension.prm`, `cookbooks/crustal_deformation/crustal_model_2D.prm`, `cookbooks/free_surface_with_crust/free_surface_with_crust.prm`
- **Subduction**: `cookbooks/kinematically_driven_subduction_2d/kinematically_driven_subduction_2d_case1.prm`, `cookbooks/subduction_initiation/subduction_initiation_compositional_fields.prm`, `benchmarks/slab_detachment/slab_detachment.prm`
- **Rift or extension**: `cookbooks/allken_et_al_2012_rift_interaction/allken.prm`, `cookbooks/continental_extension/continental_extension.prm`, `benchmarks/viscoelastic_plastic_shear_bands/kaus_2010/kaus_2010_extension.prm`
- **Weak zone or shear localization**: `benchmarks/shear_bands/shear_bands.prm`, `benchmarks/finite_strain/simple_shear.prm`, `cookbooks/transform_fault_behn_2007/transform_fault_behn_2007.prm`
- **Free surface and topography**: `cookbooks/free_surface/free_surface.prm`, `cookbooks/free_surface_with_crust/free_surface_with_crust.prm`, `benchmarks/free_surface_tractions/viscous/free_surface_viscous_cylinder_2D_loading.prm`
- **Particles**: `cookbooks/convection-box-particles/convection-box-particles.prm`, `cookbooks/grain_size_ridge/grain_size_ridge.prm`, `benchmarks/finite_strain/pure_shear.prm`
- **Melt/two-phase flow**: `cookbooks/global_melt/global_melt.prm`, `cookbooks/mid_ocean_ridge/mid_ocean_ridge.prm`, `benchmarks/solitary_wave/solitary_wave.prm`
- **External plugin examples**: `cookbooks/vankeken_subduction/vankeken_corner_flow.prm`, `benchmarks/finite_strain/simple_shear.prm`, `benchmarks/davies_et_al/case-2.3.prm`

## Structural Pattern Of ASPECT Parameter Files

Many local files follow this order:

1. Top-level runtime: `Dimension`, `Start time`, `End time`, output years/seconds, solver scheme.
2. Output location: `Output directory`.
3. Discretization and refinement.
4. Geometry and gravity.
5. Boundary velocity and boundary temperature.
6. Initial temperature and initial composition.
7. Compositional fields.
8. Material model and heating model.
9. Mesh deformation, particles, melt, or plugin-specific sections if needed.
10. Postprocess and visualization.
11. Solver parameters and termination/checkpointing.

Not every file follows this order. When editing an existing model, preserve its structure unless a local pattern strongly suggests a clearer placement.

## Plugin Pattern

Some files use `set Additional shared libraries = ...`, commonly with benchmark or cookbook plugins. Examples include:

- `cookbooks/vankeken_subduction/vankeken_corner_flow.prm`
- `benchmarks/finite_strain/simple_shear.prm`
- `benchmarks/finite_strain/pure_shear.prm`
- `benchmarks/davies_et_al/case-2.3.prm`
- `benchmarks/nsinker/nsinker.prm`

For geologist-facing guidance, explain that this line loads compiled plugin libraries; it does not by itself select every plugin. The relevant `Model name` or `List of model names` must also reference registered plugin names.
