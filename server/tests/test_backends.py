from __future__ import annotations

from vegas_director_mcp.backends import create_backend, editor_from_env, list_editors, reset_backend
from vegas_director_mcp.backends.vegas import VegasBackend
from vegas_director_mcp import tools


def test_default_editor_is_vegas(monkeypatch):
    monkeypatch.delenv("DIRECTOR_EDITOR", raising=False)
    monkeypatch.delenv("VEGAS_DIRECTOR_EDITOR", raising=False)
    assert editor_from_env() == "vegas"
    listed = list_editors()
    assert listed["ok"] is True
    ids = [e["id"] for e in listed["editors"]]
    assert ids == ["vegas", "resolve", "otio"]
    resolve = next(e for e in listed["editors"] if e["id"] == "resolve")
    assert resolve["studio_required"] is True


def test_editor_aliases(monkeypatch):
    monkeypatch.setenv("DIRECTOR_EDITOR", "davinci-resolve")
    assert editor_from_env() == "resolve"
    monkeypatch.setenv("DIRECTOR_EDITOR", "fcpxml")
    assert editor_from_env() == "otio"
    monkeypatch.setenv("DIRECTOR_EDITOR", "kdenlive")
    assert editor_from_env() == "otio"


def test_vegas_backend_passthrough(fake_session):
    def handler(method, params):
        if method == "ping":
            return {"ok": True, "host": "vegas-director", "mode": "extension"}
        raise AssertionError(method)

    fake_session(handler)
    reset_backend(VegasBackend())
    result = tools.ping()
    assert result["ok"] is True
    assert result["mode"] == "extension"
    assert result["editor"] == "vegas"


def test_vegas_markers_soft_fail(fake_session):
    fake_session(lambda m, p: {"ok": True})
    reset_backend(create_backend("vegas"))
    result = tools.add_marker(1.0, "hook")
    assert result["ok"] is False
    assert result.get("unsupported") is True


def test_create_backend_resolve_does_not_touch_live_app():
    backend = create_backend("resolve", auto_launch=False, connector=lambda: None)
    ping = backend.call("ping")
    assert ping["ok"] is False
    assert ping["studio_required"] is True
    assert ping["scripting_available"] is False
    assert "21.1" in ping["error"]
