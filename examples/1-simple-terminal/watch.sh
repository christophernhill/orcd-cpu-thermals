#!/usr/bin/env bash
# Live colored TUI table at the default 2-second refresh interval.
# Press Ctrl-C to exit. Pass extra flags through, e.g. ./watch.sh --backend lm-sensors
exec cpu-thermals "$@"
