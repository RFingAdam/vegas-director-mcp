"""vegas-director-mcp: FastMCP server entry point.

Run with: python -m vegas_director_mcp

Default transport is TCP 127.0.0.1:8752 (set VEGAS_HOST_TRANSPORT=pipe for named pipe).
"""
from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from . import tools

mcp = FastMCP("vegas-director-mcp")


@mcp.tool()
def ping() -> dict:
    """Ping the VEGAS script host. Use this to verify the host is listening."""
    return tools.ping()


@mcp.tool()
def host_info() -> dict:
    """Host version, mode (script vs extension), and request count."""
    return tools.host_info()


@mcp.tool()
def get_project_state() -> dict:
    """Get timeline length, tracks, and events from the open VEGAS project."""
    return tools.get_project_state()


@mcp.tool()
def get_selected_events() -> dict:
    """List currently selected timeline events with track_index and event_index."""
    return tools.get_selected_events()


@mcp.tool()
def save_project(path: str | None = None) -> dict:
    """Save the current VEGAS project. Optional path to Save As."""
    return tools.save_project(path)


@mcp.tool()
def add_track(type: str = "video", name: str = "", index: int | None = None) -> dict:
    """Add a video or audio track. type is 'video' or 'audio'."""
    return tools.add_track(type=type, name=name, index=index)


@mcp.tool()
def set_track_composite_level(track_index: int, level: float) -> dict:
    """Set a video track CompositeLevel (0..1 track opacity)."""
    return tools.set_track_composite_level(track_index, level)


@mcp.tool()
def import_media(path: str) -> dict:
    """Import a media file into the project media pool. Absolute Windows path."""
    return tools.import_media(path)


@mcp.tool()
def place_media(
    path: str,
    track_index: int,
    start_seconds: float = 0.0,
    length_seconds: float = -1.0,
) -> dict:
    """Place media on a timeline track. Host chooses video/audio from track type. length_seconds=-1 uses full media length."""
    return tools.place_media(path, track_index, start_seconds, length_seconds)


@mcp.tool()
def add_video_event(
    track_index: int,
    media_path: str,
    start_seconds: float = 0.0,
    length_seconds: float = -1.0,
) -> dict:
    """Place a video clip on a video track. length_seconds=-1 uses full media length."""
    return tools.add_video_event(track_index, media_path, start_seconds, length_seconds)


@mcp.tool()
def add_audio_event(
    track_index: int,
    media_path: str,
    start_seconds: float = 0.0,
    length_seconds: float = -1.0,
) -> dict:
    """Place an audio clip on an audio track."""
    return tools.add_audio_event(track_index, media_path, start_seconds, length_seconds)


@mcp.tool()
def add_title(
    track_index: int,
    start_seconds: float,
    length_seconds: float,
    text: str,
    preset: str | None = "(Default)",
) -> dict:
    """Add native Titles & Text generator event and set OFX Text via RTF. Soft-fails if generator missing (use PNG overlays)."""
    return tools.add_title(track_index, start_seconds, length_seconds, text, preset)


@mcp.tool()
def trim_event(
    track_index: int,
    event_index: int,
    start_seconds: float | None = None,
    length_seconds: float | None = None,
    take_offset_seconds: float | None = None,
) -> dict:
    """Trim or set length/take offset of an existing event. Omit a field to leave it unchanged."""
    return tools.trim_event(
        track_index, event_index, start_seconds, length_seconds, take_offset_seconds
    )


@mcp.tool()
def move_event(track_index: int, event_index: int, start_seconds: float) -> dict:
    """Move an event to a new start time on its track."""
    return tools.move_event(track_index, event_index, start_seconds)


@mcp.tool()
def delete_event(track_index: int, event_index: int) -> dict:
    """Delete an event from a track."""
    return tools.delete_event(track_index, event_index)


