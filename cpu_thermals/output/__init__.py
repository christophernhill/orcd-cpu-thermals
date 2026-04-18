"""Output renderers for cpu_thermals.

A ``Renderer`` is the "where do the readings go?" half of the program. The
backends (see :mod:`cpu_thermals.backends`) decide *what* to read; renderers
decide *how to present it*. Each renderer implements three small methods:

* ``start(labels)`` — once, before the first row (write headers, banners).
* ``row(readings)`` — for every sample.
* ``stop()`` — once, on Ctrl-C (cleanup, summary lines).

Two concrete renderers ship in-tree:

* :class:`~cpu_thermals.output.table.TableRenderer` — the live colored TUI.
* :class:`~cpu_thermals.output.csv.CsvRenderer` — append-safe CSV file.

When more than one renderer is active (for example ``--csv`` keeps the TUI
on screen while also recording a CSV file), :class:`MultiRenderer` fans the
calls out to each. The run loop in :mod:`cpu_thermals.cli` is therefore
unaware of how many destinations are in play.
"""

from __future__ import annotations

from typing import List, Optional, Protocol, Sequence

from ..backends import Reading


class Renderer(Protocol):
    """Where temperature readings go.

    Implementations must be safe to use as a context for one full session:
    a single ``start`` call, many ``row`` calls, and a single ``stop`` call.
    """

    name: str

    def start(self, labels: Sequence[str]) -> None: ...

    def row(self, readings: Sequence[Reading]) -> None: ...

    def stop(self) -> None: ...


class MultiRenderer:
    """Composite renderer that fans ``start``/``row``/``stop`` to children.

    This is a tiny example of the Composite pattern: callers treat one
    renderer or a group identically.
    """

    name = "multi"

    def __init__(self, *renderers: Renderer) -> None:
        self._renderers: tuple[Renderer, ...] = renderers

    def start(self, labels: Sequence[str]) -> None:
        for r in self._renderers:
            r.start(labels)

    def row(self, readings: Sequence[Reading]) -> None:
        for r in self._renderers:
            r.row(readings)

    def stop(self) -> None:
        for r in self._renderers:
            r.stop()


def select(*, tui: bool, csv_path: Optional[str]) -> Renderer:
    """Build the renderer (or composite) for this run.

    ``tui=True`` includes the live colored table; ``csv_path`` (if set)
    adds a CSV file destination. When both are active the result is a
    :class:`MultiRenderer`; when only one is active that renderer is
    returned directly so the call stack stays shallow.

    Refuses to build a "do nothing" renderer (``tui=False`` and no CSV)
    rather than silently sampling temps to the void.
    """
    # Imports are local so importing this module never forces the rest of
    # the output stack (and its third-party-free deps) to load.
    from .table import TableRenderer
    from .csv import CsvRenderer

    parts: List[Renderer] = []
    if tui:
        parts.append(TableRenderer())
    if csv_path:
        parts.append(CsvRenderer(csv_path))

    if not parts:
        raise SystemExit(
            "error: --no-tui requires --csv: there would be nothing to do"
        )

    return parts[0] if len(parts) == 1 else MultiRenderer(*parts)


__all__ = ["Renderer", "MultiRenderer", "select"]
