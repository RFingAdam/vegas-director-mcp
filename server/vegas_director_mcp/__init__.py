"""Deprecated alias for :mod:`takerelay` (the project was renamed to TakeRelay MCP).

``import vegas_director_mcp``, ``from vegas_director_mcp.tools import ping``
and ``python -m vegas_director_mcp`` keep working for one release and emit a
DeprecationWarning. New code should use ``takerelay``.
"""
from __future__ import annotations

from takerelay import main, mcp  # noqa: F401
from takerelay._compat import install_alias

install_alias(__name__)
del install_alias
