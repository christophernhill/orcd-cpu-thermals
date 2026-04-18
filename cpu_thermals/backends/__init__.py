"""Temperature source backends for cpu_thermals.

Each backend is a small object exposing:
  - ``name``: short identifier used by the ``--backend`` flag
  - ``install_help``: multi-line string shown when the underlying tool is missing
  - ``check()``: validates the tool is installed and runnable; exits otherwise
  - ``read()``: returns a sequence of ``Reading`` for the current moment

Adding a new platform means dropping a new module in this directory and
registering it in :data:`_BACKENDS` below.
"""

from __future__ import annotations

import platform
import sys
from typing import NamedTuple, Optional, Protocol, Sequence


class Reading(NamedTuple):
    """A single labelled temperature sample."""

    label: str
    celsius: float


class TempSource(Protocol):
    """The interface every backend implements.

    Attributes:
        name: short identifier used by the ``--backend`` flag.
        install_help: multi-line message printed when the underlying tool
            is missing.
    """

    name: str
    install_help: str

    def check(self) -> None: ...

    def read(self) -> Sequence[Reading]: ...


def _make_lm_sensors() -> TempSource:
    from .lm_sensors import LmSensorsSource
    return LmSensorsSource()


def _make_smctemp() -> TempSource:
    from .smctemp import SmctempSource
    return SmctempSource()


_BACKENDS = {
    "lm-sensors": _make_lm_sensors,
    "smctemp": _make_smctemp,
}

_AUTO_BY_PLATFORM = {
    "Linux": "lm-sensors",
    "Darwin": "smctemp",
}

BACKEND_NAMES = ["auto", *_BACKENDS.keys()]


def detect(name: Optional[str] = None) -> TempSource:
    """Pick a backend by explicit name, or auto-detect from the current OS.

    Exits with a clear error if the requested backend is unknown or if the
    current OS has no registered backend.
    """
    if name and name != "auto":
        if name not in _BACKENDS:
            sys.stderr.write(
                f"Unknown backend: {name!r}. "
                f"Choose from: {', '.join(BACKEND_NAMES)}\n"
            )
            sys.exit(2)
        return _BACKENDS[name]()

    system = platform.system()
    chosen = _AUTO_BY_PLATFORM.get(system)
    if chosen is None:
        supported = ", ".join(sorted(_AUTO_BY_PLATFORM))
        sys.stderr.write(
            f"No cpu_thermals backend for OS {system!r}. "
            f"Supported: {supported}.\n"
            "Use --backend to force a specific backend.\n"
        )
        sys.exit(1)
    return _BACKENDS[chosen]()


__all__ = ["Reading", "TempSource", "detect", "BACKEND_NAMES"]
