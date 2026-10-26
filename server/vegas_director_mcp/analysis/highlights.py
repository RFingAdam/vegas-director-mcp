"""Rank 20–35 s Short candidates from scenes, audio spikes, and transcript."""
from __future__ import annotations

import os
import re
from typing import Any

from .audio import analyze_audio
from .probe import probe_media
from .scenes import detect_scenes

_HOOK_WORDS = re.compile(
    r"\b(kill|killed|down|clutch|cash|nice|oh+|holy|nope|run|reload|headshot|squad|go)\b",
    re.I,
)


def _score_window(
    start: float,
    end: float,
    *,
    spikes: list[dict[str, Any]],
    cuts: list[float],
    segments: list[dict[str, Any]],
) -> tuple[float, list[str]]:
    reasons: list[str] = []
    score = 0.0
    length = end - start
    # Prefer 24–30 s in the 20–35 band.
    score += 1.2 - abs(length - 27.0) / 15.0

    early = [s for s in spikes if start <= s["at_seconds"] <= start + 2.5]
    inside = [s for s in spikes if start <= s["at_seconds"] < end]
    if early:
        score += 3.0
        kinds = sorted({s.get("kind") or "reaction" for s in early})
        reasons.append("hook spike in first 2.5s (" + ", ".join(kinds) + ")")
    if inside:
        score += min(2.5, 0.45 * len(inside))
        if any(s.get("kind") == "kill_cash" for s in inside):
            score += 1.5
            reasons.append("kill/cash peak inside window")
        if any(s.get("kind") == "squad_shout" for s in inside):
            score += 0.8
            reasons.append("squad shout inside window")
        if not early:
            reasons.append(f"{len(inside)} audio spike(s) in window")

    nearby_cuts = [c for c in cuts if abs(c - start) < 0.6]
    mid_cuts = [c for c in cuts if start + 0.8 < c < end - 0.4]
    if nearby_cuts:
        score += 1.0
        reasons.append("scene cut near in-point")
    # A couple of cuts is good; a strobe is not.
    if 1 <= len(mid_cuts) <= 4:
        score += 0.4
    elif len(mid_cuts) > 8:
        score -= 1.0
        reasons.append("too many mid-window cuts")

    hits = []
    for seg in segments:
        t0 = float(seg.get("start_seconds") or 0)
        t1 = float(seg.get("end_seconds") or 0)
        if t1 < start or t0 > end:
            continue
        text = seg.get("text") or ""
        if _HOOK_WORDS.search(text):
            hits.append(text.strip())
    if hits:
        score += 1.6
        reasons.append("dialogue hook: " + hits[0][:80])

    if not reasons:
        reasons.append("neutral window — weak hook")
    return score, reasons


def find_highlights(
    path: str,
    min_seconds: float = 20.0,
    max_seconds: float = 35.0,
    max_candidates: int = 8,
    scene_threshold: float = 0.30,
    transcript: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Rank candidate Short segments with in/out points and reasons."""
    if not path:
        return {"ok": False, "error": "path is required"}
    if not os.path.isfile(path):
        return {"ok": False, "error": f"file not found: {path}"}

    probe = probe_media(path)
    if not probe.get("ok"):
        return probe
    duration = float(probe.get("duration_seconds") or 0)
    if duration <= 0:
        return {"ok": False, "error": "media duration is 0"}

    prod_min, prod_max = min_seconds, max_seconds
    if duration < min_seconds:
        min_seconds = max(0.4, duration * 0.35)
        max_seconds = duration
        clamped = True
    else:
        clamped = False

    scenes = detect_scenes(path, threshold=scene_threshold) if probe.get("has_video") else {"ok": True, "cuts": [], "scenes": []}
    audio = analyze_audio(path) if probe.get("has_audio") else {"ok": True, "spikes": []}
    cuts = [float(c["at_seconds"]) for c in (scenes.get("cuts") or [])]
    spikes = list(audio.get("spikes") or [])
    segments = list((transcript or {}).get("segments") or [])

    # Candidate starts: audio spikes (hook), scene cuts, plus a coarse grid.
    starts: list[float] = [0.0]
    for s in spikes:
        hook = max(0.0, float(s["at_seconds"]) - 0.7)
        starts.append(hook)
    for c in cuts:
        starts.append(max(0.0, c))
    step = 4.0 if duration > 20 else max(0.4, duration / 6)
    t = 0.0
    while t < duration:
        starts.append(t)
        t += step

    uniq: list[float] = []
    for s in sorted(starts):
        if s > duration - min_seconds + 0.05:
            continue
        if not uniq or abs(s - uniq[-1]) > 0.45:
            uniq.append(s)

    lengths = []
    span = max_seconds - min_seconds
    if span <= 0.5:
        lengths = [min(max_seconds, duration)]
    else:
        lengths = [min_seconds, min_seconds + span * 0.5, max_seconds]

    scored: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for start in uniq:
        for length in lengths:
            end = min(duration, start + length)
            if end - start < min_seconds * 0.85:
                continue
            key = (int(start * 10), int(end * 10))
            if key in seen:
                continue
            seen.add(key)
            score, reasons = _score_window(
                start, end, spikes=spikes, cuts=cuts, segments=segments
            )
            scored.append(
                {
                    "in_seconds": round(start, 3),
                    "out_seconds": round(end, 3),
                    "length_seconds": round(end - start, 3),
                    "score": round(score, 3),
                    "reasons": reasons,
                }
            )
    scored.sort(key=lambda x: x["score"], reverse=True)
    # Suppress overlapping winners (keep higher score).
    winners: list[dict[str, Any]] = []
    for cand in scored:
        if any(
            not (cand["out_seconds"] <= w["in_seconds"] + 1 or cand["in_seconds"] >= w["out_seconds"] - 1)
            for w in winners
        ):
            continue
        winners.append(cand)
        if len(winners) >= max_candidates:
            break

    return {
        "ok": True,
        "path": os.path.abspath(path),
        "duration_seconds": duration,
        "target_seconds": [prod_min, prod_max],
        "clamped_to_media": clamped,
        "candidate_count": len(winners),
        "candidates": winners,
        "audio_spike_count": len(spikes),
        "scene_cut_count": len(cuts),
        "used_transcript": bool(segments),
    }
