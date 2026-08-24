"""ASPECT version support policy and PRM compatibility checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .prm import validate_prm


RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "UNKNOWN": 3}


@dataclass(frozen=True)
class SupportPolicyRow:
    version_pattern: str
    support_tier: str
    new_model_recommendation: str
    paper_reproduction_recommendation: str
    plugin_api_risk: str
    prm_compatibility_risk: str

    def to_dict(self) -> dict[str, str]:
        return {
            "version_pattern": self.version_pattern,
            "support_tier": self.support_tier,
            "new_model_recommendation": self.new_model_recommendation,
            "paper_reproduction_recommendation": self.paper_reproduction_recommendation,
            "plugin_api_risk": self.plugin_api_risk,
            "prm_compatibility_risk": self.prm_compatibility_risk,
        }


SUPPORT_POLICY = [
    SupportPolicyRow(
        "3.0.x",
        "primary-supported",
        "Best target for new teaching models in this skill.",
        "Use for reproduction only when the paper or code used ASPECT 3.0.x.",
        "low to medium; still verify external plugins against the local headers.",
        "low for starter PRMs; paper PRMs still require a parse/smoke test.",
    ),
    SupportPolicyRow(
        "3.1-pre / development 3.1",
        "experimental",
        "Useful for testing new ASPECT behavior, not the safest teaching default.",
        "Use only when the paper code explicitly targets this development version.",
        "medium to high because interfaces may still move.",
        "medium because parameter defaults and names may change.",
    ),
    SupportPolicyRow(
        "2.4.x-2.5.x",
        "legacy-supported",
        "Acceptable for paper reproduction; not preferred for new beginner models.",
        "Often the right choice for papers written against those releases.",
        "medium; plugin interfaces should be built with the matching ASPECT.",
        "medium; run ASPECT parsing/smoke tests before changing the model.",
    ),
    SupportPolicyRow(
        "<=2.3",
        "historical-reproduction",
        "Do not use for new models unless there is a specific paper reason.",
        "Prefer an isolated historical build or the paper's original container.",
        "high; plugin APIs and dependencies may differ substantially.",
        "high; migration should be explicit and reviewed.",
    ),
    SupportPolicyRow(
        "unknown",
        "unknown",
        "Find the local ASPECT binary/version before generating or validating models.",
        "Treat the run as compatibility testing until paper/local versions are known.",
        "unknown.",
        "unknown.",
    ),
]


def parse_aspect_version(text: str | None) -> dict[str, Any]:
    """Parse a best-effort ASPECT version from raw text without fabricating data."""

    raw = (text or "").strip()
    if not raw:
        return {"raw": raw, "version": None, "major": None, "minor": None, "patch": None, "suffix": None}
    match = re.search(r"([0-9]+)\.([0-9]+)(?:\.([0-9]+))?([A-Za-z0-9._+\-]*)", raw)
    if not match:
        return {"raw": raw, "version": None, "major": None, "minor": None, "patch": None, "suffix": None}
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3) or 0)
    suffix = match.group(4) or ""
    version = f"{major}.{minor}.{patch}"
    if suffix:
        version += suffix
    return {"raw": raw, "version": version, "major": major, "minor": minor, "patch": patch, "suffix": suffix}


def classify_version(version_text: str | None) -> dict[str, Any]:
    parsed = parse_aspect_version(version_text)
    major = parsed["major"]
    minor = parsed["minor"]
    suffix = (parsed["suffix"] or "").lower()
    if major is None:
        tier = "unknown"
        channel = "unknown"
        row = SUPPORT_POLICY[-1]
    elif major == 3 and minor == 0:
        tier = "primary-supported"
        channel = "stable"
        row = SUPPORT_POLICY[0]
    elif major == 3 and minor == 1 and ("pre" in suffix or "dev" in suffix or suffix):
        tier = "experimental"
        channel = "development"
        row = SUPPORT_POLICY[1]
    elif major == 3 and minor == 1:
        tier = "experimental"
        channel = "development"
        row = SUPPORT_POLICY[1]
    elif major == 2 and minor in {4, 5}:
        tier = "legacy-supported"
        channel = "legacy"
        row = SUPPORT_POLICY[2]
    elif major < 2 or (major == 2 and minor <= 3):
        tier = "historical-reproduction"
        channel = "historical"
        row = SUPPORT_POLICY[3]
    else:
        tier = "unknown"
        channel = "unknown"
        row = SUPPORT_POLICY[-1]
    return {
        **parsed,
        "support_tier": tier,
        "version_channel": channel,
        "policy": row.to_dict(),
    }


def policy_matrix() -> list[dict[str, str]]:
    return [row.to_dict() for row in SUPPORT_POLICY]


def format_policy_matrix() -> str:
    lines = [
        "ASPECT Version Compatibility Matrix",
        "",
        "ASPECT version       Support tier",
    ]
    for row in SUPPORT_POLICY:
        lines.append(f"{row.version_pattern:<20} {row.support_tier}")
    lines.extend([
        "",
        "Guidance for geologists:",
        "- New starter models: prefer primary-supported ASPECT 3.0.x when available.",
        "- Paper reproduction: prefer the paper's original ASPECT version, commit, or container when known.",
        "- Plugin API risk: external plugins must be built against the matching ASPECT headers.",
        "- PRM compatibility risk: a clean lint report is not proof that every ASPECT parameter is valid in every version.",
    ])
    return "\n".join(lines)


def inspect_prm_features(prm: Path) -> list[dict[str, str]]:
    text = prm.read_text(errors="ignore")
    features: list[dict[str, str]] = []

    def add(name: str, risk: str, evidence: str, explanation: str) -> None:
        features.append({"name": name, "risk": risk, "evidence": evidence, "explanation": explanation})

    checks = [
        ("external shared library", "HIGH", r"^\s*set\s+Additional shared libraries\s*=", "External plugin libraries are version-sensitive."),
        ("World Builder", "MEDIUM", r"world builder|world_builder", "World Builder files/options should be checked against the target ASPECT version."),
        ("free surface", "MEDIUM", r"free surface|Free surface", "Free-surface settings can be version-sensitive and numerically sensitive."),
        ("particles", "MEDIUM", r"^\s*subsection\s+Particles\b|particle", "Particle output/advection settings may vary across versions."),
        ("melt transport", "MEDIUM", r"\bmelt\b|melt transport", "Melt/two-phase flow parameters are version-sensitive."),
        ("visco-plastic material", "MEDIUM", r"visco[ -]?plastic|Drucker|Peierls|yield", "Visco-plastic material settings need version-specific verification."),
        ("compositional fields", "LOW", r"Compositional fields|Number of fields|composition", "Composition is common, but field counts and material parameter lists still need checking."),
        ("FastScape", "HIGH", r"FastScape|fastscape", "FastScape coupling depends on external libraries and build options."),
    ]
    for name, risk, pattern, explanation in checks:
        match = re.search(pattern, text, flags=re.I | re.M)
        if match:
            line = _line_for_offset(text, match.start())
            add(name, risk, f"line {line}: {match.group(0).strip()}", explanation)
    return features


def assess_compatibility(prm: Path, aspect_profile: dict[str, Any]) -> dict[str, Any]:
    lint = validate_prm(prm)
    features = inspect_prm_features(prm)
    classification = classify_version(aspect_profile.get("aspect_version") or aspect_profile.get("version_raw"))
    tier = classification["support_tier"]
    syntax = "fail" if any(item["level"] == "ERROR" for item in lint) else "pass" if any(item["level"] == "PASS" for item in lint) else "warning"
    prm_risk = _base_prm_risk(tier)
    plugin_risk = _base_plugin_risk(tier)
    for feature in features:
        if feature["name"] == "external shared library":
            plugin_risk = _max_risk(plugin_risk, "HIGH")
        prm_risk = _max_risk(prm_risk, feature["risk"])
    if syntax == "fail":
        prm_risk = "HIGH"
    recommendation = _recommendation(tier, prm_risk, plugin_risk, features)
    return {
        "prm": str(prm),
        "detected_aspect": aspect_profile.get("aspect_version"),
        "support_tier": tier,
        "version_channel": classification["version_channel"],
        "prm_syntax": syntax,
        "prm_lint": lint,
        "prm_compatibility_risk": prm_risk,
        "plugin_api_risk": plugin_risk,
        "version_sensitive_features": features,
        "recommendation": recommendation,
        "evidence": aspect_profile.get("detection_evidence", []),
    }


def format_compat_check(result: dict[str, Any]) -> str:
    lines = [
        f"Detected ASPECT: {result.get('detected_aspect') or 'unknown'}",
        f"Support tier: {result.get('support_tier') or 'unknown'}",
        f"PRM syntax: {result.get('prm_syntax')}",
        f"PRM compatibility risk: {result.get('prm_compatibility_risk')}",
        f"Plugin/API risk: {result.get('plugin_api_risk')}",
        "",
        "Version-sensitive features detected:",
    ]
    features = result.get("version_sensitive_features") or []
    if features:
        for feature in features:
            lines.append(f"- {feature['name']} [{feature['risk']}]: {feature['explanation']} Evidence: {feature['evidence']}")
    else:
        lines.append("- none detected by static inspection")
    lines.extend(["", "Recommendation:", str(result.get("recommendation") or "needs verification")])
    evidence = result.get("evidence") or []
    if evidence:
        lines.extend(["", "Evidence:"])
        lines.extend(f"- {item}" for item in evidence[:12])
    return "\n".join(lines)


def format_compat_explain(result: dict[str, Any]) -> str:
    version = result.get("detected_aspect") or "unknown"
    tier = result.get("support_tier") or "unknown"
    features = result.get("version_sensitive_features") or []
    portable = "basic geometry, output directory, and simple subsection structure" if result.get("prm_syntax") != "fail" else "not enough; structural lint found errors"
    sensitive = ", ".join(feature["name"] for feature in features) if features else "none detected by static inspection"
    plugin_note = "External plugin compatibility is a concern." if any(f["name"] == "external shared library" for f in features) else "No external shared library was detected, but plugin use still needs verification if the model loads custom code elsewhere."
    if tier in {"legacy-supported", "historical-reproduction"}:
        version_note = "For paper reproduction, using the original paper version is safer than migrating first."
    elif tier == "primary-supported":
        version_note = "This is the preferred teaching-version tier for new Aspect_Yuan starter models."
    else:
        version_note = "The ASPECT version is not fully supported as a default teaching target; verify before trusting a long run."
    return "\n".join([
        f"This PRM was checked against detected ASPECT: {version}.",
        f"Aspect_Yuan support tier: {tier}.",
        f"Likely portable parts: {portable}.",
        f"Version-sensitive parts: {sensitive}.",
        plugin_note,
        version_note,
        f"Next step: {result.get('recommendation') or 'run a parse/smoke test and keep the original geological settings unchanged.'}",
    ])


def _line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _base_prm_risk(tier: str) -> str:
    if tier == "primary-supported":
        return "LOW"
    if tier in {"legacy-supported", "experimental"}:
        return "MEDIUM"
    if tier == "historical-reproduction":
        return "HIGH"
    return "UNKNOWN"


def _base_plugin_risk(tier: str) -> str:
    if tier == "primary-supported":
        return "LOW"
    if tier in {"legacy-supported", "experimental"}:
        return "MEDIUM"
    if tier == "historical-reproduction":
        return "HIGH"
    return "UNKNOWN"


def _max_risk(left: str, right: str) -> str:
    if left == "UNKNOWN":
        return right if right == "HIGH" else "UNKNOWN"
    if right == "UNKNOWN":
        return left
    return left if RISK_ORDER[left] >= RISK_ORDER[right] else right


def _recommendation(tier: str, prm_risk: str, plugin_risk: str, features: list[dict[str, str]]) -> str:
    if tier == "unknown":
        return "Find or pass the ASPECT binary first, then rerun compatibility checking. Treat this as needs verification."
    if plugin_risk == "HIGH":
        return "Use the ASPECT version that built the original plugin, or rebuild the plugin against this exact ASPECT before running."
    if tier == "historical-reproduction":
        return "Use an isolated historical ASPECT build or the paper container before attempting any migration."
    if prm_risk == "HIGH":
        return "Do not rewrite the PRM automatically. Verify the reported feature with the target ASPECT version and run a short smoke test."
    if features:
        return "Run a short ASPECT parse/smoke test with unchanged geological settings and keep the detected version in the case notes."
    return "Compatibility risk is low by static inspection, but scientific correctness still requires ASPECT run/log/statistics checks."
