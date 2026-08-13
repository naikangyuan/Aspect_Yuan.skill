# ASPECT Installation Matrix

Use this reference before installing or building ASPECT for reproduction.

## Safe Layout

Install paper-specific versions outside the main checkout:

- Source: `$HOME/aspect-work/aspect-versions/aspect-<tag-or-commit>`
- Build: `$HOME/aspect-work/aspect-builds/aspect-<tag-or-commit>-release`
- Runs: `$HOME/aspect-work/aspect-runs/<paper-or-project>`

Never overwrite `$HOME/aspect-work/aspect` unless the user explicitly asks.

## Build Choices

- Existing local binary: use only if its `--version` matches the target or the user accepts a compatibility test.
- Git release tag: use for official ASPECT releases.
- Git commit hash: use for paper repositories that state a commit.
- Paper fork: use if the paper provides modified ASPECT source or custom plugins tied to a fork.
- Container: prefer when provided by the paper because it captures dependencies.

## Installation Checks

Before build:

- record ASPECT source URL, tag/commit, and destination directory;
- record deal.II path or `Aspect_DIR`;
- check CMake version, compiler, MPI, Trilinos, p4est, and optional plugins;
- explain disk/time cost and ask approval if downloads or long builds are needed.

After build:

- run `<aspect-bin> --version`;
- run the paper's smallest `.prm`;
- store log and generated parameters file;
- compare generated parameters against the paper archive.

## Script

Use `scripts/install_aspect_version.sh` as a guarded helper. It prepares an isolated checkout/build command path, but it should be executed only after the target version and install directory are explicit.
