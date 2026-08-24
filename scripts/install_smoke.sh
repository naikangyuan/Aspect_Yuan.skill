#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: install_smoke.sh [--aspect-bin PATH] [--work-dir DIR]

Verify that a freshly cloned or Codex-installed Aspect_Yuan skill can run.

Checks:
  1. script permissions and CLI help
  2. environment discovery
  3. model generation from packaged template configs
  4. beginner generation for subduction, mantle_convection, and rift
  5. GeoSpec geology.yaml workflow
  6. paper reproduction MVP inspection
  7. unit tests and rule-based evals
  8. optional real ASPECT subduction smoke when --aspect-bin is provided

Options:
  --aspect-bin PATH  ASPECT executable for the optional real smoke test.
  --work-dir DIR     Temporary work directory, default: /tmp/aspect-yuan-install-smoke
  -h, --help         Show this help.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ASPECT_BIN=""
WORK_DIR="/tmp/aspect-yuan-install-smoke"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --aspect-bin)
      ASPECT_BIN="${2:-}"
      shift 2
      ;;
    --work-dir)
      WORK_DIR="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

cd "$SKILL_ROOT"
export PYTHONDONTWRITEBYTECODE=1
find scripts -maxdepth 1 -type f -exec chmod +x {} +
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

echo "[1/8] CLI help"
scripts/aspect-yuan --help >/dev/null

echo "[2/8] Environment discovery"
scripts/aspect-yuan env check >/dev/null

echo "[3/8] Packaged template configs"
for model in mantle_convection rift subduction; do
  test -f "templates/models/$model/config.yaml"
  scripts/aspect-yuan model create "templates/models/$model/config.yaml" --output-dir "$WORK_DIR/template-$model" >/dev/null
done

echo "[4/8] Beginner generation"
for model in mantle_convection rift subduction; do
  scripts/aspect-yuan beginner "$model" --output-dir "$WORK_DIR/beginner-$model" >/dev/null
done

echo "[5/8] GeoSpec geology.yaml workflow"
scripts/aspect-yuan geospec init subduction --output "$WORK_DIR/geology.yaml" >/dev/null
scripts/aspect-yuan geospec validate "$WORK_DIR/geology.yaml" >/dev/null
scripts/aspect-yuan geospec explain "$WORK_DIR/geology.yaml" >/dev/null
scripts/aspect-yuan geospec create-case "$WORK_DIR/geology.yaml" --output-dir "$WORK_DIR/geospec-subduction" >/dev/null
test -f "$WORK_DIR/geospec-subduction/case.prm"
test -f "$WORK_DIR/geospec-subduction/GEOSPEC_EXPLANATION.md"

echo "[6/8] Paper reproduction MVP"
PAPER_CODE="$WORK_DIR/paper-code"
PAPER_PROJECT="$WORK_DIR/paper-project"
mkdir -p "$PAPER_CODE"
cat > "$PAPER_CODE/README.md" <<'EOF'
Example paper code. ASPECT version 2.5.0, branch paper-model, commit 0123456789abcdef0123456789abcdef01234567.
EOF
cat > "$PAPER_CODE/Dockerfile" <<'EOF'
FROM ubuntu:22.04
EOF
cat > "$PAPER_CODE/CMakeLists.txt" <<'EOF'
add_library(plugin SHARED material_model.cc)
EOF
cat > "$PAPER_CODE/material_model.cc" <<'EOF'
// material model plugin
EOF
cat > "$PAPER_CODE/model.prm" <<'EOF'
set Dimension = 2
subsection Geometry model
  set Model name = box
end
EOF
scripts/aspect-yuan reproduce init "$PAPER_PROJECT" >/dev/null
scripts/aspect-yuan reproduce inspect "$PAPER_CODE" --project "$PAPER_PROJECT" >/dev/null
scripts/aspect-yuan reproduce status "$PAPER_PROJECT" >/dev/null
test -f "$PAPER_PROJECT/reproduction.yaml"
test -f "$PAPER_PROJECT/REPRODUCTION_REPORT.md"
test -f "$PAPER_PROJECT/parameter_inventory.csv"

echo "[7/8] Unit tests"
PYTHONPATH="$SKILL_ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m unittest discover -s tests

echo "[8/8] Static validation and evals"
python3 scripts/static_validate_skill.py
python3 scripts/run_skill_evals.py

if [[ -n "$ASPECT_BIN" ]]; then
  echo "[extra] Real ASPECT subduction smoke"
  scripts/aspect-yuan beginner subduction --output-dir "$WORK_DIR/real-subduction" --run --aspect-bin "$ASPECT_BIN" >/dev/null
else
  echo "[extra] Real ASPECT subduction smoke skipped: pass --aspect-bin PATH to run it."
fi

echo "Install smoke passed. Work directory: $WORK_DIR"
