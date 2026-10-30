# nle-mcp

An MCP (Model Context Protocol) server that puts a model in the editor's
chair. The same tools (timeline, clips, markers, FX, render) can target
more than one backend:

| `DIRECTOR_EDITOR` | Backend | Needs |
|---|---|---|
| `ffmpeg` | Headless FFmpeg | `ffmpeg` / `ffprobe` on PATH. No GUI NLE. |
| `vegas` (default) | MAGIX VEGAS Pro via `ScriptPortal.Vegas` | Windows + VEGAS Pro 22+ |
| `resolve` | DaVinci Resolve via `DaVinciResolveScript` | **Resolve Studio 21.1+**, External scripting = Local. Free Resolve has **no** Scripting API since 21.1. |
| `otio` | In-memory OTIO / FCPXML / MLT import and export | Nothing. Timeline I/O only — not a renderer. |

The GitHub repository is still named `vegas-director-mcp`. The Python
package, MCP server name, and docs use **nle-mcp**. Proposed public names
are in the pull request that introduced this layout. See
[docs/MIGRATION.md](docs/MIGRATION.md) if you used the old package name.

**Not affiliated with MAGIX or Blackmagic Design.** See [NOTICE](NOTICE).

## Why this exists

GUI NLEs have scripting surfaces but no first-party MCP API. This project
exposes a shared tool set over MCP so an agent can cut, mix, caption, and
render. FFmpeg is the headless path (full edits with no editor GUI). VEGAS
and Resolve keep live control of a running NLE. OTIO / FCPXML / MLT are
plain timeline interchange.

The intended workflow is inspect-and-revise: the model proposes an edit,
the backend executes it, and the model can read the timeline back.

## What is implemented

**Shared timeline tools** (every backend):

- Inspect the open project (length, tracks, events, media paths, take offsets)
- New / open / save project; list / replace media
- Add video/audio tracks; rename, mute, solo, volume
- Import media, place it, trim / move / delete events, set event gain
- Motion pan/crop keyframes, fades, opacity, titles
- Volume envelopes (set points or clear)
- Named render presets (`vertical` / `1080p` / `4k`), `render_status`

**FFmpeg (headless):** probe, cut/trim, concat, transitions (crossfade),
audio mix / loudness normalize, caption burn-in, reframe (cover-crop),
and render to MP4. An agent can finish an edit with no GUI NLE.

**VEGAS live control:** C# host inside VEGAS over TCP `127.0.0.1:8752`
(Application Extension or Script Menu). Play / stop / seek, native Titles
& Text, VideoMotion, VEGAS render templates.

**Resolve live control:** DaVinci Resolve Studio scripting. Studio-only
extras: `CreateSubtitlesFromAudio`, `SmartReframe`, `SetVoiceIsolationState`.
Setup: [docs/RESOLVE.md](docs/RESOLVE.md).

**Interchange:** `DIRECTOR_EDITOR=otio` — `project.save` writes `.otio`,
`.fcpxml`, or `.mlt`. Not a renderer.

**Analysis (no NLE required):**

- `probe_media`, `detect_scenes`, `analyze_audio`, optional `transcribe_media`
- `generate_captions` / `burn_captions` (generic SRT + ASS)
- File-level `cut_media`, `concat_media`, `reframe_media`, `mix_audio`,
  `normalize_audio`
- `apply_crossfade`, `apply_ducking`

