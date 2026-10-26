"""Phase 3 media grounding: ffprobe, scenes, loudness, captions, highlights.

These modules are pure Python + ffmpeg. They do not talk to VEGAS.
"""
from .audio import analyze_audio
from .captions import burn_captions, generate_captions
from .highlights import find_highlights
from .probe import probe_media
from .scenes import detect_scenes
from .whisper import transcribe_media

__all__ = [
    "analyze_audio",
    "burn_captions",
    "detect_scenes",
    "find_highlights",
    "generate_captions",
    "probe_media",
    "transcribe_media",
]
