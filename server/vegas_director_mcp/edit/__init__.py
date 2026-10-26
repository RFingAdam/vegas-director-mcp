"""Higher-level edit helpers built on host primitives."""
from .helpers import apply_crossfade, apply_ducking
from .propose import propose_edit
from .shorts import apply_vertical_short

__all__ = ["apply_crossfade", "apply_ducking", "apply_vertical_short", "propose_edit"]
