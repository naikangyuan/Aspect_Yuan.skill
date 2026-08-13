# Model Generator

P0 supports:

- `mantle_convection`
- `subduction`
- `rift`

Create:

```bash
scripts/aspect-yuan model create examples/models/rift_basic.yaml --output-dir /tmp/rift-basic
```

The output directory contains `case.prm`, `config.yaml`, `run.sh`, `output/`, and `README.md`.

Validate before running:

```bash
scripts/aspect-yuan model validate /tmp/rift-basic/case.prm
```

