# vegas-director-mcp

An MCP (Model Context Protocol) server that puts a model in the editor's
chair for **MAGIX VEGAS Pro** — driving the timeline through VEGAS's own
scripting API (`ScriptPortal.Vegas`) instead of simulated mouse/keyboard
input.

Inspired by the pattern used by [Bitwig MCP Server](https://github.com/WeModulate/bitwig-mcp-server)
for DAWs, and by an early architecture sketch in
[MarcoRavich/VEGAS-AI-control](https://github.com/MarcoRavich/VEGAS-AI-control)
(CC0-1.0). This repo is a working pair: a C# host that runs inside VEGAS,
and a Python FastMCP server that talks to it over localhost TCP.

**Not affiliated with MAGIX.** See [NOTICE](NOTICE).

## Why this exists

VEGAS Pro has no first-party remote-control or AI API. It does have a mature
`.NET` scripting surface used for decades by editors writing macro tools.
This project exposes that surface over MCP so Claude / Grok Bot can cut
Shorts and long-form for a gaming channel (16:9 sources cropped to 9:16)
and promo spots.

The intended workflow is editor-in-the-loop: the model proposes an edit,
the host executes it inside a running VEGAS instance, and the model can
read the timeline back and revise.

## What is implemented

**Host + MCP tools (Phases 1–2 plus the Oct 2026 host-side Phase 3 tools):**

- Inspect the open project (length, tracks, events, media paths, take offsets)
- New / open / save project; list / replace / alpha-tag media
- Add video/audio tracks (optional insert index); rename, mute, solo, volume
- Import media, place it, trim / move / delete events, set event gain
- VideoMotion pan/crop keyframes, fades, opacity, Titles & Text
- Volume / CompositeLevel envelopes (set points or clear)
- Play, stop, seek; list render templates; best-effort `render.start`
- `host.info` reports script-dialog vs extension mode

**Two ways to start the host** (same TCP interface):

1. **Application Extension (preferred).** `host/build.ps1` compiles
   `VegasDirector.dll` and installs it under
   `Documents\Vegas Application Extensions`. VEGAS Pro 22 loads
   `ICustomCommandModule` at startup and keeps it for the process lifetime,
   so nobody has to open *Tools > Scripting*. Extension mode requires the
   runtime token at `%LOCALAPPDATA%\vegas-director-mcp\token`.
2. **Script Menu fallback.** Copy `host/VegasDirectorHost.cs` into a Script
   Menu folder and run *Tools > Scripting > VegasDirectorHost*. Leave the
   dialog open. No token required.

The host binds **TCP `127.0.0.1:8752` only**.

**Phase 3/4 (default editing path):**

- `probe_media`, `detect_scenes`, `analyze_audio`, optional `transcribe_media`
  (`faster-whisper`, GPU if present) — no VEGAS required
- `generate_captions` / `burn_captions` (SRT + 9:16 ASS)
- `find_highlights` ranks 20–35 s Short candidates
- `apply_crossfade`, `apply_ducking`, `apply_vertical_short`, `propose_edit`
- Named render presets (`vertical` / `1080p` / `4k`), async
  `Vegas.BeginRender` + `render_status`, ffprobe verify, `<output>.edit.json`
  sidecar
- Same tools auto-pick live TCP vs launching VEGAS (`/RUNSCRIPT` or the
  Application Extension) and report `used_mode`

Skill: [skills/vegas-director/SKILL.md](skills/vegas-director/SKILL.md).

## Architecture

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

Times on the wire are **seconds** (`start_seconds`, `length_seconds`), not
VEGAS ticks.

See [docs/PROTOCOL.md](docs/PROTOCOL.md) for the wire format and
[docs/API_COVERAGE.md](docs/API_COVERAGE.md) for what is implemented.

## Requirements

- Windows, with **VEGAS Pro 22** (scripting surface this host was written
  against) and a valid license. Older 18+ installs may work; they are
  untested here.
- Python 3.11+ for the MCP server, same machine as VEGAS (or an SSH tunnel
  to `127.0.0.1:8752`).
- Optional: .NET Framework 4.x `csc.exe` if you want the Application
  Extension DLL (`host/build.ps1`). Script Menu mode does not need a compile
  — VEGAS compiles the `.cs` when you run it.

`ffmpeg` / `ffprobe` are required for media grounding, caption burn-in, and
render verification. Optional: `pip install 'vegas-director-mcp[whisper]'`.

## Quick start

[docs/SETUP.md](docs/SETUP.md) — extension or Script Menu, venv, smoke
test, Claude Desktop registration.

## Layout

| Path | What |
|---|---|
| `host/VegasDirectorHost.cs` | In-process VEGAS script / TCP host |
| `host/VegasDirectorExtension.cs` | `ICustomCommandModule` auto-start wrapper |
| `host/build.ps1` | Compile + install the extension DLL |
| `host/reflect_api.ps1` | Optional ScriptPortal.Vegas reflection helper |
| `server/vegas_director_mcp/` | FastMCP server + JSON-RPC client |
| `scripts/register_claude.py` | Write Claude Desktop MCP config from this checkout |
| `skills/vegas-director/SKILL.md` | Default Short / long-form workflow |
| `server/tests/` | Mocked host + synthetic ffmpeg fixtures |
| `docs/` | Protocol, API coverage, setup, roadmap |

## License

MIT — [LICENSE](LICENSE). Affiliation and trademark notes — [NOTICE](NOTICE).

Initial architecture informed by a CC0-1.0 reference project (credited
above); no code reused verbatim.

## Contributing

Issues and PRs welcome. Personal project, best-effort, not a supported
product. How to run a checkout: [docs/SETUP.md](docs/SETUP.md). Short
contributor notes: [CONTRIBUTING.md](CONTRIBUTING.md).
