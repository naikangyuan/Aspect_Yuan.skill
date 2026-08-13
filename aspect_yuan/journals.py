"""Publication-ready figure presets.

These presets are practical defaults, not official journal specifications.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JournalPreset:
    name: str
    width_mm: int
    dpi: int
    font_size: int
    line_width: float
    formats: tuple[str, ...]


PRESETS: dict[str, JournalPreset] = {
    "grl": JournalPreset("GRL", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
    "jgr solid earth": JournalPreset("JGR Solid Earth", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
    "g3": JournalPreset("G3", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
    "epsl": JournalPreset("EPSL", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
    "tectonics": JournalPreset("Tectonics", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
    "nature": JournalPreset("Nature", 180, 300, 7, 0.7, ("png", "pdf", "svg", "tiff")),
    "nature geoscience": JournalPreset("Nature Geoscience", 180, 300, 7, 0.7, ("png", "pdf", "svg", "tiff")),
    "science advances": JournalPreset("Science Advances", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
    "gji": JournalPreset("Geophysical Journal International", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
    "solid earth": JournalPreset("Solid Earth", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
    "open geosciences": JournalPreset("Open Geosciences", 180, 300, 8, 0.8, ("png", "pdf", "svg", "tiff")),
}


def get_journal(name: str | None) -> JournalPreset:
    if not name:
        return PRESETS["grl"]
    return PRESETS.get(name.lower(), PRESETS["grl"])

