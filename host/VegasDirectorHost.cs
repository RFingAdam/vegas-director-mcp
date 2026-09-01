// VegasDirectorHost.cs
//
// VEGAS Pro script that starts a local JSON-RPC listener so an external
// process (the vegas-director-mcp Python MCP server) can drive the running
// VEGAS instance via its scripting API.
//
// Install: copy into your VEGAS Script Menu folder, then run via
// Tools > Scripting > VegasDirectorHost inside VEGAS.
//
// IMPORTANT: all ScriptPortal.Vegas API calls MUST happen on VEGAS's UI
// thread. The pipe listener runs on a background thread; every handler
// marshals back onto the UI thread via Vegas.Invoke(...) before touching
// any Vegas.* object. Skipping this is the #1 cause of native crashes when
// scripting VEGAS from an async/threaded context.

using System;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Threading;
using ScriptPortal.Vegas;

// Minimal hand-rolled JSON handling is used here deliberately: VEGAS's
// scripting host targets an older .NET Framework profile that may not have
// a modern JSON library available out of the box. Swap for
// System.Text.Json or Newtonsoft if your VEGAS scripting runtime supports
// it -- see docs/SETUP.md for how to check your version.

public class EntryPoint
{
    private const string PipeName = "vegas-director";
    private Vegas myVegas;
    private volatile bool running = true;

    public void FromVegas(Vegas vegas)
    {
        myVegas = vegas;
        Log("VegasDirectorHost starting, pipe name: " + PipeName);

        Thread listenerThread = new Thread(RunListener);
        listenerThread.IsBackground = true;
        listenerThread.Start();

        MessageBox.Show(
            "vegas-director-mcp host is running.\n\nPipe: \\\\.\\pipe\\" + PipeName +
            "\n\nLeave this script running while you want external control. " +
            "Closing this dialog stops the listener.",
            "vegas-director-mcp");

        running = false;
    }

    private void RunListener()
    {
        while (running)
        {
            try
            {
                using (NamedPipeServerStream pipe = new NamedPipeServerStream(
                    PipeName, PipeDirection.InOut, 1,
                    PipeTransmissionMode.Byte, PipeOptions.Asynchronous))
                {
                    pipe.WaitForConnection();
                    Log("Client connected.");
                    HandleConnection(pipe);
                }
            }
            catch (Exception ex)
            {
                Log("Listener error: " + ex.Message);
                Thread.Sleep(1000);
            }
        }
    }

    private void HandleConnection(NamedPipeServerStream pipe)
    {
        StreamReader reader = new StreamReader(pipe, Encoding.UTF8);
        StreamWriter writer = new StreamWriter(pipe, Encoding.UTF8);
        writer.AutoFlush = true;

        while (pipe.IsConnected)
        {
            string line = reader.ReadLine();
            if (line == null) break;

            string response = Dispatch(line);
            writer.WriteLine(response);
        }
    }

    // Dispatch is intentionally simple/explicit rather than reflection-based
    // -- keeps the RPC surface auditable and matches docs/PROTOCOL.md's
    // method table one-to-one as it grows.
    private string Dispatch(string requestJson)
    {
        RpcRequest req;
        try
        {
            req = RpcRequest.Parse(requestJson);
        }
        catch (Exception ex)
        {
            return RpcResponse.Error(null, -32700, "Parse error: " + ex.Message);
        }

        try
        {
            switch (req.Method)
            {
                case "project.get_state":
                    return InvokeOnUiThread(req, GetProjectState);

                // Additional methods land here as they're implemented --
                // see docs/API_COVERAGE.md for the full planned surface
                // (track.*, event.*, media.*, fx.*, envelope.*, render.*).
                // Each new case should follow the same InvokeOnUiThread
                // pattern -- never call myVegas.* directly from this
                // (background-thread) method body.

                default:
                    return RpcResponse.Error(req.Id, -32601,
                        "Method not found: " + req.Method);
            }
        }
        catch (Exception ex)
        {
            return RpcResponse.Error(req.Id, -32603, "Internal error: " + ex.Message);
        }
    }

    private string InvokeOnUiThread(RpcRequest req, Func<RpcRequest, string> handler)
    {
        string result = null;
        Exception thrown = null;

        myVegas.Invoke(new MethodInvoker(delegate
        {
            try { result = handler(req); }
            catch (Exception ex) { thrown = ex; }
        }));

        if (thrown != null)
            return RpcResponse.Error(req.Id, -32603, thrown.Message);
        return result;
    }

    // --- Handlers (run on UI thread) ---

    private string GetProjectState(RpcRequest req)
    {
        Project project = myVegas.Project;
        if (project == null)
            return RpcResponse.Error(req.Id, -32001, "No active VEGAS project");

        int videoTracks = 0, audioTracks = 0;
        foreach (Track t in project.Tracks)
        {
            if (t.IsVideo()) videoTracks++;
            if (t.IsAudio()) audioTracks++;
        }

        StringBuilder sb = new StringBuilder();
        sb.Append("{\"length_ticks\":").Append(project.Length.ToString())
          .Append(",\"video_track_count\":").Append(videoTracks)
          .Append(",\"audio_track_count\":").Append(audioTracks)
          .Append("}");

        return RpcResponse.Result(req.Id, sb.ToString());
    }

    private void Log(string msg)
    {
        // Swap for a real log file under docs/SETUP.md guidance if the
        // MessageBox-per-line approach proves too noisy during development.
        Console.WriteLine("[vegas-director-mcp] " + msg);
    }
}

// --- Minimal RPC plumbing ---

public class RpcRequest
{
    public string Id;
    public string Method;
    public string ParamsJson;

    public static RpcRequest Parse(string json)
    {
        // Deliberately minimal parser for the fixed shape we emit from the
        // Python side: {"jsonrpc":"2.0","id":N,"method":"...","params":{...}}
        // Replace with a real JSON library once the target .NET profile is
        // confirmed (see file header comment).
        RpcRequest r = new RpcRequest();
        r.Id = ExtractField(json, "id");
        r.Method = ExtractStringField(json, "method");
        r.ParamsJson = ExtractObjectField(json, "params");
        if (r.Method == null)
            throw new Exception("Missing 'method' field");
        return r;
    }

    private static string ExtractField(string json, string key)
    {
        string marker = "\"" + key + "\":";
        int i = json.IndexOf(marker);
        if (i < 0) return null;
        i += marker.Length;
        int j = i;
        while (j < json.Length && json[j] != ',' && json[j] != '}') j++;
        return json.Substring(i, j - i).Trim();
    }

    private static string ExtractStringField(string json, string key)
    {
        string raw = ExtractField(json, key);
        if (raw == null) return null;
        return raw.Trim('"');
    }

    private static string ExtractObjectField(string json, string key)
    {
        string marker = "\"" + key + "\":";
        int i = json.IndexOf(marker);
        if (i < 0) return "{}";
        i += marker.Length;
        return json.Substring(i).Trim();
    }
}

public static class RpcResponse
{
    public static string Result(string id, string resultJson)
    {
        return "{\"jsonrpc\":\"2.0\",\"id\":" + (id ?? "null") +
               ",\"result\":" + resultJson + "}";
    }

    public static string Error(string id, int code, string message)
    {
        return "{\"jsonrpc\":\"2.0\",\"id\":" + (id ?? "null") +
               ",\"error\":{\"code\":" + code + ",\"message\":\"" +
               message.Replace("\"", "'") + "\"}}";
    }
}
