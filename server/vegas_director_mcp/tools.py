"""MCP tool definitions: the VEGAS-facing surface exposed to the model.

Phase 0 scaffold: one real end-to-end tool (get_project_state) to prove the
round trip works, plus stub signatures for the Phase 1/2/3 surface so the
shape of the eventual tool set is visible in one place. See
docs/API_COVERAGE.md for what's implemented vs. planned, and docs/ROADMAP.md
for build order.
"""
from __future__ import annotations

from .host_client import VegasHostClient, VegasHostError

_client = VegasHostClient()


def get_project_state() -> dict:
    """Return the current VEGAS project's basic state: timeline length and
    track counts. Fails clearly if no project is open or the host isn't
    reachable -- never silently returns empty/default data.
    """
    try:
        return _client.call("project.get_state")
    except VegasHostError as exc:
        return {"error": True, "code": exc.code, "message": exc.message}
    except (ConnectionRefusedError, FileNotFoundError, OSError) as exc:
        return {
            "error": True,
            "code": -1,
            "message": (
                "Could not reach the VEGAS script host. Is VEGAS running "
                f"with VegasDirectorHost active? ({exc})"
            ),
        }


# --- Planned surface (Phase 1+, not yet implemented) ---
# Left as explicit placeholders rather than omitted, so the intended tool
# set is visible to anyone reading this file. Each raises NotImplementedError
# rather than silently no-op'ing, so a premature call fails loud.


def add_video_event(track_index: int, start_seconds: float, length_seconds: float,
                     media_path: str) -> dict:
    """Place a video clip on a track at a given position. (Phase 1)"""
    raise NotImplementedError("event.add_video not yet wired -- see docs/ROADMAP.md Phase 1")


def add_audio_event(track_index: int, start_seconds: float, length_seconds: float,
                     media_path: str) -> dict:
    """Place an audio clip on a track at a given position. (Phase 1)"""
    raise NotImplementedError("event.add_audio not yet wired -- see docs/ROADMAP.md Phase 1")


def render_project(output_path: str, template_name: str) -> dict:
    """Render the current project to a file using a named render template.
    (Phase 1/4)
    """
    raise NotImplementedError("render.start not yet wired -- see docs/ROADMAP.md Phase 1/4")


def probe_media(path: str) -> dict:
    """Return duration/resolution/fps/audio-peak data for a media file via
    ffprobe. Local analysis -- does not touch the VEGAS host at all.
    (Phase 2)
    """
    raise NotImplementedError("probe_media not yet implemented -- see docs/ROADMAP.md Phase 2")


def detect_scenes(path: str) -> dict:
    """Return scene-change timestamps for a media file via ffmpeg. Local
    analysis -- does not touch the VEGAS host. (Phase 2)
    """
    raise NotImplementedError("detect_scenes not yet implemented -- see docs/ROADMAP.md Phase 2")
