"""macOS (Apple Silicon) backend: reads temps via the ``smctemp`` CLI.

``smctemp`` (https://github.com/narugit/smctemp) reads SMC sensor keys
without requiring sudo. We invoke ``smctemp -c`` for the CPU die temperature
and ``smctemp -g`` for the GPU. Both print a single floating-point value on
stdout (e.g. ``"54.2"``); a missing / unparseable value yields a Reading of
``0.0`` rather than crashing the loop, mirroring the lm-sensors backend.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from typing import List

from . import Reading


INSTALL_HELP = """\
Error: 'smctemp' command not found.

cpu_thermals on macOS depends on the third-party 'smctemp' tool, which
reads SMC sensor keys without requiring sudo. It is not in homebrew-core;
install it from the maintainer's tap:

  brew tap narugit/tap
  brew install narugit/tap/smctemp

Or build from source:

  git clone https://github.com/narugit/smctemp.git
  cd smctemp && sudo make install

After installation, run 'smctemp -c' to verify it works, then re-run
cpu_thermals.
"""


_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _read_one(flag: str) -> float:
    """Run ``smctemp <flag>`` and parse the first numeric token.

    Returns 0.0 if the command fails or the output has no number; smctemp
    sometimes exits 0 even when a sensor is not populated, so we don't
    bail out on that path.
    """
    try:
        out = subprocess.check_output(
            ["smctemp", flag],
            stderr=subprocess.STDOUT,
            timeout=5,
        ).decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return 0.0

    match = _NUM_RE.search(out)
    if not match:
        return 0.0
    try:
        return float(match.group(0))
    except ValueError:
        return 0.0


class SmctempSource:
    name = "smctemp"
    install_help = INSTALL_HELP

    def check(self) -> None:
        if shutil.which("smctemp") is None:
            sys.stderr.write(self.install_help)
            sys.exit(127)

        try:
            subprocess.check_output(
                ["smctemp", "-c"],
                stderr=subprocess.STDOUT,
                timeout=5,
            )
        except subprocess.CalledProcessError as e:
            sys.stderr.write(
                "Error: 'smctemp' is installed but failed to run "
                f"(exit code {e.returncode}).\n"
                "Try running 'smctemp -c' manually to see the error.\n"
            )
            sys.exit(e.returncode or 1)
        except (subprocess.TimeoutExpired, OSError) as e:
            sys.stderr.write(f"Error invoking 'smctemp': {e}\n")
            sys.exit(1)

    def read(self) -> List[Reading]:
        return [
            Reading("CPU", _read_one("-c")),
            Reading("GPU", _read_one("-g")),
        ]
