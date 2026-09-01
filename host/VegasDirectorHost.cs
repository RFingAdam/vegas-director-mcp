// VegasDirectorHost.cs — VEGAS Pro 22 TCP host (no Pipes; WinForms marshal; soft ok:false errors)
// Tools > Scripting > VegasDirectorHost — leave dialog open.

using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    private const int TcpPort = 8752;
    private Vegas myVegas;
    private volatile bool running = true;
    private Control uiMarshal;

    public void FromVegas(Vegas vegas)
    {
        myVegas = vegas;

        // Vegas has no Invoke. A WinForms control created on this (UI) thread
        // is how we marshal ScriptPortal calls back from the TCP listener.
        Form marshalForm = new Form();
        marshalForm.ShowInTaskbar = false;
        marshalForm.FormBorderStyle = FormBorderStyle.FixedToolWindow;
        marshalForm.Opacity = 0;
        marshalForm.Size = new System.Drawing.Size(0, 0);
        marshalForm.Show();
        uiMarshal = marshalForm;

        Log("VegasDirectorHost starting tcp=127.0.0.1:" + TcpPort);

        Thread tcpThread = new Thread(RunTcpListener);
        tcpThread.IsBackground = true;
        tcpThread.Start();

        MessageBox.Show(
            "vegas-director-mcp host is running.\n\n" +
            "TCP: 127.0.0.1:" + TcpPort + "\n\n" +
            "Leave this dialog open while you want external control.\n" +
            "Closing it stops the listener.",
            "vegas-director-mcp");

        running = false;
        try { marshalForm.Close(); } catch { }
    }

    private void RunTcpListener()
    {
        TcpListener listener = null;
        try
        {
            listener = new TcpListener(IPAddress.Loopback, TcpPort);
            listener.Start();
            Log("TCP listening on 127.0.0.1:" + TcpPort);
            while (running)
            {
                if (!listener.Pending())
                {
                    Thread.Sleep(50);
                    continue;
                }
                using (TcpClient client = listener.AcceptTcpClient())
                using (NetworkStream stream = client.GetStream())
                {
                    Log("TCP client connected.");
                    HandleStream(stream);
                }
            }
        }
        catch (Exception ex)
        {
            Log("TCP listener error: " + ex.Message);
        }
        finally
        {
            if (listener != null) listener.Stop();
        }
    }

    private void HandleStream(Stream stream)
    {
        StreamReader reader = new StreamReader(stream, Encoding.UTF8);
        StreamWriter writer = new StreamWriter(stream, Encoding.UTF8);
        writer.AutoFlush = true;
        while (true)
        {
            string line;
            try { line = reader.ReadLine(); }
            catch { break; }
            if (line == null) break;
            if (line.Trim().Length == 0) continue;
            string response = Dispatch(line);
            try { writer.WriteLine(response); }
            catch { break; }
        }
    }

    private string Dispatch(string requestJson)
    {
        RpcRequest req;
        try { req = RpcRequest.Parse(requestJson); }
        catch (Exception ex)
        {
            return RpcResponse.Error(null, -32700, "Parse error: " + ex.Message);
        }

        try
        {
            switch (req.Method)
            {
                case "ping":
                    return RpcResponse.Result(req.Id, "{\"ok\":true,\"host\":\"vegas-director\"}");
                case "project.get_state":
                    return InvokeOnUiThread(req, GetProjectState);
                case "project.save":
                    return InvokeOnUiThread(req, SaveProject);
                case "track.add":
                    return InvokeOnUiThread(req, AddTrack);
                case "media.import":
                    return InvokeOnUiThread(req, ImportMedia);
                case "media.place":
                    return InvokeOnUiThread(req, PlaceMedia);
                case "event.add_video":
                    return InvokeOnUiThread(req, AddVideoEvent);
                case "event.add_audio":
                    return InvokeOnUiThread(req, AddAudioEvent);
                case "event.trim":
                    return InvokeOnUiThread(req, TrimEvent);
                case "event.move":
                    return InvokeOnUiThread(req, MoveEvent);
                case "event.delete":
                    return InvokeOnUiThread(req, DeleteEvent);
                case "transport.play":
                    return InvokeOnUiThread(req, TransportPlay);
                case "transport.stop":
                    return InvokeOnUiThread(req, TransportStop);
                case "transport.seek":
                    return InvokeOnUiThread(req, TransportSeek);
                default:
                    return RpcResponse.Error(req.Id, -32601, "Method not found: " + req.Method);
            }
        }
        catch (Exception ex)
        {
            return SoftFail(req.Id, "Internal error: " + ex.Message);
        }
    }

    private string InvokeOnUiThread(RpcRequest req, Func<RpcRequest, string> handler)
    {
        if (uiMarshal == null || uiMarshal.IsDisposed)
            return SoftFail(req.Id, "UI marshal unavailable");

        string result = null;
        Exception thrown = null;
        ManualResetEvent done = new ManualResetEvent(false);

        uiMarshal.BeginInvoke((MethodInvoker)delegate
        {
            try { result = handler(req); }
            catch (Exception ex) { thrown = ex; }
            finally { done.Set(); }
        });

        if (!done.WaitOne(60000))
            return SoftFail(req.Id, "UI marshal timed out");
        if (thrown != null)
            return SoftFail(req.Id, thrown.Message);
        return result;
    }

    private static string SoftFail(string id, string error)
    {
        return RpcResponse.Result(id, "{\"ok\":false,\"error\":" + Json.Str(error) + "}");
    }

    private Project RequireProject()
    {
        Project project = myVegas.Project;
        if (project == null)
            throw new Exception("No active VEGAS project");
        return project;
    }

    private static double TimecodeToSeconds(Timecode tc)
    {
        return tc.ToMilliseconds() / 1000.0;
    }

    private static Timecode SecondsToTimecode(double seconds)
    {
        return Timecode.FromSeconds(seconds);
    }

    private string GetProjectState(RpcRequest req)
    {
        Project project = RequireProject();
        StringBuilder tracks = new StringBuilder();
        tracks.Append("[");
        int videoTracks = 0, audioTracks = 0;
        bool first = true;
        for (int i = 0; i < project.Tracks.Count; i++)
        {
            Track t = project.Tracks[i];
            string kind = t.IsVideo() ? "video" : (t.IsAudio() ? "audio" : "other");
            if (t.IsVideo()) videoTracks++;
            if (t.IsAudio()) audioTracks++;
            if (!first) tracks.Append(",");
            first = false;
            tracks.Append("{\"index\":").Append(i)
                  .Append(",\"name\":").Append(Json.Str(t.Name))
                  .Append(",\"type\":").Append(Json.Str(kind))
                  .Append(",\"event_count\":").Append(t.Events.Count)
                  .Append("}");
        }
        tracks.Append("]");

        StringBuilder events = new StringBuilder();
        events.Append("[");
        first = true;
        for (int ti = 0; ti < project.Tracks.Count; ti++)
        {
            Track t = project.Tracks[ti];
            for (int ei = 0; ei < t.Events.Count; ei++)
            {
                TrackEvent ev = t.Events[ei];
                if (!first) events.Append(",");
                first = false;
                events.Append("{\"track_index\":").Append(ti)
                      .Append(",\"event_index\":").Append(ei)
                      .Append(",\"start_seconds\":").Append(Json.Num(TimecodeToSeconds(ev.Start)))
                      .Append(",\"length_seconds\":").Append(Json.Num(TimecodeToSeconds(ev.Length)))
                      .Append("}");
            }
        }
        events.Append("]");

        StringBuilder sb = new StringBuilder();
        sb.Append("{\"ok\":true")
          .Append(",\"length_seconds\":").Append(Json.Num(TimecodeToSeconds(project.Length)))
          .Append(",\"video_track_count\":").Append(videoTracks)
          .Append(",\"audio_track_count\":").Append(audioTracks)
          .Append(",\"tracks\":").Append(tracks)
          .Append(",\"events\":").Append(events)
          .Append("}");
        return RpcResponse.Result(req.Id, sb.ToString());
    }

    private string SaveProject(RpcRequest req)
    {
        string path = Json.GetString(req.ParamsJson, "path");
        if (path != null && path.Length > 0)
            myVegas.SaveProject(path);
        else
            myVegas.SaveProject();
        return RpcResponse.Result(req.Id, "{\"ok\":true}");
    }

    private string AddTrack(RpcRequest req)
    {
        Project project = RequireProject();
        string type = (Json.GetString(req.ParamsJson, "type") ?? "video").ToLowerInvariant();
        string name = Json.GetString(req.ParamsJson, "name") ?? "";
        int index = project.Tracks.Count;
        if (type == "audio")
            project.Tracks.Add(new AudioTrack(project, index, name));
        else
            project.Tracks.Add(new VideoTrack(project, index, name));
        return RpcResponse.Result(req.Id,
            "{\"ok\":true,\"track_index\":" + index + ",\"type\":" + Json.Str(type) + "}");
    }

    private string ImportMedia(RpcRequest req)
    {
        Project project = RequireProject();
        string path = Json.GetString(req.ParamsJson, "path");
        if (path == null || path.Length == 0)
            return SoftFail(req.Id, "params.path required");
        if (!File.Exists(path))
            return SoftFail(req.Id, "Media file not found: " + path);

        Media media;
        try { media = project.MediaPool.AddMedia(path); }
        catch (Exception ex) { return SoftFail(req.Id, "Import failed: " + ex.Message); }
        bool hasVideo = false;
        bool hasAudio = false;
        try { hasVideo = media.HasVideo(); } catch { }
        try { hasAudio = media.HasAudio(); } catch { }
        double len = TimecodeToSeconds(media.Length);

        StringBuilder sb = new StringBuilder();
        sb.Append("{\"ok\":true")
          .Append(",\"path\":").Append(Json.Str(path))
          .Append(",\"length_seconds\":").Append(Json.Num(len))
          .Append(",\"has_video\":").Append(hasVideo ? "true" : "false")
          .Append(",\"has_audio\":").Append(hasAudio ? "true" : "false")
          .Append("}");
        return RpcResponse.Result(req.Id, sb.ToString());
    }

    private Media FindMediaByPath(Project project, string path)
    {
        string full = Path.GetFullPath(path);
        foreach (Media m in project.MediaPool)
        {
            try
            {
                if (m.FilePath != null &&
                    string.Equals(Path.GetFullPath(m.FilePath), full, StringComparison.OrdinalIgnoreCase))
                    return m;
            }
            catch { }
        }
        return null;
    }

    private Media EnsureMedia(Project project, string path)
    {
        Media media = FindMediaByPath(project, path);
        if (media != null) return media;
        if (!File.Exists(path))
            throw new Exception("Media file not found: " + path);
        return project.MediaPool.AddMedia(path);
    }

    private string PlaceEventResult(string id, int trackIndex, int eventIndex, double start, double length, string kind)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append("{\"ok\":true")
          .Append(",\"track_index\":").Append(trackIndex)
          .Append(",\"event_index\":").Append(eventIndex)
          .Append(",\"start_seconds\":").Append(Json.Num(start))
          .Append(",\"length_seconds\":").Append(Json.Num(length))
          .Append(",\"media_kind\":").Append(Json.Str(kind))
          .Append("}");
        return RpcResponse.Result(id, sb.ToString());
    }

    private string PlaceMedia(RpcRequest req)
    {
        Project project = RequireProject();
        string path = Json.GetString(req.ParamsJson, "path");
        if (path == null || path.Length == 0)
            path = Json.GetString(req.ParamsJson, "media_path");
        if (path == null || path.Length == 0)
            return SoftFail(req.Id, "params.path or params.media_path required");

        int trackIndex = Json.GetInt(req.ParamsJson, "track_index", -1);
        double start = Json.GetDouble(req.ParamsJson, "start_seconds", 0);
        double length = Json.GetDouble(req.ParamsJson, "length_seconds", -1);
        if (trackIndex < 0 || trackIndex >= project.Tracks.Count)
            return SoftFail(req.Id, "Invalid track_index");

        Track track = project.Tracks[trackIndex];
        Media media;
        try { media = EnsureMedia(project, path); }
        catch (Exception ex) { return SoftFail(req.Id, ex.Message); }

        if (length < 0)
            length = TimecodeToSeconds(media.Length);

        try
        {
            if (track.IsVideo())
            {
                VideoTrack vtrack = (VideoTrack)track;
                VideoEvent ve = vtrack.AddVideoEvent(SecondsToTimecode(start), SecondsToTimecode(length));
                MediaStream stream = media.Streams.GetItemByMediaType(MediaType.Video, 0);
                if (stream == null)
                    return SoftFail(req.Id, "Media has no video stream: " + path);
                ve.AddTake(stream);
                return PlaceEventResult(req.Id, trackIndex, vtrack.Events.Count - 1, start, length, "video");
            }
            if (track.IsAudio())
            {
                AudioTrack atrack = (AudioTrack)track;
                AudioEvent ae = atrack.AddAudioEvent(SecondsToTimecode(start), SecondsToTimecode(length));
                MediaStream stream = media.Streams.GetItemByMediaType(MediaType.Audio, 0);
                if (stream == null)
                    return SoftFail(req.Id, "Media has no audio stream: " + path);
                ae.AddTake(stream);
                return PlaceEventResult(req.Id, trackIndex, atrack.Events.Count - 1, start, length, "audio");
            }
            return SoftFail(req.Id, "Track is neither video nor audio");
        }
        catch (Exception ex)
        {
            return SoftFail(req.Id, "Place failed: " + ex.Message);
        }
    }

    private string AddVideoEvent(RpcRequest req)
    {
        Project project = RequireProject();
        int trackIndex = Json.GetInt(req.ParamsJson, "track_index", 0);
        double start = Json.GetDouble(req.ParamsJson, "start_seconds", 0);
        double length = Json.GetDouble(req.ParamsJson, "length_seconds", -1);
        string path = Json.GetString(req.ParamsJson, "media_path");
        if (path == null || path.Length == 0)
            path = Json.GetString(req.ParamsJson, "path");
        if (path == null || path.Length == 0)
            return SoftFail(req.Id, "params.media_path required");
        if (trackIndex < 0 || trackIndex >= project.Tracks.Count || !project.Tracks[trackIndex].IsVideo())
            return SoftFail(req.Id, "Invalid video track_index");

        Media media;
        try { media = EnsureMedia(project, path); }
        catch (Exception ex) { return SoftFail(req.Id, ex.Message); }
        if (length < 0)
            length = TimecodeToSeconds(media.Length);

        try
        {
            VideoTrack vtrack = (VideoTrack)project.Tracks[trackIndex];
            VideoEvent ve = vtrack.AddVideoEvent(SecondsToTimecode(start), SecondsToTimecode(length));
            MediaStream stream = media.Streams.GetItemByMediaType(MediaType.Video, 0);
            if (stream == null)
                return SoftFail(req.Id, "Media has no video stream: " + path);
            ve.AddTake(stream);
            return PlaceEventResult(req.Id, trackIndex, vtrack.Events.Count - 1, start, length, "video");
        }
        catch (Exception ex)
        {
            return SoftFail(req.Id, "Add video failed: " + ex.Message);
        }
    }

    private string AddAudioEvent(RpcRequest req)
    {
        Project project = RequireProject();
        int trackIndex = Json.GetInt(req.ParamsJson, "track_index", 0);
        double start = Json.GetDouble(req.ParamsJson, "start_seconds", 0);
        double length = Json.GetDouble(req.ParamsJson, "length_seconds", -1);
        string path = Json.GetString(req.ParamsJson, "media_path");
        if (path == null || path.Length == 0)
            path = Json.GetString(req.ParamsJson, "path");
        if (path == null || path.Length == 0)
            return SoftFail(req.Id, "params.media_path required");
        if (trackIndex < 0 || trackIndex >= project.Tracks.Count || !project.Tracks[trackIndex].IsAudio())
            return SoftFail(req.Id, "Invalid audio track_index");

        Media media;
        try { media = EnsureMedia(project, path); }
        catch (Exception ex) { return SoftFail(req.Id, ex.Message); }
        if (length < 0)
            length = TimecodeToSeconds(media.Length);

        try
        {
            AudioTrack atrack = (AudioTrack)project.Tracks[trackIndex];
            AudioEvent ae = atrack.AddAudioEvent(SecondsToTimecode(start), SecondsToTimecode(length));
            MediaStream stream = media.Streams.GetItemByMediaType(MediaType.Audio, 0);
            if (stream == null)
                return SoftFail(req.Id, "Media has no audio stream: " + path);
            ae.AddTake(stream);
            return PlaceEventResult(req.Id, trackIndex, atrack.Events.Count - 1, start, length, "audio");
        }
        catch (Exception ex)
        {
            return SoftFail(req.Id, "Add audio failed: " + ex.Message);
        }
    }

    private TrackEvent GetEvent(Project project, int trackIndex, int eventIndex)
    {
        if (trackIndex < 0 || trackIndex >= project.Tracks.Count)
            throw new Exception("Invalid track_index");
        Track t = project.Tracks[trackIndex];
        if (eventIndex < 0 || eventIndex >= t.Events.Count)
            throw new Exception("Invalid event_index");
        return t.Events[eventIndex];
    }

    private string TrimEvent(RpcRequest req)
    {
        Project project = RequireProject();
        int trackIndex = Json.GetInt(req.ParamsJson, "track_index", -1);
        int eventIndex = Json.GetInt(req.ParamsJson, "event_index", -1);
        double start = Json.GetDouble(req.ParamsJson, "start_seconds", double.NaN);
        double length = Json.GetDouble(req.ParamsJson, "length_seconds", double.NaN);
        TrackEvent ev;
        try { ev = GetEvent(project, trackIndex, eventIndex); }
        catch (Exception ex) { return SoftFail(req.Id, ex.Message); }
        try
        {
            if (!double.IsNaN(start))
                ev.Start = SecondsToTimecode(start);
            if (!double.IsNaN(length))
                ev.Length = SecondsToTimecode(length);
        }
        catch (Exception ex)
        {
            return SoftFail(req.Id, "Trim failed: " + ex.Message);
        }
        return RpcResponse.Result(req.Id,
            "{\"ok\":true,\"start_seconds\":" + Json.Num(TimecodeToSeconds(ev.Start)) +
            ",\"length_seconds\":" + Json.Num(TimecodeToSeconds(ev.Length)) + "}");
    }

    private string MoveEvent(RpcRequest req)
    {
        Project project = RequireProject();
        int trackIndex = Json.GetInt(req.ParamsJson, "track_index", -1);
        int eventIndex = Json.GetInt(req.ParamsJson, "event_index", -1);
        double start = Json.GetDouble(req.ParamsJson, "start_seconds", 0);
        TrackEvent ev;
        try { ev = GetEvent(project, trackIndex, eventIndex); }
        catch (Exception ex) { return SoftFail(req.Id, ex.Message); }
        try { ev.Start = SecondsToTimecode(start); }
        catch (Exception ex) { return SoftFail(req.Id, "Move failed: " + ex.Message); }
        return RpcResponse.Result(req.Id,
            "{\"ok\":true,\"start_seconds\":" + Json.Num(TimecodeToSeconds(ev.Start)) + "}");
    }

    private string DeleteEvent(RpcRequest req)
    {
        Project project = RequireProject();
        int trackIndex = Json.GetInt(req.ParamsJson, "track_index", -1);
        int eventIndex = Json.GetInt(req.ParamsJson, "event_index", -1);
        TrackEvent ev;
        try { ev = GetEvent(project, trackIndex, eventIndex); }
        catch (Exception ex) { return SoftFail(req.Id, ex.Message); }
        try { ev.Track.Events.Remove(ev); }
        catch (Exception ex) { return SoftFail(req.Id, "Delete failed: " + ex.Message); }
        return RpcResponse.Result(req.Id, "{\"ok\":true}");
    }

    private string TransportPlay(RpcRequest req)
    {
        myVegas.Transport.Play();
        return RpcResponse.Result(req.Id, "{\"ok\":true}");
    }

    private string TransportStop(RpcRequest req)
    {
        myVegas.Transport.Stop();
        return RpcResponse.Result(req.Id, "{\"ok\":true}");
    }

    private string TransportSeek(RpcRequest req)
    {
        double seconds = Json.GetDouble(req.ParamsJson, "seconds", 0);
        myVegas.Transport.CursorPosition = SecondsToTimecode(seconds);
        return RpcResponse.Result(req.Id, "{\"ok\":true,\"seconds\":" + Json.Num(seconds) + "}");
    }

    private void Log(string msg)
    {
        try
        {
            string dir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "vegas-director-mcp");
            Directory.CreateDirectory(dir);
            File.AppendAllText(Path.Combine(dir, "host.log"),
                DateTime.Now.ToString("s") + " " + msg + Environment.NewLine);
        }
        catch { }
    }
}

