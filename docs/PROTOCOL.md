# Wire Protocol

The MCP server and the VEGAS script host talk JSON-RPC 2.0, one JSON
object per line, over TCP.

## Transport

The host in `host/VegasDirectorHost.cs` binds **TCP loopback only**:
`127.0.0.1:8752`. There is no authentication layer. Do not bind this
off localhost. If the MCP server must run on another machine, use an
SSH tunnel or VPN to that loopback port.

The Python client (`server/vegas_director_mcp/host_client.py`) defaults
to TCP via `VEGAS_HOST_TRANSPORT` (default `tcp`). It still contains a
Windows named-pipe path (`\\.\pipe\vegas-director`). The current host
does not create that pipe; `VEGAS_HOST_TRANSPORT=pipe` will fail against
this tree.

The host accepts one client at a time and handles that connection until
it closes, then accepts the next. The Python client opens a **new**
TCP connection per RPC call.

## Message shape

```json
{"jsonrpc": "2.0", "id": 1, "method": "project.get_state", "params": {}}
```

```json
{"jsonrpc": "2.0", "id": 1, "result": {"ok": true, "length_seconds": 0, "video_track_count": 0, "audio_track_count": 0, "tracks": [], "events": []}}
```

Parse failures and unknown methods use a JSON-RPC **error** object:

```json
{"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "Method not found: render.start"}}
```

Almost every VEGAS-side failure is a JSON-RPC **result** with
`ok: false` so the script host does not crash the editor:

```json
{"jsonrpc": "2.0", "id": 1, "result": {"ok": false, "error": "No active VEGAS project"}}
```

## Methods implemented in this tree

| Method | Params (common) | Notes |
|---|---|---|
| `ping` | — | `{ok, host}` |
| `project.get_state` | — | length, track counts, tracks, events |
| `project.save` | `path?` | omit `path` to save in place |
| `track.add` | `type` (`video`\|`audio`), `name?` | |
| `media.import` | `path` | media pool only |
| `media.place` | `path` or `media_path`, `track_index`, `start_seconds?`, `length_seconds?` | video vs audio from track type; `length_seconds=-1` = full media |
| `event.add_video` | `track_index`, `media_path` or `path`, `start_seconds?`, `length_seconds?` | video track required |
| `event.add_audio` | same | audio track required |
| `event.trim` | `track_index`, `event_index`, `start_seconds?`, `length_seconds?` | omitted fields unchanged |
| `event.move` | `track_index`, `event_index`, `start_seconds` | |
| `event.delete` | `track_index`, `event_index` | |
| `transport.play` | — | |
| `transport.stop` | — | |
| `transport.seek` | `seconds` | cursor position |

MCP tool names are the Python functions in
`server/vegas_director_mcp/__init__.py` (`get_project_state`,
`add_track`, `place_media`, …). They are thin wrappers over the RPC
names above. See [API_COVERAGE.md](API_COVERAGE.md).

Planned, not implemented: `transition.*`, `fx.*`, `envelope.*`,
`render.*`, project open/close, media probe tools.

## Threading

`ScriptPortal.Vegas` is not thread-safe. The TCP listener runs on a
background thread. Each mutating call is marshaled to the UI thread
with a hidden WinForms form (`Control.BeginInvoke`), 60s timeout.
Callers do not marshal.

## Timecodes

Positions and durations on the wire are **seconds** (`start_seconds`,
`length_seconds`, `seconds`). The host converts with
`Timecode.FromSeconds` / `ToMilliseconds`. The MCP tools do not parse
`HH:MM:SS` and do not convert ticks.

## Error codes

| Code | When |
|---|---|
| `-32700` | JSON parse failure (JSON-RPC error) |
| `-32601` | Unknown method (JSON-RPC error) |
| *(none)* | VEGAS/validation failures: result `{ok: false, error}` |

The older `-32001` / `-32002` / … table was a plan. The host does not
emit those codes today.
