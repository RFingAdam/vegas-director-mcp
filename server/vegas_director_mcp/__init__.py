"""vegas-director-mcp: FastMCP server entry point.

Run with: python -m vegas_director_mcp
"""
from __future__ import annotations

from fastmcp import FastMCP

from . import tools

mcp = FastMCP("vegas-director-mcp")


@mcp.tool()
def get_project_state() -> dict:
    """Get the current VEGAS project's timeline length and track counts.
    Use this first to confirm the script host is reachable and a project
    is open before attempting any edit operations.
    """
    return tools.get_project_state()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
