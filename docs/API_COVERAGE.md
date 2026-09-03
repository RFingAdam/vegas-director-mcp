# ScriptPortal.Vegas API Coverage

Legend: ✅ in this tree (host + MCP tool) · ⬜ not in this tree

Times are seconds. Soft failures are JSON-RPC **result**
`{ "ok": false, "error": "..." }` so VEGAS does not crash.

| Area | RPC | MCP tool | Status |
|---|---|---|---|
| Health | `ping` | `ping` | ✅ |
| Project | `project.get_state` | `get_project_state` | ✅ |
| Project | `project.save` | `save_project` | ✅ |
| Tracks | `track.add` | `add_track` | ✅ |
| Media | `media.import` | `import_media` | ✅ |
| Media | `media.place` | `place_media` | ✅ |
| Events | `event.add_video` | `add_video_event` | ✅ |
| Events | `event.add_audio` | `add_audio_event` | ✅ |
| Events | `event.trim` | `trim_event` | ✅ |
| Events | `event.move` | `move_event` | ✅ |
| Events | `event.delete` | `delete_event` | ✅ |
| Transport | `transport.play` | `transport_play` | ✅ |
| Transport | `transport.stop` | `transport_stop` | ✅ |
| Transport | `transport.seek` | `transport_seek` | ✅ |
| FX / transitions / envelopes / render | — | — | ⬜ |
| Media probe / scenes / transcript | — | — | ⬜ |

`project.get_state` returns `length_seconds`, `video_track_count`,
`audio_track_count`, `tracks[]` (`index`, `name`, `type`, `event_count`),
and `events[]` (`track_index`, `event_index`, `start_seconds`,
`length_seconds`). It does not currently return media paths or take
offsets.

Validate live against VEGAS Pro 22 after installing the host script.
See [SETUP.md](SETUP.md).
