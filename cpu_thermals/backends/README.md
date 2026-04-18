# `cpu_thermals.backends` — temperature sources

Each module in this directory teaches the program how to read CPU temperatures on one platform. The shared interface is small enough to fit on a postcard:

```python
class TempSource(Protocol):
    name: str           # short id used by --backend
    install_help: str   # message shown when the underlying tool is missing
    def check(self) -> None: ...                # exit cleanly if unusable
    def read(self) -> Sequence[Reading]: ...    # one shot of readings
```

A `Reading` is just `(label: str, celsius: float)`.

## Current backends

| Module             | Platform              | Underlying tool        | Notes                                                |
| ------------------ | --------------------- | ---------------------- | ---------------------------------------------------- |
| `lm_sensors.py`    | Linux (Intel + AMD)   | `sensors` (lm-sensors) | Parses `Package id` (Intel) and `Tctl` (AMD).        |
| `smctemp.py`       | macOS Apple Silicon   | `smctemp` (third-party)| No sudo; CPU and GPU die temps via SMC keys.         |

Auto-selection lives in [`__init__.py`](__init__.py): the `_AUTO_BY_PLATFORM` table maps `platform.system()` to a backend name, and `detect()` picks one (or honours an explicit `--backend` choice).

## Adding a new backend

Drop a new file (say `mybackend.py`) here that defines a class with the four members above. Then register it in [`__init__.py`](__init__.py):

```python
def _make_mybackend() -> TempSource:
    from .mybackend import MyBackendSource
    return MyBackendSource()

_BACKENDS["mybackend"] = _make_mybackend          # exposes --backend mybackend
_AUTO_BY_PLATFORM["FreeBSD"] = "mybackend"        # optional auto-select rule
```

The lazy `from .mybackend import ...` keeps the import graph small: a Linux machine never imports the macOS backend, and vice versa. That's also why each backend's `INSTALL_HELP` string lives next to its implementation rather than in this `__init__`.

## Known wart: padding in `lm_sensors.py`

`LmSensorsSource.read()` always returns exactly two readings, padding with a fake `0.0°C` if only one CPU package was found. This keeps the original two-column TUI layout simple but lies a bit: `0.0°C` is indistinguishable from "no sensor". A future cleanup would let backends return any number of readings and let renderers handle a 1- or 0-column case. The CSV renderer is unaffected — each reading is a row, and a missing sensor would simply not appear.
