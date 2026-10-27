# ScriptPortal.Vegas API Coverage

Legend: ✅ implemented in host · 🟨 partial / best-effort · ⬜ not started

Based on Magix VEGAS Pro 22 Scripting FAQ patterns (Tracks/Events, Envelopes,
Generators, VideoMotion, RenderArgs) and the Application Extensions FAQ
(`ICustomCommandModule`, Known Folder `Documents\Vegas Application Extensions`,
including OneDrive-redirected Documents). Extension-mode writes run inside
an `UndoBlock` on the UI thread.

| Area | MCP / RPC | Status |
|---|---|---|
| Health | `ping`, `host.info` | ✅ (`mode` is `script` or `extension`) |
| Project | `project.get_state` | ✅ (includes `media_path`, `media_name`, `take_offset_seconds`, `take_length_seconds`) |
| Project | `project.get_selected_events` | ✅ |
| Project | `project.save` | ✅ |
| Project | `project.new`, `project.open` | ✅ (`save_current_to` or `discard_unsaved`) |
| Tracks | `track.add` | ✅ (optional `index`) |
| Tracks | `track.set_composite_level` | ✅ (`VideoTrack.CompositeLevel`) |
| Tracks | `track.set_props` | ✅ (name / mute / solo / audio volume) |
| Tracks | `track.clear_events` | ✅ |
| Media | `media.import`, `media.place` | ✅ |
| Media | `media.list`, `media.replace`, `media.set_alpha` | ✅ |
| Events | `event.add_video`, `event.add_audio` | ✅ |
| Events | `event.add_title` | ✅ (Titles & Text + OFX `Text` RTF; SoftFail if generator missing → use PNG overlays) |
| Events | `event.trim` (+ `take_offset_seconds`), `event.move`, `event.delete` | ✅ |
| Events | `event.set_motion` | ✅ (VideoMotion keyframes: Bounds crop-zoom, Type, Smoothness) |
| Events | `event.set_fades` | ✅ (Length + CurveType.Smooth; optional Dissolve; `reciprocal_curve`) |
| Events | `event.set_opacity` | ✅ (`VideoEvent.FadeIn.Gain`) |
| Events | `event.set_gain` | ✅ (audio FadeIn.Gain + Normalize) |
| Envelopes | `envelope.set_points` | ✅ (Volume / CompositeLevel; create if missing) |
| Envelopes | `envelope.clear` | ✅ |
| Transport | `transport.play/stop/seek` | ✅ |
| Render | `render.list_templates` | ✅ (`limit=0` unlimited; `offset` pages; `truncated` when capped) |
| Render | `render.start` | ✅ `async=true` (default) uses `Vegas.BeginRender`; `async=false` is blocking `Vegas.Render` |
| Render | `render.status` | ✅ job_id / state / percent (progress events, no UI-marshal wait) |
| Project | `project.set_video` | ✅ width / height / frame_rate |
| Host start | Application Extension / Script Menu / `ensure_host` | ✅ live TCP, `/RUNSCRIPT`, or `/CMDMODULE` path; tools set `used_mode` |
| Analysis (no VEGAS) | `probe_media`, `detect_scenes`, `analyze_audio`, `transcribe_media`, `generate_captions`, `burn_captions`, `find_highlights` | ✅ |
| Edit helpers | `apply_crossfade`, `apply_ducking`, `apply_vertical_short`, `propose_edit` | ✅ |
| Delivery | `render_with_preset`, `verify_output`, sidecar `<output>.edit.json` | ✅ (preset matching walks the full template list; MAGIX AVC/AAC aliases) |

Soft failures return JSON-RPC **result** `{ "ok": false, "error": "..." }` (never crash VEGAS).

Extension mode rejects requests that do not carry the runtime token
(JSON-RPC error `-32001`). Script-menu mode does not require a token.

## Sample: `event.set_motion`

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "event.set_motion",
  "params": {
    "track_index": 0,
    "event_index": 0,
    "reset": true,
    "keyframes": [
      { "at_seconds": 0, "scale": 1.0, "pan_x": 0, "pan_y": 0 },
      { "at_seconds": 2.5, "scale": 1.4, "pan_x": -0.6, "pan_y": -0.55, "type": "smooth", "smoothness": 0.5 }
    ]
  }
}
```

The host binds TCP `127.0.0.1:8752` only. After pulling, reload the host:
restart VEGAS if you use the extension, or re-run
*Tools > Scripting > VegasDirectorHost* for Script Menu mode.

## Sample: `media.replace`

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "media.replace",
  "params": {
    "old_path": "D:\\captures\\wardogs.mkv",
    "new_path": "D:\\captures\\wardogs.mp4"
  }
}
```
