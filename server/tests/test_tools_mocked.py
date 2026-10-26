from __future__ import annotations

from vegas_director_mcp import tools
from vegas_director_mcp.render.presets import match_preset
from vegas_director_mcp.render.sidecar import verify_output, write_sidecar


def test_ping_and_host_info(fake_session):
    def handler(method, params):
        if method == "ping":
            return {"ok": True, "host": "vegas-director", "mode": "extension"}
        if method == "host.info":
            return {"ok": True, "version": 2, "mode": "extension", "requests": 3}
        raise AssertionError(method)

    fake_session(handler)
    assert tools.ping()["mode"] == "extension"
    info = tools.host_info()
    assert info["version"] == 2
    assert info["used_mode"] == "live"


def test_new_project_and_add_track(fake_session):
    def handler(method, params):
        if method == "project.new":
            assert params.get("discard_unsaved") is True
            return {"ok": True}
        if method == "track.add":
            return {"ok": True, "track_index": params.get("index", 0), "type": params["type"]}
        raise AssertionError(method)

    fake_session(handler)
    assert tools.new_project(discard_unsaved=True)["ok"] is True
    added = tools.add_track("video", "V1", index=0)
    assert added["track_index"] == 0


def test_crossfade_moves_and_fades(fake_session):
    state = {
        "ok": True,
        "events": [
            {"track_index": 0, "event_index": 0, "start_seconds": 0.0, "length_seconds": 4.0},
            {"track_index": 0, "event_index": 1, "start_seconds": 4.0, "length_seconds": 4.0},
        ],
    }

    def handler(method, params):
        if method == "project.get_state":
            return state
        if method == "event.move":
            return {"ok": True, **params}
        if method == "event.set_fades":
            return {"ok": True, **params}
        raise AssertionError(method)

    host, _ = fake_session(handler)
    from vegas_director_mcp.edit.helpers import apply_crossfade

    result = apply_crossfade(0, 0, 1, seconds=0.5)
    assert result["ok"] is True
    assert abs(result["right_start_seconds"] - 3.5) < 1e-6
    methods = [m for m, _ in host.calls]
    assert methods.count("event.set_fades") == 2


def test_ducking_writes_volume_points(fake_session):
    def handler(method, params):
        if method == "project.get_state":
            return {
                "ok": True,
                "events": [
                    {"track_index": 1, "event_index": 0, "start_seconds": 2.0, "length_seconds": 3.0},
                ],
            }
        if method == "envelope.set_points":
            assert params["envelope_type"] == "Volume"
            assert params["track_index"] == 0
            assert len(params["points"]) >= 4
            return {"ok": True, "points_applied": len(params["points"])}
        raise AssertionError(method)

    fake_session(handler)
    from vegas_director_mcp.edit.helpers import apply_ducking

    result = apply_ducking(0, 1, reduction_db=-9)
    assert result["ok"] is True
    assert result["voice_events"] == 1


def test_vertical_short_template(fake_session):
    def handler(method, params):
        if method == "project.set_video":
            return {"ok": True, "width": 1080, "height": 1920}
        if method == "track.add":
            name = params.get("name") or ""
            idx = 0 if "Caption" in name else 1
            return {"ok": True, "track_index": idx, "type": params.get("type")}
        if method in {"event.add_video", "event.trim", "event.set_motion", "event.set_fades", "event.add_title"}:
            return {"ok": True}
        raise AssertionError(method)

    fake_session(handler)
    from vegas_director_mcp.edit.shorts import apply_vertical_short

    result = apply_vertical_short(
        r"D:\media\wardogs.mp4",
        10.0,
        34.0,
        caption_cues=[{"start_seconds": 10.2, "end_seconds": 12.0, "text": "DOWN"}],
    )
    assert result["ok"] is True
    assert result["template"] == "vertical_short"
    assert result["zoom_count"] == 2
    assert result["edit_meta"]["caption_style"] == "shorts"
    assert result["motion"]["ok"] is True