@mcp.tool()
def set_motion_keyframes(
    track_index: int,
    event_index: int,
    keyframes: list[dict[str, Any]],
    reset: bool = True,
) -> dict:
    """Set VideoMotion pan/crop keyframes. Each item: {at_seconds, scale, pan_x, pan_y}. scale 1.0=identity; 1.4~=zoom-in. pan -1..1."""
    return tools.set_motion_keyframes(track_index, event_index, keyframes, reset)


@mcp.tool()
def set_event_fades(
    track_index: int,
    event_index: int,
    fade_in_seconds: float | None = None,
    fade_out_seconds: float | None = None,
    dissolve: bool = False,
    curve: str = "smooth",
    reciprocal_curve: str | None = None,
) -> dict:
    """Set event FadeIn/FadeOut lengths and curve. dissolve=true attaches Dissolve transition (video)."""
    return tools.set_event_fades(
        track_index,
        event_index,
        fade_in_seconds,
        fade_out_seconds,
        dissolve,
        curve,
        reciprocal_curve,
    )


@mcp.tool()
def set_event_opacity(track_index: int, event_index: int, opacity: float) -> dict:
    """Set video event opacity via FadeIn.Gain (0..1)."""
    return tools.set_event_opacity(track_index, event_index, opacity)


@mcp.tool()
def set_envelope_points(
    track_index: int,
    envelope_type: str,
    points: list[dict[str, Any]],
) -> dict:
    """Create/update Volume (audio) or CompositeLevel (video) envelope points: [{at_seconds, value, curve}]."""
    return tools.set_envelope_points(track_index, envelope_type, points)


@mcp.tool()
def render_start(
    output_path: str | None = None,
    template_name: str | None = None,
    renderer_name: str | None = None,
    start_seconds: float | None = None,
    length_seconds: float | None = None,
    async_render: bool = True,
) -> dict:
    """Start a VEGAS render. Default async=True uses BeginRender + render_status polling (does not sit on the UI marshal)."""
    return tools.render_start(
        output_path, template_name, renderer_name, start_seconds, length_seconds, async_render
    )


@mcp.tool()
def transport_play() -> dict:
    """Start playback in VEGAS."""
    return tools.transport_play()


@mcp.tool()
def transport_stop() -> dict:
    """Stop playback in VEGAS."""
    return tools.transport_stop()


@mcp.tool()
def transport_seek(seconds: float) -> dict:
    """Move the cursor to an absolute time in seconds."""
    return tools.transport_seek(seconds)


@mcp.tool()
def new_project(save_current_to: str | None = None, discard_unsaved: bool = False) -> dict:
    """Start an empty VEGAS project. Saves the open one to save_current_to first, or pass discard_unsaved=True."""
    return tools.new_project(save_current_to, discard_unsaved)


@mcp.tool()
def open_project(path: str, save_current_to: str | None = None, discard_unsaved: bool = False) -> dict:
    """Open a .veg (saves or discards the open project first)."""
    return tools.open_project(path, save_current_to, discard_unsaved)


@mcp.tool()
def list_media() -> dict:
    """List the media pool with offline status and alpha mode."""
    return tools.list_media()


@mcp.tool()
def replace_media(old_path: str, new_path: str) -> dict:
    """Replace every use of one media file with another (e.g. .mkv -> remuxed .mp4)."""
    return tools.replace_media(old_path, new_path)


@mcp.tool()
def set_media_alpha(alpha: str = "Straight", path: str | None = None, path_contains: str | None = None) -> dict:
    """Set alpha interpretation for a file or every file whose path contains a string."""
    return tools.set_media_alpha(alpha, path, path_contains)


@mcp.tool()
def set_track_props(track_index: int, name: str | None = None, mute: bool | None = None, solo: bool | None = None,
                    volume: float | None = None) -> dict:
    """Rename/mute/solo a track, or set an audio track's volume (linear, 1.0 = 0 dB)."""
    return tools.set_track_props(track_index, name, mute, solo, volume)


@mcp.tool()
def clear_track_events(track_index: int) -> dict:
    """Delete every event on a track."""
    return tools.clear_track_events(track_index)


