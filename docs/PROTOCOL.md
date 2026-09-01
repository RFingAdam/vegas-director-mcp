# Wire Protocol

The MCP server and the VEGAS script host talk JSON-RPC 2.0 over a local
transport (named pipe on Windows by default; TCP loopback as a fallback for
easier debugging / cross-machine setups where the MCP server runs on a
different box than VEGAS itself).

## Transport

- **Named pipe (default):** `\\.\pipe\vegas-director` — lowest latency,
  no open network port, no auth needed since the pipe is local-machine-only
  by OS enforcement.
- **TCP loopback (opt-in):** `127.0.0.1:8752` — only bind non-loopback if you
  understand the risk; the protocol below has no authentication layer of its
  own. If the MCP server must run on a different machine than VEGAS, put it
  behind an SSH tunnel or a VPN, don't expose the port directly.

## Message shape

Standard JSON-RPC 2.0 request/response, newline-delimited over the pipe/socket.

```json
{"jsonrpc": "2.0", "id": 1, "method": "project.get_state", "params": {}}
```

```json
{"jsonrpc": "2.0", "id": 1, "result": {"tracks": [...], "length_ticks": 0}}
```

Errors follow standard JSON-RPC error objects:

```json
{"jsonrpc": "2.0", "id": 1, "error": {"code": -32001, "message": "No active VEGAS project"}}
```

## Method namespaces (planned surface)

| Namespace | Purpose |
|---|---|
| `project.*` | Open/close/save project, get current state |
| `track.*` | Add/remove video or audio tracks, set composite mode |
| `event.*` | Add/trim/move/delete video or audio events on a track |
| `transition.*` | Apply a transition between two adjacent events |
| `fx.*` | Add/configure a track or event effect (color, audio) |
| `envelope.*` | Add/edit automation envelopes (volume, pan, opacity) |
| `transport.*` | Play/stop/seek — mostly for interactive/preview use |
| `render.*` | Render the current project (or a time range) to a file |
| `media.*` | Import media into the project's media pool |

Every method that mutates project state runs on VEGAS's UI thread via
`Vegas.Invoke(...)` inside the host — the host owns marshaling, callers never
need to think about threading.

## Timecodes

All positions/durations are passed as **ticks** (VEGAS's native `Timecode`
unit — see the scripting API docs) to avoid frame-rate ambiguity across
projects. The MCP server's Python-side tools accept human units (seconds,
`HH:MM:SS.mmm`) and convert using the project's actual frame rate, queried
live from `project.get_state` rather than assumed.

## Error codes

| Code | Meaning |
|---|---|
| -32001 | No active VEGAS project |
| -32002 | Invalid track/event index |
| -32003 | Media file not found or unreadable by VEGAS |
| -32004 | Render already in progress |
| -32700 / -32600 / -32601 / -32602 / -32603 | Standard JSON-RPC parse/invalid-request/method-not-found/invalid-params/internal errors |
