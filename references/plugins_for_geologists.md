# Plugins For Geologists

Use this reference when a geologist's scientific question cannot be represented cleanly with built-in ASPECT `.prm` options.

## When A Geologist Needs A Plugin

Try built-in `.prm` features first. A plugin is justified when the geological behavior is a new rule, not just a new number:

- a rheology, density law, weakening law, phase rule, or melt law not available in built-in material models;
- a boundary velocity that depends on time, position, plate geometry, or imported data in a way built-in `function` or `ascii data` cannot express;
- a boundary temperature that depends on geology, time, topography, or other model state;
- an initial temperature field such as a custom slab, plume, geotherm, or tomography-derived field that is too complex for `Function` or `Ascii data`;
- an initial composition field for realistic faults, cratons, slabs, weak zones, or mapped lithologies;
- a gravity field that is not vertical/radial/function/ascii-data enough for the problem;
- a postprocessor that computes a geologically meaningful diagnostic such as trench retreat rate, integrated weak-zone strain, lithosphere thickness, plume flux, or custom heat-flow statistics.

Do not use a plugin to hide an unclear geological assumption. First state what the plugin changes in geoscience terms.

## Plugin And `.prm` Relationship

A plugin is compiled C++ code loaded by ASPECT. The `.prm` file controls it in two steps:

1. If the plugin is external, load the shared library:

```text
set Additional shared libraries = ./libmy_plugin.so
```

2. Select the registered plugin name in the appropriate subsection:

```text
subsection Material model
  set Model name = my material model
  subsection My material model
    set Some geological parameter = ...
  end
end
```

The shared library path and the registered `Model name` are different things. Loading a `.so` does not automatically select a plugin.

## What Plugin Types Can Change

- **Material model plugin**: density, viscosity, thermal expansivity, thermal conductivity, heat capacity, compressibility, reaction terms, additional outputs, and nonlinear dependence flags. Use for custom rheology, weak-zone behavior, composition-dependent properties, lithosphere/craton laws, melt laws, or tomography-to-density conversion.
- **Boundary velocity plugin**: velocity vector on selected boundaries. Use for plate motions, trench migration, oblique convergence, basal flow, or time-dependent boundary forcing.
- **Boundary temperature plugin**: temperature imposed on selected boundaries, plus min/max temperatures used by heat-flux diagnostics. Use for variable surface temperature, basal anomalies, lateral thermal structure, or data-driven thermal boundaries.
- **Initial temperature plugin**: starting temperature at each position. Use for slabs, plumes, lithospheric geotherms, tomography perturbations, or imported thermal reconstructions.
- **Initial composition plugin**: starting value of each compositional field at each position. Use for rock units, slabs, crust, weak zones, cratons, faults, melt regions, or mapped lithology.
- **Gravity model plugin**: gravity vector as a function of position. Use for non-standard body-force direction or magnitude.
- **Postprocessor plugin**: statistics and diagnostics at output time. Use for science measurements that ASPECT does not already write.

## Minimum Development Flow

1. Translate the geologist's request into one plugin type and one sentence of geological behavior.
2. Search local ASPECT examples before coding. Start with `references/aspect300_plugin_interfaces.md`.
3. Copy the closest template from `assets/plugin_templates/` into a new external plugin directory.
4. Rename class, registered plugin name, CMake target, and file names.
5. Add only the parameters needed for the geological behavior.
6. Build outside ASPECT source with `scripts/build_aspect_plugin.sh <plugin-dir> --aspect-dir <ASPECT build/install dir>`.
7. Add `set Additional shared libraries = ...` to the `.prm` if using an external plugin.
8. Select the plugin in the relevant `.prm` subsection.
9. Run a minimal smoke test and inspect one output field or statistic proving the plugin is active.

## Compile And Enable

Use the template `assets/plugin_templates/CMakeLists.txt.template`. It follows the local ASPECT pattern from `doc/plugin-CMakeLists.txt`, `benchmarks/annulus/plugin/CMakeLists.txt`, and `cookbooks/vankeken_subduction/plugin/CMakeLists.txt`.

Typical build:

```bash
mkdir -p build
cmake -D Aspect_DIR=/path/to/aspect/build ..
make
```

The helper script does the same without modifying ASPECT source:

```bash
.codex-skill-dev/geologist-aspect-300/scripts/build_aspect_plugin.sh ./my_plugin --aspect-dir /path/to/aspect/build
```

Then in `.prm`:

```text
set Additional shared libraries = ./my_plugin/build/libmy_plugin.so
```

Use the exact library path produced by the build.

## Development Risks

- ASPECT API details can change between 3.0.0 and the local checkout. The local `VERSION` is `3.1.0-pre`; verify against the user's target ASPECT.
- A plugin can compile but still encode the wrong geology. Always compare output fields against the intended scientific behavior.
- Material models must fill all required output arrays consistently; missing values can produce unstable or meaningless runs.
- Boundary plugins must respect geometry boundary names and units.
- Initial-condition plugins must match declared compositional field names and counts.
- Postprocessors can be expensive if they loop over all cells every timestep.
- Shared library paths are runtime configuration; moving files can break the `.prm`.
- Do not modify `source/` or `include/` for ordinary user plugins unless the user explicitly asks to change ASPECT itself.
