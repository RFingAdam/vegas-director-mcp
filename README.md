# vegas-director-mcp

An MCP (Model Context Protocol) server that puts an AI model in the editor's
chair for **MAGIX VEGAS Pro** — driving the timeline, trimming and ordering
clips, applying transitions/FX, mixing audio, and rendering output, using
VEGAS's own scripting API instead of simulating mouse/keyboard input.

Inspired by the pattern used by [Bitwig MCP Server](https://github.com/WeModulate/bitwig-mcp-server)
for DAWs, and by an early architecture sketch in
[MarcoRavich/VEGAS-AI-control](https://github.com/MarcoRavich/VEGAS-AI-control)
(CC0-1.0). This project implements a working system, not just a mapping doc:
a real in-process script host, a real IPC transport, and a real MCP server —
plus a media-analysis layer (scene detection, audio levels, transcripts) so
the model has enough grounding to make actual editorial decisions, not just
mechanical timeline edits.

## Why this exists

VEGAS Pro has no first-party remote-control or AI API. It does have a mature
`.NET` scripting surface (`ScriptPortal.Vegas` namespace) used for decades by
editors writing macro tools. This project exposes that surface over MCP so a
model can:

- Ingest a folder of raw clips and understand what's in each one (duration,
  resolution, audio peaks, detected scene cuts, optional transcript)
- Build an edit: place events on tracks, trim in/out points, order clips,
  add crossfades/transitions, apply basic color/audio FX
- Add audio ducking / music bed envelopes under dialogue
- Render the final timeline to a delivery format
- Iterate — inspect the current timeline state and revise

The goal is an editor-in-the-loop workflow: the model proposes an edit from
raw footage plus a brief ("60-second trailer, upbeat, lead with the best
action shot"), the host executes it inside a real running VEGAS instance,
and the model can inspect the result and refine it.

## Architecture

Two processes, one local IPC channel:

```
┌─────────────────────┐        JSON-RPC over          ┌──────────────────────┐
│   MCP Server         │◄──── named pipe / TCP ───────►│  VEGAS Script Host    │
│   (Python, FastMCP)  │        (localhost only)        │  (C#, runs inside     │
│                       │                                │   the VEGAS process)  │
│  - MCP tool surface   │                                │  - ScriptPortal.Vegas │
│  - media probing      │                                │    calls              │
│    (ffprobe/ffmpeg)   │                                │  - executes on the    │
│  - scene detection    │                                │    UI thread via      │
│  - optional Whisper   │                                │    Vegas.Invoke()     │
│    transcription      │                                │                       │
└─────────────────────┘                                └──────────────────────┘
```

- The **script host** (`host/VegasDirectorHost.cs`) is loaded into VEGAS via
  *Tools > Scripting > Run Script*, or auto-loaded via VEGAS's Startup
  Scripts folder. It opens a local named-pipe (Windows) or TCP loopback
  listener and marshals every request onto VEGAS's UI thread with
  `Vegas.Invoke(...)`, since the scripting API is not thread-safe.
- The **MCP server** (`server/`) is a normal FastMCP process — can run on
  the same Windows box or anywhere with network access to it. It exposes MCP
  tools that either call the script host directly (timeline/track/render
  operations) or do local media analysis (ffprobe, scene-cut detection,
  transcription) before handing the model grounded facts to reason over.

See [`docs/PROTOCOL.md`](docs/PROTOCOL.md) for the wire format and
[`docs/API_COVERAGE.md`](docs/API_COVERAGE.md) for which `ScriptPortal.Vegas`
surface is wired up vs. planned.

## Status

Early scaffold. See [`docs/ROADMAP.md`](docs/ROADMAP.md) for build phases.
Nothing here is production-verified yet — this repo currently defines the
protocol and skeleton for both processes; connecting them to a real running
VEGAS instance and validating end-to-end is the first milestone.

## Requirements

- VEGAS Pro (18+ recommended; scripting API surface referenced here matches
  the VEGAS Pro 22 docs) on Windows, with a valid license.
- .NET Framework matching your VEGAS install's scripting runtime (see VEGAS's
  own scripting docs for the exact version per release).
- Python 3.11+ for the MCP server.
- `ffmpeg`/`ffprobe` on the machine running the MCP server, for media
  analysis tools.

## Quick start

See [`docs/SETUP.md`](docs/SETUP.md).

## License

MIT — see [`LICENSE`](LICENSE). Initial architecture informed by a CC0-1.0
reference project (credited above); no code reused verbatim.

## Contributing

Issues and PRs welcome. This is a personal project maintained on a best-
effort basis, not a supported product.