def test_propose_edit_uses_highlights(fake_session, monkeypatch, spike_clip):
    def handler(method, params):
        if method == "project.set_video":
            return {"ok": True, "width": 1080, "height": 1920}
        if method == "track.add":
            return {"ok": True, "track_index": 0, "type": "video"}
        if method == "event.add_video":
            return {"ok": True, "event_index": 0}
        if method in {"event.trim", "event.set_motion", "event.set_fades"}:
            return {"ok": True}
        if method == "project.get_state":
            return {
                "ok": True,
                "events": [
                    {"track_index": 0, "event_index": 0, "start_seconds": 0.0, "length_seconds": 2.5},
                ],
            }
        raise AssertionError(method)

    fake_session(handler)
    from vegas_director_mcp.edit.propose import propose_edit

    result = propose_edit(str(spike_clip), vertical_short=True)
    assert result["ok"] is True
    assert result["in_seconds"] < result["out_seconds"]
    assert result["steps"]


def test_render_with_preset_async_verify(fake_session, color_clip, tmp_path):
    out = tmp_path / "out.mp4"
    out.write_bytes(color_clip.read_bytes())

    def handler(method, params):
        if method == "render.list_templates":
            return {
                "ok": True,
                "templates": [
                    {
                        "renderer": "MAGIX AVC/AAC MP4",
                        "renderer_name": "MAGIX AVC/AAC MP4",
                        "template": "Internet HD 1080p",
                        "width": 1920,
                        "height": 1080,
                    },
                    {
                        "renderer": "MAGIX AVC/AAC MP4",
                        "renderer_name": "MAGIX AVC/AAC MP4",
                        "template": "Vertical 1080x1920",
                        "width": 1080,
                        "height": 1920,
                    },
                ],
            }
        if method == "render.start":
            assert params.get("async") is True
            assert params["template_name"] == "Vertical 1080x1920"
            return {"ok": True, "job_id": "abc123", "state": "running", "async": True}
        if method == "render.status":
            return {"ok": True, "job_id": "abc123", "state": "complete", "percent": 100}
        raise AssertionError(method)

    fake_session(handler)
    # verify_output will ffprobe the copied clip (320x180) — expect mismatch on vertical size.
    result = tools.render_with_preset(
        str(out),
        "vertical",
        edit_meta={"length": 2.2, "hook_start_time": 0.1, "caption_style": "shorts", "zoom_count": 2, "music": False, "template": "vertical_short"},
        wait=True,
    )
    assert result["started"]["job_id"] == "abc123"
    assert result["status"]["state"] == "complete"
    assert result["sidecar"]["sidecar_path"].endswith(".edit.json")
    assert result["verify"]["ok"] is False  # 320x180 != 1080x1920
    assert result["verify"]["problems"]


def test_match_preset_picks_vertical():
    templates = [
        {"renderer": "MP4", "template": "1080p", "width": 1920, "height": 1080},
        {"renderer": "MAGIX AVC/AAC MP4", "template": "Vertical 1080x1920", "width": 1080, "height": 1920},
    ]
    matched = match_preset("vertical", templates)
    assert matched["ok"] is True
    assert matched["template_name"] == "Vertical 1080x1920"


def test_sidecar_schema(tmp_path, color_clip):
    dest = tmp_path / "short.mp4"
    dest.write_bytes(color_clip.read_bytes())
    payload = write_sidecar(
        str(dest),
        {
            "length": 27.0,
            "hook_start_time": 142.5,
            "caption_style": "shorts",
            "zoom_count": 2,
            "music": True,
            "template": "vertical_short",
        },
    )
    assert payload["ok"] is True
    edit = payload["edit"]
    assert edit["length"] == 27.0
    assert edit["hook_start_time"] == 142.5
    assert edit["caption_style"] == "shorts"
    assert edit["zoom_count"] == 2
    assert edit["music"] is True
    assert edit["template"] == "vertical_short"
    verify = verify_output(str(dest), expect_audio=True)
    assert verify["ok"] is True
    assert verify["probe"]["has_audio"] is True


def test_host_unreachable_message(fake_session, monkeypatch):
    host, session = fake_session(lambda m, p: {"ok": True}, reachable=False)

    def boom(*_a, **_k):
        raise ConnectionRefusedError("nope")

    monkeypatch.setattr(session, "ensure", lambda **k: {"ok": False, "used_mode": "none", "error": "could not launch"})
    monkeypatch.setattr(session.client, "call", boom)
    result = tools.ping()
    assert result["ok"] is False
    assert result["used_mode"] == "none"
