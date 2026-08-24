"""ASPECT environment fingerprinting."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .compatibility import classify_version, parse_aspect_version
from .env import discover_aspect


def fingerprint_aspect(
    aspect_bin: str | None = None,
    search_roots: list[Path] | None = None,
) -> dict[str, Any]:
    """Build a portable, evidence-preserving ASPECT environment profile."""

    evidence: list[str] = []
    warnings: list[str] = []
    binary = _select_binary(aspect_bin, search_roots, evidence, warnings)
    version_raw = _run_version(binary, evidence, warnings) if binary else None
    source_root = _detect_source_root(binary, search_roots, evidence)
    version_file = _read_version_file(source_root, evidence)
    version_source = "binary --version" if version_raw else "VERSION file" if version_file else None
    aspect_version_text = version_raw or version_file
    classification = classify_version(aspect_version_text)
    git_commit = _git_commit(source_root, evidence) or _commit_from_version_raw(version_raw, evidence)
    build_root = _detect_build_root(binary, evidence)
    build_type = _detect_build_type(build_root, evidence)
    cookbooks_path = source_root / "cookbooks" if source_root and (source_root / "cookbooks").exists() else None
    world_builder = _detect_world_builder(source_root, build_root, evidence)
    parameter_schema = _detect_parameter_schema(binary, evidence)
    return {
        "schema_version": "1",
        "binary": str(binary) if binary else None,
        "aspect_version": classification["version"],
        "version_raw": version_raw,
        "version_source": version_source,
        "git_commit": git_commit,
        "source_root": str(source_root) if source_root else None,
        "build_root": str(build_root) if build_root else None,
        "build_type": build_type,
        "support_tier": classification["support_tier"],
        "version_channel": classification["version_channel"],
        "parameter_schema": parameter_schema,
        "world_builder": world_builder,
        "plugin_support": {"external_shared_libraries": "unknown"},
        "cookbooks": {"detected": bool(cookbooks_path), "path": str(cookbooks_path) if cookbooks_path else None},
        "detection_evidence": evidence,
        "warnings": warnings,
    }


def format_fingerprint(profile: dict[str, Any]) -> str:
    lines = [
        "ASPECT environment fingerprint:",
        f"- Binary: {profile.get('binary') or 'not found'}",
        f"- ASPECT version: {profile.get('aspect_version') or 'unknown'}",
        f"- Version source: {profile.get('version_source') or 'unknown'}",
        f"- Support tier: {profile.get('support_tier') or 'unknown'}",
        f"- Version channel: {profile.get('version_channel') or 'unknown'}",
        f"- Git commit: {profile.get('git_commit') or 'unknown'}",
        f"- Source root: {profile.get('source_root') or 'unknown'}",
        f"- Build root: {profile.get('build_root') or 'unknown'}",
        f"- Cookbooks: {profile.get('cookbooks', {}).get('path') or 'not detected'}",
        f"- World Builder: {'detected' if profile.get('world_builder', {}).get('detected') else 'not detected'}",
    ]
    warnings = profile.get("warnings") or []
    if warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    evidence = profile.get("detection_evidence") or []
    if evidence:
        lines.append("Evidence:")
        lines.extend(f"- {item}" for item in evidence[:12])
    return "\n".join(lines)


def _select_binary(aspect_bin: str | None, search_roots: list[Path] | None, evidence: list[str], warnings: list[str]) -> Path | None:
    if aspect_bin:
        path = Path(aspect_bin).expanduser()
        if path.exists() and path.is_file():
            resolved = path.resolve()
            evidence.append(f"explicit --aspect-bin: {resolved}")
            if not os.access(resolved, os.X_OK):
                warnings.append(f"ASPECT binary is not executable: {resolved}")
            return resolved
        warnings.append(f"explicit --aspect-bin was not found: {path}")
        return None
    candidates = discover_aspect(extra_roots=search_roots or [], probe_version=False)
    if candidates:
        evidence.append(f"selected ASPECT candidate from {candidates[0].source}: {candidates[0].path}")
        return candidates[0].path
    warnings.append("No ASPECT binary detected. Set ASPECT_BIN, pass --aspect-bin, or use --search-root.")
    return None


def _run_version(binary: Path | None, evidence: list[str], warnings: list[str]) -> str | None:
    if not binary:
        return None
    try:
        proc = subprocess.run([str(binary), "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        warnings.append(f"Could not run ASPECT --version: {exc}")
        return None
    output = proc.stdout.strip()
    if output:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        first = lines[0] if lines else output
        evidence.append(f"{binary} --version returned: {first}")
        for line in lines:
            if parse_aspect_version(line)["version"]:
                if line != first:
                    evidence.append(f"parseable version line: {line}")
                return line
        warnings.append(f"{binary} --version did not contain a parseable ASPECT version.")
        return None
    warnings.append(f"{binary} --version returned no text.")
    return None


def _detect_source_root(binary: Path | None, search_roots: list[Path] | None, evidence: list[str]) -> Path | None:
    roots: list[Path] = []
    env_root = os.environ.get("ASPECT_ROOT")
    if env_root:
        roots.append(Path(env_root).expanduser())
    if search_roots:
        roots.extend(Path(root).expanduser() for root in search_roots)
    if binary:
        roots.extend(binary.parents)
    for root in roots:
        source = _find_source_root(root)
        if source:
            evidence.append(f"source root detected: {source}")
            return source
    return None


def _find_source_root(root: Path) -> Path | None:
    try:
        root = root.resolve()
    except OSError:
        return None
    candidates = [root, *root.parents]
    for candidate in candidates:
        if (candidate / "VERSION").exists() and ((candidate / "source").exists() or (candidate / "include" / "aspect").exists()):
            return candidate
    return None


def _read_version_file(source_root: Path | None, evidence: list[str]) -> str | None:
    if not source_root:
        return None
    version_file = source_root / "VERSION"
    if not version_file.exists():
        return None
    text = version_file.read_text(errors="ignore").strip()
    if text:
        evidence.append(f"VERSION file: {version_file} -> {text}")
        return text
    return None


def _git_commit(source_root: Path | None, evidence: list[str]) -> str | None:
    if not source_root or not (source_root / ".git").exists():
        return None
    try:
        proc = subprocess.run(["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    commit = proc.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", commit):
        evidence.append(f"git commit from source root: {commit}")
        return commit
    return None


def _commit_from_version_raw(version_raw: str | None, evidence: list[str]) -> str | None:
    if not version_raw:
        return None
    match = re.search(r"\b([0-9a-f]{7,40})\b", version_raw)
    if not match:
        return None
    commit = match.group(1)
    evidence.append(f"git commit candidate from ASPECT --version: {commit}")
    return commit


def _detect_build_root(binary: Path | None, evidence: list[str]) -> Path | None:
    if not binary:
        return None
    for candidate in [binary.parent, *binary.parents]:
        if (candidate / "CMakeCache.txt").exists():
            evidence.append(f"build root detected from CMakeCache.txt: {candidate}")
            return candidate
    return binary.parent if binary.parent.exists() else None


def _detect_build_type(build_root: Path | None, evidence: list[str]) -> str | None:
    if not build_root:
        return None
    cache = build_root / "CMakeCache.txt"
    if not cache.exists():
        return None
    for line in cache.read_text(errors="ignore").splitlines():
        if line.startswith("CMAKE_BUILD_TYPE:"):
            value = line.split("=", 1)[-1].strip() or None
            if value:
                evidence.append(f"CMAKE_BUILD_TYPE from {cache}: {value}")
            return value
    return None


def _detect_world_builder(source_root: Path | None, build_root: Path | None, evidence: list[str]) -> dict[str, Any]:
    candidates = []
    for root in (source_root, build_root):
        if root:
            candidates.extend([root / "world_builder", root / "WorldBuilder", root / "contrib" / "world_builder"])
    for path in candidates:
        if path.exists():
            evidence.append(f"World Builder-related path detected: {path}")
            return {"detected": True, "details": str(path)}
    return {"detected": False, "details": None}


def _detect_parameter_schema(binary: Path | None, evidence: list[str]) -> dict[str, Any]:
    if not binary:
        return {"available": False, "source": None}
    try:
        proc = subprocess.run([str(binary), "--help"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15, check=False)
    except (OSError, subprocess.SubprocessError):
        return {"available": False, "source": None}
    text = proc.stdout.lower()
    if "parameter" in text or ".prm" in text:
        evidence.append(f"{binary} --help exposes parameter/prm help text")
        return {"available": True, "source": "aspect --help"}
    return {"available": False, "source": None}
