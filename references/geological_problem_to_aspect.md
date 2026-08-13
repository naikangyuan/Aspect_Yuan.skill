# Geological Problem To ASPECT

Use this reference when translating a geologist's question into an ASPECT model.

## Translation Checklist

- **Scientific question**: What process is being tested: convection, subduction, extension, shortening, plume rise, delamination, craton-edge flow, or weak-zone localization?
- **Dimensionality**: 2-D is a cross-section assumption; 3-D is required for along-strike variability, toroidal flow, oblique convergence, plume-lithosphere interaction, or segmented weak zones.
- **Geometry**: Box, spherical shell, chunk, annulus, or custom geometry must match the geological setting.
- **Timescale**: Convert geological duration to model end time and output cadence.
- **Material domains**: Mantle, crust, slab, lithosphere, asthenosphere, weak zone, plume, craton, sediment, or air/overburden proxies must map to compositions or plugin logic.
- **Thermal structure**: Decide whether to use boundary-layer geotherms, half-space cooling, prescribed anomalies, adiabatic mantle, or data-derived fields.
- **Rheology**: Choose viscosity law and yielding assumptions from the science goal. Never switch rheology silently to improve convergence.
- **Driving forces**: Boundary velocities, density contrasts, buoyancy, slab pull, basal traction, imposed inflow, or free convection must be explicit.
- **Outputs**: Match outputs to scientific tests: velocity, temperature, composition, viscosity, strain rate, stress, topography, heat flux, melt, or particles.

## First Answer Pattern

Start with: "Geologically, this model represents ..." Then map the scientific elements to ASPECT subsections and plugins.

If the user's description omits essential choices, make conservative defaults and label them as defaults, or ask a focused question if the default would change the science.
