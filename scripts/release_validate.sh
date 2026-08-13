#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: release_validate.sh [--aspect-bin PATH] [--smoke-dir DIR]

Run the Aspect_Yuan/geologist-aspect release checks.

Checks:
  1. static_validate_skill.py
  2. run_skill_evals.py
  3. Python unit tests
  4. Optional beginner subduction ASPECT smoke when --aspect-bin is provided

Options:
  --aspect-bin PATH  ASPECT executable for the release smoke test.
  --smoke-dir DIR    Smoke output directory, default: /tmp/aspect-yuan-release-smoke
  -h, --help         Show this help.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ASPECT_ROOT="$(cd "$SKILL_ROOT/../.." && pwd)"
ASPECT_BIN=""
SMOKE_DIR="/tmp/aspect-yuan-release-smoke"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --aspect-bin)
      ASPECT_BIN="${2:-}"
      shift 2
      ;;
    --smoke-dir)
      SMOKE_DIR="${2:-}"
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

echo "[1/4] Static skill validation"
python3 "$SCRIPT_DIR/static_validate_skill.py"

echo "[2/4] Rule-based skill evals"
python3 "$SCRIPT_DIR/run_skill_evals.py"

echo "[3/4] Python unit tests"
PYTHONPATH="$SKILL_ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m unittest discover -s "$SKILL_ROOT/tests"

if [[ -n "$ASPECT_BIN" ]]; then
  echo "[4/4] Beginner subduction ASPECT smoke"
  rm -rf "$SMOKE_DIR"
  "$SCRIPT_DIR/aspect-yuan" beginner subduction --output-dir "$SMOKE_DIR" --run --aspect-bin "$ASPECT_BIN"
  echo "Smoke directory: $SMOKE_DIR"
else
  echo "[4/4] Beginner subduction ASPECT smoke skipped: pass --aspect-bin PATH to run it."
fi

echo "Release validation complete."
