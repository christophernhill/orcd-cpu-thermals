#!/usr/bin/env bash
#
# Smoke tests for cpu_thermals.
#
# Usage:
#   ./tests/smoke.sh
#
# Each check prints "  ok    <name>" or "  FAIL  <name>". The script
# uses `set -e` so the first failing check stops the run with a
# non-zero exit code.
#
# No third-party packages are required. Just python3 and bash.

set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"   # so `python3 -m cpu_thermals` works without pip install

ok()      { printf "  ok    %s\n" "$1"; }
fail()    { printf "  FAIL  %s\n" "$1"; exit 1; }
section() { printf "\n== %s ==\n" "$1"; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT


# -------------------------------------------------------------- CLI args

section "CLI argument handling"

python3 -m cpu_thermals --help >/dev/null \
    || fail "--help should exit 0"
python3 -m cpu_thermals --help | grep -q -- "--csv" \
    || fail "--help should mention --csv"
python3 -m cpu_thermals --help | grep -q -- "--no-tui" \
    || fail "--help should mention --no-tui"
ok "--help works and lists --csv / --no-tui"

# `set -e` would abort on the expected non-zero exit, so wrap with `!`.
! python3 -m cpu_thermals --no-tui 2>"$TMP/err" \
    || fail "--no-tui without --csv should exit non-zero"
grep -q "requires --csv" "$TMP/err" \
    || fail "--no-tui error should mention 'requires --csv'"
ok "--no-tui without --csv is rejected with a clear message"

! python3 -m cpu_thermals --backend bogus 2>/dev/null \
    || fail "--backend bogus should exit non-zero"
ok "--backend rejects unknown values"

! python3 -m cpu_thermals not-a-number 2>/dev/null \
    || fail "non-numeric interval should exit non-zero"
ok "interval must be a number"


# ------------------------------------------------ CSV pipeline (fake backend)

section "CSV pipeline (fake backend)"

# --csv to a file
python3 tests/fake_run.py 0 --csv "$TMP/out.csv" --no-tui \
    >/dev/null 2>"$TMP/err"
# Note: csv.writer emits RFC 4180 CRLF line endings, so we strip \r
# before comparing the header line.
[[ "$(head -1 "$TMP/out.csv" | tr -d '\r')" == "timestamp,node,sensor,celsius" ]] \
    || fail "csv file should start with the header"
[[ "$(wc -l <"$TMP/out.csv")" -eq 7 ]] \
    || fail "csv file should be header + 3 reads * 2 sensors = 7 lines"
grep -q "wrote 6 rows" "$TMP/err" \
    || fail "stderr should report 'wrote 6 rows'"
ok "--csv FILE writes header + 6 rows + summary on stderr"

# Re-running appends without a duplicate header.
python3 tests/fake_run.py 0 --csv "$TMP/out.csv" --no-tui \
    >/dev/null 2>/dev/null
[[ "$(grep -c '^timestamp,' "$TMP/out.csv")" -eq 1 ]] \
    || fail "second run should not add a duplicate header"
[[ "$(wc -l <"$TMP/out.csv")" -eq 13 ]] \
    || fail "second run should leave header + 12 data rows"
ok "second --csv FILE run appends cleanly"

# --csv -  (stdout, TUI auto-suppressed)
python3 tests/fake_run.py 0 --csv - >"$TMP/out.csv" 2>"$TMP/err"
[[ "$(head -1 "$TMP/out.csv" | tr -d '\r')" == "timestamp,node,sensor,celsius" ]] \
    || fail "--csv - should write header to stdout"
grep -q "TUI suppressed" "$TMP/err" \
    || fail "stderr should warn about TUI auto-suppress"
grep -q "recording CSV to stdout" "$TMP/err" \
    || fail "stderr should have the recording banner"
ok "--csv - streams CSV to stdout, banner + auto-suppress note on stderr"

# --csv -  --no-tui  (explicit; no auto-suppress note)
python3 tests/fake_run.py 0 --csv - --no-tui >/dev/null 2>"$TMP/err"
! grep -q "TUI suppressed" "$TMP/err" \
    || fail "--no-tui should silence the auto-suppress note"
ok "explicit --no-tui silences the auto-suppress note"


# ----------------------------------------------------- example shell scripts

section "examples/ shell scripts"

bash -n examples/2-mprime-stress/run.sh \
    || fail "run.sh has a bash syntax error"
bash -n examples/3-systemd-csv-rotation/install.sh \
    || fail "install.sh has a bash syntax error"
ok "shell scripts pass bash -n"

if command -v shellcheck >/dev/null 2>&1; then
    shellcheck examples/2-mprime-stress/run.sh \
        || fail "shellcheck on run.sh"
    shellcheck examples/3-systemd-csv-rotation/install.sh \
        || fail "shellcheck on install.sh"
    ok "shell scripts pass shellcheck"
else
    ok "shellcheck not installed (skipping)"
fi


# ------------------------------------------------ systemd unit + logrotate

section "examples/ systemd + logrotate"

UNIT="examples/3-systemd-csv-rotation/cpu-thermals.service"
for required in '^\[Unit\]' '^\[Service\]' '^\[Install\]' \
                '^ExecStart=/usr/local/bin/cpu-thermals --csv -' \
                '^StandardOutput=append:' '^Restart=always'; do
    grep -qE "$required" "$UNIT" || fail "systemd unit missing: $required"
done
ok "systemd unit has required sections + critical keys"

LR="examples/3-systemd-csv-rotation/cpu-thermals.logrotate"
[[ "$(tr -cd '{' <"$LR" | wc -c)" -eq "$(tr -cd '}' <"$LR" | wc -c)" ]] \
    || fail "logrotate config has unbalanced braces"
grep -q "postrotate" "$LR" || fail "logrotate config missing postrotate"
grep -q "endscript"  "$LR" || fail "logrotate config missing endscript"
ok "logrotate config is well-formed"

echo
echo "All checks passed."
