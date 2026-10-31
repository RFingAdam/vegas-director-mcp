"""Deprecated alias for :mod:`cutrelay` (the project was renamed to CutRelay MCP).

``import vegas_director_mcp``, ``from vegas_director_mcp.tools import ping``
and ``python -m vegas_director_mcp`` keep working for one release and emit a
DeprecationWarning. New code should use ``cutrelay``.
"""
from __future__ import annotations

from cutrelay import main, mcp  # noqa: F401
from cutrelay._compat import install_alias

install_alias(__name__)
del install_alias
