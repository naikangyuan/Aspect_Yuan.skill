# Common Errors For Geologists

Use this reference to diagnose model setup problems.

- **Unknown parameter or subsection**: Check spelling against local examples and `aspect --help`.
- **Model runs but geology changed**: Compare geometry, boundary velocities, material domains, and rheology against the stated science question.
- **Nonlinear solver failure**: Look for viscosity jumps, yielding thresholds, mesh resolution, timestep size, and boundary-condition conflicts before changing geology.
- **Unphysical velocities**: Check units, viscosity scale, density contrasts, imposed velocities, and gravity direction.
- **No deformation in expected weak zone**: Check composition initialization, weak-zone material parameters, and whether the material model uses composition-dependent rheology.
- **Thermal anomaly disappears or dominates**: Check diffusivity, initial temperature, boundary temperatures, mesh resolution, and output times.
- **Composition not visible**: Confirm compositional fields are declared, initialized, advected, and selected for visualization.
- **Plugin not found**: Check build/install path, registration name, shared library loading, and `.prm` selection syntax.

Always separate numerical fixes from geological changes.
