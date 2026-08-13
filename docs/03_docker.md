# Docker

Docker environment commands are planned for P1. For v0.2-dev P0, use existing paper-provided Dockerfiles when reproducing papers and record the exact `aspect --version` output.

Current supported check:

```bash
docker --version
docker compose version
```

Do not overwrite a paper repository's Dockerfile unless the user explicitly asks for a new isolated environment.

