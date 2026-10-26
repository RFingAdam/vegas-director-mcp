# Roadmap

## Phase 0 — Scaffold
- Done: repo structure, protocol, license.

## Phase 1 — First real round-trip (complete)
- Host: TCP `127.0.0.1:8752` only, WinForms UI-thread marshal, SoftFail `ok:false`.
- Methods: ping / project.get_state (+ media_path, take offsets) / save /
  track.add / media.import / media.place / event.add_video|audio / trim
  (+ take_offset) / move / delete / transport.*.
- MCP: matching FastMCP tools; default transport TCP.

## Phase 2 — Magix FAQ editorial primitives (complete)
- `event.set_motion` — VideoMotion pan/crop keyframes (Bounds crop-zoom).
- `event.set_fades` — FadeIn/Out Length + Smooth curve; optional Dissolve;
  reciprocal_curve for overlaps.
- `event.set_opacity` — FadeIn.Gain.
- `event.add_title` — Titles & Text generator + OFX Text RTF (PNG lower-thirds
  remain as branded backup under ironhaven thumbs).
- `track.set_composite_level` — track opacity.
- `envelope.set_points` — Volume / CompositeLevel create-or-update points.
- `project.get_selected_events` — selected track/event indices.
- `render.start` — best-effort RenderArgs or SoftFail → File > Render As.
- Use case: cut a ~2 min Raid Hours promo (9.9/10) with zooms, fades, clarifying
  text (native titles and/or PNG overlays).

## Phase 3a — Host-side project / media / track tools (complete on disk)
Oct 2026 local work, now the GitHub source of truth:

- `project.new` / `project.open` with save-or-discard.
- `media.list` / `media.replace` / `media.set_alpha`.
- `track.set_props` / `track.clear_events` / `track.add` insert `index`.
- `envelope.clear`, `event.set_gain`, `render.list_templates`.
- v2 host: `StartHeadless` + `ICustomCommandModule` Application Extension so
  the TCP listener starts with VEGAS; runtime token under
  `%LOCALAPPDATA%\vegas-director-mcp\token` (generated, never committed).

Still needed from Adam: run `host\build.ps1` (or re-copy the Script Menu
`.cs`) and restart VEGAS so the live editor matches disk.

## Phase 3b — Media grounding + higher-level edit helpers (not done)
- `probe_media` (ffprobe) and `detect_scenes` (ffmpeg) for real in/out candidates.
- Audio loudness / peak detection (reaction spikes, kill/cash, squad shout).
- Optional local Whisper (`faster-whisper`, GPU if present).
- Caption generation (SRT/ASS + burned-in vertical Short style).
- `find_highlights` ranking 20–35 s Short candidates.
- Crossfade / music-voice ducking helpers on envelope + fades primitives.
- Vertical Short template (16:9 → 9:16 crop/pan, punch-in, captions, loop end).
- `propose_edit` composite tool iterating place → inspect → revise.

## Phase 4 — Render & delivery (not done)
- Named render presets (vertical 1080×1920 / 1080p / 4K).
- Async status polling via `Vegas.BeginRender` + `RenderProgress` /
  `RenderFinished` so a long encode does not sit on the UI-marshal wait.
- Verify the output file (duration / resolution / audio) with ffprobe.
- Edit-metadata sidecar JSON next to every render (length, hook start,
  caption style, zoom count, music on/off, template) for a weekly
  retention loop.

## Non-goals (for now)
- Full VEGAS UI parity — editing/automation surface, not remote desktop.
- Multi-user/remote collaboration — single local VEGAS instance only.
- True GUI-less VEGAS. Pro 22 has `/RUNSCRIPT`, `/SCRIPTARGS`, and
  `/CMDMODULE`, but no documented headless/no-UI mode. "No-host" means
  auto-start the in-process host (extension) or generate a one-shot
  script, not a separate render farm.