public class RpcRequest
{
    public string Id;
    public string Method;
    public string ParamsJson;

    public static RpcRequest Parse(string json)
    {
        RpcRequest r = new RpcRequest();
        r.Id = Json.GetRaw(json, "id");
        r.Method = Json.GetString(json, "method");
        r.ParamsJson = Json.GetObject(json, "params") ?? "{}";
        if (r.Method == null || r.Method.Length == 0)
            throw new Exception("Missing method");
        return r;
    }
}

public static class RpcResponse
{
    public static string Result(string id, string resultJson)
    {
        return "{\"jsonrpc\":\"2.0\",\"id\":" + (id ?? "null") + ",\"result\":" + resultJson + "}";
    }

    public static string Error(string id, int code, string message)
    {
        return "{\"jsonrpc\":\"2.0\",\"id\":" + (id ?? "null") +
               ",\"error\":{\"code\":" + code + ",\"message\":" + Json.Str(message) + "}}";
    }
}

public static class Json
{
    public static string Str(string s)
    {
        if (s == null) return "null";
        StringBuilder sb = new StringBuilder();
        sb.Append('"');
        foreach (char c in s)
        {
            if (c == '"' || c == '\\') sb.Append('\\').Append(c);
            else if (c == '\n') sb.Append("\\n");
            else if (c == '\r') sb.Append("\\r");
            else if (c == '\t') sb.Append("\\t");
            else sb.Append(c);
        }
        sb.Append('"');
        return sb.ToString();
    }

