# ScriptPortal.Vegas API Coverage

Legend: ✅ implemented in host · ⬜ not started

| Area | MCP / RPC | Status |
|---|---|---|
| Health | `ping` | ✅ |
| Project | `project.get_state` | ✅ |
| Project | `project.save` | ✅ |
| Tracks | `track.add` | ✅ |
| Media | `media.import`, `media.place` | ✅ |
| Events | `event.add_video`, `event.add_audio` | ✅ |
| Events | `event.trim`, `event.move`, `event.delete` | ✅ |
| Transport | `transport.play/stop/seek` | ✅ |
| FX / transitions / envelopes / render | — | ⬜ |

Soft failures return JSON-RPC **result** `{ "ok": false, "error": "..." }` (never crash VEGAS).

Validate live against VEGAS Pro 22 after installing the host script.
