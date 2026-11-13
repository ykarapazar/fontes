"""Auto-discovers jurisdiction adapters and resolves codes/aliases."""
from __future__ import annotations

import importlib
import pkgutil

from . import _http, jurisdictions
from .base import Jurisdiction

_all: dict[str, Jurisdiction] = {}      # code -> adapter instance
_aliases: dict[str, str] = {}           # alias -> code
_enabled: set[str] | None = None        # None = all (see enable_only)


def register(j: Jurisdiction) -> None:
    _all[j.code] = j
    for a in j.aliases:
        _aliases[a.lower()] = j.code
    for host, secs in j.min_interval.items():
        _http.set_min_interval(host, secs)


def discover() -> None:
    """Import every module in world_legal_mcp.jurisdictions and register its adapters."""
    if _all:
        return
    for mod in pkgutil.iter_modules(jurisdictions.__path__):
        if mod.name.startswith("_"):
            continue
        module = importlib.import_module(f"{jurisdictions.__name__}.{mod.name}")
        for obj in vars(module).values():
            if (isinstance(obj, type) and issubclass(obj, Jurisdiction)
                    and obj is not Jurisdiction and obj.code):
                register(obj())


def canonical(code: str) -> str:
    c = (code or "").strip().lower()
    return _aliases.get(c, c)


def enable_only(codes: list[str]) -> None:
    """Restrict the server to these jurisdictions (codes or aliases)."""
    global _enabled
    discover()
    wanted = {canonical(c) for c in codes if c.strip()}
    unknown = wanted - _all.keys()
    if unknown:
        raise SystemExit(f"Unknown jurisdiction(s): {', '.join(sorted(unknown))}. "
                         f"Available: {', '.join(sorted(_all))}")
    _enabled = wanted


def available() -> list[Jurisdiction]:
    discover()
    return [j for code, j in sorted(_all.items()) if _enabled is None or code in _enabled]


def get(code: str) -> Jurisdiction | None:
    discover()
    c = canonical(code)
    if c in _all and (_enabled is None or c in _enabled):
        return _all[c]
    return None
