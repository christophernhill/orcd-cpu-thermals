#!/usr/bin/env bash
# Build cpu_thermals.sif. Runs from the repo root so %files paths in
# the .def can reference cpu_thermals/ and pyproject.toml directly.
# Requires apptainer 1.x on PATH.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/../../.."   # repo root
exec apptainer build --force \
    "$HERE/cpu_thermals.sif" \
    "$HERE/cpu_thermals.def"
