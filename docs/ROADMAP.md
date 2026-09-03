# Roadmap

## Phase 0 — Scaffold
- Done: repo structure, protocol, license.

## Phase 1 — First real round-trip (complete on disk; requires host reload in VEGAS)
- Host: TCP 8752 (+ pipe client), WinForms UI-thread marshal, SoftFail `ok:false`.
- Methods: ping / project.get_state (+ media_path, take offsets) / save /
  track.add / media.import / media.place / event.add_video|audio / trim
  (+ take_offset) / move / delete / transport.*.
- MCP: matching FastMCP tools; default transport TCP.
- Still needed from Adam: reload Script Menu host so live VEGAS matches disk.

## Phase 2 — Magix FAQ editorial primitives (this PR)
- `event.set_motion` — VideoMotion pan/crop keyframes (ScaleBy / MoveBy).
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

## Phase 3 — Media grounding + higher-level edit helpers
- `probe_media` (ffprobe) and `detect_scenes` (ffmpeg) for real in/out candidates.
- Optional Whisper for dialogue-driven cuts.
- Crossfade / ducking helpers built on envelope + fades primitives.
- `propose_edit` composite tool iterating place → inspect → revise.

## Phase 4 — Render & delivery
- Named render presets (vertical / 1080p / 4K) with **async** status polling
  (do not block the host dialog on multi-minute jobs).
- End-to-end: raw clips in → verified output file (duration/resolution).

## Non-goals (for now)
- Full VEGAS UI parity — editing/automation surface, not remote desktop.
- Multi-user/remote collaboration — single local VEGAS instance only.
- Auth beyond "don't expose the TCP port publicly".
