# Setup

## 1. Script host (Windows, inside VEGAS)

1. Copy `host/VegasDirectorHost.cs` into your VEGAS Application Data
   Scripts folder (or a subfolder under it) so it shows up under
   *Tools > Scripting* in VEGAS. The exact path depends on your VEGAS
   version — check *Options > Preferences > Folders* inside VEGAS, or
   VEGAS's own scripting docs, for the current Script Menu folder location.
2. In VEGAS: *Tools > Scripting > VegasDirectorHost*. This starts the local
   listener (named pipe by default) and keeps running until you stop it or
   close VEGAS. A console/log window shows connection activity.
3. (Optional, once stable) add it to VEGAS's Startup Scripts folder so it's
   always listening whenever VEGAS is open.

## 2. MCP server (any machine with network access to the host)

```bash
cd server
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env        # set VEGAS_HOST_ADDRESS if using TCP transport
python -m vegas_director_mcp
```

Point your MCP client (Claude Desktop, Claude Code, etc.) at the running
server per your client's normal MCP server configuration.

## 3. Verify the round-trip

Call the `get_project_state` tool with an empty VEGAS project open. You
should get back a real (if mostly empty) project state, not a connection
error. If this fails:

- Confirm the script host's log shows a listener started and (if applicable)
  an incoming connection.
- If using TCP across machines, confirm nothing between the two hosts is
  blocking the port (firewall, VLAN ACL).
- Confirm your VEGAS version's scripting runtime matches what the host was
  compiled against — see VEGAS's own scripting API docs for your version.
