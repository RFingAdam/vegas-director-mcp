# vegas-director-mcp

An MCP (Model Context Protocol) server that puts a model in the editor's
chair. Same tools (timeline, clips, markers, FX, render) can target more
than one NLE:

| `DIRECTOR_EDITOR` | Backend | Needs |
|---|---|---|
| `vegas` (default) | MAGIX VEGAS Pro via `ScriptPortal.Vegas` | Windows + VEGAS Pro 22 |
| `resolve` | DaVinci Resolve via `DaVinciResolveScript` | **Resolve Studio 21.1+**, External scripting = Local. Free Resolve has **no** Scripting API since 21.1. |
| `otio` | In-memory OTIO / FCPXML / MLT export | Nothing. Free Resolve can import the file. |

Default is still VEGAS — existing installs do not change. Resolve setup
and the Studio vs free line: [docs/RESOLVE.md](docs/RESOLVE.md). Other
NLEs and what to build next: [docs/EDITORS.md](docs/EDITORS.md).

The VEGAS path drives the timeline through VEGAS's own scripting API
(`ScriptPortal.Vegas`) instead of simulated mouse/keyboard input.

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
┌─────────────────────┐
│   MCP Server         │  DIRECTOR_EDITOR=vegas|resolve|otio
│   (Python, FastMCP)  │
│                       │
│  tools.py ──► backends/
│               ├─ vegas   ── TCP 127.0.0.1:8752 ──► VEGAS C# host
│               ├─ resolve ── DaVinciResolveScript ──► Resolve Studio
│               └─ otio    ── in-memory ──► .otio / .fcpxml / .mlt
└─────────────────────┘
```

The VEGAS path is still:

```
MCP tools ── JSON-RPC / TCP 127.0.0.1:8752 ──► host/VegasDirectorHost.cs
```

Times on the wire are **seconds** (`start_seconds`, `length_seconds`), not
VEGAS ticks.

See [docs/PROTOCOL.md](docs/PROTOCOL.md) for the wire format and
[docs/API_COVERAGE.md](docs/API_COVERAGE.md) for what is implemented.

## Requirements

Depends on `DIRECTOR_EDITOR` (default `vegas`):

- **VEGAS (`vegas`):** Windows, **VEGAS Pro 22**, valid license. Older 18+
  installs may work; they are untested here. Python 3.11+ on the same
  machine (or an SSH tunnel to `127.0.0.1:8752`). Optional: .NET Framework
  4.x `csc.exe` for the Application Extension DLL (`host/build.ps1`).
  Script Menu mode does not need a compile — VEGAS compiles the `.cs`
  when you run it.
- **Resolve (`resolve`):** **DaVinci Resolve Studio 21.1+** on Windows,
  macOS, or Linux. The free edition has had **no Scripting API** since
  21.1 (Blackmagic feature sheet: `Scripting API: Studio`). External
  `scriptapp` already required Studio before that. Set
  Preferences → System → General → **External scripting = Local**.
  Studio-only extras: `CreateSubtitlesFromAudio`, `SmartReframe`,
  `SetVoiceIsolationState`. See [docs/RESOLVE.md](docs/RESOLVE.md).
- **Interchange (`otio`):** Python 3.11+ only. `project.save` writes
  `.otio`, `.fcpxml`, or `.mlt`. Free Resolve can import OTIO/FCPXML.

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
| `docs/` | Protocol, API coverage, setup, roadmap, editors, Resolve, licensing |

## License

MIT — [LICENSE](LICENSE). Affiliation and trademark notes — [NOTICE](NOTICE).
GitHub may show the license as "Other" because LICENSE also carries MAGIX
and CC0 notes; options for a later SPDX-clean release (and how to ask for
SwampBewdy credit without blocking adoption) are in
[docs/LICENSING_OPTIONS.md](docs/LICENSING_OPTIONS.md). **This repo does
not change LICENSE in the multi-editor PR.**

Initial architecture informed by a CC0-1.0 reference project (credited
above); no code reused verbatim.

## Made by SwampBewdy

Built by Adam ([RFingAdam](https://github.com/RFingAdam)), who streams as
**SwampBewdy**.

- Twitch: [twitch.tv/swampbewdy](https://twitch.tv/swampbewdy)
- YouTube: SwampBewdy
- Discord: [discord.gg/WWvJXUS6mb](https://discord.gg/WWvJXUS6mb)

If this saves you a cut, a credit is appreciated. Not required by the
license — see [docs/LICENSING_OPTIONS.md](docs/LICENSING_OPTIONS.md).

## Contributing

Issues and PRs welcome. Personal project, best-effort, not a supported
product. How to run a checkout: [docs/SETUP.md](docs/SETUP.md). Short
contributor notes: [CONTRIBUTING.md](CONTRIBUTING.md). Do not merge
multi-editor work until Adam has; the agent opens the PR only.
