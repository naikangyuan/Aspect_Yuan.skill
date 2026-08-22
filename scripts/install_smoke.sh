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
  5. unit tests and rule-based evals
  6. optional real ASPECT subduction smoke when --aspect-bin is provided

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
chmod +x scripts/*
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

echo "[1/7] CLI help"
scripts/aspect-yuan --help >/dev/null

echo "[2/7] Environment discovery"
scripts/aspect-yuan env check >/dev/null

echo "[3/7] Packaged template configs"
for model in mantle_convection rift subduction; do
  test -f "templates/models/$model/config.yaml"
  scripts/aspect-yuan model create "templates/models/$model/config.yaml" --output-dir "$WORK_DIR/template-$model" >/dev/null
done

echo "[4/7] Beginner generation"
for model in mantle_convection rift subduction; do
  scripts/aspect-yuan beginner "$model" --output-dir "$WORK_DIR/beginner-$model" >/dev/null
done

echo "[5/7] Unit tests"
PYTHONPATH="$SKILL_ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m unittest discover -s tests

echo "[6/7] Static validation and evals"
python3 scripts/static_validate_skill.py
python3 scripts/run_skill_evals.py

if [[ -n "$ASPECT_BIN" ]]; then
  echo "[7/7] Real ASPECT subduction smoke"
  scripts/aspect-yuan beginner subduction --output-dir "$WORK_DIR/real-subduction" --run --aspect-bin "$ASPECT_BIN" >/dev/null
else
  echo "[7/7] Real ASPECT subduction smoke skipped: pass --aspect-bin PATH to run it."
fi

echo "Install smoke passed. Work directory: $WORK_DIR"