Inspired by the pattern used by [Bitwig MCP Server](https://github.com/WeModulate/bitwig-mcp-server)
for DAWs, and by an early architecture sketch in
[MarcoRavich/VEGAS-AI-control](https://github.com/MarcoRavich/VEGAS-AI-control)
(CC0-1.0).

## Architecture

```
┌─────────────────────┐
│   MCP Server         │  DIRECTOR_EDITOR=ffmpeg|vegas|resolve|otio
│   (Python, FastMCP)  │
│                       │
│  tools.py ──► backends/
│               ├─ ffmpeg  ── in-memory timeline ──► ffmpeg encode
│               ├─ vegas   ── TCP 127.0.0.1:8752 ──► VEGAS C# host
│               ├─ resolve ── DaVinciResolveScript ──► Resolve Studio
│               └─ otio    ── in-memory ──► .otio / .fcpxml / .mlt
└─────────────────────┘
```

Times on the wire are **seconds** (`start_seconds`, `length_seconds`).

See [docs/PROTOCOL.md](docs/PROTOCOL.md) for the VEGAS wire format,
[docs/API_COVERAGE.md](docs/API_COVERAGE.md) for coverage,
[docs/FFMPEG.md](docs/FFMPEG.md) for the headless path, and
[docs/EDITORS.md](docs/EDITORS.md) for other NLEs.

## Requirements

Depends on `DIRECTOR_EDITOR` (default `vegas`, for existing installs):

- **FFmpeg (`ffmpeg`):** Python 3.11+ and `ffmpeg` / `ffprobe` on PATH.
  Works on Windows, macOS, and Linux.
- **VEGAS (`vegas`):** Windows, **VEGAS Pro 22+**, valid license. Python 3.11+
  on the same machine (or an SSH tunnel to `127.0.0.1:8752`). Optional:
  .NET Framework 4.x `csc.exe` for the Application Extension DLL
  (`host/build.ps1`). Script Menu mode does not need a compile.
- **Resolve (`resolve`):** **DaVinci Resolve Studio 21.1+** on Windows,
  macOS, or Linux. Preferences → System → General → **External scripting = Local**.
  See [docs/RESOLVE.md](docs/RESOLVE.md).
- **Interchange (`otio`):** Python 3.11+ only. `project.save` writes
  `.otio`, `.fcpxml`, or `.mlt`.

`ffmpeg` / `ffprobe` are required for media grounding, caption burn-in,
the FFmpeg backend, and render verification. Optional:
`pip install 'nle-mcp[whisper]'`.

## Quick start

- Headless: [docs/FFMPEG.md](docs/FFMPEG.md)
- VEGAS: [docs/SETUP.md](docs/SETUP.md)
- Resolve: [docs/RESOLVE.md](docs/RESOLVE.md)

```bat
cd <clone>\server
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
set DIRECTOR_EDITOR=ffmpeg
python -m nle_mcp
```

`python -m vegas_director_mcp` is a backward-compatible alias.

## Layout

| Path | What |
|---|---|
| `host/VegasDirectorHost.cs` | In-process VEGAS script / TCP host |
| `host/VegasDirectorExtension.cs` | `ICustomCommandModule` auto-start wrapper |
| `host/build.ps1` | Compile + install the extension DLL |
| `server/nle_mcp/` | FastMCP server + backends + JSON-RPC client |
| `server/vegas_director_mcp/` | Import / `python -m` alias for `nle_mcp` |
| `scripts/register_claude.py` | Write Claude Desktop MCP config from this checkout |
| `skills/nle-mcp/SKILL.md` | Generic example of how to drive the tools |
| `server/tests/` | Mocked hosts + synthetic ffmpeg fixtures |
| `docs/` | Protocol, API coverage, setup, ffmpeg, roadmap, editors, Resolve, licensing, migration |

## License

MIT — [LICENSE](LICENSE). Affiliation and trademark notes — [NOTICE](NOTICE).
GitHub may show the license as "Other" because LICENSE also carries MAGIX
and CC0 notes; SPDX options are in [docs/LICENSING_OPTIONS.md](docs/LICENSING_OPTIONS.md).
**This repo does not change LICENSE in this PR.**

Initial architecture informed by a CC0-1.0 reference project (credited
above); no code reused verbatim.

## Contributing

Issues and PRs welcome. How to run a checkout: [docs/SETUP.md](docs/SETUP.md)
or [docs/FFMPEG.md](docs/FFMPEG.md). Contributor notes: [CONTRIBUTING.md](CONTRIBUTING.md).
