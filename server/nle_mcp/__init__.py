"""Deprecated alias for :mod:`cutrelay` (``nle-mcp`` was renamed to CutRelay MCP).

``import nle_mcp`` and ``python -m nle_mcp`` keep working for one release and
emit a DeprecationWarning. New code should use ``cutrelay``.
"""
from __future__ import annotations

from cutrelay import main, mcp  # noqa: F401
from cutrelay._compat import install_alias

install_alias(__name__)
del install_alias
