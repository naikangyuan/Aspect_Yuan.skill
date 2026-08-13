# Run README

## Files

- Parameter file:
- Output directory:
- Related plugin libraries:

## Before Running

- Verify the `.prm` with the target ASPECT version.
- Run the skill lint helper:

```bash
python3 .codex-skill-dev/geologist-aspect-300/scripts/aspect_prm_lint.py path/to/model.prm
```

- Confirm all TODO values have been reviewed.
- Confirm output directory will not overwrite important results.

## Example Run

```bash
aspect path/to/model.prm
```

## First Outputs To Check

- `log.txt` or terminal output for parameter/plugin errors.
- `statistics` for timestep, velocity, temperature, and selected diagnostics.
- Visualization files for temperature, velocity, composition, viscosity, strain rate, heat flux, or topography.

## Common Early Failures

- Unknown subsection or parameter name.
- Boundary indicator names do not match geometry.
- Composition field count does not match material parameter lists.
- Timestep too large for deformation or thermal advection.
- Plugin library path is wrong or plugin name is not selected.
