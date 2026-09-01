# Setup (VEGAS Pro 22 on Windows)

## 1. Script host

1. Copy `host/VegasDirectorHost.cs` into a VEGAS Script Menu folder:
   - `C:\Program Files\VEGAS\VEGAS Pro 22.0\Script Menu\` (may need admin), or
   - A folder listed under *Options > Preferences > Folders > Script Menu*
2. Open **VEGAS Pro 22**, create/open a project.
3. *Tools > Scripting > VegasDirectorHost*
4. Leave the dialog open. It listens on:
   - Named pipe `\\.\pipe\vegas-director`
   - TCP `127.0.0.1:8752`
5. Logs: `%LOCALAPPDATA%\vegas-director-mcp\host.log`

## 2. MCP server (same Windows PC)

```bat
cd C:\src\vegas-director-mcp\server
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set VEGAS_HOST_TRANSPORT=tcp
python -m vegas_director_mcp
```

Point your MCP client at that process (stdio FastMCP).

## 3. Smoke test

With the host dialog open:

```bat
cd C:\src\vegas-director-mcp\server
.venv\Scripts\activate
set VEGAS_HOST_TRANSPORT=tcp
python -c "from vegas_director_mcp.tools import ping, get_project_state; print(ping()); print(get_project_state())"
```

You should see `ok: true` and track counts, not a connection error.
