# Other editors — survey and next backend

`vegas-director-mcp` now has an editor adapter. MCP tool names stay the same.
`DIRECTOR_EDITOR` selects the backend:

| Value | What | License of the *editor* | Live? |
|---|---|---|---|
| `vegas` (default) | MAGIX VEGAS Pro 22 C# host, TCP `127.0.0.1:8752` | VEGAS Pro license | Yes |
| `resolve` | DaVinci Resolve **Studio** via `DaVinciResolveScript` | Studio ($295 perpetual) | Yes |
| `otio` (aliases: `fcpxml`, `mlt`, `kdenlive`, `shotcut`) | In-memory timeline; `project.save` writes `.otio` / `.fcpxml` / `.mlt` | None | No |

VEGAS behaviour is unchanged when `DIRECTOR_EDITOR` is unset.

## Resolve (implemented) — Studio only

See [RESOLVE.md](RESOLVE.md) for setup, mapping, and Adam's Windows checklist.

**Free Resolve cannot run this backend.** Blackmagic's 21.1 feature sheet
lists `Scripting API: Studio`. In 21.1 they removed Python scripting from
the free edition (it was being used to unlock Studio features). External
`scriptapp("Resolve")` already required Studio before that.

Required for live control:

- Resolve **Studio 21.1+**
- Preferences → System → General → **External scripting = Local**

Studio-only extras even on Studio: `CreateSubtitlesFromAudio`,
`SmartReframe`, `SetVoiceIsolationState`.

If Adam (or a viewer) only has free Resolve, use `DIRECTOR_EDITOR=otio`
and import the file — that is the adoption path that does not ask them
to buy Studio on day one.

## Why a second, free-friendly backend shipped in this PR

Live Resolve is the right *quality* target (real timeline, real render,
official API) but a poor *funnel*: every free-Resolve user would bounce.
An OTIO / FCPXML / MLT export path is cheap (no NLE, no extra pip
dependency, JSON/XML we already know how to write) and lets:

- free Resolve import `.otio` or `.fcpxml` (`ImportTimelineFromFile`)
- Shotcut / Kdenlive / `melt` open `.mlt`
- Premiere / FCP adapters consume OTIO later

That is implemented as `OtioBackend`. It is not a live editor — no play,
no Resolve-quality render — but `apply_crossfade` / place / trim / markers
work, and `project.save` is the handoff.

## Survey of the rest

### Premiere Pro (UXP + leftover ExtendScript)

- **Surface:** UXP `require("premierepro")` (Premiere 25.6+). CEP/ExtendScript
  is in a one-year sunset. Sequence edits go through
  `project.executeTransaction` / `SequenceEditor`.
- **Shape:** same as our VEGAS host — an in-app plugin talking to the MCP
  server. There is no official external Python attach.
- **Cost:** a UXP panel (TypeScript) + a thin TCP or stdio bridge. Weeks of
  work, Adobe developer account, installer.
- **Adoption:** largest remaining NLE audience after Resolve.
- **Rank for a *live* backend:** #1 after Resolve — but it is **not** cheap.

### Final Cut Pro (FCPXML, almost no Apple Events)

- **Surface:** FCPXML import/export is the automation API. Apple Events can
  open a library and little else. No supported timeline mutation API.
- **Cost of a live backend:** high / impossible. Cost of an export path:
  already covered (`DIRECTOR_EDITOR=otio` → `.fcpxml`).
- **Adoption:** large on Mac, zero on Adam's Windows streaming box.
- **Rank:** export-only; do not build a live FCP backend.

### Shotcut and Kdenlive (MLT XML)

- **Surface:** both are MLT. Projects are XML. `melt` renders headless.
  Shotcut has a weak CLI; Kdenlive has `kdenlive_render`.
- **Cost:** the `.mlt` writer is already in `OtioBackend`. A *live* backend
  would be D-Bus / CLI wrangling for little extra.
- **Adoption:** real in Linux/FOSS circles, small versus Premiere/Resolve.
- **Rank:** keep the file export; do not invest in a live Shotcut backend yet.

### CapCut

- **Surface:** no public automation API. Desktop drafts are undocumented
  JSON that changes with every app update. Cloud/CapCutAPI is a different
  product with ToS risk.
- **Rank:** skip. Do not reverse-engineer drafts.

### OpenTimelineIO as interchange (implemented)

- Adapters exist or are emerging for Resolve, Premiere, FCP, Flame.
- We write OTIO 1.x JSON plus a `metadata.director` blob so we can re-open
  our own files. No `opentimelineio` pip dependency.
- Resolve (including **free**) can import OTIO / FCPXML via
  `MediaPool.ImportTimelineFromFile`.

## Ranked recommendation — what to build next

1. **Already done, free-friendly:** OTIO + FCPXML + MLT export (`otio`
   backend). Use this whenever Studio is not available. Best adoption
   increment per line of code.
2. **Next live editor, if the goal is users:** **Premiere Pro UXP host**
   (in-app plugin + the same adapter). Biggest remaining audience. Same
   architecture as VEGAS, so the Python side stays thin. Not cheap.
3. **Next cheap increment:** none that beat #1. Deepening the OTIO writer
   (audio tracks in FCPXML, fade metadata → MLT filters) is more valuable
   than a half-live Shotcut process.
4. **Do not do:** CapCut drafts, a fake "live" FCP via GUI scripting, or
   anything that needs Studio-only Resolve features to be the default path.

### Overlap with open PR #6

PR #6 (extension `UndoBlock`, OneDrive Documents, render-template cap) is
VEGAS-host-only. This work does **not** touch `host/*.cs`, `host/build.ps1`,
`windows_paths.py`, `host_launch.py`, or `render/presets.py`. The only
shared files are README / docs / `tools.py` (`_call` + new tools at the
bottom) / `__init__.py` (new tools). `list_render_templates` /
`render_with_preset` are left as on main so #6 can merge cleanly.
