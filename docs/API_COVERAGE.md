# ScriptPortal.Vegas API Coverage

Legend: ✅ implemented in host · 🟨 partial / best-effort · ⬜ not started

Based on Magix VEGAS Pro 22 Scripting FAQ patterns (Tracks/Events, Envelopes, Generators, VideoMotion, RenderArgs).

| Area | MCP / RPC | Status |
|---|---|---|
| Health | `ping` | ✅ |
| Project | `project.get_state` | ✅ (includes `media_path`, `media_name`, `take_offset_seconds`, `take_length_seconds`) |
| Project | `project.get_selected_events` | ✅ |
| Project | `project.save` | ✅ |
| Tracks | `track.add` | ✅ |
| Tracks | `track.set_composite_level` | ✅ (`VideoTrack.CompositeLevel`) |
| Media | `media.import`, `media.place` | ✅ |
| Events | `event.add_video`, `event.add_audio` | ✅ |
| Events | `event.add_title` | ✅ (Titles & Text + OFX `Text` RTF; SoftFail if generator missing → use PNG overlays) |
| Events | `event.trim` (+ `take_offset_seconds`), `event.move`, `event.delete` | ✅ |
| Events | `event.set_motion` | ✅ (VideoMotion keyframes: ScaleBy / MoveBy) |
| Events | `event.set_fades` | ✅ (Length + CurveType.Smooth; optional Dissolve; `reciprocal_curve`) |
| Events | `event.set_opacity` | ✅ (`VideoEvent.FadeIn.Gain`) |
| Envelopes | `envelope.set_points` | ✅ (Volume / CompositeLevel; create if missing) |
| Transport | `transport.play/stop/seek` | ✅ |
| Render | `render.start` | 🟨 best-effort `RenderArgs` when `template_name` given; else SoftFail → File > Render As (no fake success) |
| FX / color / ducking helpers | — | ⬜ Phase 3+ |
| Async render status polling | — | ⬜ Phase 4 |

Soft failures return JSON-RPC **result** `{ "ok": false, "error": "..." }` (never crash VEGAS).

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
      { "at_seconds": 2.5, "scale": 1.4, "pan_x": -0.6, "pan_y": -0.55 }
    ]
  }
}
```

Validate live against VEGAS Pro 22 after **reloading** the host script (Tools > Scripting > VegasDirectorHost).
