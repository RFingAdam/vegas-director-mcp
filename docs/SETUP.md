# Setup (VEGAS Pro 22 on Windows)

Phase 1 only. You need a licensed VEGAS Pro 22 install. The MCP server
talks to a script that runs **inside** VEGAS over TCP `127.0.0.1:8752`.

Phase 2 (media probing, or the separate editorial-primitives PR) is not
in this tree. Do not expect `probe_media`, FX, or render tools.

## 1. Script host

No Visual Studio project. VEGAS compiles `VegasDirectorHost.cs` when you
run it from the Scripting menu.

1. Copy `host/VegasDirectorHost.cs` into a Script Menu folder:
   - `C:\Program Files\VEGAS\VEGAS Pro 22.0\Script Menu\` (often needs
     admin), or
   - A user-writable folder listed under
     *Options > Preferences > Folders > Script Menu*
2. Open **VEGAS Pro 22** and create or open a project. The host refuses
   most calls if no project is active (`ok: false`).
3. *Tools > Scripting > VegasDirectorHost*
   - If the item is missing, restart VEGAS so it rescans the Script Menu.
4. Leave the dialog open. Closing it stops the listener.
5. Confirm the dialog says `TCP: 127.0.0.1:8752`.
6. Logs: `%LOCALAPPDATA%\vegas-director-mcp\host.log`

The current host does **not** open `\\.\pipe\vegas-director`. If you
re-copy the `.cs` file after a git pull, close the old dialog and run
the script again.

## 2. MCP server (same Windows PC)

From a clone of this repo (`<clone>` is wherever you put it):

```bat
cd <clone>\server
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
set VEGAS_HOST_TRANSPORT=tcp
set VEGAS_HOST_ADDRESS=127.0.0.1
set VEGAS_HOST_PORT=8752
python -m vegas_director_mcp
```

`pip install -e .` makes `python -m vegas_director_mcp` work even when
the MCP client does not set a working directory. `requirements.txt`
matches `pyproject.toml` plus `pywin32` on Windows (only needed if you
force named-pipe transport, which the current host does not serve).

The process is stdio FastMCP. Point the MCP client at that command; do
not open a browser on port 8752 — that port is the **host**, not the
MCP server.

### Env vars

| Variable | Default | Role |
|---|---|---|
| `VEGAS_HOST_TRANSPORT` | `tcp` | `tcp` or `pipe` (pipe client exists; host does not listen) |
| `VEGAS_HOST_ADDRESS` | `127.0.0.1` | TCP host |
| `VEGAS_HOST_PORT` | `8752` | TCP port |
| `VEGAS_HOST_PIPE_NAME` | `vegas-director` | Unused unless transport is `pipe` |

### MCP client snippet

Cursor / Claude Desktop-style config. Use the venv interpreter and the
`server` directory as `cwd` (or rely on `pip install -e .`):

```json
{
  "mcpServers": {
    "vegas-director": {
      "command": "C:\\path\\to\\vegas-director-mcp\\server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "vegas_director_mcp"],
      "cwd": "C:\\path\\to\\vegas-director-mcp\\server",
      "env": {
        "VEGAS_HOST_TRANSPORT": "tcp",
        "VEGAS_HOST_ADDRESS": "127.0.0.1",
        "VEGAS_HOST_PORT": "8752"
      }
    }
  }
}
```

Replace `C:\\path\\to\\vegas-director-mcp` with your clone path.

## 3. Smoke test

With the host dialog still open:

```bat
cd <clone>\server
.venv\Scripts\activate
set VEGAS_HOST_TRANSPORT=tcp
python -c "from vegas_director_mcp.tools import ping, get_project_state; print(ping()); print(get_project_state())"
```

Success looks like `ok: true` plus `video_track_count` / `audio_track_count`
/ `tracks`. A connection error means the dialog is closed, VEGAS is not
running, or something else is bound to 8752.

`ffmpeg` is not part of this smoke test.

## 4. If the host is already running an old copy

1. Close the vegas-director-mcp MessageBox (that stops the listener).
2. Replace `VegasDirectorHost.cs` in the Script Menu folder.
3. *Tools > Scripting > VegasDirectorHost* again.
