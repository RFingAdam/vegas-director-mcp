"""Editor backends. Default is VEGAS so existing installs keep working.

Select an editor with DIRECTOR_EDITOR (or VEGAS_DIRECTOR_EDITOR):

  vegas     MAGIX VEGAS Pro (C# host, TCP 127.0.0.1:8752) — default
  resolve   DaVinci Resolve Studio via DaVinciResolveScript / fusionscript
  otio      In-memory timeline; project.save writes .otio or .mlt
"""
from __future__ import annotations

import os
from typing import Any

from .protocol import EditorBackend, fail
from .vegas import VegasBackend

KNOWN_EDITORS = {
    "vegas": "vegas",
    "vegas-pro": "vegas",
    "vegas_pro": "vegas",
    "resolve": "resolve",
    "davinci": "resolve",
    "davinci-resolve": "resolve",
    "davinci_resolve": "resolve",
    "otio": "otio",
    "opentimelineio": "otio",
    "mlt": "otio",
    "fcpxml": "otio",
    "kdenlive": "otio",
    "shotcut": "otio",
    "interchange": "otio",
}


def editor_from_env() -> str:
    raw = (
        os.environ.get("DIRECTOR_EDITOR")
        or os.environ.get("VEGAS_DIRECTOR_EDITOR")
        or "vegas"
    )
    key = raw.strip().lower().replace(" ", "-")
    return KNOWN_EDITORS.get(key, key)


def create_backend(name: str | None = None, **kwargs: Any) -> EditorBackend:
    editor = name or editor_from_env()
    if editor == "vegas":
        return VegasBackend(**kwargs)
    if editor == "resolve":
        from .resolve import ResolveBackend

        return ResolveBackend(**kwargs)
    if editor == "otio":
        from .otio import OtioBackend

        return OtioBackend(**kwargs)
    raise ValueError(
        f"Unknown editor {editor!r}. Use one of: vegas, resolve, otio "
        f"(DIRECTOR_EDITOR)."
    )


_BACKEND: EditorBackend | None = None


def get_backend() -> EditorBackend:
    global _BACKEND
    if _BACKEND is None:
        try:
            _BACKEND = create_backend()
        except ValueError as exc:
            # Fall back to VEGAS rather than crash MCP startup on a typo;
            # the first tool call still reports the error via a stub.
            _BACKEND = _UnknownBackend(str(exc))
    return _BACKEND


def reset_backend(backend: EditorBackend | None = None) -> EditorBackend | None:
    """Test helper. Pass None to rebuild from the environment on next get."""
    global _BACKEND
    _BACKEND = backend
    return _BACKEND


def list_editors() -> dict[str, Any]:
    current = editor_from_env()
    return {
        "ok": True,
        "editor": current if current in {"vegas", "resolve", "otio"} else current,
        "editors": [
            {
                "id": "vegas",
                "label": "MAGIX VEGAS Pro",
                "live": True,
                "default": True,
            },
            {
                "id": "resolve",
                "label": "DaVinci Resolve Studio 21.1+",
                "live": True,
                "default": False,
                "studio_required": True,
                "note": "Free Resolve has no Scripting API since 21.1.",
            },
            {
                "id": "otio",
                "label": "OpenTimelineIO / FCPXML / MLT interchange",
                "live": False,
                "default": False,
                "studio_required": False,
                "note": "Free-friendly export. Free Resolve imports .otio / .fcpxml.",
            },
        ],
        "env": "DIRECTOR_EDITOR",
    }


class _UnknownBackend:
    name = "unknown"

    def __init__(self, error: str):
        self.error = error

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return fail(self.error, editor=self.name, method=method)

    def ensure(self, project_path: str | None = None) -> dict[str, Any]:
        return fail(self.error, editor=self.name)

    def capabilities(self) -> dict[str, Any]:
        return fail(self.error, editor=self.name)
