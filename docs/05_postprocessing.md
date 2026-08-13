# Postprocessing

Scan an ASPECT output directory:

```bash
scripts/aspect-yuan postprocess scan output/
scripts/aspect-yuan postprocess scan output/ --json --output output_scan.json
```

The scanner detects PVD, PVTU, VTU, statistics, depth-average files, particle outputs, and logs. It extracts PVD timesteps and variable names from VTU/PVTU headers when possible.

