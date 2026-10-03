"""Render a uniform diamond shadow, without a projected tree or grid."""

from pathlib import Path

import numpy as np
from PIL import Image, PngImagePlugin

from .smx import Layer, encode_layer

SHADOW_ALPHA = 96


def render_shadow(width: int, height: int, empty: bool, destination: Path) -> int:
    cx, cy = width // 2, height // 2
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    if not empty:
        y, x = np.indices((height, width))
        # Test pixel centers against the full diamond, not width-1/height-1 vertices.
        inside = (np.abs(2*x + 1 - width) * height
                  + np.abs(2*y + 1 - height) * width) < width*height
        rgba[inside, 3] = SHADOW_ALPHA
    image = Image.fromarray(rgba)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("hotspot_x", str(cx))
    metadata.add_text("hotspot_y", str(cy))
    temporary = destination.with_suffix(".tmp.png")
    image.save(temporary, pnginfo=metadata)
    temporary.replace(destination)
    return int(np.count_nonzero(np.asarray(image)[:, :, 3]))


def shadow_from_png(path: Path) -> Layer:
    with Image.open(path) as image:
        rgba = np.asarray(image.convert("RGBA"))
        hotspot = (int(image.info["hotspot_x"]), int(image.info["hotspot_y"]))
    assert not rgba[:, :, :3].any(), "Shadow intensity belongs in alpha, not RGB."
    pixels = np.where(rgba[:, :, 3] > 0, rgba[:, :, 3].astype(np.int32), -1)
    return encode_layer("shadow", pixels, hotspot)
