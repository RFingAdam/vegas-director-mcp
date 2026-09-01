# ScriptPortal.Vegas API Coverage

Tracks which parts of the VEGAS Pro scripting API
(`ScriptPortal.Vegas` namespace — see the
[official API summary](https://help.magix-hub.com/video/vegas/22/en/content/topics/external/vegasscriptapi.html))
are wired up in the script host vs. still planned. Update this table as
methods are implemented — don't let it drift from the actual `host/` code.

Legend: ✅ implemented + tested against a real VEGAS instance · 🚧 stubbed
(RPC method exists, not yet calling real API) · ⬜ not started

| Area | VEGAS API surface | MCP method(s) | Status |
|---|---|---|---|
| Project | `Vegas.Project`, `Project.Length`, `Project.Tracks` | `project.get_state` | ⬜ |
| Project | `Vegas.SaveProject()` / `OpenProject()` | `project.save`, `project.open` | ⬜ |
| Tracks | `Tracks.Add(MediaType)`, `Track.Delete()` | `track.add`, `track.remove` | ⬜ |
| Tracks | `VideoTrack.CompositeMode`, `CompositeLevel` | `track.set_composite` | ⬜ |
| Events | `VideoTrack.AddVideoEvent(start, length)` | `event.add_video` | ⬜ |
| Events | `AudioTrack.AddAudioEvent(start, length)` | `event.add_audio` | ⬜ |
| Events | `TrackEvent.Start`, `.Length`, `.Delete()` | `event.trim`, `event.move`, `event.delete` | ⬜ |
| Media | `Project.MediaPool.AddMedia(path)` | `media.import` | ⬜ |
| Effects | `Effects` collection, `Effect` presets | `fx.add`, `fx.set_param` | ⬜ |
| Transitions | Transition on adjacent events (via `Effect` on the event) | `transition.add` | ⬜ |
| Envelopes | `Envelopes`, `Envelope.Points.AddPoint()` | `envelope.add`, `envelope.add_point` | ⬜ |
| Transport | `Vegas.Transport.Play()/Stop()`, `Transport.CursorPosition` | `transport.play`, `transport.seek` | ⬜ |
| Render | `Vegas.Render(templateName, outputPath, ...)` | `render.start`, `render.status` | ⬜ |

Every row starts at ⬜ until validated live against a real VEGAS install —
see `docs/ROADMAP.md` Phase 1 for the "first real round-trip" milestone that
should flip the first handful of rows to ✅.
