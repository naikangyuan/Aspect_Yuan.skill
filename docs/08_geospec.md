# GeoSpec / geology.yaml

GeoSpec is a small geology-first specification for Aspect_Yuan teaching models. It records the scientific question, model family, geometry, thermal structure, motion intent, rheology intent, output checks, and guardrails before generating an ASPECT starter case.

Create a starter file:

```bash
scripts/aspect-yuan geospec init subduction --output geology.yaml
```

Validate and explain it:

```bash
scripts/aspect-yuan geospec validate geology.yaml
scripts/aspect-yuan geospec explain geology.yaml
```

Generate a teaching case:

```bash
scripts/aspect-yuan geospec create-case geology.yaml --output-dir geospec-subduction
```

The generated case still needs normal checks:

```bash
scripts/aspect-yuan model validate geospec-subduction/case.prm
scripts/aspect-yuan env fingerprint --aspect-bin /path/to/aspect
```

GeoSpec does not automatically migrate ASPECT versions, rewrite published paper PRMs, or guarantee research-grade correctness. Changes to geometry, boundary velocities, rheology, composition fields, temperature structure, gravity, dimension, and timescale must remain explicit geological choices.
