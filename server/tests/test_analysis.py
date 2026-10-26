from __future__ import annotations

from vegas_director_mcp.analysis.audio import analyze_audio
from vegas_director_mcp.analysis.captions import generate_captions
from vegas_director_mcp.analysis.highlights import find_highlights
from vegas_director_mcp.analysis.probe import probe_media
from vegas_director_mcp.analysis.scenes import detect_scenes
from vegas_director_mcp.analysis.whisper import transcribe_media


def test_probe_color_clip(color_clip):
    info = probe_media(str(color_clip))
    assert info["ok"] is True
    assert info["has_video"] is True
    assert info["has_audio"] is True
    assert info["width"] == 320
    assert info["height"] == 180
    assert 1.8 <= info["duration_seconds"] <= 2.6


def test_probe_missing():
    info = probe_media("/no/such/file.mp4")
    assert info["ok"] is False


def test_detect_scenes(scene_clip):
    result = detect_scenes(str(scene_clip), threshold=0.2)
    assert result["ok"] is True
    assert result["duration_seconds"] > 1.5
    # Hard color cut should register near 1s.
    cuts = [c["at_seconds"] for c in result["cuts"]]
    assert any(0.7 <= t <= 1.3 for t in cuts) or any(
        0.7 <= s["start_seconds"] <= 1.3 or 0.7 <= s["end_seconds"] <= 1.3
        for s in result["scenes"]
    )


def test_analyze_audio_finds_spike(spike_clip):
    result = analyze_audio(str(spike_clip), spike_ratio=1.8)
    assert result["ok"] is True
    assert result["has_audio"] is True
    assert result["spike_count"] >= 1
    times = [s["at_seconds"] for s in result["spikes"]]
    assert any(0.8 <= t <= 1.8 for t in times)


def test_captions_srt_ass(tmp_path, color_clip):
    cues = [
        {"start_seconds": 0.0, "end_seconds": 0.8, "text": "hook"},
        {"start_seconds": 0.8, "end_seconds": 1.6, "text": "payoff"},
    ]
    result = generate_captions(
        path=str(color_clip),
        segments=cues,
        output_dir=str(tmp_path),
        style="shorts",
        group_words=False,
    )
    assert result["ok"] is True
    srt = (tmp_path / "bars.srt").read_text(encoding="utf-8")
    ass = (tmp_path / "bars.ass").read_text(encoding="utf-8")
    assert "hook" in srt and "payoff" in srt
    assert "-->" in srt
    assert "PlayResX: 1080" in ass
    assert "PlayResY: 1920" in ass
    assert "Arial Black" in ass
    assert "Dialogue:" in ass


def test_word_grouped_captions(tmp_path):
    words = [
        {"start_seconds": 0.0, "end_seconds": 0.2, "word": "oh"},
        {"start_seconds": 0.2, "end_seconds": 0.4, "word": "my"},
        {"start_seconds": 0.4, "end_seconds": 0.6, "word": "god"},
        {"start_seconds": 0.6, "end_seconds": 0.8, "word": "down"},
        {"start_seconds": 2.0, "end_seconds": 2.2, "word": "nice"},
    ]
    result = generate_captions(words=words, output_dir=str(tmp_path), stem="grouped")
    assert result["ok"] is True
    assert result["cue_count"] >= 2
    joined = " ".join(c["text"] for c in result["cues"])
    assert "oh" in joined and "nice" in joined


def test_find_highlights_ranks_spike(spike_clip):
    result = find_highlights(str(spike_clip), min_seconds=20, max_seconds=35, max_candidates=3)
    assert result["ok"] is True
    assert result["clamped_to_media"] is True
    assert result["candidate_count"] >= 1
    top = result["candidates"][0]
    assert top["out_seconds"] > top["in_seconds"]
    assert top["reasons"]


def test_whisper_soft_fail_or_runs(color_clip):
    result = transcribe_media(str(color_clip), model_size="tiny")
    if result.get("available") is False:
        assert result["ok"] is False
        assert "faster-whisper" in result["error"]
    else:
        # Installed: must not crash. Empty speech on a sine wave is fine.
        assert "error" in result or result.get("ok") is True
