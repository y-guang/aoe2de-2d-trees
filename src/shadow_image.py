"""Render a uniform diamond shadow, without a projected tree or grid."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin

from .smx import Layer, encode_layer

SHADOW_ALPHA = 96


def render_shadow(width: int, height: int, empty: bool, destination: Path) -> int:
    cx, cy = width // 2, height // 2
    image = Image.new("RGBA", (width, height))
    if not empty:
        ImageDraw.Draw(image).polygon(
            [(cx, 0), (width - 1, cy), (cx, height - 1), (0, cy)],
            fill=(0, 0, 0, SHADOW_ALPHA),
        )
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("hotspot_x", str(cx))
    metadata.add_text("hotspot_y", str(cy))
    image.save(destination, pnginfo=metadata)
    return int(np.count_nonzero(np.asarray(image)[:, :, 3]))


def shadow_from_png(path: Path) -> Layer:
    with Image.open(path) as image:
        rgba = np.asarray(image.convert("RGBA"))
        hotspot = (int(image.info["hotspot_x"]), int(image.info["hotspot_y"]))
    assert not rgba[:, :, :3].any(), "Shadow intensity belongs in alpha, not RGB."
    pixels = np.where(rgba[:, :, 3] > 0, rgba[:, :, 3].astype(np.int32), -1)
    return encode_layer("shadow", pixels, hotspot)
