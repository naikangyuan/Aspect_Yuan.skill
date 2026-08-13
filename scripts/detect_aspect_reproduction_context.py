#!/usr/bin/env python3
"""Detect ASPECT reproduction clues from paper notes, README files, or code folders."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


VERSION_PATTERNS = [
    r"ASPECT\s+(?:version\s*)?v?([0-9]+(?:\.[0-9]+){1,2}(?:[-\w.]*)?)",
    r"aspect[-_ ]?([0-9]+(?:\.[0-9]+){1,2}(?:[-\w.]*)?)",
    r"VERSION\s*[:=]\s*([0-9]+(?:\.[0-9]+){1,2}(?:[-\w.]*)?)",
]
COMMIT_PATTERNS = [
    r"\bcommit\s+([0-9a-f]{7,40})\b",
    r"\bgit\s+(?:hash|sha|commit)\s*[:=]?\s*([0-9a-f]{7,40})\b",
    r"\b([0-9a-f]{40})\b",
]
URL_PATTERNS = [
    r"https?://(?:github|gitlab)\.com/[^\s)>\"]+",
    r"https?://doi\.org/[^\s)>\"]+",
    r"https?://zenodo\.org/[^\s)>\"]+",
]
ASPECT_SOURCE_MARKERS = (
    "/src_aspect/aspect/",
    "/src_aspect/",
    "/src/aspect/",
    "/src/fastscape_update_again/",
)
ASPECT_TREE_SUBDIRS = (
    "/tests/",
    "/cookbooks/",
    "/benchmarks/",
    "/source/",
    "/include/",
    "/doc/",
)


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def collect_text_from_path(path: Path) -> tuple[str, list[str]]:
    files: list[Path] = []
    if path.is_file():
        files = [path]
    elif path.is_dir():
        names = {
            "README", "README.md", "readme.md", "CMakeLists.txt", "Dockerfile",
            "Singularity", "environment.yml", "conda.yml", "VERSION", "log.txt", "statistics",
        }
        for candidate in path.rglob("*"):
            if candidate.is_file() and (candidate.name in names or candidate.suffix in {".prm", ".cc", ".h", ".txt", ".md", ".yml", ".yaml", ".so", ".sh"}):
                files.append(candidate)
    text_parts = []
    rel_files = []
    for file in files[:300]:
        rel_files.append(str(file))
        text_parts.append(f"\n--- {file} ---\n{read_text_file(file)}")
    return "\n".join(text_parts), rel_files


def unique(matches: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in matches:
        item = item.strip().rstrip(".,;")
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def is_embedded_source_file(file_name: str) -> bool:
    normalized = file_name.lower().replace("\\", "/")
    if any(marker in normalized for marker in ASPECT_SOURCE_MARKERS):
        return True
    return any(part in normalized for part in ASPECT_TREE_SUBDIRS) and "/plugins" not in normalized


def looks_like_paper_model_file(file_name: str) -> bool:
    normalized = file_name.lower().replace("\\", "/")
    if is_embedded_source_file(file_name):
        return False
    return any(part in normalized for part in ("/prms/", "/inputfiles_outputs/", "/run-output/")) or normalized.endswith(".prm")


def looks_like_paper_plugin_file(file_name: str) -> bool:
    normalized = file_name.lower().replace("\\", "/")
    if "/plugins" not in normalized and "/plugins_aspect/" not in normalized:
        return False
    return normalized.endswith((".cc", ".h", ".so", "cmakelists.txt"))


def source_dirs(files: list[str]) -> list[str]:
    dirs = []
    for file_name in files:
        normalized = file_name.replace("\\", "/")
        lower = normalized.lower()
        for marker in ASPECT_SOURCE_MARKERS:
            idx = lower.find(marker)
            if idx >= 0:
                dirs.append(normalized[: idx + len(marker.rstrip("/"))])
    return unique(dirs)


def detect(text: str, files: list[str]) -> dict:
    versions = []
    for pattern in VERSION_PATTERNS:
        versions.extend(re.findall(pattern, text, flags=re.I))
    commits = []
    for pattern in COMMIT_PATTERNS:
        commits.extend(re.findall(pattern, text, flags=re.I))
    urls = []
    for pattern in URL_PATTERNS:
        urls.extend(re.findall(pattern, text, flags=re.I))
    prm_files = [f for f in files if f.endswith(".prm")]
    paper_prm_files = [f for f in prm_files if looks_like_paper_model_file(f)]
    source_prm_files = [f for f in prm_files if is_embedded_source_file(f)]
    plugin_files = [f for f in files if f.endswith((".cc", ".h", ".so")) and any(k in f.lower() for k in ("material", "boundary", "initial", "postprocess", "gravity", "heating", "riftplugin"))]
    paper_plugin_files = [f for f in plugin_files if looks_like_paper_plugin_file(f)]
    source_plugin_files = [f for f in plugin_files if is_embedded_source_file(f)]
    logs = [f for f in files if Path(f).name in {"log.txt", "statistics"} or "/run-output/" in f.replace("\\", "/")]
    has_container = any(Path(f).name in {"Dockerfile", "Singularity"} for f in files)
    has_cmake = any(Path(f).name == "CMakeLists.txt" for f in files)
    return {
        "aspect_versions": unique(versions),
        "git_commits": unique(commits),
        "urls": unique(urls),
        "paper_prm_files": paper_prm_files[:100],
        "embedded_source_prm_files_sample": source_prm_files[:20],
        "paper_plugin_files": paper_plugin_files[:100],
        "embedded_source_plugin_files_sample": source_plugin_files[:20],
        "run_log_or_statistics_files": logs[:100],
        "embedded_aspect_source_dirs": source_dirs(files),
        "has_container_file": has_container,
        "has_cmake": has_cmake,
        "version_status": "verified_candidate" if versions or commits else "unknown",
        "next_steps": [
            "Verify any detected version against the paper supplement, run log, README, or repository tag.",
            "Run aspect --version for the selected binary.",
            "Smoke-test the smallest original .prm before editing scientific parameters.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect ASPECT paper-reproduction version/code clues.")
    parser.add_argument("--text", type=Path, help="Text file containing paper notes, README content, or copied article metadata.")
    parser.add_argument("--path", type=Path, help="Downloaded paper code directory or a single source file.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()
    if not args.text and not args.path:
        parser.error("provide --text or --path")

    text_parts = []
    files: list[str] = []
    if args.text:
        files.append(str(args.text))
        text_parts.append(read_text_file(args.text))
    if args.path:
        text, collected = collect_text_from_path(args.path)
        files.extend(collected)
        text_parts.append(text)

    result = detect("\n".join(text_parts), files)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("ASPECT reproduction context")
        print(f"- Version status: {result['version_status']}")
        print(f"- ASPECT versions: {', '.join(result['aspect_versions']) or 'unknown'}")
        print(f"- Git commits: {', '.join(result['git_commits']) or 'unknown'}")
        print(f"- URLs: {', '.join(result['urls']) or 'none detected'}")
        print(f"- Paper PRM files found: {len(result['paper_prm_files'])}")
        print(f"- Paper plugin files found: {len(result['paper_plugin_files'])}")
        print(f"- Embedded ASPECT source dirs: {', '.join(result['embedded_aspect_source_dirs']) or 'none detected'}")
        print(f"- Run log/statistics files found: {len(result['run_log_or_statistics_files'])}")
        print(f"- Container file: {result['has_container_file']}")
        print(f"- CMake file: {result['has_cmake']}")
        print("Next steps:")
        for step in result["next_steps"]:
            print(f"- {step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
