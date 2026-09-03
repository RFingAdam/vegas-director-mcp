# Contributing

Personal project, best-effort. Issues and PRs are welcome.

## Run a checkout

A stranger can run **Phase 1** with [docs/SETUP.md](docs/SETUP.md):

1. Windows + VEGAS Pro 22
2. `host/VegasDirectorHost.cs` in a Script Menu folder
3. *Tools > Scripting > VegasDirectorHost*, leave the dialog open
4. `server/`: venv, `pip install -r requirements.txt`, `pip install -e .`,
   `python -m vegas_director_mcp`

Phase 2 is not on `main`. Do not document or test probe/FX/render tools
as if they shipped.

## Docs vs code

If you change a host method or MCP tool, update
[docs/API_COVERAGE.md](docs/API_COVERAGE.md) and
[docs/PROTOCOL.md](docs/PROTOCOL.md) in the same PR. Do not describe
planned work as implemented.

## Affiliation

This is not a MAGIX product. Keep the disclaimer in [NOTICE](NOTICE) and
the README. Do not imply endorsement.

## License

MIT. See [LICENSE](LICENSE).