@mcp.tool()
def clear_envelope(track_index: int, envelope_type: str = "Volume") -> dict:
    """Remove a track envelope (Volume, CompositeLevel, ...)."""
    return tools.clear_envelope(track_index, envelope_type)


@mcp.tool()
def set_event_gain(track_index: int, event_index: int, gain_db: float | None = None, gain: float | None = None,
                   normalize: bool | None = None) -> dict:
    """Set an audio event's gain (dB or linear) and/or normalize."""
    return tools.set_event_gain(track_index, event_index, gain_db, gain, normalize)


@mcp.tool()
def list_render_templates(renderer_contains: str = "", template_contains: str = "", limit: int = 200) -> dict:
    """List renderer + template names (use the exact names with render_start)."""
    return tools.list_render_templates(renderer_contains, template_contains, limit)


@mcp.tool()
def set_project_video(width: int | None = None, height: int | None = None, frame_rate: float | None = None) -> dict:
    """Set the open project's video size / frame rate (e.g. 1080x1920 for Shorts)."""
    return tools.set_project_video(width, height, frame_rate)


@mcp.tool()
def ensure_host(project_path: str | None = None) -> dict:
    """Reach the live TCP host, or launch VEGAS so the extension /RUNSCRIPT host starts. Reports used_mode."""
    return tools.ensure_host(project_path)


@mcp.tool()
def probe_media(path: str) -> dict:
    """ffprobe a media file (duration, size, fps, audio). Does not need VEGAS."""
    from .analysis.probe import probe_media as _probe

    return _probe(path)


@mcp.tool()
def detect_scenes(path: str, threshold: float = 0.3) -> dict:
    """ffmpeg scene cuts. Does not need VEGAS."""
    from .analysis.scenes import detect_scenes as _detect

    return _detect(path, threshold)


@mcp.tool()
def analyze_audio(path: str, spike_ratio: float = 2.2, max_spikes: int = 40) -> dict:
    """Windowed loudness/peaks for reaction spikes, kill/cash, squad shouting. No VEGAS."""
    from .analysis.audio import analyze_audio as _audio

    return _audio(path, spike_ratio=spike_ratio, max_spikes=max_spikes)


@mcp.tool()
def transcribe_media(path: str, model_size: str = "base", language: str | None = "en") -> dict:
    """Optional local Whisper (faster-whisper). Uses GPU if ctranslate2 sees CUDA; else CPU. Soft-fails if not installed."""
    from .analysis.whisper import transcribe_media as _whisper

    return _whisper(path, model_size=model_size, language=language)


@mcp.tool()
def generate_captions(
    path: str | None = None,
    segments: list[dict[str, Any]] | None = None,
    words: list[dict[str, Any]] | None = None,
    output_dir: str | None = None,
    style: str = "shorts",
    group_words: bool = True,
) -> dict:
    """Write SRT + ASS (big high-contrast word groups for 9:16 Shorts). No VEGAS."""
    from .analysis.captions import generate_captions as _caps

    return _caps(path, segments, words, output_dir, style, group_words)


@mcp.tool()
def burn_captions(media_path: str, ass_path: str, output_path: str | None = None) -> dict:
    """Burn ASS captions into a new MP4 with ffmpeg. No VEGAS."""
    from .analysis.captions import burn_captions as _burn

    return _burn(media_path, ass_path, output_path)


@mcp.tool()
def find_highlights(
    path: str,
    min_seconds: float = 20.0,
    max_seconds: float = 35.0,
    max_candidates: int = 8,
    scene_threshold: float = 0.3,
) -> dict:
    """Rank 20–35 s Short candidates with in/out points and reasons. No VEGAS."""
    from .analysis.highlights import find_highlights as _hl

    return _hl(path, min_seconds, max_seconds, max_candidates, scene_threshold)


