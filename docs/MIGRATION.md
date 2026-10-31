# Migration to CutRelay MCP (from vegas-director-mcp / nle-mcp)

This public repo is an editor-agnostic MCP bridge, now named **CutRelay MCP**.
The Python project is **cutrelay-mcp**, the import package is **cutrelay**, and
the MCP server name is **"CutRelay MCP"**. The GitHub repository name is
unchanged for now.

## Package and entry points

| Old | New |
|---|---|
| Project name `vegas-director-mcp` / `nle-mcp` | `cutrelay-mcp` |
| `import vegas_director_mcp` / `import nle_mcp` | `import cutrelay` |
| `python -m vegas_director_mcp` / `python -m nle_mcp` | `python -m cutrelay` |
| Console script `vegas-director-mcp` / `nle-mcp` | `cutrelay-mcp` |
| FastMCP name `vegas-director-mcp` / `nle-mcp` | `CutRelay MCP` |
| `pip install 'vegas-director-mcp[whisper]'` | `pip install 'cutrelay-mcp[whisper]'` |
| `skills/nle-mcp/SKILL.md` | `skills/cutrelay/SKILL.md` |

Compatibility kept for one release (the Python aliases emit a
`DeprecationWarning` on import, on stderr):

- `import vegas_director_mcp` and `import nle_mcp` (re-export `cutrelay`,
  including submodules such as `vegas_director_mcp.tools`)
- `python -m vegas_director_mcp` and `python -m nle_mcp`
- console scripts `vegas-director-mcp` and `nle-mcp`
- every MCP tool name (unchanged)
- env `VEGAS_DIRECTOR_EDITOR` (same as `DIRECTOR_EDITOR`)
- `VEGAS_WHISPER_DEVICE` / `VEGAS_WHISPER_COMPUTE` (also `NLE_WHISPER_*`)

Not renamed (on-disk / wire compatibility with installed VEGAS hosts):

- VEGAS host token and log folder `%LOCALAPPDATA%\vegas-director-mcp\`
- `VegasDirector.dll`, `VegasDirectorHost.cs`, `VegasDirectorExtension.cs`,
  the *Vegas Director Host* view, and the `Vegas Director:` undo labels
- the `vegas-director` pipe name and the `"host": "vegas-director"` ping field

## MCP client config

The MCP server name is display-only; clients key servers on whatever label you
put in your config, so an existing `"vegas-director"` entry keeps working as-is.
After pulling, run `pip install -e .` in `server\.venv` once so the new
`cutrelay` package is registered. To switch, set `args` to `["-m", "cutrelay"]`
(and optionally rename the key to `"cutrelay"`), then restart Claude Desktop,
Grok, Cursor, or whichever client you use. `scripts/register_claude.py` writes
a `"cutrelay-mcp"` entry and leaves an existing `"vegas-director"` entry alone.

Default `DIRECTOR_EDITOR` is still `vegas` so existing VEGAS installs keep
working. Set `DIRECTOR_EDITOR=ffmpeg` for headless editing.

## Removed tools (stubs remain)

These tools still exist as named MCP stubs so old clients get a clear error
instead of a missing-tool failure. They no longer contain clip-selection
heuristics or Shorts recipes:

- `find_highlights`
- `apply_vertical_short`
- `propose_edit`

Use `probe_media`, `detect_scenes`, `analyze_audio`, `cut_media`,
`concat_media`, `reframe_media`, `generate_captions`, and the shared
timeline tools instead.

`generate_captions` default style is `default` (16:9). `vertical` is a
generic 9:16 layout. `shorts` is accepted as a deprecated alias of
`vertical`.

`analyze_audio` still returns windowed RMS/peak spikes. Spike `kind` values
are `peak` / `loud` / `rise` — not game-specific labels.

## History

Removing those files from `main` does not erase them from git history.
Past commits still contain the proprietary ranking, recipes, and brand
copy. The repository owner can decide later whether to rewrite history
or leave it.
