# Migration from vegas-director-mcp

This public repo is now an editor-agnostic MCP bridge. The Python package
and MCP server name are **nle-mcp**. The GitHub repository name is unchanged.

## Package and entry points

| Old | New |
|---|---|
| PyPI / project name `vegas-director-mcp` | `nle-mcp` |
| `import vegas_director_mcp` | `import nle_mcp` |
| `python -m vegas_director_mcp` | `python -m nle_mcp` |
| FastMCP name `vegas-director-mcp` | `nle-mcp` |
| `pip install 'vegas-director-mcp[whisper]'` | `pip install 'nle-mcp[whisper]'` |

Cheap aliases that still work:

- `import vegas_director_mcp` (re-exports `nle_mcp`, including submodules)
- `python -m vegas_director_mcp`
- console script `vegas-director-mcp`
- env `VEGAS_DIRECTOR_EDITOR` (same as `DIRECTOR_EDITOR`)
- `VEGAS_WHISPER_DEVICE` / `VEGAS_WHISPER_COMPUTE` (also `NLE_WHISPER_*`)
- MCP tool names for timeline, analysis, and render helpers
- VEGAS host token path `%LOCALAPPDATA%\vegas-director-mcp\token` (the C# host still writes there)

Claude Desktop / Cursor config: change `"vegas-director"` to `"nle-mcp"` and
`args` to `["-m", "nle_mcp"]` when you are ready. The old `-m vegas_director_mcp`
still launches the server.

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
