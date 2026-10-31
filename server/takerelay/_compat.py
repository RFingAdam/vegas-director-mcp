"""Helpers for the deprecated ``cutrelay`` / ``vegas_director_mcp`` / ``nle_mcp`` aliases.

Every old package name re-exports :mod:`takerelay` (including every submodule,
so ``from vegas_director_mcp.tools import ping`` keeps working) for one
release, and emit a :class:`DeprecationWarning` on import.
"""
from __future__ import annotations

import importlib
import pkgutil
import sys
import warnings


def install_alias(alias: str, *, stacklevel: int = 3) -> None:
    """Map ``alias`` and ``alias.<sub>`` onto ``takerelay`` / ``takerelay.<sub>``."""
    warnings.warn(
        f"'{alias}' is deprecated and will be removed in a future release; "
        "import 'takerelay' (or run 'python -m takerelay') instead.",
        DeprecationWarning,
        stacklevel=stacklevel,
    )
    import takerelay

    pkg = sys.modules[alias]
    for name, value in vars(takerelay).items():
        if not name.startswith("_"):
            setattr(pkg, name, value)
    for mod in pkgutil.walk_packages(takerelay.__path__, prefix="takerelay."):
        if mod.name.endswith(".__main__"):
            continue
        loaded = importlib.import_module(mod.name)
        rest = mod.name[len("takerelay.") :]
        sys.modules[f"{alias}.{rest}"] = loaded
        if "." not in rest:
            setattr(pkg, rest, loaded)
