# vegas-director-mcp

An MCP (Model Context Protocol) server that puts a model in the editor's
chair for **MAGIX VEGAS Pro** — driving the timeline through VEGAS's own
scripting API (`ScriptPortal.Vegas`) instead of simulated mouse/keyboard
input.

Inspired by the pattern used by [Bitwig MCP Server](https://github.com/WeModulate/bitwig-mcp-server)
for DAWs, and by an early architecture sketch in
[MarcoRavich/VEGAS-AI-control](https://github.com/MarcoRavich/VEGAS-AI-control)
(CC0-1.0). This repo is a working Phase 1 pair: a C# script that runs
inside VEGAS, and a Python FastMCP server that talks to it over localhost
TCP.

**Not affiliated with MAGIX.** See [NOTICE](NOTICE).

## Why this exists

VEGAS Pro has no first-party remote-control or AI API. It does have a mature
`.NET` scripting surface used for decades by editors writing macro tools.
This project exposes that surface over MCP.

**This tree (Phase 1)** can:

- Inspect the open project (length, tracks, events)
- Add video/audio tracks
- Import media into the pool and place it on a track
- Trim, move, and delete events
- Play, stop, and seek the transport
- Save the project

**Later phases** (see [docs/ROADMAP.md](docs/ROADMAP.md)): media probing
(ffprobe / scene cuts / optional transcript), transitions, FX, envelopes,
and render. Those tools are not in this tree.

The intended workflow is editor-in-the-loop: the model proposes an edit,
the host executes it inside a running VEGAS instance, and the model can
read the timeline back and revise.

## Architecture

Two processes, one local JSON-RPC channel:

```
┌─────────────────────┐     JSON-RPC / TCP      ┌──────────────────────┐
│   MCP Server         │◄── 127.0.0.1:8752 ────►│  VEGAS Script Host    │
│   (Python, FastMCP)  │     (loopback only)     │  (C#, inside VEGAS)   │
│                       │                         │                       │
│  server/vegas_director_mcp/                     │  host/VegasDirectorHost.cs
│  - MCP tool surface   │                         │  - ScriptPortal.Vegas │
│  - host_client.py     │                         │  - UI-thread marshal  │
└─────────────────────┘                         └──────────────────────┘
```

- The **script host** (`host/VegasDirectorHost.cs`) is a VEGAS script, not
  a separate .exe. Copy it into a Script Menu folder and run
  *Tools > Scripting > VegasDirectorHost*. Leave the dialog open — closing
  it stops the listener. The host binds **TCP `127.0.0.1:8752` only**. It
  marshals `ScriptPortal.Vegas` calls onto the UI thread with a hidden
  WinForms control (`Control.BeginInvoke`). VEGAS scripting has no
  `Vegas.Invoke`.
- The **MCP server** (`server/vegas_director_mcp/`) is a stdio FastMCP
  process. Default client transport is TCP to `127.0.0.1:8752`. Run it on
  the same Windows machine as VEGAS (or tunnel loopback; do not bind the
  host off localhost). The Python client still has a named-pipe code path;
  the current host does not listen on a pipe.

Times on the wire are **seconds** (`start_seconds`, `length_seconds`), not
VEGAS ticks.

See [docs/PROTOCOL.md](docs/PROTOCOL.md) for the wire format and
[docs/API_COVERAGE.md](docs/API_COVERAGE.md) for what is implemented.

## Status

Phase 1 is implemented on disk. It is not production-verified. You still
need a licensed VEGAS Pro 22 instance on Windows, the host dialog left
open, and a live smoke test. FX, transitions, envelopes, render, and media
analysis are not implemented here.

A separate open PR explores Phase 2 editorial primitives. That work is
not on `main` and is not part of this docs update.

## Requirements

- Windows, with **VEGAS Pro 22** (scripting surface this host was written
  against) and a valid license. Older 18+ installs may work; they are
  untested here.
- No separate C# build. VEGAS compiles the `.cs` script when you run it.
- Python 3.11+ for the MCP server.
- Same machine as VEGAS (or an SSH tunnel to `127.0.0.1:8752`).

`ffmpeg` / `ffprobe` are **not** required for Phase 1.

## Quick start

[docs/SETUP.md](docs/SETUP.md) — host into the Script Menu, venv, smoke
test, MCP client snippet.

## Layout

| Path | What |
|---|---|
| `host/VegasDirectorHost.cs` | In-process VEGAS script (TCP host) |
| `server/vegas_director_mcp/` | FastMCP server + JSON-RPC client |
| `server/requirements.txt` | Python deps (`fastmcp`, `pydantic`, `pywin32` on Windows) |
| `server/pyproject.toml` | Package metadata (`pip install -e .` from `server/`) |
| `docs/` | Protocol, API coverage, setup, roadmap |

## License

MIT — [LICENSE](LICENSE). Affiliation and trademark notes — [NOTICE](NOTICE).

Initial architecture informed by a CC0-1.0 reference project (credited
above); no code reused verbatim.

## Contributing

Issues and PRs welcome. Personal project, best-effort, not a supported
product. How to run a checkout: [docs/SETUP.md](docs/SETUP.md). Short
contributor notes: [CONTRIBUTING.md](CONTRIBUTING.md).
