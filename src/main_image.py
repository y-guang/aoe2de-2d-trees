"""Render a small green cube without depending on SMX or palette files."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin

TOP = (58, 170, 64, 255)
LEFT = (35, 124, 42, 255)
RIGHT = (24, 90, 31, 255)


def _cube(radius: int, height: int) -> tuple[Image.Image, tuple[int, int]]:
    depth = max(1, radius // 2)
    image = Image.new("RGBA", (2 * radius + 1, 2 * depth + height + 1))
    draw = ImageDraw.Draw(image)
    north = (radius, 0)
    east = (2 * radius, depth)
    south = (radius, 2 * depth)
    west = (0, depth)
    bottom = (radius, 2 * depth + height)
    draw.polygon([west, south, bottom, (0, depth + height)], fill=LEFT)
    draw.polygon([south, east, (2 * radius, depth + height), bottom], fill=RIGHT)
    draw.polygon([north, east, south, west], fill=TOP)
    return image, (radius, depth + height)


def render_main(shadow_area: int, destination: Path) -> tuple[int, int]:
    """Match opaque cube area to one quarter of nonzero-alpha shadow area."""
    if shadow_area == 0:
        image, hotspot = Image.new("RGBA", (1, 1)), (0, 0)
        image.save(destination, pnginfo=_metadata(hotspot))
        return hotspot
    target = shadow_area / 4
    candidates = ((r, h) for r in range(1, int(shadow_area**0.5) + 2)
                  for h in range(max(1, r//4 - 1), r//4 + 2))
    radius, height = min(
        candidates,
        key=lambda size: abs(int(np.count_nonzero(np.asarray(_cube(*size)[0])[:, :, 3])) - target),
    )
    image, hotspot = _cube(radius, height)
    image.save(destination, pnginfo=_metadata(hotspot))
    return hotspot


def _metadata(hotspot: tuple[int, int]) -> PngImagePlugin.PngInfo:
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("hotspot_x", str(hotspot[0]))
    metadata.add_text("hotspot_y", str(hotspot[1]))
    return metadata
