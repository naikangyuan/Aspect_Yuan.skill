#!/usr/bin/env python3
"""Rule-based ASPECT model-family and version-strategy planner."""

from __future__ import annotations

import argparse
import json


FAMILIES = [
    ("deep_shallow_coupling", ["deep", "shallow", "coupling", "global regional", "regional coupling", "深浅", "耦合"], "high", "cookbooks/global_regional_coupling/global_regional_coupling.prm"),
    ("subduction", ["subduction", "slab", "trench", "俯冲", "板片"], "high", "model_wizards/subduction_wizard.md"),
    ("rift", ["rift", "extension", "breakup", "伸展", "裂谷", "破裂"], "medium", "model_wizards/rift_wizard.md"),
    ("mantle_convection", ["mantle convection", "rayleigh", "convection", "地幔对流", "热对流"], "low", "model_wizards/mantle_convection_wizard.md"),
    ("weak_zone", ["weak zone", "shear band", "fault", "弱带", "剪切带", "断层"], "medium", "model_wizards/weak_zone_wizard.md"),
    ("plume", ["plume", "hot anomaly", "地幔柱", "热异常"], "medium", "model_wizards/plume_wizard.md"),
    ("shortening", ["shortening", "collision", "convergence", "缩短", "碰撞", "挤压"], "medium", "model_wizards/lithosphere_shortening_wizard.md"),
    ("craton_edge", ["craton", "keel", "克拉通", "岩石圈根", "边缘"], "high", "model_wizards/craton_edge_wizard.md"),
]


def classify(text: str) -> dict:
    lowered = text.lower()
    matches = []
    for name, keywords, risk, reference in FAMILIES:
        score = sum(1 for kw in keywords if kw.lower() in lowered)
        if score:
            matches.append({"family": name, "score": score, "version_risk": risk, "first_reference": reference})
    matches.sort(key=lambda x: x["score"], reverse=True)
    paper_like = any(k in lowered for k in ["paper", "doi", "reproduce", "replicate", "article", "论文", "复现", "文章"])
    best = matches[0] if matches else {"family": "unknown", "score": 0, "version_risk": "unknown", "first_reference": "references/geological_problem_to_aspect.md"}
    strategy = "paper-first exact version detection" if paper_like else "local cookbook/template first, then pin version if a paper is named"
    return {
        "best_match": best,
        "all_matches": matches,
        "paper_reproduction_likely": paper_like,
        "version_strategy": strategy,
        "required_references": [
            "references/paper_reproduction_first.md" if paper_like else "references/model_family_version_map.md",
            "references/aspect_version_strategy.md",
            best["first_reference"],
        ],
        "next_steps": [
            "If reproducing a paper, identify DOI/code repository/ASPECT tag or commit before running.",
            "If designing a new model, start from the listed wizard/template and run a small smoke test.",
            "Do not change geometry, rheology, boundary conditions, temperature, gravity, or dimensionality silently.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan ASPECT version strategy from a geology or paper-reproduction request.")
    parser.add_argument("request", nargs="+", help="User request text.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()
    result = classify(" ".join(args.request))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        best = result["best_match"]
        print("ASPECT version/model-family plan")
        print(f"- Model family: {best['family']}")
        print(f"- Version risk: {best['version_risk']}")
        print(f"- First reference: {best['first_reference']}")
        print(f"- Paper reproduction likely: {result['paper_reproduction_likely']}")
        print(f"- Version strategy: {result['version_strategy']}")
        print("Required references:")
        for ref in result["required_references"]:
            print(f"- {ref}")
        print("Next steps:")
        for step in result["next_steps"]:
            print(f"- {step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
