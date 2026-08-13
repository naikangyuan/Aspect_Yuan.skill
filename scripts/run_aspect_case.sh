#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_aspect_case.sh <case.prm> [--mpi N] [--aspect-bin PATH] [--log PATH] [--dry-run]

Run an ASPECT parameter file and save a timestamped run log.

Options:
  --mpi N             Run with N MPI processes. Default: 1.
  --aspect-bin PATH   ASPECT executable. Default: ASPECT_BIN env var, then "aspect".
  --log PATH          Log file path. Default: <prm-dir>/<prm-name>.run-YYYYmmdd-HHMMSS.log.
  --dry-run           Print the command and log path without running.
  -h, --help          Show this help.

This script does not modify the original .prm file.
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

prm_file=""
mpi_ranks=1
aspect_bin="${ASPECT_BIN:-aspect}"
log_file=""
dry_run=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mpi|-n)
      [[ $# -ge 2 ]] || { echo "error: --mpi requires a value" >&2; exit 2; }
      mpi_ranks="$2"
      shift 2
      ;;
    --aspect-bin)
      [[ $# -ge 2 ]] || { echo "error: --aspect-bin requires a value" >&2; exit 2; }
      aspect_bin="$2"
      shift 2
      ;;
    --log)
      [[ $# -ge 2 ]] || { echo "error: --log requires a value" >&2; exit 2; }
      log_file="$2"
      shift 2
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "error: unknown option: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [[ -n "$prm_file" ]]; then
        echo "error: only one .prm file may be provided" >&2
        exit 2
      fi
      prm_file="$1"
      shift
      ;;
  esac
done

if [[ -z "$prm_file" ]]; then
  echo "error: missing .prm file" >&2
  usage
  exit 2
fi

if [[ ! -f "$prm_file" ]]; then
  echo "error: .prm file not found: $prm_file" >&2
  exit 2
fi

if ! [[ "$mpi_ranks" =~ ^[0-9]+$ ]] || [[ "$mpi_ranks" -lt 1 ]]; then
  echo "error: --mpi must be a positive integer" >&2
  exit 2
fi

prm_dir="$(cd "$(dirname "$prm_file")" && pwd)"
prm_base="$(basename "$prm_file")"
prm_abs="$prm_dir/$prm_base"

if [[ -z "$log_file" ]]; then
  timestamp="$(date +%Y%m%d-%H%M%S)"
  log_file="$prm_dir/${prm_base%.prm}.run-${timestamp}.log"
fi

mkdir -p "$(dirname "$log_file")"

if [[ "$mpi_ranks" -gt 1 ]]; then
  cmd=(mpirun -np "$mpi_ranks" "$aspect_bin" "$prm_abs")
else
  cmd=("$aspect_bin" "$prm_abs")
fi

echo "ASPECT run command:"
printf ' %q' "${cmd[@]}"
echo
echo "Run log: $log_file"
echo "Geologist note: inspect the log first, then the statistics and visualization outputs."

if [[ "$dry_run" == true ]]; then
  exit 0
fi

{
  echo "# ASPECT run started: $(date -Is)"
  echo "# Command:"
  printf '# %q' "${cmd[@]}"
  echo
  set +e
  "${cmd[@]}"
  status=$?
  set -e
  echo "# ASPECT run finished: $(date -Is)"
  echo "# Exit status: $status"
  exit "$status"
} 2>&1 | tee "$log_file"
