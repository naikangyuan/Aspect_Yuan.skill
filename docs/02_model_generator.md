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

## GeoSpec / geology.yaml

GeoSpec is the geology-first entry point. It records the scientific question and geological assumptions before generating a teaching starter PRM.

```bash
scripts/aspect-yuan geospec init subduction --output /tmp/geology.yaml
scripts/aspect-yuan geospec validate /tmp/geology.yaml
scripts/aspect-yuan geospec explain /tmp/geology.yaml
scripts/aspect-yuan geospec create-case /tmp/geology.yaml --output-dir /tmp/geospec-subduction
```

`geology.yaml` is not an automatic migration format. It does not rewrite paper PRMs or hide changes to geometry, boundary conditions, rheology, temperature, composition fields, dimension, or timescale.