    public static string Num(double d)
    {
        if (double.IsNaN(d) || double.IsInfinity(d)) return "0";
        return d.ToString("0.####", System.Globalization.CultureInfo.InvariantCulture);
    }

    public static string GetRaw(string json, string key)
    {
        string marker = "\"" + key + "\":";
        int i = json.IndexOf(marker);
        if (i < 0) return null;
        i += marker.Length;
        while (i < json.Length && char.IsWhiteSpace(json[i])) i++;
        if (i >= json.Length) return null;
        if (json[i] == '"')
        {
            int j = i + 1;
            while (j < json.Length)
            {
                if (json[j] == '\\') { j += 2; continue; }
                if (json[j] == '"') break;
                j++;
            }
            return json.Substring(i, j - i + 1);
        }
        int k = i;
        while (k < json.Length && json[k] != ',' && json[k] != '}' && json[k] != ']') k++;
        return json.Substring(i, k - i).Trim();
    }

    public static string GetString(string json, string key)
    {
        string raw = GetRaw(json, key);
        if (raw == null) return null;
        raw = raw.Trim();
        if (raw.Length >= 2 && raw[0] == '"')
        {
            StringBuilder sb = new StringBuilder();
            for (int i = 1; i < raw.Length - 1; i++)
            {
                if (raw[i] == '\\' && i + 1 < raw.Length - 1)
                {
                    char n = raw[i + 1];
                    if (n == 'n') sb.Append('\n');
                    else if (n == 'r') sb.Append('\r');
                    else if (n == 't') sb.Append('\t');
                    else sb.Append(n);
                    i++;
                }
                else sb.Append(raw[i]);
            }
            return sb.ToString();
        }
        if (raw == "null") return null;
        return raw;
    }

