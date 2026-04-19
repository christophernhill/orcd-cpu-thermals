#!/usr/bin/env bash
# Run the built cpu_thermals.sif. Forwards args to the in-image
# `cpu-thermals` entrypoint, e.g. ./run.sh 5, ./run.sh --csv ~/cpu.csv,
# ./run.sh --csv -.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[[ -f "$HERE/cpu_thermals.sif" ]] \
    || { echo "build first: $HERE/build.sh" >&2; exit 1; }
exec apptainer run "$HERE/cpu_thermals.sif" "$@"
