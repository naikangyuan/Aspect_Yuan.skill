# Expected Output: GeoSpec Subduction

Must include:

- GeoSpec route before direct PRM editing.
- Command: `scripts/aspect-yuan geospec init subduction`.
- Command: `scripts/aspect-yuan geospec validate`.
- Command: `scripts/aspect-yuan geospec explain`.
- Command: `scripts/aspect-yuan geospec create-case`.
- Example path: `examples/geospec/subduction_geology.yaml`.
- Version step: `scripts/aspect-yuan env fingerprint`.
- Compatibility step: `scripts/aspect-yuan compat check`.
- Guardrail: no silent changes to geometry, boundary velocities, rheology, temperature, composition fields, dimension, or timescale.
