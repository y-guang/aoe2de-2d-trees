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


def render_main(shadow_area: int, shadow_width: int, destination: Path, *, fallen: bool = False) -> tuple[int, int]:
    """Keep the cube unchanged and pad its canvas to the shadow width."""
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
    cube, hotspot = _cube(radius, height)
    if fallen:
        # An inset X follows the top face perspective without enlarging its silhouette.
        depth = max(1, radius // 2)
        dx, dy = 2 * radius // 5, 2 * depth // 5
        draw = ImageDraw.Draw(cube)
        for direction in (-1, 1):
            draw.line([(radius - dx, depth - direction * dy),
                       (radius + dx, depth + direction * dy)],
                      fill=(0, 0, 0, 255), width=max(1, radius // 10))
    # User-confirmed in-game: main-layer bounds expand the clickable area even
    # with alpha=0 padding. Preserve this canvas through PNG and SMX encoding;
    # cropping to visible pixels would undo the fix. See
    # agent/reports/261003_2241-transparent-main-click-area.md.
    canvas_height = round(cube.height * shadow_width / cube.width)
    image = Image.new("RGBA", (shadow_width, canvas_height))
    # Put two thirds of the vertical transparent margin above the cube.
    # Hotspot compensation preserves its placement on the shadow.
    offset = ((image.width - cube.width) // 2, round(2 * (image.height - cube.height) / 3))
    image.paste(cube, offset)
    # Keep the unchanged cube at the same position relative to the game origin.
    hotspot = (hotspot[0] + offset[0], hotspot[1] + offset[1])
    image.save(destination, pnginfo=_metadata(hotspot))
    return hotspot


def _metadata(hotspot: tuple[int, int]) -> PngImagePlugin.PngInfo:
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("hotspot_x", str(hotspot[0]))
    metadata.add_text("hotspot_y", str(hotspot[1]))
    return metadata
