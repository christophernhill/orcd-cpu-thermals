#!/usr/bin/env bash
# Headless capture: record CSV to an auto-named file with NO live table.
# Suitable for running over SSH, in cron, or backgrounded with `&`.
# Banner ("recording CSV to ...") and final summary go to stderr.
exec cpu-thermals --csv --no-tui "$@"
