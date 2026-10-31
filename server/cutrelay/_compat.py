"""Helpers for the deprecated ``vegas_director_mcp`` / ``nle_mcp`` aliases.

Both old package names re-export :mod:`cutrelay` (including every submodule,
so ``from vegas_director_mcp.tools import ping`` keeps working) for one
release, and emit a :class:`DeprecationWarning` on import.
"""
from __future__ import annotations

import importlib
import pkgutil
import sys
import warnings


def install_alias(alias: str, *, stacklevel: int = 3) -> None:
    """Map ``alias`` and ``alias.<sub>`` onto ``cutrelay`` / ``cutrelay.<sub>``."""
    warnings.warn(
        f"'{alias}' is deprecated and will be removed in a future release; "
        "import 'cutrelay' (or run 'python -m cutrelay') instead.",
        DeprecationWarning,
        stacklevel=stacklevel,
    )
    import cutrelay

    pkg = sys.modules[alias]
    for name, value in vars(cutrelay).items():
        if not name.startswith("_"):
            setattr(pkg, name, value)
    for mod in pkgutil.walk_packages(cutrelay.__path__, prefix="cutrelay."):
        if mod.name.endswith(".__main__"):
            continue
        loaded = importlib.import_module(mod.name)
        rest = mod.name[len("cutrelay.") :]
        sys.modules[f"{alias}.{rest}"] = loaded
        if "." not in rest:
            setattr(pkg, rest, loaded)
