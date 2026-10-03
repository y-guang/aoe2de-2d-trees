"""Replace the listed tree models with one cube or an empty placeholder."""

from dataclasses import dataclass
import json
from pathlib import Path

from PIL import Image

from .main_image import render_main
from .shadow_image import render_shadow, shadow_from_png
from .smx import Frame, Sprite, load_palette, main_from_png, read_layer_file, read_smx, write_smx

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
MOD_TITLE = "2D Trees - Minimalist, Flat Trees, Full-Tile Clickable"
MOD = ROOT / "dist" / MOD_TITLE
PALETTE = ROOT / "external/SMX-Workshop/palettes/n_trees.pal"


@dataclass(frozen=True)
class Model:
    filename: str
    width: int
    height: int
    frames: int
    fallen: bool
    empty: bool = False


MODELS: tuple[Model, ...] = (
    Model(filename="n_tree_acacia_x1.smx", width=96, height=48, frames=30, fallen=False),
    Model(filename="n_tree_acacia_x2.smx", width=192, height=96, frames=30, fallen=False),
    Model(filename="n_tree_asian_maple_autumn_x1.smx", width=96, height=48, frames=18, fallen=False),
    Model(filename="n_tree_asian_maple_autumn_x2.smx", width=192, height=96, frames=18, fallen=False),
    Model(filename="n_tree_asian_maple_green_x1.smx", width=96, height=48, frames=9, fallen=False),
    Model(filename="n_tree_asian_maple_green_x2.smx", width=192, height=96, frames=9, fallen=False),
    Model(filename="n_tree_asian_pine_x1.smx", width=96, height=48, frames=4, fallen=False),
    Model(filename="n_tree_asian_pine_x2.smx", width=192, height=96, frames=4, fallen=False),
    Model(filename="n_tree_autumn_oak_x1.smx", width=96, height=48, frames=42, fallen=False),
    Model(filename="n_tree_autumn_oak_x2.smx", width=192, height=96, frames=42, fallen=False),
    Model(filename="n_tree_bamboo_x1.smx", width=96, height=48, frames=12, fallen=False),
    Model(filename="n_tree_bamboo_x2.smx", width=192, height=96, frames=12, fallen=False),
    Model(filename="n_tree_baobab_x1.smx", width=96, height=48, frames=45, fallen=False),
    Model(filename="n_tree_baobab_x2.smx", width=192, height=96, frames=45, fallen=False),
    Model(filename="n_tree_birch_x1.smx", width=96, height=48, frames=42, fallen=False),
    Model(filename="n_tree_birch_x2.smx", width=192, height=96, frames=42, fallen=False),
    Model(filename="n_tree_brazilwood_x1.smx", width=96, height=48, frames=14, fallen=False),
    Model(filename="n_tree_brazilwood_x2.smx", width=192, height=96, frames=14, fallen=False),
    Model(filename="n_tree_bush_a_x1.smx", width=96, height=48, frames=6, fallen=False),
    Model(filename="n_tree_bush_a_x2.smx", width=192, height=96, frames=6, fallen=False),
    Model(filename="n_tree_bush_b_x1.smx", width=96, height=48, frames=54, fallen=False),
    Model(filename="n_tree_bush_b_x2.smx", width=192, height=96, frames=54, fallen=False),
    Model(filename="n_tree_bush_c_x1.smx", width=96, height=48, frames=27, fallen=False),
    Model(filename="n_tree_bush_c_x2.smx", width=192, height=96, frames=27, fallen=False),
    Model(filename="n_tree_bush_d_x1.smx", width=96, height=48, frames=8, fallen=False),
    Model(filename="n_tree_bush_d_x2.smx", width=192, height=96, frames=8, fallen=False),
    Model(filename="n_tree_cypress_x1.smx", width=96, height=48, frames=12, fallen=False),
    Model(filename="n_tree_cypress_x2.smx", width=192, height=96, frames=12, fallen=False),
    Model(filename="n_tree_dead_x1.smx", width=96, height=48, frames=21, fallen=False),
    Model(filename="n_tree_dead_x2.smx", width=192, height=96, frames=21, fallen=False),
    Model(filename="n_tree_dragon_x1.smx", width=96, height=48, frames=36, fallen=False),
    Model(filename="n_tree_dragon_x2.smx", width=192, height=96, frames=36, fallen=False),
    Model(filename="n_tree_felled_bamboo_x1.smx", width=96, height=48, frames=9, fallen=True),
    Model(filename="n_tree_felled_bamboo_x2.smx", width=192, height=96, frames=9, fallen=True),
    Model(filename="n_tree_felled_baobab_x1.smx", width=96, height=48, frames=15, fallen=True),
    Model(filename="n_tree_felled_baobab_x2.smx", width=192, height=96, frames=15, fallen=True),
    Model(filename="n_tree_felled_generic_x1.smx", width=96, height=48, frames=6, fallen=True),
    Model(filename="n_tree_felled_generic_x2.smx", width=192, height=96, frames=6, fallen=True),
    Model(filename="n_tree_felled_lush_bamboo_x1.smx", width=96, height=48, frames=4, fallen=True),
    Model(filename="n_tree_felled_lush_bamboo_x2.smx", width=192, height=96, frames=4, fallen=True),
    Model(filename="n_tree_green_oak_x1.smx", width=96, height=48, frames=27, fallen=False),
    Model(filename="n_tree_green_oak_x2.smx", width=192, height=96, frames=27, fallen=False),
    Model(filename="n_tree_italian_pine_x1.smx", width=96, height=48, frames=24, fallen=False),
    Model(filename="n_tree_italian_pine_x2.smx", width=192, height=96, frames=24, fallen=False),
    Model(filename="n_tree_jungle_x1.smx", width=96, height=48, frames=39, fallen=False),
    Model(filename="n_tree_jungle_x2.smx", width=192, height=96, frames=39, fallen=False),
    Model(filename="n_tree_lush_bamboo_x1.smx", width=96, height=48, frames=16, fallen=False),
    Model(filename="n_tree_lush_bamboo_x2.smx", width=192, height=96, frames=16, fallen=False),
    Model(filename="n_tree_mangrove_x1.smx", width=96, height=48, frames=36, fallen=False),
    Model(filename="n_tree_mangrove_x2.smx", width=192, height=96, frames=36, fallen=False),
    Model(filename="n_tree_monkey_puzzle_x1.smx", width=96, height=48, frames=8, fallen=False),
    Model(filename="n_tree_monkey_puzzle_x2.smx", width=192, height=96, frames=8, fallen=False),
    Model(filename="n_tree_oak_x1.smx", width=96, height=48, frames=42, fallen=False),
    Model(filename="n_tree_oak_x2.smx", width=192, height=96, frames=42, fallen=False),
    Model(filename="n_tree_olive_x1.smx", width=96, height=48, frames=24, fallen=False),
    Model(filename="n_tree_olive_x2.smx", width=192, height=96, frames=24, fallen=False),
    Model(filename="n_tree_palm_x1.smx", width=96, height=48, frames=39, fallen=False),
    Model(filename="n_tree_palm_x2.smx", width=192, height=96, frames=39, fallen=False),
    Model(filename="n_tree_peach_blossom_x1.smx", width=96, height=48, frames=5, fallen=False),
    Model(filename="n_tree_peach_blossom_x2.smx", width=192, height=96, frames=5, fallen=False),
    Model(filename="n_tree_pine_x1.smx", width=96, height=48, frames=27, fallen=False),
    Model(filename="n_tree_pine_x2.smx", width=192, height=96, frames=27, fallen=False),
    Model(filename="n_tree_rainforest_x1.smx", width=96, height=48, frames=69, fallen=False),
    Model(filename="n_tree_rainforest_x2.smx", width=192, height=96, frames=69, fallen=False),
    Model(filename="n_tree_reeds_x1.smx", width=96, height=48, frames=12, fallen=False),
    Model(filename="n_tree_reeds_x2.smx", width=192, height=96, frames=12, fallen=False),
    Model(filename="n_tree_scenario_a_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_a_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_b_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_b_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_c_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_c_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_d_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_d_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_e_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_e_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_f_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_f_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_g_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_g_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_h_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_h_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_i_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_i_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_j_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_j_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_k_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_k_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_scenario_l_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_scenario_l_x2.smx", width=192, height=96, frames=3, fallen=False),
    Model(filename="n_tree_snow_autumn_oak_x1.smx", width=96, height=48, frames=42, fallen=False),
    Model(filename="n_tree_snow_autumn_oak_x2.smx", width=192, height=96, frames=42, fallen=False),
    Model(filename="n_tree_snow_pine_x1.smx", width=96, height=48, frames=27, fallen=False),
    Model(filename="n_tree_snow_pine_x2.smx", width=192, height=96, frames=27, fallen=False),
    Model(filename="n_tree_spruce_snow_x1.smx", width=96, height=48, frames=12, fallen=False),
    Model(filename="n_tree_spruce_snow_x2.smx", width=192, height=96, frames=12, fallen=False),
    Model(filename="n_tree_spruce_x1.smx", width=96, height=48, frames=25, fallen=False),
    Model(filename="n_tree_spruce_x2.smx", width=192, height=96, frames=25, fallen=False),
    Model(filename="n_tree_stump_bamboo_x1.smx", width=96, height=48, frames=3, empty=True, fallen=False),
    Model(filename="n_tree_stump_bamboo_x2.smx", width=192, height=96, frames=3, empty=True, fallen=False),
    Model(filename="n_tree_stump_baobab_x1.smx", width=96, height=48, frames=3, empty=True, fallen=False),
    Model(filename="n_tree_stump_baobab_x2.smx", width=192, height=96, frames=15, empty=True, fallen=False),
    Model(filename="n_tree_stump_generic_x1.smx", width=96, height=48, frames=3, empty=True, fallen=False),
    Model(filename="n_tree_stump_generic_x2.smx", width=192, height=96, frames=9, empty=True, fallen=False),
    Model(filename="n_tree_stump_lush_bamboo_x1.smx", width=96, height=48, frames=4, empty=True, fallen=False),
    Model(filename="n_tree_stump_lush_bamboo_x2.smx", width=192, height=96, frames=4, empty=True, fallen=False),
    Model(filename="n_tree_wax_palm_x1.smx", width=96, height=48, frames=8, fallen=False),
    Model(filename="n_tree_wax_palm_x2.smx", width=192, height=96, frames=8, fallen=False),
    Model(filename="n_tree_willow_x1.smx", width=96, height=48, frames=3, fallen=False),
    Model(filename="n_tree_willow_x2.smx", width=192, height=96, frames=3, fallen=False),
)


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    graphics = MOD / "resources/_common/drs/graphics"
    graphics.mkdir(parents=True, exist_ok=True)
    filenames = {model.filename for model in MODELS}
    assert len(filenames) == len(MODELS)
    assert all(Path(name).name == name and name.endswith(".smx") for name in filenames)

    # Clean only stale outputs in our own generated graphics directory.
    for path in graphics.glob("*.smx"):
        if path.name not in filenames:
            path.unlink()

    palette = load_palette(PALETTE)
    variants: dict[tuple[int, int, bool, bool], Frame] = {}
    for model in MODELS:
        name = model.filename
        width, height, empty = model.width, model.height, model.empty
        assert width > 0 and height > 0 and model.frames > 0
        key = (width, height, empty, model.fallen)
        if key not in variants:
            suffix = f"{width}x{height}" + ("_empty" if empty else "")
            main_suffix = suffix + ("_fallen" if model.fallen else "")
            main_png = BUILD / f"preview_main_{main_suffix}.png"
            shadow_png = BUILD / f"preview_shadow_{suffix}.png"
            area = render_shadow(width, height, empty, shadow_png)
            render_main(area, width, main_png, fallen=model.fallen)
            main_bin = BUILD / f"main_{main_suffix}.bin"
            shadow_bin = BUILD / f"shadow_{suffix}.bin"
            main_bin.write_bytes(main_from_png(main_png, palette).encoded)
            shadow_bin.write_bytes(shadow_from_png(shadow_png).encoded)
            # Assemble from the binary layer files, not the preview images.
            variants[key] = Frame(3, 30, 0, [
                read_layer_file(main_bin, "main"),
                read_layer_file(shadow_bin, "shadow"),
            ])
        sprite = Sprite(2, b"2D Trees".ljust(16, b"\0"),
                        [variants[key]] * model.frames)
        write_smx(sprite, graphics / name)

    info = {
        "Title": MOD_TITLE,
        "Author": "y-guang",
        "Description": (
            "Trees are reduced to an extremely thin, almost completely flat layer, "
            "keeping the map clear and unobstructed.\n"
            "More importantly, the entire tree tile is clickable.\n"
            "You no longer need to carefully hunt for the small clickable part of the "
            "original tree graphic — simply click anywhere on the tile to select it.\n\n"
            "将树木简化为近乎平面，让地图清晰、无遮挡。点击地块任意位置即可选中树木。\n\n"
            "Inspired by Anne_HK's Identical Pine Trees with Grid Shadow mod."
            "\n\nSource: https://github.com/y-guang/aoe2de-2d-trees"
        ),
        "CacheStatus": 0,
    }
    (MOD / "info.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")

    # Make the thumbnail from our generated PNGs.
    with Image.open(BUILD / "preview_shadow_192x96.png") as shadow, \
         Image.open(BUILD / "preview_main_192x96.png") as cube:
        canvas = Image.new("RGBA", shadow.size, (235, 235, 235, 255))
        canvas.alpha_composite(shadow)
        position = (shadow.width // 2 - int(cube.info["hotspot_x"]),
                    shadow.height // 2 - int(cube.info["hotspot_y"]))
        canvas.alpha_composite(cube, position)
        canvas.convert("RGB").resize((384, 192), Image.Resampling.NEAREST).save(MOD / "thumbnail.jpg")

    for name in filenames:
        read_smx(graphics / name)
    print(f"Generated {len(MODELS)} SMX files using {len(variants)} image variants.")
    print(f"PNG assets: {BUILD}")
    print(f"Local mod: {MOD}")


if __name__ == "__main__":
    main()