    public static int GetInt(string json, string key, int fallback)
    {
        string raw = GetRaw(json, key);
        if (raw == null) return fallback;
        int v;
        if (int.TryParse(raw.Trim().Trim('"'), out v)) return v;
        return fallback;
    }

    public static double GetDouble(string json, string key, double fallback)
    {
        string raw = GetRaw(json, key);
        if (raw == null) return fallback;
        double v;
        if (double.TryParse(raw.Trim().Trim('"'),
            System.Globalization.NumberStyles.Float,
            System.Globalization.CultureInfo.InvariantCulture, out v)) return v;
        return fallback;
    }

    public static string GetObject(string json, string key)
    {
        string marker = "\"" + key + "\":";
        int i = json.IndexOf(marker);
        if (i < 0) return null;
        i += marker.Length;
        while (i < json.Length && char.IsWhiteSpace(json[i])) i++;
        if (i >= json.Length || json[i] != '{') return "{}";
        int depth = 0;
        int start = i;
        for (; i < json.Length; i++)
        {
            char c = json[i];
            if (c == '"')
            {
                i++;
                while (i < json.Length)
                {
                    if (json[i] == '\\') { i += 2; continue; }
                    if (json[i] == '"') break;
                    i++;
                }
                continue;
            }
            if (c == '{') depth++;
            else if (c == '}')
            {
                depth--;
                if (depth == 0) return json.Substring(start, i - start + 1);
            }
        }
        return json.Substring(start);
    }
}
