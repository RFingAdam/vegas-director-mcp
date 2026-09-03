# Roadmap

## Phase 0 — Scaffold

Done: repo layout, protocol sketch, MIT license.

## Phase 1 — First real round-trip (on disk; live VEGAS still operator-owned)

Implemented in this tree:

- Host: TCP `127.0.0.1:8752` only, WinForms UI-thread marshal, soft
  `{ok: false}` errors. No named-pipe listener.
- Methods: `ping`, `project.get_state`, `project.save`, `track.add`,
  `media.import`, `media.place`, `event.add_video` / `event.add_audio`,
  `event.trim` / `event.move` / `event.delete`, `transport.*`
- MCP: matching FastMCP tools in `server/vegas_director_mcp/`; default
  transport TCP.

Still needed: load the script from the VEGAS Scripting menu on a real
machine, leave the dialog open, run the [SETUP.md](SETUP.md) smoke test.
`render.*` is not Phase 1.

## Phase 2 — Media grounding (not in this tree)

- `probe_media` (ffprobe: duration, resolution, fps, audio)
- `detect_scenes` (ffmpeg scene-change detection)
- Optional local Whisper for dialogue-driven cuts

A separate open PR explores editorial primitives (motion, fades, titles,
envelopes, best-effort render). That is not merged here and is not
required to run Phase 1.

## Phase 3 — Editorial primitives

- Transitions, basic color FX presets, crossfade helpers
- Audio ducking envelopes under dialogue
- A `propose_edit` composite tool (brief + probed clips → place /
  inspect / revise)

## Phase 4 — Render and delivery

- Render presets (vertical / 16:9 1080p / 4K) with status polling so a
  long VEGAS render does not block the MCP tool forever
- End-to-end check against the output file (duration, resolution), not
  only the render call's return value

## Non-goals (for now)

- Full VEGAS UI parity
- Multi-user / remote collaboration — one local VEGAS instance
- Auth beyond "do not expose the TCP port"
