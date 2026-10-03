# AoE2DE Flat Trees

Generate an AoE2DE mod that replaces trees with small green cubes on uniform gray
diamond bases. Standard and UHD graphics are included; stumps are hidden.

## Generate the mod

You need Python 3.14+, uv, and the palette file at
`reference/SMX-Workshop/palettes/n_trees.pal`.

Run from the project root:

```powershell
uv run python main.py
```

The generated mod is in `dist/Flat Trees/`. Install it as a local mod in AoE2DE,
enable it, and check the appearance in-game.

Preview images are in `build/preview_*.png`. Running the command again replaces
the generated output.
