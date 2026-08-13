# Scientific Guardrails

Use this reference before finalizing any model or plugin.

## Do Not Silently Change

- Dimension: 2-D versus 3-D.
- Geometry: box, spherical shell, chunk, annulus, or custom domain.
- Boundary conditions: velocities, temperatures, tractions, inflow/outflow, free slip.
- Rheology: viscosity law, yielding, weakening, compositional dependence.
- Material layout: crust, mantle, slab, weak zone, plume, craton, sediment.
- Gravity: direction, magnitude, approximation.
- Temperature structure: geotherm, anomalies, boundary-layer thickness.
- Timescale, velocities, lengths, units, and scaling.

## Acceptable Simplifications

A simplification is acceptable only if it is explicitly labeled and the scientific consequence is explained. Example: a 2-D cross-section can test first-order slab rollback geometry but cannot test along-strike segmentation.

## Final Check

Before giving a file or code:

- State which geological assumptions are encoded.
- State which assumptions remain defaults.
- State which ASPECT syntax needs verification.
- State how the user can tell from outputs whether the intended geology was represented.
