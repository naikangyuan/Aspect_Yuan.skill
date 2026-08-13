#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: build_aspect_plugin.sh <plugin-dir> [--aspect-dir <Aspect_DIR>] [--build-dir <build-dir>]

Build an external ASPECT plugin without modifying ASPECT source.

Inputs:
  <plugin-dir>              Directory containing CMakeLists.txt
  --aspect-dir <Aspect_DIR> ASPECT build/install directory passed to CMake
  --build-dir <build-dir>   Build directory, default: <plugin-dir>/build

ASPECT_DIR environment variable is used when --aspect-dir is omitted.
EOF
}

if [[ $# -ge 1 && ( "$1" == "-h" || "$1" == "--help" ) ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

plugin_dir="$1"
shift
aspect_dir="${ASPECT_DIR:-}"
build_dir=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --aspect-dir)
      [[ $# -ge 2 ]] || { echo "error: --aspect-dir requires a value" >&2; exit 2; }
      aspect_dir="$2"
      shift 2
      ;;
    --build-dir)
      [[ $# -ge 2 ]] || { echo "error: --build-dir requires a value" >&2; exit 2; }
      build_dir="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

plugin_dir="$(cd "$plugin_dir" && pwd)"
if [[ ! -f "$plugin_dir/CMakeLists.txt" ]]; then
  echo "error: $plugin_dir/CMakeLists.txt does not exist" >&2
  echo "Copy assets/plugin_templates/CMakeLists.txt.template to CMakeLists.txt and edit TARGET/SOURCES." >&2
  exit 2
fi

if [[ -z "$build_dir" ]]; then
  build_dir="$plugin_dir/build"
fi
mkdir -p "$build_dir"
build_dir="$(cd "$build_dir" && pwd)"

cmake_args=()
if [[ -n "$aspect_dir" ]]; then
  cmake_args+=("-D" "Aspect_DIR=$aspect_dir")
fi

echo "Configuring plugin:"
echo "  plugin dir: $plugin_dir"
echo "  build dir:  $build_dir"
if [[ -n "$aspect_dir" ]]; then
  echo "  Aspect_DIR: $aspect_dir"
else
  echo "  Aspect_DIR: <from CMake hints or ASPECT_DIR environment>"
fi

cmake -S "$plugin_dir" -B "$build_dir" "${cmake_args[@]}"
cmake --build "$build_dir"

echo
echo "Shared libraries produced:"
find "$build_dir" -maxdepth 3 -type f \( -name '*.so' -o -name '*.dylib' -o -name '*.dll' \) -print
