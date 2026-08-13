# PRM For Geologists

Use this reference when drafting, reviewing, or explaining ASPECT `.prm` files for ordinary geologists.

## What A `.prm` File Is

An ASPECT `.prm` file is the experiment design for a geodynamics run. It states the geological domain, initial state, boundary conditions, material behavior, numerical resolution, runtime, and outputs. It is not just a solver input: changing a parameter can change the geological hypothesis.

ASPECT parameter files are organized as nested blocks:

```text
subsection Geometry model
  set Model name = box
  subsection Box
    set X extent = 1e6
  end
end
```

- `subsection` opens a named group of parameters.
- `set` assigns a value to one parameter inside the current subsection path.
- `end` closes the current subsection.

Read a subsection path as a geological sentence: `Geometry model > Box > X extent` means "the horizontal size of the box-shaped model region."

## Source Priority

1. Existing local `.prm` files in `cookbooks/`, `benchmarks/`, and `tests/`.
2. Local documentation in `doc/`.
3. `aspect --help` or official parameter documentation when available.
4. If none confirm a parameter, mark it as needing verification.

The generated inventory in `references/aspect300_local_inventory.md` and `references/aspect300_local_inventory.json` lists common subsections and parameters found in the local checkout. The local checkout reports `VERSION = 3.1.0-pre`; treat differences from ASPECT 3.0.0 as compatibility risks.

## Subsections As Geological Concepts

- `Geometry model`: the shape and coordinates of the modeled Earth region.
- `Gravity model`: the direction and magnitude of buoyancy forcing.
- `Boundary velocity model`: plate motion, convergence, extension, basal flow, or no-slip/free-slip choices.
- `Boundary temperature model`: surface cooling, basal temperature, side temperatures, or imported thermal boundary data.
- `Initial temperature model`: initial geotherm, slab anomaly, plume anomaly, adiabatic state, or imported thermal field.
- `Compositional fields`: named geological units or tracers, such as crust, lithosphere, slab, weak zone, melt, or finite strain.
- `Initial composition model`: where those geological units are placed at time zero.
- `Material model`: density, viscosity, rheology, yielding, thermal properties, phase behavior, and composition dependence.
- `Heating model`: radiogenic, shear, adiabatic, latent, or melt-related heat sources.
- `Mesh refinement`: where resolution follows slabs, weak zones, thermal gradients, particles, or free surfaces.
- `Postprocess` and `Visualization`: which measurements and maps will be written.
- `Solver parameters`, `Discretization`, and `Stabilization parameters`: numerical controls; adjust them carefully and keep the geological assumptions unchanged.

## Parameters Beginners Most Often Change

- `Dimension`
- `End time`, `Start time`, `Maximum time step`, `CFL number`
- `Output directory`, `Use years in output instead of seconds`
- `Initial global refinement`, `Initial adaptive refinement`
- Geometry sizes such as `X extent`, `Y extent`, `Z extent`, `Inner radius`, `Outer radius`, `Opening angle`
- Boundary indicators for fixed temperature, prescribed velocity, tangential velocity, zero velocity, or traction
- Temperature values such as `Top temperature`, `Bottom temperature`, `Inner temperature`, `Outer temperature`
- Material constants such as density, viscosity, thermal expansion, thermal conductivity, heat capacity, friction angle, cohesion, and viscosity bounds
- `Number of fields`, `Names of fields`, and output variables
- `List of postprocessors`, `List of output variables`, and graphical output cadence

## Parameters Not To Change Casually

- `Dimension`: changes the scientific meaning of cross-section versus volume.
- Geometry type and extents: change length scale, aspect ratio, and boundary meaning.
- Boundary indicators: names must match the selected geometry; a wrong boundary can impose motion or temperature on the wrong side.
- Boundary velocities: change tectonic forcing.
- Gravity direction or coordinate system: changes buoyancy.
- Material model name and rheology parameters: change deformation mechanism.
- `Number of fields`, `Names of fields`, and composition-dependent material lists: mismatches can silently invalidate material domains or crash.
- `Formulation`, compressibility, and mass conservation settings: change the physics approximation.
- Viscosity limits and averaging: can dominate the solution even if intended as numerical safeguards.
- Mesh refinement strategy: can decide whether a slab, weak zone, or boundary layer is resolved.
- Shared libraries and plugin names: must match built plugin files and registration names.

## From Geological Question To `.prm` Structure

1. State the geological process: convection, shortening, subduction, rifting, weak-zone localization, plume rise, melt transport, free-surface topography, or benchmark reproduction.
2. Choose dimension and geometry. Use 2-D only when a cross-section is scientifically acceptable.
3. Define materials and fields. Decide which geological units need compositional fields.
4. Define initial temperature and composition. Make geotherms, slabs, plumes, weak zones, and crustal layers explicit.
5. Define driving forces. Choose boundary velocities, tractions, gravity, and thermal boundaries.
6. Choose material model and rheology from local examples.
7. Add mesh refinement where the geological gradients live.
8. Add postprocessors and visualization variables needed to answer the science question.
9. Run `scripts/aspect_prm_lint.py` for structural risks, then validate actual ASPECT syntax with ASPECT itself.

## Drafting Rules

- Keep the first model minimal but geologically faithful.
- Use comments to explain scientific meaning.
- Separate physical assumptions from numerical controls.
- Do not change units without stating the conversion.
- Prefer named local examples: "adapted from cookbook X" or "pattern found in benchmark Y".
- Include expected diagnostics and failure modes.

## Review Rules

- Check whether boundary conditions match the stated tectonic setting.
- Check whether geometry and dimension match the cross-section or volume being modeled.
- Check whether compositions map cleanly to geological units.
- Check whether material parameters have plausible magnitudes and units.
- Check whether mesh refinement targets the process, such as slabs, weak zones, thermal gradients, or shear bands.
- Check whether postprocessors will output the fields needed to answer the science question.

## Uncertainty Language

Use this exact phrase for uncertain ASPECT syntax: `needs verification with local ASPECT examples, aspect --help, or official parameter documentation`.
