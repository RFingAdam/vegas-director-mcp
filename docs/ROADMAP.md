# Roadmap

## Phase 0 — Scaffold (this commit)
- Repo structure, protocol spec, license, gitignore.
- Skeleton script host (compiles, opens a pipe, handles `project.get_state`
  as a real round-trip proof).
- Skeleton MCP server (FastMCP, one working tool: `get_project_state`).

## Phase 1 — First real round-trip
- Confirm the C# host actually loads in a real VEGAS install (Tools >
  Scripting) and responds over the pipe from a real running instance.
- Wire `project.get_state`, `track.add`, `event.add_video`/`add_audio`,
  `media.import`, `render.start` end-to-end against a real project.
- MCP server: matching tools, with real error surfacing (no swallowed
  exceptions — a VEGAS-side error must reach the model as a tool error, not
  a silent no-op).

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
