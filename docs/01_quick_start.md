# Quick Start

Create a first model:

```bash
scripts/aspect-yuan model create examples/models/mantle_convection_basic.yaml --output-dir /tmp/aspect-yuan-demo
```

Validate the generated PRM:

```bash
scripts/aspect-yuan model validate /tmp/aspect-yuan-demo/case.prm
```

Run with ASPECT when available:

```bash
cd /tmp/aspect-yuan-demo
ASPECT_BIN=/path/to/aspect ./run.sh
```

Scan outputs:

```bash
scripts/aspect-yuan postprocess scan /tmp/aspect-yuan-demo/output
```

Create a figure recipe or field plot:

```bash
scripts/aspect-yuan plot examples/figures/temperature.yaml
```

