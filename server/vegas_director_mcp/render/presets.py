"""Named render presets. Template names are matched against VEGAS's list."""
from __future__ import annotations

from typing import Any

RENDER_PRESETS: dict[str, dict[str, Any]] = {
    "vertical": {
        "name": "vertical",
        "width": 1080,
        "height": 1920,
        "label": "Vertical 1080x1920 Short",
        "renderer_contains": "MP4",
        "template_contains": "",
        "prefer_template_substrings": ["1080", "1920", "vertical", "tiktok", "9:16", "portrait"],
    },
    "1080p": {
        "name": "1080p",
        "width": 1920,
        "height": 1080,
        "label": "1080p landscape",
        "renderer_contains": "MP4",
        "template_contains": "",
        "prefer_template_substrings": ["1080", "1920"],
    },
    "4k": {
        "name": "4k",
        "width": 3840,
        "height": 2160,
        "label": "4K landscape",
        "renderer_contains": "MP4",
        "template_contains": "",
        "prefer_template_substrings": ["2160", "3840", "4k", "4K", "UHD"],
    },
}


def match_preset(preset: str, templates: list[dict[str, Any]]) -> dict[str, Any]:
    """Pick the best VEGAS renderer/template for a named preset."""
    spec = RENDER_PRESETS.get(preset.lower())
    if spec is None:
        return {"ok": False, "error": f"unknown preset {preset!r}; use vertical, 1080p, or 4k"}
    width, height = spec["width"], spec["height"]
    prefers = [s.lower() for s in spec.get("prefer_template_substrings") or []]
    renderer_f = (spec.get("renderer_contains") or "").lower()

    scored: list[tuple[int, dict[str, Any]]] = []
    for t in templates:
        tw = int(t.get("width") or 0)
        th = int(t.get("height") or 0)
        renderer = f"{t.get('renderer') or ''} {t.get('renderer_name') or ''}".lower()
        name = (t.get("template") or "").lower()
        if renderer_f and renderer_f not in renderer and renderer_f not in name:
            continue
        score = 0
        if tw == width and th == height:
            score += 50
        elif tw and th and abs(tw / th - width / height) < 0.05:
            score += 15
        for token in prefers:
            if token and token in name:
                score += 8
            if token and token in renderer:
                score += 3
        if "magix" in renderer and "avc" in renderer:
            score += 4
        if score > 0:
            scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return {
            "ok": False,
            "error": (
                f"no VEGAS template matched preset {preset!r} "
                f"({width}x{height}). Run list_render_templates and pass "
                "renderer_name + template_name to render_start."
            ),
            "preset": spec,
        }
    best = scored[0][1]
    return {
        "ok": True,
        "preset": spec,
        "renderer_name": best.get("renderer") or best.get("renderer_name"),
        "template_name": best.get("template"),
        "matched": best,
        "alternates": [t for _, t in scored[1:6]],
    }
