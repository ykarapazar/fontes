"""User-facing strings for the `fontes` command line (bug reports), shared with the installer.

The module and its locales/<lang>.json files live in installer/ (the installer runs before
Fontes is installed, so it cannot import this package). The wheel carries copies as
world_legal_mcp/_fontes_i18n.py and world_legal_mcp/locales/ (see pyproject.toml); a source
checkout loads them from installer/ directly.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

try:
    from . import _fontes_i18n as _impl
except ImportError:
    _path = Path(__file__).resolve().parents[2] / "installer" / "fontes_i18n.py"
    _spec = importlib.util.spec_from_file_location("world_legal_mcp._fontes_i18n", _path)
    _impl = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_impl)

t = _impl.t
yes = _impl.yes
language = _impl.language
strings = _impl.strings
