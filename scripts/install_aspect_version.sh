#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  install_aspect_version.sh --source-url URL --ref TAG_OR_COMMIT --prefix DIR [--deal-ii-dir DIR] [--fastscape-dir DIR] [--dry-run]

Purpose:
  Prepare an isolated ASPECT checkout/build for paper reproduction.
  This helper must not overwrite the user's main ASPECT checkout.

Notes:
  - Use --dry-run first.
  - Downloads/builds may take substantial time and need user approval.
  - If a paper provides a container, prefer the container before rebuilding manually.
EOF
}

SOURCE_URL=""
REF=""
PREFIX=""
DEAL_II_DIR=""
FASTSCAPE_DIR=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-url) SOURCE_URL="$2"; shift 2 ;;
    --ref) REF="$2"; shift 2 ;;
    --prefix) PREFIX="$2"; shift 2 ;;
    --deal-ii-dir) DEAL_II_DIR="$2"; shift 2 ;;
    --fastscape-dir) FASTSCAPE_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$SOURCE_URL" || -z "$REF" || -z "$PREFIX" ]]; then
  echo "Error: --source-url, --ref, and --prefix are required." >&2
  usage
  exit 2
fi

SRC_DIR="$PREFIX/source/aspect-$REF"
BUILD_DIR="$PREFIX/build/aspect-$REF-release"

echo "ASPECT isolated installation plan"
echo "- Source URL: $SOURCE_URL"
echo "- Ref/tag/commit: $REF"
echo "- Source directory: $SRC_DIR"
echo "- Build directory: $BUILD_DIR"
if [[ -n "$DEAL_II_DIR" ]]; then
  echo "- deal.II directory: $DEAL_II_DIR"
else
  echo "- deal.II directory: use CMake defaults or environment"
fi
if [[ -n "$FASTSCAPE_DIR" ]]; then
  echo "- FastScape directory: $FASTSCAPE_DIR"
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo
  echo "Dry run only. Commands that would be executed:"
  echo "mkdir -p \"$PREFIX/source\" \"$PREFIX/build\""
  echo "git clone \"$SOURCE_URL\" \"$SRC_DIR\""
  echo "git -C \"$SRC_DIR\" checkout \"$REF\""
  echo "cmake -S \"$SRC_DIR\" -B \"$BUILD_DIR\" -DCMAKE_BUILD_TYPE=Release ${DEAL_II_DIR:+-DDEAL_II_DIR=\"$DEAL_II_DIR\"} ${FASTSCAPE_DIR:+-DFASTSCAPE_DIR=\"$FASTSCAPE_DIR\"}"
  echo "cmake --build \"$BUILD_DIR\" --parallel"
  echo "\"$BUILD_DIR/aspect\" --version"
  exit 0
fi

if [[ -e "$SRC_DIR" || -e "$BUILD_DIR" ]]; then
  echo "Error: source or build directory already exists. Refusing to overwrite." >&2
  exit 1
fi

mkdir -p "$PREFIX/source" "$PREFIX/build"
git clone "$SOURCE_URL" "$SRC_DIR"
git -C "$SRC_DIR" checkout "$REF"

CMAKE_ARGS=(-S "$SRC_DIR" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release)
if [[ -n "$DEAL_II_DIR" ]]; then
  CMAKE_ARGS+=("-DDEAL_II_DIR=$DEAL_II_DIR")
fi
if [[ -n "$FASTSCAPE_DIR" ]]; then
  CMAKE_ARGS+=("-DFASTSCAPE_DIR=$FASTSCAPE_DIR")
fi
cmake "${CMAKE_ARGS[@]}"
cmake --build "$BUILD_DIR" --parallel

if [[ -x "$BUILD_DIR/aspect" ]]; then
  "$BUILD_DIR/aspect" --version
else
  echo "Build finished, but $BUILD_DIR/aspect was not found or is not executable." >&2
  exit 1
fi
