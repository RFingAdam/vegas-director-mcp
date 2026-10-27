---
name: vegas-director
description: Cut YouTube Shorts and long-form in MAGIX VEGAS Pro 22 via vegas-director-mcp. Use when editing SwampBewdy / Wardogs gameplay, Ironhaven promos, 16:9 to 9:16 verticals, captions, highlight finding, ducking, or rendering and verifying an export.
---

# VEGAS Director

Default editing path for this repo. The MCP server talks to a C# host inside VEGAS Pro 22 (`127.0.0.1:8752`) and also runs ffmpeg analysis **without** VEGAS.

## Modes

Tools report `used_mode`.

| Mode | When | What you do |
|---|---|---|
| `live` | Host already listening | Just call tools. |
| `launched_extension` | VEGAS was started; Application Extension auto-bound TCP | Preferred. Nobody opens *Tools > Scripting*. Writes run on the UI thread inside an `UndoBlock` (required off the Script Menu). |
| `launched_runscript` | No extension DLL; `Vegas220.exe /RUNSCRIPT VegasDirectorHost.cs` | Script-menu fallback. Leave the host dialog open. |
| `oneshot_runscript` | Fire-and-forget generated `.cs` + `.job.json` | Last resort. VEGAS GUI still opens — Pro 22 has **no** documented headless/no-UI mode. |

Call `ensure_host` first if you are unsure. Analysis tools (`probe_media`, `detect_scenes`, `analyze_audio`, `transcribe_media`, `generate_captions`, `find_highlights`) never need VEGAS.

Use **live / extension** for an interactive cut (place → inspect → revise). Use **oneshot** only when you cannot keep the host up and the job is a short explicit op list.

## Default Short workflow

1. `probe_media` on the 16:9 capture (OBS mkv/mp4).
2. `analyze_audio` + `detect_scenes`. Optional `transcribe_media` (faster-whisper; GPU if present, else CPU; soft-fails if not installed).
3. `find_highlights` — take a 20–35 s candidate (`in_seconds` / `out_seconds` + `reasons`).
4. `generate_captions` (SRT + ASS, `style=shorts`, word-grouped).
5. `ensure_host` (opens VEGAS if needed).
6. `propose_edit` with those in/out points and caption cues (`vertical_short=true`) — or `apply_vertical_short` directly.
7. Inspect with `get_project_state`. Revise with `trim_event` / `set_motion_keyframes` / `apply_crossfade` / `apply_ducking`.
8. `render_with_preset` `vertical` (1080×1920). It lists **all** VEGAS render templates (no 400-item cap; paginates; matches MAGIX AVC/AAC MP4 even when those templates sit after AVI/MXF), starts `Vegas.BeginRender`, polls `render_status` (does **not** block the VEGAS UI thread), `verify_output` via ffprobe, and writes `<output>.edit.json`.
9. Sidecar fields: `length`, `hook_start_time`, `caption_style`, `zoom_count`, `music`, `template`. Keep them — weekly retention loops correlate style with watch time.

## Default long-form workflow

1. `probe_media` + `detect_scenes` + `analyze_audio` (and Whisper if dialogue matters).
2. `ensure_host` → `open_project` or `new_project`.
3. `add_track` / `place_media` / `trim_event` / `move_event` for the A-roll.
4. `apply_crossfade` on joins. `apply_ducking` for music under voice/game comms.
5. Titles via `add_title` or PNG overlays. Motion via `set_motion_keyframes`.
6. `render_with_preset` `1080p` or `4k`. Same verify + sidecar.

## Vertical Short template (what it actually does)

- Sets project video to 1080×1920 when the host supports `project.set_video`.
- Places the source with `take_offset = in_seconds`.
- VideoMotion crop-zoom ≈ 16/9 so 16:9 fills 9:16, plus a punch-in keyframe on the payoff.
- Optional captions track (`add_title`) and music track with a loop-friendly fade out.

## Guardrails

- Times are seconds, not ticks.
- Soft failures are `{ok: false, error}` — never assume success.
- Extension mode needs `%LOCALAPPDATA%\vegas-director-mcp\token` (auto-sent). Do not commit it.
- `host\build.ps1` and `ensure_host` install/find the DLL via the Windows **My Documents** known folder (follows OneDrive redirection). `%USERPROFILE%\Documents` is the wrong path on those PCs.
- `replace_media` is how you swap an OBS `.mkv` for a remuxed `.mp4`.
- If render templates still do not match after a host rebuild, `list_render_templates` (`limit=0` for the full list) and pass exact names to `render_start`.