@mcp.tool()
def apply_crossfade(
    track_index: int,
    event_index: int,
    next_event_index: int | None = None,
    seconds: float = 0.4,
    dissolve: bool = True,
) -> dict:
    """Overlap two events and set reciprocal fades (optional Dissolve)."""
    from .edit.helpers import apply_crossfade as _xf

    return _xf(track_index, event_index, next_event_index, seconds, dissolve)


@mcp.tool()
def apply_ducking(
    music_track_index: int,
    voice_track_index: int,
    reduction_db: float = -12.0,
    pad_seconds: float = 0.15,
) -> dict:
    """Duck music Volume under voice-track events."""
    from .edit.helpers import apply_ducking as _duck

    return _duck(music_track_index, voice_track_index, reduction_db, pad_seconds)


@mcp.tool()
def apply_vertical_short(
    media_path: str,
    in_seconds: float,
    out_seconds: float,
    punch_at_seconds: float | None = None,
    punch_scale: float = 1.35,
    caption_cues: list[dict[str, Any]] | None = None,
    music_path: str | None = None,
    pan_x: float = 0.0,
) -> dict:
    """16:9→9:16 crop/pan, punch-in on the payoff, captions track, loop-friendly fade out."""
    from .edit.shorts import apply_vertical_short as _short

    return _short(
        media_path,
        in_seconds,
        out_seconds,
        punch_at_seconds=punch_at_seconds,
        punch_scale=punch_scale,
        caption_cues=caption_cues,
        music_path=music_path,
        pan_x=pan_x,
    )


@mcp.tool()
def propose_edit(
    media_path: str,
    in_seconds: float | None = None,
    out_seconds: float | None = None,
    vertical_short: bool = True,
    caption_cues: list[dict[str, Any]] | None = None,
    music_path: str | None = None,
) -> dict:
    """Composite: find/accept a window, place, inspect, revise. Default path for a Short."""
    from .edit.propose import propose_edit as _prop

    return _prop(
        media_path,
        in_seconds=in_seconds,
        out_seconds=out_seconds,
        vertical_short=vertical_short,
        caption_cues=caption_cues,
        music_path=music_path,
    )


@mcp.tool()
def render_status(job_id: str | None = None) -> dict:
    """Poll an async VEGAS render started by render_start / render_with_preset."""
    return tools.render_status(job_id)


@mcp.tool()
def wait_for_render(job_id: str | None = None, timeout_seconds: float = 1800, poll_seconds: float = 1.5) -> dict:
    """Poll render.status until complete. MCP-side wait; does not block the VEGAS UI thread."""
    return tools.wait_for_render(job_id, timeout_seconds, poll_seconds)


@mcp.tool()
def render_with_preset(
    output_path: str,
    preset: str = "vertical",
    start_seconds: float | None = None,
    length_seconds: float | None = None,
    edit_meta: dict[str, Any] | None = None,
    wait: bool = True,
) -> dict:
    """Named preset (vertical / 1080p / 4k): async render, verify with ffprobe, write sidecar JSON."""
    return tools.render_with_preset(
        output_path,
        preset,
        start_seconds=start_seconds,
        length_seconds=length_seconds,
        edit_meta=edit_meta,
        wait=wait,
    )


@mcp.tool()
def verify_output(
    path: str,
    expect_width: int | None = None,
    expect_height: int | None = None,
    expect_audio: bool = True,
    expect_duration: float | None = None,
) -> dict:
    """ffprobe-check a rendered file (duration, resolution, audio present)."""
    from .render.sidecar import verify_output as _verify

    return _verify(
        path,
        expect_width=expect_width,
        expect_height=expect_height,
        expect_audio=expect_audio,
        expect_duration=expect_duration,
    )


@mcp.tool()
def write_edit_sidecar(output_path: str, edit_meta: dict[str, Any] | None = None) -> dict:
    """Write <output>.edit.json (length, hook start, caption style, zoom count, music, template)."""
    from .render.sidecar import write_sidecar

    return write_sidecar(output_path, edit_meta)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
