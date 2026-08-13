"""Environment discovery helpers for ASPECT installations."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ASPECT_EXECUTABLE_NAMES = ("aspect", "aspect-release", "aspect-debug")


@dataclass(frozen=True)
class AspectCandidate:
    path: Path
    source: str
    executable: bool
    version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "source": self.source,
            "executable": self.executable,
            "version": self.version,
        }


def discover_aspect(
    extra_roots: list[Path] | None = None,
    max_depth: int = 5,
    probe_version: bool = True,
    include_defaults: bool = True,
) -> list[AspectCandidate]:
    """Find likely ASPECT executables without assuming a user-specific path."""

    candidates: list[AspectCandidate] = []
    seen: set[Path] = set()

    def add(path: Path, source: str) -> None:
        try:
            resolved = path.expanduser().resolve()
        except OSError:
            return
        if resolved in seen or not resolved.exists() or resolved.is_dir():
            return
        seen.add(resolved)
        executable = os.access(resolved, os.X_OK)
        version = _aspect_version(resolved) if executable and probe_version else None
        candidates.append(AspectCandidate(resolved, source, executable, version))

    env_bin = os.environ.get("ASPECT_BIN")
    if env_bin:
        add(Path(env_bin), "ASPECT_BIN")

    env_root = os.environ.get("ASPECT_ROOT")
    if env_root:
        _search_root(Path(env_root), "ASPECT_ROOT", add, max_depth=max_depth)

    for name in ASPECT_EXECUTABLE_NAMES:
        found = shutil.which(name)
        if found:
            add(Path(found), f"PATH:{name}")

    roots = _default_search_roots() if include_defaults else []
    if extra_roots:
        roots = [Path(p) for p in extra_roots] + roots
    for root in roots:
        _search_root(root, f"search:{root}", add, max_depth=max_depth)

    candidates.sort(key=lambda c: (not c.executable, _source_rank(c.source), str(c.path)))
    return candidates


def resolve_aspect_binary(aspect_bin: str | None = None) -> str:
    """Resolve the ASPECT executable for run helpers."""

    if aspect_bin:
        return aspect_bin
    candidates = discover_aspect(probe_version=False)
    for candidate in candidates:
        if candidate.executable:
            return str(candidate.path)
    return "aspect"


def format_aspect_candidates(candidates: list[AspectCandidate]) -> str:
    if not candidates:
        return (
            "No ASPECT executable was found.\n"
            "Set ASPECT_BIN=/path/to/aspect, add ASPECT to PATH, or pass --search-root PATH."
        )
    lines = ["ASPECT candidates:"]
    for index, candidate in enumerate(candidates, start=1):
        status = "executable" if candidate.executable else "not executable"
        version = f" | {candidate.version}" if candidate.version else ""
        lines.append(f"{index}. {candidate.path} [{status}, {candidate.source}{version}]")
    lines.append("")
    lines.append(f"Recommended ASPECT_BIN: {candidates[0].path}")
    return "\n".join(lines)


def environment_check(extra_roots: list[Path] | None = None, include_defaults: bool = True) -> dict[str, Any]:
    tools = {
        "git": shutil.which("git"),
        "cmake": shutil.which("cmake"),
        "mpirun": shutil.which("mpirun") or shutil.which("mpiexec"),
        "python3": shutil.which("python3"),
        "docker": shutil.which("docker"),
        "paraview": shutil.which("paraview"),
    }
    candidates = discover_aspect(extra_roots=extra_roots, probe_version=True, include_defaults=include_defaults)
    return {
        "tools": {name: {"found": bool(path), "path": path} for name, path in tools.items()},
        "aspect": {
            "found": bool(candidates),
            "recommended": str(candidates[0].path) if candidates else None,
            "candidates": [candidate.to_dict() for candidate in candidates],
        },
        "environment": {
            "ASPECT_BIN": os.environ.get("ASPECT_BIN"),
            "ASPECT_ROOT": os.environ.get("ASPECT_ROOT"),
        },
    }


def format_environment_check(result: dict[str, Any]) -> str:
    lines = ["Environment check:"]
    for name, info in result["tools"].items():
        status = "PASS" if info["found"] else "WARNING"
        path = info["path"] or "not found"
        lines.append(f"- {status}: {name}: {path}")
    aspect = result["aspect"]
    if aspect["found"]:
        lines.append(f"- PASS: ASPECT: {aspect['recommended']}")
    else:
        lines.append("- WARNING: ASPECT: not found. Set ASPECT_BIN or install/build ASPECT first.")
    return "\n".join(lines)


def _default_search_roots() -> list[Path]:
    roots = [Path.cwd()]
    for name in ("fem3", "aspect", "ASPECT", "software", "src", "code", "projects"):
        roots.append(Path.home() / name)
    return roots


def _search_root(root: Path, source: str, add, max_depth: int) -> None:
    root = root.expanduser()
    if not root.exists():
        return
    if root.is_file():
        add(root, source)
        return
    for name in ASPECT_EXECUTABLE_NAMES:
        for relative in (
            Path(name),
            Path("build") / name,
            Path("build-release") / name,
            Path("build_debug") / name,
            Path("build-debug") / name,
            Path("bin") / name,
        ):
            add(root / relative, source)
    if max_depth <= 0:
        return
    try:
        for path in root.rglob("*"):
            if len(path.relative_to(root).parts) > max_depth:
                continue
            if path.name in ASPECT_EXECUTABLE_NAMES:
                add(path, source)
    except (OSError, PermissionError):
        return


def _aspect_version(path: Path) -> str | None:
    try:
        proc = subprocess.run([str(path), "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    for line in lines:
        lower = line.lower()
        if "aspect" in lower or "version" in lower:
            return line
    return None


def _source_rank(source: str) -> int:
    if source == "ASPECT_BIN":
        return 0
    if source == "ASPECT_ROOT":
        return 1
    if source.startswith("PATH:"):
        return 2
    return 3
