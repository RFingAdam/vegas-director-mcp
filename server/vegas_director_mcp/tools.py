"""MCP tool definitions backed by the VEGAS script host."""
from __future__ import annotations

from typing import Any

from .host_client import VegasHostClient, VegasHostError

_client = VegasHostClient()


def _call(method: str, params: dict[str, Any] | None = None) -> dict:
    try:
        result = _client.call(method, params)
        if isinstance(result, dict):
            return result
        return {"result": result}
    except VegasHostError as exc:
        return {"error": True, "code": exc.code, "message": exc.message}
    except (ConnectionRefusedError, FileNotFoundError, OSError, TimeoutError) as exc:
        return {
            "error": True,
            "code": -1,
            "message": (
                "Could not reach the VEGAS script host. Open VEGAS Pro, run "
                "Tools > Scripting > VegasDirectorHost, leave the dialog open. "
                f"({exc})"
            ),
        }


def ping() -> dict:
    return _call("ping")


def get_project_state() -> dict:
    return _call("project.get_state")


def save_project(path: str | None = None) -> dict:
    params: dict[str, Any] = {}
    if path:
        params["path"] = path
    return _call("project.save", params)


def add_track(type: str = "video", name: str = "") -> dict:
    return _call("track.add", {"type": type, "name": name})


def import_media(path: str) -> dict:
    return _call("media.import", {"path": path})


def add_video_event(
    track_index: int,
    media_path: str,
    start_seconds: float = 0.0,
    length_seconds: float = -1.0,
) -> dict:
    return _call(
        "event.add_video",
        {
            "track_index": track_index,
            "media_path": media_path,
            "start_seconds": start_seconds,
            "length_seconds": length_seconds,
        },
    )


def add_audio_event(
    track_index: int,
    media_path: str,
    start_seconds: float = 0.0,
    length_seconds: float = -1.0,
) -> dict:
    return _call(
        "event.add_audio",
        {
            "track_index": track_index,
            "media_path": media_path,
            "start_seconds": start_seconds,
            "length_seconds": length_seconds,
        },
    )


def trim_event(
    track_index: int,
    event_index: int,
    start_seconds: float | None = None,
    length_seconds: float | None = None,
) -> dict:
    params: dict[str, Any] = {
        "track_index": track_index,
        "event_index": event_index,
    }
    if start_seconds is not None:
        params["start_seconds"] = start_seconds
    if length_seconds is not None:
        params["length_seconds"] = length_seconds
    return _call("event.trim", params)


def move_event(track_index: int, event_index: int, start_seconds: float) -> dict:
    return _call(
        "event.move",
        {
            "track_index": track_index,
            "event_index": event_index,
            "start_seconds": start_seconds,
        },
    )


def delete_event(track_index: int, event_index: int) -> dict:
    return _call(
        "event.delete",
        {"track_index": track_index, "event_index": event_index},
    )


def transport_play() -> dict:
    return _call("transport.play")


def transport_stop() -> dict:
    return _call("transport.stop")


def transport_seek(seconds: float) -> dict:
    return _call("transport.seek", {"seconds": seconds})
