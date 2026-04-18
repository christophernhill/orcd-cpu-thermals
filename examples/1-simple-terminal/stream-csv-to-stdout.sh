#!/usr/bin/env bash
# Stream long-format CSV to stdout for piping into other tools.
# The TUI is auto-suppressed (stdout is the CSV); banner + summary go to
# stderr so they never contaminate the pipe.
#
# Examples:
#   ./stream-csv-to-stdout.sh | gzip > thermals.csv.gz
#   ./stream-csv-to-stdout.sh | head -20
#   ssh fleetnode ./stream-csv-to-stdout.sh >> all-nodes.csv
exec cpu-thermals --csv - "$@"
