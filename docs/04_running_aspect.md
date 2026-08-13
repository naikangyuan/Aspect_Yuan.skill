# Running ASPECT

For generated cases:

```bash
scripts/aspect-yuan env find-aspect
scripts/aspect-yuan model create examples/models/mantle_convection_basic.yaml --output-dir /tmp/aspect-yuan-demo
cd /tmp/aspect-yuan-demo
ASPECT_BIN=/path/to/aspect ./run.sh
```

For existing `.prm` files, the older run helper remains supported:

```bash
scripts/run_aspect_case.sh path/to/case.prm --aspect-bin /path/to/aspect
```

After the run:

```bash
scripts/check_aspect_log.py run.log
scripts/parse_aspect_statistics.py output/statistics --json
scripts/make_case_report.py .
```
