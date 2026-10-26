"""16:9 → 9:16 Short template: crop/pan, punch-in, captions, loop-friendly end."""
from __future__ import annotations

from typing import Any

from .. import tools
from ..analysis.captions import generate_captions


def apply_vertical_short(
    media_path: str,
    in_seconds: float,
    out_seconds: float,
    *,
    punch_at_seconds: float | None = None,
    punch_scale: float = 1.35,
    caption_cues: list[dict[str, Any]] | None = None,
    music_path: str | None = None,
    pan_x: float = 0.0,
    project_width: int = 1080,
    project_height: int = 1920,
    loop_end_seconds: float = 0.45,
) -> dict[str, Any]:
    """Build a vertical Short on a clean pair of tracks.

    Crop is a VideoMotion Bounds zoom (scale > 1) so a 16:9 source fills 9:16.
    Punch-in is a second keyframe at the payoff. Captions go on a titles track
    when cues are provided. The last `loop_end_seconds` fade out so a rewatch
    loop does not hard-cut.
    """
    length = out_seconds - in_seconds
    if length <= 0:
        return {"ok": False, "error": "out_seconds must be after in_seconds"}
    if punch_at_seconds is None:
        punch_at_seconds = min(length * 0.55, max(0.0, length - 1.2))

    video = tools.set_project_video(project_width, project_height)
    if not video.get("ok"):
        # Soft: keep going if the host is an older script without set_video.
        if video.get("code") == -32601:
            video = {"ok": True, "skipped": True, "note": "host has no project.set_video"}
        else:
            return video

    vtrack = tools.add_track("video", "Short V1", index=0)
    if not vtrack.get("ok"):
        return vtrack
    v_idx = int(vtrack.get("track_index", 0))

    placed = tools.add_video_event(v_idx, media_path, start_seconds=0.0, length_seconds=length)
    if not placed.get("ok"):
        return placed
    # take_offset = source in-point
    trimmed = tools.trim_event(
        v_idx,
        0,
        start_seconds=0.0,
        length_seconds=length,
        take_offset_seconds=in_seconds,
    )
    if not trimmed.get("ok"):
        return trimmed

    # 16:9 into 9:16: scale so the source height fills the frame (≈ 1.777/1 = 1.777
    # would letterbox; we zoom until the crop rectangle is 9:16 inside the 16:9).
    # Host ApplyMotionKeyframe: scale 1 = full frame, >1 crops in. 16:9→9:16
    # needs height-fill: crop width = src_h * 9/16, scale = src_w / crop_w = 16/9.
    fill_scale = 16.0 / 9.0
    keys = [
        {"at_seconds": 0.0, "scale": fill_scale, "pan_x": pan_x, "pan_y": 0.0, "type": "smooth"},
        {
            "at_seconds": max(0.0, punch_at_seconds),
            "scale": fill_scale * punch_scale,
            "pan_x": pan_x,
            "pan_y": -0.15,
            "type": "smooth",
        },
    ]
    motion = tools.set_motion_keyframes(v_idx, 0, keys, reset=True)
    fades = tools.set_event_fades(
        v_idx,
        0,
        fade_in_seconds=0.12,
        fade_out_seconds=loop_end_seconds,
        dissolve=False,
        curve="smooth",
    )

    caption_track = None
    titles: list[dict[str, Any]] = []
    caption_files = None
    if caption_cues:
        caption_files = generate_captions(
            path=media_path,
            segments=caption_cues,
            style="shorts",
            group_words=False,
            stem="short-captions",
        )
        ctrack = tools.add_track("video", "Short Captions", index=0)
        if ctrack.get("ok"):
            caption_track = int(ctrack.get("track_index", 0))
            # After inserting at 0, the media track shifted to 1.
            v_idx = v_idx + 1
            for cue in caption_cues:
                start = max(0.0, float(cue.get("start_seconds") or 0) - in_seconds)
                end = min(length, float(cue.get("end_seconds") or 0) - in_seconds)
                if end - start < 0.2:
                    continue
                titles.append(
                    tools.add_title(
                        caption_track,
                        start,
                        end - start,
                        cue.get("text") or "",
                    )
                )

    music = None
    if music_path:
        atrack = tools.add_track("audio", "Short Music")
        if atrack.get("ok"):
            music = tools.add_audio_event(
                int(atrack.get("track_index", 0)),
                music_path,
                start_seconds=0.0,
                length_seconds=length,
            )
            if music.get("ok"):
                tools.set_event_fades(
                    int(atrack.get("track_index", 0)),
                    0,
                    fade_in_seconds=0.2,
                    fade_out_seconds=loop_end_seconds,
                )

    ok = motion.get("ok") and fades.get("ok")
    return {
        "ok": bool(ok),
        "template": "vertical_short",
        "video_track_index": v_idx,
        "caption_track_index": caption_track,
        "in_seconds": in_seconds,
        "out_seconds": out_seconds,
        "length_seconds": length,
        "punch_at_seconds": punch_at_seconds,
        "zoom_count": len(keys),
        "music": bool(music_path),
        "caption_style": "shorts" if caption_cues else None,
        "caption_files": caption_files,
        "project_video": video,
        "placed": placed,
        "motion": motion,
        "fades": fades,
        "titles": titles,
        "music_event": music,
        "used_mode": vtrack.get("used_mode") or placed.get("used_mode"),
        "edit_meta": {
            "length": length,
            "hook_start_time": in_seconds,
            "caption_style": "shorts" if caption_cues else None,
            "zoom_count": len(keys),
            "music": bool(music_path),
            "template": "vertical_short",
        },
    }
