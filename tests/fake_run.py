"""Run cpu_thermals.cli.main() with a fake backend.

Used by tests/smoke.sh to exercise the full CSV pipeline end-to-end
without needing a real `sensors` or `smctemp` binary on the host. The
fake source returns 3 fixed readings then raises KeyboardInterrupt,
which trips the CLI's existing teardown path the same way Ctrl-C would.
"""
import sys

import cpu_thermals.cli as cli
from cpu_thermals.backends import Reading


class FiniteFake:
    name = "fake"
    install_help = ""

    def __init__(self):
        self._count = 0

    def check(self):
        pass

    def read(self):
        if self._count >= 3:
            raise KeyboardInterrupt
        self._count += 1
        return [Reading("CPU", 50.0), Reading("GPU", 40.0)]


cli.detect = lambda name=None: FiniteFake()
cli.time.sleep = lambda _s: None   # don't actually wait between samples

sys.exit(cli.main(sys.argv[1:]))
