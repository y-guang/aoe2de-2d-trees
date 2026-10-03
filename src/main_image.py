"""Render a small green cube without depending on SMX or palette files."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin

TOP = (58, 170, 64, 255)
LEFT = (24, 90, 31, 255)
RIGHT = (35, 124, 42, 255)


def _cube(radius: int, height: int, depth: int | None = None) -> tuple[Image.Image, tuple[int, int]]:
    depth = max(1, radius // 2) if depth is None else depth
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


def render_main(shadow_area: int, shadow_width: int, destination: Path, *, fallen: bool = False) -> tuple[int, int]:
    """Use the original small cube, with half the base area when fallen."""
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
    cube, _ = _cube(radius, height)
    # Both states retain the existing padded canvas and center hotspot.
    canvas_height = round(cube.height * shadow_width / cube.width)
    if fallen:
        # Halve the ground-plane area: scale both edge lengths by sqrt(1/2).
        # Preserve the vertical thickness; round projected dimensions to pixels.
        scale = 0.5**0.5
        cube, _ = _cube(round(radius * scale), height, round((radius // 2) * scale))
    # User-confirmed in-game: main-layer bounds expand the clickable area even
    # with alpha=0 padding. Preserve this canvas through PNG and SMX encoding;
    # cropping to visible pixels would undo the fix. See
    # agent/reports/261003_2241-transparent-main-click-area.md.
    image = Image.new("RGBA", (shadow_width, canvas_height))
    # Align the main canvas center with the shadow center for stable click bounds.
    # Center the visible cube too; odd/even pixel sizes can differ by one pixel.
    hotspot = (image.width // 2, image.height // 2)
    offset = ((image.width - cube.width) // 2, (image.height - cube.height) // 2)
    image.paste(cube, offset)
    image.save(destination, pnginfo=_metadata(hotspot))
    return hotspot


def _metadata(hotspot: tuple[int, int]) -> PngImagePlugin.PngInfo:
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("hotspot_x", str(hotspot[0]))
    metadata.add_text("hotspot_y", str(hotspot[1]))
    return metadata
