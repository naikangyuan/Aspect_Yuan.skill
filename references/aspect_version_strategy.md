# ASPECT Version Strategy

Use this reference when choosing which ASPECT version to run.

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

## Required Response

When version evidence is incomplete, answer with:

- what is verified;
- what is inferred;
- what remains unknown;
- the safest next command or file to inspect.

Do not say a paper used ASPECT 3.0.0 unless the paper code, supplement, log, README, or repository proves it.
