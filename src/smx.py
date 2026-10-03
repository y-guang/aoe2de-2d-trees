"""Read and write the limited SMX variants present in the reference tree mod.

Only version 2, 4plus1, ordinary main pixels and empty outlines are supported.
PNG main and shadow layers are encoded; original blank placeholders stay untouched.
"""

from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from PIL import Image

Pixels = NDArray[np.int32]
Kind = Literal["main", "shadow", "outline"]
PALETTE_FILES = {20: "b_east.pal", 28: "b_scen.pal", 30: "n_trees.pal"}


@dataclass
class Layer:
    kind: Kind
    width: int
    height: int
    hotspot: tuple[int, int]
    pixels: Pixels
    encoded: bytes
    smp_size: int


@dataclass
class Frame:
    flags: int
    palette: int
    smp_size: int
    layers: list[Layer]


@dataclass
class Sprite:
    version: int
    memo: bytes
    frames: list[Frame]


def _decode(kind: Kind, width: int, height: int, edges: list[tuple[int, int]],
            commands: bytes, data: bytes) -> Pixels:
    pixels = np.full((height, width), -1, dtype=np.int32)
    slots: list[int] = []
    if kind == "main":
        assert len(data) % 5 == 0
        for a, b, c, d, sections in struct.iter_unpack("5B", data):
            slots.extend(v | (((sections >> (2*i)) & 3) << 8)
                         for i, v in enumerate((a, b, c, d)))
    pos = used = 0
    for y, (left, right) in enumerate(edges):
        if left == 65535:
            assert right == 65535
            continue
        x = left
        while True:
            assert pos < len(commands)
            byte = commands[pos]
            pos += 1
            op, count = byte & 3, (byte >> 2) + 1
            if op == 3:
                assert x == width - right
                break
            assert x + count <= width - right
            if op:
                if kind == "main":
                    assert op == 1, "Player-color pixels are outside this mod's scope."
                    values = slots[used:used+count]
                    assert len(values) == count
                    pixels[y, x:x+count] = values
                    used += count
                elif kind == "shadow":
                    values = commands[pos:pos+count]
                    assert len(values) == count
                    pixels[y, x:x+count] = list(values)
                    pos += count
                else:
                    raise AssertionError("Nonempty outlines are outside this mod's scope.")
            x += count
    assert pos == len(commands)
    return pixels



def _read_layer(blob: bytes, pos: int, kind: Kind) -> tuple[Layer, int]:
    start = pos
    width, height, hx, hy, _, unknown = struct.unpack_from("<HHhhII", blob, pos)
    assert unknown == 0
    pos += 16
    edges = [struct.unpack_from("<HH", blob, pos + 4*y) for y in range(height)]
    pos += 4*height
    command_size, = struct.unpack_from("<I", blob, pos)
    pos += 4
    pixel_size = 0
    if kind == "main":
        pixel_size, = struct.unpack_from("<I", blob, pos)
        pos += 4
    commands = blob[pos:pos+command_size]
    pos += command_size
    data = blob[pos:pos+pixel_size]
    pos += pixel_size
    assert pos <= len(blob)
    pixels = _decode(kind, width, height, edges, commands, data)
    expanded_size = 32 + 8*height + len(commands)
    if kind == "main":
        expanded_size += 4*int(np.count_nonzero(pixels >= 0))
    return Layer(kind, width, height, (hx, hy), pixels, blob[start:pos], expanded_size), pos


def read_layer_file(path: Path, kind: Kind) -> Layer:
    blob = path.read_bytes()
    layer, end = _read_layer(blob, 0, kind)
    assert end == len(blob)
    return layer


