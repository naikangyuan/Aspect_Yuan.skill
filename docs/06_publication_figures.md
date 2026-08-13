# Publication Figures

Use a figure config:

```bash
scripts/aspect-yuan plot templates/figures/field_temperature.yaml
```

The plotting engine writes:

- metadata JSON
- reproducible recipe JSON
- PNG/PDF/SVG/TIFF outputs when PyVista/VTK can render the selected ASPECT field

If PyVista is not installed, set `output.metadata_only: true` to validate configuration and recipe creation without rendering.

