# Roadmap

## Phase 0 — Scaffold
- Done: repo structure, protocol, license.

## Phase 1 — First real round-trip (in progress on VEGAS Pro 22)
- Host: pipe + TCP 8752, UI-thread marshal, ping/get_state/save/track.add/
  media.import/event.add_video|audio/trim/move/delete/transport.*
- MCP: matching FastMCP tools; default transport TCP.
- Still needed: live load in VEGAS Scripting menu, smoke test, render.*

## Phase 2 — Media grounding
- `probe_media` (ffprobe: duration, resolution, fps, audio channel/peak
  data) for every clip in a source folder.
- `detect_scenes` (ffmpeg scene-change detection) to give the model real
  in/out point candidates instead of guessing blindly.
- Optional: local Whisper transcription for dialogue-driven cut decisions
  (e.g. "cut on the line where he says X").

## Phase 3 — Editorial primitives
- Transitions, basic color-correction FX presets, crossfade helpers.
- Audio ducking envelope helper (music bed drops under dialogue
  automatically based on detected speech regions).
- A `propose_edit` composite tool: given a brief + probed clips, the model
  can iterate — place events, inspect current timeline state, revise —
  without needing to hand-compute every timecode itself.

## Phase 4 — Render & delivery
- Render presets matching common delivery targets (vertical/short-form,
  16:9 1080p/4K), with real render-status polling (VEGAS renders can be
  long-running; the MCP tool must not block/timeout on a multi-minute job).
- End-to-end test: raw clips in → rendered file out, verified by checking
  the actual output file (duration, resolution) rather than trusting the
  render call's return code alone.

## Non-goals (for now)
- Full VEGAS UI parity — this is an editing/automation surface, not a
  general remote-desktop replacement.
- Multi-user/remote collaboration — single local VEGAS instance only.
- Any auth/security hardening beyond "don't expose the TCP port publicly" —
  this is a local automation tool, not a hosted service.
