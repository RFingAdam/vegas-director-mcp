"""MCP tool definitions backed by the VEGAS script host."""
from __future__ import annotations

from typing import Any

from .host_client import VegasHostClient, VegasHostError

_client = VegasHostClient()


def _call(method: str, params: dict[str, Any] | None = None) -> dict:
    try:
        result = _client.call(method, params)
        if isinstance(result, dict):
            # Host already returns soft {ok:false,error} or success payloads.
            if "ok" not in result and "error" not in result:
                result = {"ok": True, **result}
            return result
        return {"ok": True, "result": result}
    except VegasHostError as exc:
        return {"ok": False, "error": exc.message, "code": exc.code}
    except (ConnectionRefusedError, FileNotFoundError, OSError, TimeoutError) as exc:
        return {
            "ok": False,
            "error": (
                "Could not reach the VEGAS script host. Open VEGAS Pro, run "
                "Tools > Scripting > VegasDirectorHost, leave the dialog open. "
                f"({exc})"
            ),
            "code": -1,
        }


def ping() -> dict:
    return _call("ping")


def get_project_state() -> dict:
    return _call("project.get_state")


def get_selected_events() -> dict:
    """List currently selected timeline events (track_index / event_index)."""
    return _call("project.get_selected_events")


def save_project(path: str | None = None) -> dict:
    params: dict[str, Any] = {}
    if path:
        params["path"] = path
    return _call("project.save", params)


def add_track(type: str = "video", name: str = "") -> dict:
    return _call("track.add", {"type": type, "name": name})


def set_track_composite_level(track_index: int, level: float) -> dict:
    """Set VideoTrack.CompositeLevel (0..1 opacity for the whole track)."""
    return _call(
        "track.set_composite_level",
        {"track_index": track_index, "level": level},
    )


def import_media(path: str) -> dict:
    return _call("media.import", {"path": path})


def place_media(
    path: str,
    track_index: int,
    start_seconds: float = 0.0,
    length_seconds: float = -1.0,
) -> dict:
    """Place media on a track; host picks video vs audio from track type."""
    return _call(
        "media.place",
        {
            "path": path,
            "track_index": track_index,
            "start_seconds": start_seconds,
            "length_seconds": length_seconds,
        },
    )


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


def add_title(
    track_index: int,
    start_seconds: float,
    length_seconds: float,
    text: str,
    preset: str | None = "(Default)",
) -> dict:
    """Add a native Titles & Text generator event and set OFX Text (RTF)."""
    params: dict[str, Any] = {
        "track_index": track_index,
        "start_seconds": start_seconds,
        "length_seconds": length_seconds,
        "text": text,
    }
    if preset is not None:
        params["preset"] = preset
    return _call("event.add_title", params)


def trim_event(
    track_index: int,
    event_index: int,
    start_seconds: float | None = None,
    length_seconds: float | None = None,
    take_offset_seconds: float | None = None,
) -> dict:
    params: dict[str, Any] = {
        "track_index": track_index,
        "event_index": event_index,
    }
    if start_seconds is not None:
        params["start_seconds"] = start_seconds
    if length_seconds is not None:
        params["length_seconds"] = length_seconds
    if take_offset_seconds is not None:
        params["take_offset_seconds"] = take_offset_seconds
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


def set_motion_keyframes(
    track_index: int,
    event_index: int,
    keyframes: list[dict[str, Any]],
    reset: bool = True,
) -> dict:
    """Set VideoMotion pan/crop keyframes.

    Each keyframe dict: {at_seconds, scale, pan_x, pan_y}
    scale 1.0 = no zoom; 1.4 ~= 40% zoom-in. pan_* in -1..1 (neg = left/up).
    """
    return _call(
        "event.set_motion",
        {
            "track_index": track_index,
            "event_index": event_index,
            "reset": reset,
            "keyframes": keyframes,
        },
    )


def set_event_fades(
    track_index: int,
    event_index: int,
    fade_in_seconds: float | None = None,
    fade_out_seconds: float | None = None,
    dissolve: bool = False,
    curve: str = "smooth",
    reciprocal_curve: str | None = None,
) -> dict:
    """Set FadeIn/FadeOut Length + Curve; optional Dissolve transition."""
    params: dict[str, Any] = {
        "track_index": track_index,
        "event_index": event_index,
        "dissolve": dissolve,
        "curve": curve,
    }
    if fade_in_seconds is not None:
        params["fade_in_seconds"] = fade_in_seconds
    if fade_out_seconds is not None:
        params["fade_out_seconds"] = fade_out_seconds
    if reciprocal_curve is not None:
        params["reciprocal_curve"] = reciprocal_curve
    return _call("event.set_fades", params)


def set_event_opacity(track_index: int, event_index: int, opacity: float) -> dict:
    """Set VideoEvent opacity via FadeIn.Gain (0..1)."""
    return _call(
        "event.set_opacity",
        {
            "track_index": track_index,
            "event_index": event_index,
            "opacity": opacity,
        },
    )


def set_envelope_points(
    track_index: int,
    envelope_type: str,
    points: list[dict[str, Any]],
) -> dict:
    """Create/update a track envelope and set points.

    envelope_type: Volume (audio) or CompositeLevel (video).
    points: [{at_seconds, value, curve}]
    """
    return _call(
        "envelope.set_points",
        {
            "track_index": track_index,
            "envelope_type": envelope_type,
            "points": points,
        },
    )


def render_start(
    output_path: str | None = None,
    template_name: str | None = None,
    renderer_name: str | None = None,
    start_seconds: float | None = None,
    length_seconds: float | None = None,
) -> dict:
    """Best-effort render via RenderArgs, or soft-fail with File>Render As guidance."""
    params: dict[str, Any] = {}
    if output_path is not None:
        params["output_path"] = output_path
    if template_name is not None:
        params["template_name"] = template_name
    if renderer_name is not None:
        params["renderer_name"] = renderer_name
    if start_seconds is not None:
        params["start_seconds"] = start_seconds
    if length_seconds is not None:
        params["length_seconds"] = length_seconds
    return _call("render.start", params)


def transport_play() -> dict:
    return _call("transport.play")


def transport_stop() -> dict:
    return _call("transport.stop")


def transport_seek(seconds: float) -> dict:
    return _call("transport.seek", {"seconds": seconds})
