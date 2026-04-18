#!/usr/bin/env bash
# Live colored TUI table AND record CSV to an auto-named file in the
# current directory. Filename is cpu_thermals-<host>-<YYYYMMDD-HHMMSS>.csv.
# Press Ctrl-C to stop; a "wrote N rows to ..." summary appears on stderr.
exec cpu-thermals --csv "$@"
