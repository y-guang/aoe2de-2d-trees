# 2D Trees - Minimalist, Flat Trees, Full-Tile Clickable

Trees are reduced to an extremely thin, almost completely flat layer, keeping the map clear and unobstructed.
More importantly, the entire tree tile is clickable.
You no longer need to carefully hunt for the small clickable part of the original tree graphic — simply click anywhere on the tile to select it.

将树木简化为近乎平面，让地图清晰、无遮挡。点击地块任意位置即可选中树木。

Source: https://github.com/y-guang/aoe2de-2d-trees

## Generate the mod

You need Python 3.14+ and uv. Initialize the pinned palette dependency first:

```powershell
git submodule update --init
```

Run from the project root:

```powershell
uv run python main.py
```

The generated mod is in `dist/2D Trees - Minimalist, Flat Trees, Full-Tile Clickable/`. Install it as a local mod in AoE2DE,
enable it, and check the appearance in-game.

Preview images are in `build/preview_*.png`. Running the command again replaces
the generated output.

## Acknowledgements

Inspired by Anne HK's *Identical Pine Trees with Grid Shadow* mod, whose design
and SMX files helped guide this project. We also drew on
[SMX-Workshop](https://github.com/ImWG/SMX-Workshop) to understand the SMX format
and use its tree palette. Thank you to both for making this work possible.
