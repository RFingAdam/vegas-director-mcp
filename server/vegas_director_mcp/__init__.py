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
) -> dict:
    """Best-effort RenderArgs render, or soft-fail asking for File>Render As / template names. No fake success."""
    return tools.render_start(
        output_path, template_name, renderer_name, start_seconds, length_seconds
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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
