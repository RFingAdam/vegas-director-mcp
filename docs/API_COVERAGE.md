# ScriptPortal.Vegas API Coverage

Legend: ✅ implemented in host · 🟨 partial / best-effort · ⬜ not started

Based on Magix VEGAS Pro 22 Scripting FAQ patterns (Tracks/Events, Envelopes,
Generators, VideoMotion, RenderArgs) and the Application Extensions FAQ
(`ICustomCommandModule`, `Documents\Vegas Application Extensions`).

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
| Render | `render.list_templates` | ✅ |
| Render | `render.start` | 🟨 blocking `Vegas.Render(RenderArgs)` when `template_name` given; else SoftFail → File > Render As (no fake success) |
| Host start | Application Extension / Script Menu | ✅ extension auto-starts the TCP listener; Script Menu is the fallback |
| FX / color / ducking helpers | — | ⬜ follow-up (media grounding + edit helpers) |
| Async render status polling | `Vegas.BeginRender` + `RenderProgress` / `RenderFinished` | ⬜ follow-up |

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
