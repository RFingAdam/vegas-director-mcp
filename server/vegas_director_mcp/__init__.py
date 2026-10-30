"""Backward-compatible import alias for ``nle_mcp``.

``import vegas_director_mcp`` and ``from vegas_director_mcp.tools import ping``
still work. New code should import ``nle_mcp``.
"""
from __future__ import annotations

import importlib
import pkgutil
import sys

import nle_mcp
from nle_mcp import main, mcp  # noqa: F401
from nle_mcp import *  # noqa: F403

_pkg = sys.modules[__name__]
for _mod in pkgutil.walk_packages(nle_mcp.__path__, prefix="nle_mcp."):
    _loaded = importlib.import_module(_mod.name)
    _alias = __name__ + _mod.name[len("nle_mcp") :]
    sys.modules[_alias] = _loaded
    _rest = _mod.name[len("nle_mcp.") :]
    if "." not in _rest:
        setattr(_pkg, _rest, _loaded)
del _mod, _loaded, _alias, _rest, _pkg