def read_smx(path: Path) -> Sprite:
    blob = path.read_bytes()
    signature, version, count, _, _, memo = struct.unpack_from("<4sHHII16s", blob)
    assert signature == b"SMPX" and version == 2
    frames = []
    pos = 32
    for _ in range(count):
        flags, palette, smp_size = struct.unpack_from("<BBI", blob, pos)
        assert flags in (1, 3, 7) and palette in PALETTE_FILES
        pos += 6
        layers = []
        kinds: tuple[Kind, ...] = ("main", "shadow", "outline")
        for bit, kind in enumerate(kinds):
            if not flags & (1 << bit):
                continue
            layer, pos = _read_layer(blob, pos, kind)
            layers.append(layer)
        frames.append(Frame(flags, palette, smp_size, layers))
    assert pos == len(blob)
    return Sprite(version, memo, frames)


def load_palette(palette_id: int, directory: Path) -> Pixels:
    lines = (directory / PALETTE_FILES[palette_id]).read_text().splitlines()
    assert lines[0] == "JASC-PAL" and int(lines[2]) == 1024
    # Match Workshop's RGB loader; its fourth text column is not used as alpha.
    return np.array([[int(v) for v in line.split()[:3]] for line in lines[3:1027]], dtype=np.int32)


def main_from_png(path: Path, palette: Pixels) -> Layer:
    with Image.open(path) as image:
        rgba = np.asarray(image.convert("RGBA"))
        hotspot = (int(image.info["hotspot_x"]), int(image.info["hotspot_y"]))
    assert np.isin(rgba[:, :, 3], (0, 255)).all()
    height, width = rgba.shape[:2]
    pixels = np.full((height, width), -1, dtype=np.int32)
    visible = rgba[:, :, 3] > 0
    colors, inverse = np.unique(rgba[visible, :3], axis=0, return_inverse=True)
    distances = ((colors.astype(np.int32)[:, None, :] - palette[None, :, :])**2).sum(axis=2)
    pixels[visible] = distances.argmin(axis=1)[inverse]
    return encode_layer("main", pixels, hotspot)


def encode_layer(kind: Kind, pixels: Pixels, hotspot: tuple[int, int]) -> Layer:
    assert kind in ("main", "shadow")
    height, width = pixels.shape
    edges = bytearray()
    commands = bytearray()
    slots = []
    for row in pixels:
        occupied = np.flatnonzero(row >= 0)
        if not len(occupied):
            edges.extend(struct.pack("<HH", 65535, 65535))
            continue
        left, end = int(occupied[0]), int(occupied[-1]) + 1
        edges.extend(struct.pack("<HH", left, width-end))
        x = left
        while x < end:
            drawn = row[x] >= 0
            stop = x + 1
            while stop < min(end, x+64) and (row[stop] >= 0) == drawn:
                stop += 1
            commands.append(((stop-x-1) << 2) | int(drawn))
            if drawn:
                if kind == "main":
                    slots.extend(int(v) for v in row[x:stop])
                else:
                    commands.extend(int(v) for v in row[x:stop])
            x = stop
        commands.append(3)
    used = len(slots)
    slots.extend([0] * ((-used) % 4))
    data = bytearray()
    for i in range(0, len(slots), 4):
        group = slots[i:i+4]
        data.extend(p & 255 for p in group)
        data.append(sum((p >> 8) << (2*j) for j, p in enumerate(group)))
    sizes = struct.pack("<II", len(commands), len(data)) if kind == "main" else struct.pack("<I", len(commands))
    payload = edges + sizes + commands + data
    encoded = struct.pack("<HHhhII", width, height, *hotspot, len(payload), 0) + payload
    return Layer(kind, width, height, hotspot, pixels, encoded,
                 32 + 8*height + len(commands) + 4*used)


def write_smx(sprite: Sprite, path: Path) -> None:
    body = bytearray()
    expanded = 4*len(sprite.frames)
    for frame in sprite.frames:
        smp_size = (sum(l.smp_size for l in frame.layers) + 63) & ~63
        expanded += smp_size
        body.extend(struct.pack("<BBI", frame.flags, frame.palette, smp_size))
        for layer in frame.layers:
            body.extend(layer.encoded)
    path.write_bytes(struct.pack("<4sHHII16s", b"SMPX", sprite.version,
                                 len(sprite.frames), len(body), expanded, sprite.memo) + body)
