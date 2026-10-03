"""Check structure, generated pixels and the no-draw distinction."""

from pathlib import Path
import struct
import tempfile
import unittest

import numpy as np
from PIL import Image

from src.main import BUILD, MODELS, MOD, main
from src.smx import encode_layer, read_layer_file, read_smx


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        main()

    def test_pinned_palette(self) -> None:
        import hashlib
        path = Path(__file__).resolve().parents[1] / "external/SMX-Workshop/palettes/n_trees.pal"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         "b4eb13f5652b2f4a7dc7ff3850da833ca613f2d68a5ed9e77bb0801d965ba51b")

    def test_adjacent_shadow_tiles_have_no_gaps_or_overlap(self) -> None:
        for width, height in ((96, 48), (192, 96)):
            layer = read_layer_file(BUILD / f"shadow_{width}x{height}.bin", "shadow")
            mask = layer.pixels >= 0
            self.assertEqual(int(mask.sum()), width * height // 2)
            np.testing.assert_array_equal(mask, mask[::-1, ::-1])
            coverage = np.zeros((12*height, 12*width), dtype=np.uint16)
            for i in range(-3, 4):
                for j in range(-3, 4):
                    x = 6*width + (i-j)*width//2 - layer.hotspot[0]
                    y = 6*height + (i+j)*height//2 - layer.hotspot[1]
                    coverage[y:y+height, x:x+width] += mask
            interior = coverage[5*height:7*height, 5*width:7*width]
            np.testing.assert_array_equal(interior, np.ones_like(interior))

    def test_known_model_frame_counts(self) -> None:
        self.assertEqual(len(MODELS), 110)
        self.assertEqual(sum(m.frames for m in MODELS), 1914)
        by_name = {m.filename: m for m in MODELS}
        self.assertEqual(by_name["n_tree_acacia_x1.smx"].frames, 30)
        self.assertEqual(by_name["n_tree_willow_x2.smx"].frames, 3)
        self.assertEqual(by_name["n_tree_stump_baobab_x2.smx"].frames, 15)
        self.assertEqual(by_name["n_tree_stump_generic_x2.smx"].frames, 9)

    def test_drawn_zero_is_not_an_absent_pixel(self) -> None:
        layer = encode_layer("main", np.array([[0, -1, 1023]], dtype=np.int32), (0, 0))
        expected = (struct.pack("<HHhhII", 3, 1, 0, 0, 21, 0)
                    + struct.pack("<HHII", 0, 0, 4, 5)
                    + bytes([1, 0, 1, 3, 0, 255, 0, 0, 12]))
        self.assertEqual(layer.encoded, expected)
        shadow = encode_layer("shadow", np.array([[-1, 0, 96, -1]], dtype=np.int32), (0, 0))
        expected_shadow = (struct.pack("<HHhhII", 4, 1, 0, 0, 12, 0)
                           + struct.pack("<HHI", 1, 1, 4) + bytes([5, 0, 96, 3]))
        self.assertEqual(shadow.encoded, expected_shadow)
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            path = Path(folder) / "shadow.bin"
            path.write_bytes(shadow.encoded)
            np.testing.assert_array_equal(read_layer_file(path, "shadow").pixels, [[-1, 0, 96, -1]])

    def test_png_area_and_uniform_shadow(self) -> None:
        for width, height, empty in {(m.width, m.height, m.empty) for m in MODELS}:
            suffix = f"{width}x{height}" + ("_empty" if empty else "")
            with Image.open(BUILD / f"preview_main_{suffix}.png") as image:
                main_alpha = np.asarray(image)[:, :, 3]
                if not empty:
                    self.assertEqual(image.width, width)
                    cube_width, cube_height = (41, 25) if width == 96 else (79, 49)
                    self.assertEqual(image.height, round(cube_height * width / cube_width))
                    left, top, right, bottom = image.getbbox()
                    self.assertEqual((right - left, bottom - top), (cube_width, cube_height))
                    layer = read_layer_file(BUILD / f"main_{suffix}.bin", "main")
                    self.assertEqual((layer.width, layer.height), image.size)
                    np.testing.assert_array_equal(layer.pixels >= 0, main_alpha > 0)
            with Image.open(BUILD / f"preview_shadow_{suffix}.png") as image:
                shadow = np.asarray(image)
                self.assertEqual(image.size, (width, height))
            self.assertFalse(shadow[:, :, :3].any())
            if empty:
                self.assertFalse(main_alpha.any())
                self.assertFalse(shadow[:, :, 3].any())
            else:
                self.assertEqual(set(np.unique(shadow[:, :, 3])), {0, 96})
                ratio = np.count_nonzero(main_alpha) / np.count_nonzero(shadow[:, :, 3])
                self.assertAlmostEqual(ratio, 0.25, delta=0.02)

    def test_every_file_uses_binary_layers_and_expected_frames(self) -> None:
        graphics = MOD / "resources/_common/drs/graphics"
        self.assertEqual({p.name for p in graphics.iterdir()}, {m.filename for m in MODELS})
        for model in MODELS:
            name, width, height, empty = model.filename, model.width, model.height, model.empty
            with self.subTest(file=name):
                suffix = f"{width}x{height}" + ("_empty" if empty else "")
                layers = ((BUILD / f"main_{suffix}.bin").read_bytes()
                          + (BUILD / f"shadow_{suffix}.bin").read_bytes())
                blob = (graphics / name).read_bytes()
                _, _, count, body_size, expanded, _ = struct.unpack_from("<4sHHII16s", blob)
                self.assertEqual(count, model.frames)
                self.assertEqual(body_size, len(blob) - 32)
                pos = 32
                sizes = []
                for _ in range(count):
                    flags, palette, size = struct.unpack_from("<BBI", blob, pos)
                    self.assertEqual((flags, palette), (3, 30))
                    self.assertEqual(blob[pos+6:pos+6+len(layers)], layers)
                    pos += 6 + len(layers)
                    sizes.append(size)
                self.assertEqual(pos, len(blob))
                self.assertEqual(expanded, 4*count + sum(sizes))
                for layer in read_smx(graphics / name).frames[0].layers:
                    self.assertEqual(bool(np.any(layer.pixels >= 0)), not empty)



if __name__ == "__main__":
    unittest.main()
