# ASPECT Version Strategy

Use this reference when choosing which ASPECT version to run.

## Aspect_Yuan Support Policy

This policy describes Aspect_Yuan support tiers. It is not a guarantee that every ASPECT feature, plugin, or paper model works in every patch release.

| ASPECT version | Aspect_Yuan tier | Use for new teaching models | Use for paper reproduction |
|---|---|---|---|
| ASPECT 3.0.x | primary-supported | Preferred default. | Use when paper/code also targets 3.0.x. |
| ASPECT 3.1-pre / development 3.1 | experimental | Not the safest default. | Use only when the paper explicitly targets it. |
| ASPECT 2.4.x-2.5.x | legacy-supported | Not preferred for new beginner cases. | Often appropriate for older papers; build/run in isolation. |
| ASPECT <= 2.3 | historical-reproduction | Avoid for new models. | Use exact paper version/container if possible. |
| unknown | unknown | Fingerprint ASPECT first. | Treat as compatibility testing, not exact reproduction. |

Run:

```bash
scripts/aspect-yuan env fingerprint --aspect-bin /path/to/aspect
scripts/aspect-yuan compat matrix
scripts/aspect-yuan compat check path/to/case.prm --aspect-bin /path/to/aspect
scripts/aspect-yuan compat explain path/to/case.prm --aspect-bin /path/to/aspect
```

The design is detect -> describe -> assess compatibility -> explain. Aspect_Yuan does not automatically rewrite or migrate `.prm` files between ASPECT versions.

## Decision Order

1. **Exact paper commit or release is known**: build that exact commit or tag.
2. **Paper provides a container**: use the container first, then inspect the ASPECT binary inside it.
3. **Paper provides only `.prm` and plugin code**: inspect parameter names, plugin APIs, `Additional shared libraries`, and README/CMake files to estimate the compatible version, then verify by running `aspect --help` and a parse-only or short smoke test.
4. **Only article text is available**: identify the model family and publication era, but mark version as `unknown` until code or supplement is found.
5. **New user model, no paper**: choose the newest local stable ASPECT available unless the requested feature is known to require an older/newer API. State the local `VERSION` and binary `--version`.

## Compatibility Risks

- `.prm` parameter names can move, be renamed, or change legal values.
- Plugin interfaces and registration macros can change between ASPECT releases.
- Solver defaults may change, producing different convergence behavior.
- World Builder, FastScape, particles, melt transport, free surface, and visco-plastic settings are especially version-sensitive.
- Published examples may rely on local patches that never entered ASPECT mainline.

## Risk Labels

- **LOW**: known supported ASPECT version and only basic stable PRM features detected.
- **MEDIUM**: legacy/development version or version-sensitive features such as free surface, particles, melt transport, World Builder, or visco-plastic settings.
- **HIGH**: external shared libraries/plugins, historical ASPECT versions, FastScape coupling, structural PRM errors, or major version mismatch for paper reproduction.
- **UNKNOWN**: ASPECT version or relevant feature evidence cannot be verified.

## Required Response

When version evidence is incomplete, answer with:

- what is verified;
- what is inferred;
- what remains unknown;
- the safest next command or file to inspect.

Do not say a paper used ASPECT 3.0.0 unless the paper code, supplement, log, README, or repository proves it.
