"""propose_edit — place, inspect, revise a highlight into the open project."""
from __future__ import annotations

from typing import Any

from .. import tools
from ..analysis.highlights import find_highlights
from ..analysis.probe import probe_media
from .shorts import apply_vertical_short


def propose_edit(
    media_path: str,
    *,
    in_seconds: float | None = None,
    out_seconds: float | None = None,
    vertical_short: bool = True,
    caption_cues: list[dict[str, Any]] | None = None,
    music_path: str | None = None,
    max_revisions: int = 2,
) -> dict[str, Any]:
    """Pick (or accept) a window, place it, inspect timeline, revise if needed."""
    probe = probe_media(media_path)
    if not probe.get("ok"):
        return probe

    highlights = None
    if in_seconds is None or out_seconds is None:
        highlights = find_highlights(media_path)
        if not highlights.get("ok") or not highlights.get("candidates"):
            return {
                "ok": False,
                "error": "find_highlights produced no candidates",
                "highlights": highlights,
            }
        top = highlights["candidates"][0]
        in_seconds = float(top["in_seconds"])
        out_seconds = float(top["out_seconds"])

    steps: list[dict[str, Any]] = []
    if vertical_short:
        placed = apply_vertical_short(
            media_path,
            in_seconds,
            out_seconds,
            caption_cues=caption_cues,
            music_path=music_path,
        )
        steps.append({"step": "place_vertical_short", "result": placed})
        if not placed.get("ok"):
            return {"ok": False, "error": "place failed", "steps": steps, "used_mode": placed.get("used_mode")}
    else:
        track = tools.add_track("video", "Edit V1")
        steps.append({"step": "add_track", "result": track})
        if not track.get("ok"):
            return track
        ev = tools.add_video_event(
            int(track.get("track_index", 0)),
            media_path,
            0.0,
            out_seconds - in_seconds,
        )
        steps.append({"step": "place", "result": ev})
        if not ev.get("ok"):
            return ev
        trim = tools.trim_event(
            int(track.get("track_index", 0)),
            0,
            0.0,
            out_seconds - in_seconds,
            in_seconds,
        )
        steps.append({"step": "trim", "result": trim})
        placed = {"ok": True, "edit_meta": {"template": "flat", "length": out_seconds - in_seconds, "hook_start_time": in_seconds, "zoom_count": 0, "music": bool(music_path), "caption_style": None}}

    revisions = 0
    while revisions < max_revisions:
        state = tools.get_project_state()
        steps.append({"step": "inspect", "result": {"ok": state.get("ok"), "event_count": len(state.get("events") or [])}})
        if not state.get("ok"):
            return {"ok": False, "error": "inspect failed", "steps": steps}
        events = state.get("events") or []
        if not events:
            # Empty timeline after place — try once more with a bare place.
            revisions += 1
            retry = tools.add_track("video", "Edit Retry")
            steps.append({"step": "revise_add_track", "result": retry})
            if retry.get("ok"):
                ev = tools.add_video_event(
                    int(retry.get("track_index", 0)),
                    media_path,
                    0.0,
                    out_seconds - in_seconds,
                )
                steps.append({"step": "revise_place", "result": ev})
            continue
        # If the first video event is wildly longer than requested, trim it.
        first = min(events, key=lambda e: (e.get("track_index", 0), e.get("event_index", 0)))
        length = float(first.get("length_seconds") or 0)
        target = out_seconds - in_seconds
        if length > target + 0.35:
            revisions += 1
            trim = tools.trim_event(
                int(first["track_index"]),
                int(first["event_index"]),
                length_seconds=target,
                take_offset_seconds=in_seconds,
            )
            steps.append({"step": "revise_trim", "result": trim})
            continue
        break

    return {
        "ok": True,
        "in_seconds": in_seconds,
        "out_seconds": out_seconds,
        "length_seconds": out_seconds - in_seconds,
        "vertical_short": vertical_short,
        "revisions": revisions,
        "highlights": highlights,
        "probe": {k: probe.get(k) for k in ("duration_seconds", "width", "height", "fps", "has_audio")},
        "edit_meta": (placed or {}).get("edit_meta"),
        "steps": steps,
        "used_mode": (placed or {}).get("used_mode") or (steps[0]["result"].get("used_mode") if steps else None),
    }
