"""Paper reproduction project helpers for ASPECT code folders."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .compatibility import classify_version
from .config import dump_config, load_config
from .fingerprint import fingerprint_aspect


PROJECT_DIRS = ("paper", "source", "prm", "plugins", "docker", "runs", "figures", "comparison")

TEXT_NAMES = {
    "README",
    "README.md",
    "readme.md",
    "Dockerfile",
    "Singularity",
    "Apptainer",
    "environment.yml",
    "environment.yaml",
    "CMakeLists.txt",
    "VERSION",
}
TEXT_SUFFIXES = {".prm", ".md", ".txt", ".yml", ".yaml", ".sh", ".cmake", ".cc", ".h", ".hpp", ".cpp"}

VERSION_PATTERNS = (
    r"ASPECT\s+(?:version\s*)?v?([0-9]+(?:\.[0-9]+){1,2}(?:[-\w.]*)?)",
    r"aspect[-_ ]?([0-9]+(?:\.[0-9]+){1,2}(?:[-\w.]*)?)",
    r"VERSION\s*[:=]\s*([0-9]+(?:\.[0-9]+){1,2}(?:[-\w.]*)?)",
)
COMMIT_PATTERNS = (
    r"\bcommit\s+([0-9a-f]{7,40})\b",
    r"\bgit\s+(?:hash|sha|commit)\s*[:=]?\s*([0-9a-f]{7,40})\b",
    r"\b([0-9a-f]{40})\b",
)
BRANCH_PATTERNS = (
    r"\bbranch\s*[:=]\s*([A-Za-z0-9._/\-]+)",
    r"git\s+checkout\s+([A-Za-z0-9._/\-]+)",
)
URL_PATTERNS = (
    r"https?://(?:github|gitlab)\.com/[^\s)>\"]+",
    r"https?://doi\.org/[^\s)>\"]+",
    r"https?://zenodo\.org/[^\s)>\"]+",
)


@dataclass(frozen=True)
class ReproductionScan:
    code_path: Path
    files_scanned: list[Path]
    readmes: list[Path]
    dockerfiles: list[Path]
    prm_files: list[Path]
    plugin_files: list[Path]
    cmake_files: list[Path]
    run_files: list[Path]
    data_files: list[Path]
    versions: list[str]
    commits: list[str]
    branches: list[str]
    urls: list[str]

    def to_dict(self, base: Path | None = None) -> dict[str, Any]:
        return {
            "code_path": str(self.code_path),
            "files_scanned": len(self.files_scanned),
            "readmes": _paths(self.readmes, base),
            "dockerfiles": _paths(self.dockerfiles, base),
            "prm_files": _paths(self.prm_files, base),
            "plugin_files": _paths(self.plugin_files, base),
            "cmake_files": _paths(self.cmake_files, base),
            "run_files": _paths(self.run_files, base),
            "data_files": _paths(self.data_files, base),
            "aspect_versions": self.versions,
            "git_commits": self.commits,
            "branches": self.branches,
            "urls": self.urls,
            "version_status": "candidate_found" if self.versions or self.commits or self.branches else "unknown",
            "has_container": bool(self.dockerfiles),
            "has_plugins": bool(self.plugin_files),
            "has_prm": bool(self.prm_files),
        }


@dataclass(frozen=True)
class PaperProfile:
    key: str
    display_name: str
    model_family: str
    directory_markers: tuple[str, ...]
    expected_evidence: tuple[str, ...]
    first_pass_goal: str
    smoke_strategy: str
    version_strategy: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "display_name": self.display_name,
            "model_family": self.model_family,
            "directory_markers": list(self.directory_markers),
            "expected_evidence": list(self.expected_evidence),
            "first_pass_goal": self.first_pass_goal,
            "smoke_strategy": self.smoke_strategy,
            "version_strategy": self.version_strategy,
        }


PAPER_PROFILES: dict[str, PaperProfile] = {
    "kaili-rift": PaperProfile(
        key="kaili-rift",
        display_name="Kaili-style rifted margin/orogenic inheritance ASPECT project",
        model_family="rift",
        directory_markers=("aspect-fast_kaili", "orgenic_inheritance", "rifted_margin", "inputfiles_outputs", "plugins_Aspect", "FastScape"),
        expected_evidence=("README/Dockerfile", "ASPECT fork or commit", "continental_extension.prm", "plugins_Aspect", "FastScape coupling"),
        first_pass_goal="Run the smallest original continental_extension.prm without changing geological parameters.",
        smoke_strategy="Prefer the provided Dockerfile/container first; otherwise build the paper ASPECT fork and plugin stack in isolation.",
        version_strategy="Use the paper's ASPECT fork/tag/commit before trying local ASPECT migration.",
    ),
    "oneill-hadean-mixing": PaperProfile(
        key="oneill-hadean-mixing",
        display_name="ONeill-style Hadean lateral mixing ASPECT project",
        model_family="mantle_convection",
        directory_markers=("ONeill", "Hadean", "mixing", "mixing_100km.prm"),
        expected_evidence=("paper PDF or notes", "mixing_*.prm", "source archive", "run output/statistics when available"),
        first_pass_goal="Identify the smallest original mixing PRM and run a short parse/smoke test with the paper version.",
        smoke_strategy="Start from the original PRM and compare output fields/statistics before changing resolution or runtime.",
        version_strategy="Treat version as unknown until README/log/source VERSION evidence is found.",
    ),
    "gernon-craton-breakup": PaperProfile(
        key="gernon-craton-breakup",
        display_name="Gernon-style craton margin/interior breakup ASPECT project",
        model_family="craton_edge",
        directory_markers=("Gernon", "craton", "continental-breakup", "margins", "interiors"),
        expected_evidence=("repository README", "model PRMs", "data files", "target figures", "ASPECT version evidence"),
        first_pass_goal="Inventory the original model files and choose the shortest PRM or documented test case.",
        smoke_strategy="Run a minimal original case first; record every deviation before figure reproduction.",
        version_strategy="Use exact paper version/commit/container when evidence exists; otherwise keep version status unknown.",
    ),
}


def list_paper_profiles() -> list[dict[str, Any]]:
    return [profile.to_dict() for _, profile in sorted(PAPER_PROFILES.items())]


def init_profile_project(profile_key: str, project: Path) -> dict[str, Any]:
    profile = _get_profile(profile_key)
    result = init_project(project)
    project_dir = Path(result["project"])
    config = load_config(project_dir / "reproduction.yaml")
    _apply_profile_to_config(config, profile)
    dump_config(config, project_dir / "reproduction.yaml")
    _write_profile_file(project_dir, profile)
    _write_reproduction_checklist(project_dir, profile)
    _write_smoke_plan(project_dir, profile, None)
    _write_version_plan(project_dir, profile, None, {})
    (project_dir / "REPRODUCTION_REPORT.md").write_text(_profile_initial_report(project_dir, profile), encoding="utf-8")
    return {
        **result,
        "profile": profile.key,
        "profile_file": str(project_dir / "reproduction_profile.yaml"),
        "checklist": str(project_dir / "PAPER_REPRODUCTION_CHECKLIST.md"),
        "smoke_plan": str(project_dir / "SMOKE_TEST_PLAN.md"),
        "version_plan": str(project_dir / "VERSION_PLAN.md"),
    }


def init_project(project: Path) -> dict[str, Any]:
    project = project.resolve()
    project.mkdir(parents=True, exist_ok=True)
    for name in PROJECT_DIRS:
        (project / name).mkdir(exist_ok=True)
    config = _default_reproduction_config()
    dump_config(config, project / "reproduction.yaml")
    (project / "REPRODUCTION_REPORT.md").write_text(_initial_report(project), encoding="utf-8")
    return {"project": str(project), "config": str(project / "reproduction.yaml"), "report": str(project / "REPRODUCTION_REPORT.md")}


def inspect_code(code_path: Path, project: Path | None = None, profile_key: str | None = None) -> dict[str, Any]:
    code_path = code_path.resolve()
    if not code_path.exists():
        raise FileNotFoundError(code_path)
    project_dir = _resolve_project(project)
    project_dir.mkdir(parents=True, exist_ok=True)
    for name in PROJECT_DIRS:
        (project_dir / name).mkdir(exist_ok=True)

    scan = scan_code_path(code_path)
    profile = _resolve_profile(profile_key, scan)
    local_profile = fingerprint_aspect()
    inventory = extract_parameter_inventory(scan.prm_files)
    write_parameter_inventory(inventory, project_dir / "parameter_inventory.csv")
    reproduction = _load_or_default(project_dir / "reproduction.yaml")
    if profile:
        _apply_profile_to_config(reproduction, profile)
    _merge_scan_into_config(reproduction, scan, project_dir, local_profile)
    dump_config(reproduction, project_dir / "reproduction.yaml")
    if profile:
        _write_profile_file(project_dir, profile)
    _write_smoke_plan(project_dir, profile, scan)
    _write_version_plan(project_dir, profile, scan, local_profile)
    _write_reproduction_checklist(project_dir, profile)
    report = write_reproduction_report(project_dir, scan, inventory, local_profile, profile)
    return {
        "project": str(project_dir),
        "code_path": str(code_path),
        "profile": profile.key if profile else None,
        "reproduction_yaml": str(project_dir / "reproduction.yaml"),
        "report": str(report),
        "parameter_inventory": str(project_dir / "parameter_inventory.csv"),
        "smoke_plan": str(project_dir / "SMOKE_TEST_PLAN.md"),
        "version_plan": str(project_dir / "VERSION_PLAN.md"),
        "checklist": str(project_dir / "PAPER_REPRODUCTION_CHECKLIST.md"),
        "scan": scan.to_dict(),
        "reproduction_level": reproduction_status(project_dir)["level"],
    }


def reproduction_status(project: Path) -> dict[str, Any]:
    project = project.resolve()
    config_path = project / "reproduction.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"{config_path} not found. Run reproduce init first.")
    config = load_config(config_path)
    evidence = config.get("evidence", {}) if isinstance(config.get("evidence"), dict) else {}
    has_prm = bool(evidence.get("prm_files"))
    has_version = bool(evidence.get("aspect_versions") or evidence.get("git_commits") or evidence.get("branches"))
    has_report = (project / "REPRODUCTION_REPORT.md").exists()
    has_inventory = (project / "parameter_inventory.csv").exists()
    version_compatibility = config.get("version_compatibility", {}) if isinstance(config.get("version_compatibility"), dict) else {}
    profile = config.get("profile", {}) if isinstance(config.get("profile"), dict) else {}
    if has_prm and has_version and has_report and has_inventory:
        level = "Level 1 candidate: original PRM and version evidence found; run smoke next."
    elif has_prm:
        level = "Level 0 candidate: paper code scanned and original PRM found; version evidence remains incomplete."
    else:
        level = "Below Level 0: initialize or inspect a paper code directory with PRM files."
    return {
        "project": str(project),
        "level": level,
        "has_prm": has_prm,
        "has_version_evidence": has_version,
        "has_report": has_report,
        "has_parameter_inventory": has_inventory,
        "paper_aspect_version": version_compatibility.get("paper_aspect_version"),
        "local_aspect_version": version_compatibility.get("local_aspect_version"),
        "version_mismatch": version_compatibility.get("version_mismatch"),
        "support_tier": version_compatibility.get("support_tier"),
        "profile": profile.get("key"),
        "model_family": profile.get("model_family"),
        "next_step": "Run the smallest original .prm as a smoke test without changing geological parameters." if has_prm else "Run aspect-yuan reproduce inspect /path/to/paper-code --project PROJECT.",
    }


def scan_code_path(code_path: Path) -> ReproductionScan:
    files = _collect_files(code_path)
    readmes = [p for p in files if p.name.lower().startswith("readme")]
    dockerfiles = [p for p in files if p.name in {"Dockerfile", "Singularity", "Apptainer"}]
    all_prm_files = [p for p in files if p.suffix == ".prm"]
    prm_files = [p for p in all_prm_files if not _is_embedded_aspect_source(p)] or all_prm_files
    all_plugin_files = [p for p in files if _looks_like_plugin(p)]
    plugin_files = [p for p in all_plugin_files if not _is_embedded_aspect_source(p)] or all_plugin_files
    all_cmake_files = [p for p in files if p.name == "CMakeLists.txt" or p.suffix == ".cmake"]
    cmake_files = [p for p in all_cmake_files if not _is_embedded_aspect_source(p)] or all_cmake_files
    run_files = [p for p in files if p.name in {"log.txt", "statistics"} or "run" in p.name.lower()]
    data_files = [p for p in files if p.suffix.lower() in {".txt", ".csv", ".dat", ".mesh", ".vtu", ".pvtu", ".pvd"} and p not in run_files and p not in cmake_files and not _is_embedded_aspect_source(p)]
    text = _read_combined_text(files)
    return ReproductionScan(
        code_path=code_path,
        files_scanned=files,
        readmes=readmes,
        dockerfiles=dockerfiles,
        prm_files=prm_files,
        plugin_files=plugin_files,
        cmake_files=cmake_files,
        run_files=run_files,
        data_files=data_files,
        versions=_unique_match(text, VERSION_PATTERNS),
        commits=_unique_match(text, COMMIT_PATTERNS),
        branches=_unique_match(text, BRANCH_PATTERNS),
        urls=_unique_match(text, URL_PATTERNS),
    )


def extract_parameter_inventory(prm_files: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for prm in prm_files:
        stack: list[str] = []
        for line_number, line in enumerate(prm.read_text(errors="ignore").splitlines(), start=1):
            subsection = re.match(r"^\s*subsection\s+(.+?)\s*$", line)
            if subsection:
                stack.append(subsection.group(1).strip())
                continue
            if re.match(r"^\s*end\s*$", line):
                if stack:
                    stack.pop()
                continue
            setting = re.match(r"^\s*set\s+(.+?)\s*=\s*(.*?)\s*$", line)
            if setting:
                rows.append({
                    "source_file": str(prm),
                    "line": str(line_number),
                    "subsection": " / ".join(stack),
                    "parameter": setting.group(1).strip(),
                    "value": setting.group(2).strip(),
                })
    return rows


def write_parameter_inventory(rows: list[dict[str, str]], output: Path) -> None:
    fields = ["source_file", "line", "subsection", "parameter", "value"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_reproduction_report(project: Path, scan: ReproductionScan, inventory: list[dict[str, str]], local_profile: dict[str, Any] | None = None, profile: PaperProfile | None = None) -> Path:
    report = project / "REPRODUCTION_REPORT.md"
    smallest_prm = min(scan.prm_files, key=lambda p: p.stat().st_size) if scan.prm_files else None
    lines = [
        "# ASPECT Paper Reproduction Report",
        "",
        "## Geological Meaning",
        "",
        "This report is an evidence inventory for reproducing a published ASPECT model. It does not change geometry, rheology, boundary conditions, temperature, composition fields, gravity, dimensionality, or timescale.",
        "",
        "## Evidence Summary",
        "",
        f"- Code path: `{scan.code_path}`",
        f"- Reproduction profile: `{profile.key if profile else 'auto/unknown'}`",
        f"- Model family: `{profile.model_family if profile else 'unknown'}`",
        f"- README files: `{len(scan.readmes)}`",
        f"- Docker/Singularity files: `{len(scan.dockerfiles)}`",
        f"- PRM files: `{len(scan.prm_files)}`",
        f"- Plugin-like files: `{len(scan.plugin_files)}`",
        f"- CMake files: `{len(scan.cmake_files)}`",
        f"- ASPECT version candidates: `{', '.join(scan.versions) or 'unknown'}`",
        f"- Git commit candidates: `{', '.join(scan.commits) or 'unknown'}`",
        f"- Branch candidates: `{', '.join(scan.branches) or 'unknown'}`",
        f"- URL candidates: `{', '.join(scan.urls[:10]) or 'none detected'}`",
        "",
        "## Original PRM Files",
        "",
    ]
    lines.extend([f"- `{path}`" for path in scan.prm_files[:50]] or ["- none detected"])
    lines.extend(["", "## Plugin/CMake Evidence", ""])
    lines.extend([f"- `{path}`" for path in (scan.plugin_files + scan.cmake_files)[:50]] or ["- none detected"])
    lines.extend(_version_awareness_section(scan, local_profile or {}))
    lines.extend([
        "",
        "## Parameter Inventory",
        "",
        f"- CSV: `parameter_inventory.csv`",
        f"- Parameters extracted: `{len(inventory)}`",
        "",
        "## Smoke Test Plan",
        "",
    ])
    if smallest_prm:
        lines.extend([
            f"1. Start with the smallest original PRM: `{smallest_prm}`.",
            "2. Use the ASPECT version/commit evidence above; if unknown, mark the run as compatibility testing, not exact reproduction.",
            "3. Run without changing scientific parameters:",
            "",
            "```bash",
            f"ASPECT_BIN=/path/to/aspect scripts/run_aspect_case.sh \"{smallest_prm}\" --mpi 1",
            "```",
            "",
            "4. Check the log, statistics, and output fields before attempting figure reproduction.",
        ])
    else:
        lines.append("No `.prm` file was found. Locate the original ASPECT parameter files before running a smoke test.")
    lines.extend([
        "",
        "## Reproduction Guardrails",
        "",
        "- Do not silently change geological parameters to make the model run.",
        "- Record every difference from the paper: ASPECT version, dependency version, plugin, mesh, timestep, resolution, data file, or parameter value.",
        "- Treat this as Level 0/1 evidence until an original PRM runs cleanly.",
    ])
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def _default_reproduction_config() -> dict[str, Any]:
    return {
        "paper": {"title": None, "authors": None, "year": None, "doi": None},
        "aspect": {"version": None, "git_commit": None, "branch": None},
        "source": {"code_path": None, "github": None, "supplementary_material": None},
        "model": {"reference_prm": None, "plugins": []},
        "profile": {"key": None, "model_family": None, "display_name": None},
        "environment": {"docker": None, "mpi_processes": None},
        "evidence": {"prm_files": [], "plugin_files": [], "dockerfiles": [], "aspect_versions": [], "git_commits": [], "branches": []},
        "reproduction_level": "Below Level 0: project initialized, code not inspected.",
    }


def _initial_report(project: Path) -> str:
    return (
        "# ASPECT Paper Reproduction Report\n\n"
        "Project initialized. Next step:\n\n"
        "```bash\n"
        f"scripts/aspect-yuan reproduce inspect /path/to/paper-code --project \"{project}\"\n"
        "```\n"
    )


def _resolve_project(project: Path | None) -> Path:
    if project:
        return project.resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "reproduction.yaml").exists():
        return cwd
    return cwd


def _load_or_default(path: Path) -> dict[str, Any]:
    if path.exists():
        return load_config(path)
    return _default_reproduction_config()


def _merge_scan_into_config(config: dict[str, Any], scan: ReproductionScan, project: Path, local_profile: dict[str, Any] | None = None) -> None:
    config.setdefault("source", {})["code_path"] = str(scan.code_path)
    config.setdefault("aspect", {})["version"] = scan.versions[0] if scan.versions else None
    config.setdefault("aspect", {})["git_commit"] = scan.commits[0] if scan.commits else None
    config.setdefault("aspect", {})["branch"] = scan.branches[0] if scan.branches else None
    config.setdefault("model", {})["reference_prm"] = str(scan.prm_files[0]) if scan.prm_files else None
    config.setdefault("model", {})["plugins"] = [str(path) for path in scan.plugin_files]
    config.setdefault("environment", {})["docker"] = bool(scan.dockerfiles)
    config["evidence"] = scan.to_dict(base=project)
    paper_version = scan.versions[0] if scan.versions else None
    local_version = (local_profile or {}).get("aspect_version")
    paper_tier = classify_version(paper_version)["support_tier"]
    config["version_compatibility"] = {
        "paper_aspect_version": paper_version,
        "local_aspect_version": local_version,
        "version_mismatch": bool(paper_version and local_version and paper_version != local_version),
        "support_tier": paper_tier,
        "recommended_action": _version_reproduction_recommendation(paper_version, local_version, paper_tier),
    }
    config["reproduction_level"] = reproduction_status_from_scan(scan)


def _get_profile(profile_key: str) -> PaperProfile:
    key = profile_key.strip()
    if key not in PAPER_PROFILES:
        raise ValueError(f"Unknown paper profile: {profile_key}. Supported: {', '.join(sorted(PAPER_PROFILES))}")
    return PAPER_PROFILES[key]


def _resolve_profile(profile_key: str | None, scan: ReproductionScan) -> PaperProfile | None:
    if profile_key and profile_key != "auto":
        return _get_profile(profile_key)
    text = " ".join([str(scan.code_path), *[str(p) for p in scan.files_scanned[:300]]]).lower()
    best: tuple[int, PaperProfile] | None = None
    for profile in PAPER_PROFILES.values():
        score = sum(1 for marker in profile.directory_markers if marker.lower() in text)
        if score and (best is None or score > best[0]):
            best = (score, profile)
    return best[1] if best else None


def _apply_profile_to_config(config: dict[str, Any], profile: PaperProfile) -> None:
    config["profile"] = {
        "key": profile.key,
        "display_name": profile.display_name,
        "model_family": profile.model_family,
        "expected_evidence": list(profile.expected_evidence),
        "first_pass_goal": profile.first_pass_goal,
        "smoke_strategy": profile.smoke_strategy,
        "version_strategy": profile.version_strategy,
    }


def _write_profile_file(project: Path, profile: PaperProfile) -> Path:
    path = project / "reproduction_profile.yaml"
    dump_config(profile.to_dict(), path)
    return path


def _write_reproduction_checklist(project: Path, profile: PaperProfile | None) -> Path:
    path = project / "PAPER_REPRODUCTION_CHECKLIST.md"
    profile_line = f"`{profile.key}` ({profile.display_name})" if profile else "`auto/unknown`"
    lines = [
        "# Paper Reproduction Checklist",
        "",
        f"- Profile: {profile_line}",
        "- Preserve original paper files and paths.",
        "- Identify ASPECT version, commit, branch, or container evidence.",
        "- Inventory original `.prm` files, included files, data files, mesh files, and plugin sources.",
        "- Build or select the paper ASPECT version in an isolated environment.",
        "- Run the smallest original PRM first, without changing scientific parameters.",
        "- Check log, statistics, visualization fields, and output directory structure.",
        "- Record every deviation from the paper before figure reproduction.",
        "- Do not silently change geometry, boundary velocities, rheology, temperature, composition fields, gravity, dimension, or timescale.",
    ]
    if profile:
        lines.extend(["", "## Profile-Specific Evidence To Find", ""])
        lines.extend(f"- {item}" for item in profile.expected_evidence)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_smoke_plan(project: Path, profile: PaperProfile | None, scan: ReproductionScan | None) -> Path:
    path = project / "SMOKE_TEST_PLAN.md"
    smallest_prm = min(scan.prm_files, key=lambda p: p.stat().st_size) if scan and scan.prm_files else None
    lines = [
        "# Smoke Test Plan",
        "",
        "Goal: prove the original paper model can at least start with the intended ASPECT version before any scientific edits.",
        "",
    ]
    if profile:
        lines.extend([
            f"- Profile: `{profile.key}`",
            f"- First-pass goal: {profile.first_pass_goal}",
            f"- Strategy: {profile.smoke_strategy}",
            "",
        ])
    if smallest_prm:
        lines.extend([
            "## First PRM",
            "",
            f"`{smallest_prm}`",
            "",
            "```bash",
            f"ASPECT_BIN=/path/to/paper-aspect scripts/run_aspect_case.sh \"{smallest_prm}\" --mpi 1",
            "scripts/check_aspect_log.py /path/to/generated-run.log",
            "```",
        ])
    else:
        lines.extend([
            "## First PRM",
            "",
            "No original `.prm` has been scanned yet. Run:",
            "",
            "```bash",
            "scripts/aspect-yuan reproduce inspect /path/to/paper-code --project PROJECT --profile auto",
            "```",
        ])
    lines.extend([
        "",
        "Do not reduce resolution, shorten time, remove plugins, or change boundary/rheology settings unless the change is recorded as a reproduction deviation.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_version_plan(project: Path, profile: PaperProfile | None, scan: ReproductionScan | None, local_profile: dict[str, Any]) -> Path:
    path = project / "VERSION_PLAN.md"
    paper_version = scan.versions[0] if scan and scan.versions else None
    local_version = local_profile.get("aspect_version")
    tier = classify_version(paper_version)["support_tier"]
    lines = [
        "# ASPECT Version Plan",
        "",
        f"- Paper ASPECT version: `{paper_version or 'unknown'}`",
        f"- Local ASPECT version: `{local_version or 'unknown'}`",
        f"- Paper support tier: `{tier}`",
        f"- Version mismatch: `{'yes' if paper_version and local_version and paper_version != local_version else 'no' if paper_version and local_version else 'unknown'}`",
        "",
    ]
    if profile:
        lines.append(f"Profile strategy: {profile.version_strategy}")
        lines.append("")
    if paper_version and local_version and paper_version != local_version:
        lines.append(f"Recommended action: reproduce first with ASPECT `{paper_version}` before attempting migration to local `{local_version}`.")
    elif paper_version:
        lines.append("Recommended action: use the detected paper version for the first smoke test.")
    else:
        lines.append("Recommended action: locate version evidence in README, logs, Dockerfile, source VERSION, or git metadata before claiming reproduction.")
    lines.extend([
        "",
        "Aspect_Yuan does not automatically migrate `.prm` files or plugin APIs between ASPECT versions.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _profile_initial_report(project: Path, profile: PaperProfile) -> str:
    return "\n".join([
        "# ASPECT Paper Reproduction Report",
        "",
        f"Profile: `{profile.key}`",
        f"Model family: `{profile.model_family}`",
        "",
        "This project is initialized from a paper reproduction template. Next step:",
        "",
        "```bash",
        f"scripts/aspect-yuan reproduce inspect /path/to/paper-code --project \"{project}\" --profile {profile.key}",
        "```",
        "",
        "Do not modify the paper model before inspecting version, PRM, plugin, and data evidence.",
    ]) + "\n"


def _version_awareness_section(scan: ReproductionScan, local_profile: dict[str, Any]) -> list[str]:
    paper_version = scan.versions[0] if scan.versions else None
    local_version = local_profile.get("aspect_version")
    tier = classify_version(paper_version)["support_tier"]
    mismatch = bool(paper_version and local_version and paper_version != local_version)
    return [
        "",
        "## ASPECT Version Awareness",
        "",
        f"- Paper ASPECT version: `{paper_version or 'unknown'}`",
        f"- Local ASPECT version: `{local_version or 'unknown'}`",
        f"- Version mismatch: `{'yes' if mismatch else 'no' if paper_version and local_version else 'unknown'}`",
        f"- Aspect_Yuan support tier for paper version: `{tier}`",
        f"- Recommendation: {_version_reproduction_recommendation(paper_version, local_version, tier)}",
        "",
        "Aspect_Yuan does not silently migrate paper models. If versions differ, reproduce first with the paper's original ASPECT version/commit or container when possible.",
    ]


def _version_reproduction_recommendation(paper_version: str | None, local_version: str | None, tier: str) -> str:
    if not paper_version:
        return "Find version evidence in README, supplement, Dockerfile, logs, or repository metadata before claiming exact reproduction."
    if not local_version:
        return "Fingerprint a local ASPECT binary before running the paper model."
    if paper_version != local_version:
        return f"Reproduce first using {paper_version} before attempting migration to local ASPECT {local_version}."
    if tier in {"legacy-supported", "historical-reproduction"}:
        return "Use an isolated build/container for this paper version and run the smallest original PRM as smoke test."
    return "Versions match by detected text; run the smallest original PRM as smoke test without changing geological parameters."


def reproduction_status_from_scan(scan: ReproductionScan) -> str:
    if scan.prm_files and (scan.versions or scan.commits or scan.branches):
        return "Level 1 candidate: original PRM and version evidence found; run smoke next."
    if scan.prm_files:
        return "Level 0 candidate: original PRM found; version evidence remains incomplete."
    return "Below Level 0: no original PRM detected."


def _collect_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files: list[Path] = []
    for candidate in path.rglob("*"):
        if not candidate.is_file():
            continue
        if candidate.name in TEXT_NAMES or candidate.suffix in TEXT_SUFFIXES or candidate.suffix.lower() in {".dat", ".csv", ".mesh"}:
            files.append(candidate)
    return sorted(files)[:1000]


def _read_combined_text(files: list[Path]) -> str:
    parts = []
    for file in files[:400]:
        if file.suffix.lower() in {".so", ".vtu", ".pvtu"}:
            continue
        try:
            parts.append(file.read_text(errors="ignore"))
        except OSError:
            continue
    return "\n".join(parts)


def _looks_like_plugin(path: Path) -> bool:
    lower = str(path).lower()
    if path.suffix.lower() not in {".cc", ".h", ".hpp", ".cpp", ".so"}:
        return False
    return any(word in lower for word in ("plugin", "material", "boundary", "initial", "gravity", "postprocess", "heating"))


def _is_embedded_aspect_source(path: Path) -> bool:
    normalized = str(path).replace("\\", "/").lower()
    source_markers = (
        "/src_aspect/aspect/",
        "/src_aspect/",
        "/src/aspect/",
        "/source/",
        "/include/aspect/",
        "/benchmarks/",
        "/cookbooks/",
        "/tests/",
        "/doc/",
    )
    if any(marker in normalized for marker in ("/inputfiles_outputs/", "/prms/", "/run-output/", "/plugins_aspect/")):
        return False
    return any(marker in normalized for marker in source_markers)


def _unique_match(text: str, patterns: tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.I):
            item = match.strip().rstrip(".,;")
            if item and item not in seen:
                seen.add(item)
                out.append(item)
    return out


def _paths(paths: list[Path], base: Path | None = None) -> list[str]:
    result = []
    for path in paths:
        if base:
            try:
                result.append(str(path.relative_to(base)))
                continue
            except ValueError:
                pass
        result.append(str(path))
    return result
