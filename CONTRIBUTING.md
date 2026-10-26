# Contributing

Personal project, best-effort. Issues and PRs are welcome.

## Run a checkout

A stranger can run the host tools with [docs/SETUP.md](docs/SETUP.md):

1. Windows + VEGAS Pro 22
2. Prefer `host\build.ps1` (Application Extension auto-start), or copy
   `host/VegasDirectorHost.cs` into a Script Menu folder and run
   *Tools > Scripting > VegasDirectorHost*
3. `server/`: venv, `pip install -r requirements.txt`, `pip install -e .`,
   `python -m vegas_director_mcp`

Do not document or test `probe_media` / Whisper / `find_highlights` /
async render as if they shipped. Those are the next phase.

## Docs vs code

If you change a host method or MCP tool, update
[docs/API_COVERAGE.md](docs/API_COVERAGE.md) and
[docs/PROTOCOL.md](docs/PROTOCOL.md) in the same PR. Do not describe
planned work as implemented.

## Secrets

Never commit `%LOCALAPPDATA%\vegas-director-mcp\token`, user home paths,
or patch leftovers (`*.bak`, `*_dump.txt`, already-applied `patch_*.py`).

## Affiliation

This is not a MAGIX product. Keep the disclaimer in [NOTICE](NOTICE) and
the README. Do not imply endorsement.

## License

MIT. See [LICENSE](LICENSE).
