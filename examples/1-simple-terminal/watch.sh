#!/usr/bin/env bash
# Live colored TUI table at the default 2-second refresh interval.
# Press Ctrl-C to exit. Pass an interval (in seconds) to override the
# default, e.g. `./watch.sh 5` to refresh every 5 seconds.
exec cpu-thermals "$@"
