# Flat Trees — developer implementation notes

2026-10-03. Build structure, configuration, binary semantics and verification.

Generate one small green cube and a uniform gray diamond for every listed tree.
Stumps are generated as completely empty graphics. No reference SMX, PNG or
thumbnail is copied into the output.

## Generate

Run from the project root:

~~~powershell
uv run python main.py
~~~

Keep the SMX-Workshop palette under reference/. The reference tree mod is not read by the build.
The local mod output is dist/Flat Trees/, containing info.json, our generated
thumbnail.jpg, and resources/_common/drs/graphics/. Install and test in-game manually.

## The model records

Edit the frozen Model records in src/main.py. All fields are explicit:

~~~python
Model(filename="n_tree_acacia_x1.smx", width=WIDTH, height=HEIGHT, frames=30),
Model(filename="n_tree_acacia_x2.smx", width=2 * WIDTH, height=2 * HEIGHT, frames=30),
Model(filename="n_tree_stump_bamboo_x1.smx", width=WIDTH, height=HEIGHT, frames=3, empty=True),
~~~

WIDTH=96, HEIGHT=48. These are diamond canvas dimensions, not the old tree's
bounding box. The cube's opaque projected pixel area is approximately one quarter
of the diamond's nonzero-alpha area; rasterization rounds its size.
Its base is centered at the diamond's hotspot. Shadow RGB is black with uniform
alpha 96: a gray diamond on a light background, without a grid or tree projection.

Add one Model record to replace another filename. Frame counts are explicitly
stored in every record, including the different stump counts. There is no
reference-mod discovery, template copying or fallback frame count.
All encoded frames use palette 30 and main/shadow layers. Source-specific shadow
variants, palettes and empty outline records are not retained.

## Modules and outputs

- src/main_image.py: render a green cube or empty main preview.
- src/shadow_image.py: render a uniform diamond or empty shadow preview.
- src/smx.py: map RGB to the tree palette, encode/decode complete layers and write SMX.
- src/main.py: model records, image variants and mod packaging.

build/ contains four combinations: normal/UHD, visible/empty. For each:

- preview_main_*.png and preview_shadow_*.png: previews with hotspot metadata.
  Main RGB is before nearest-palette mapping.
- main_*.bin and shadow_*.bin: actual SMX assembly inputs. Each contains one
  complete layer: 16-byte header, row edges, stream sizes and streams.
  They are layer fragments, not standalone SMX files.

SMX is assembled by reading the binary layers. PNG alpha alone cannot capture
every SMX distinction: a drawn shadow value of zero and an absent pixel both look
transparent. This generator encodes transparent backgrounds and empty stumps as
**no draw**. A main palette index of zero is a real drawn pixel when explicitly
present. Main PNG alpha is restricted to 0/255; shadow alpha stores intensity.

RGB maps to the nearest entry in reference/SMX-Workshop/palettes/n_trees.pal.
Only RGB columns are used, matching the local Workshop loader. The palette is
read, not bundled. Different palette versions can select different green indices.
The parser deliberately supports only the reference's version-2/4plus1 variants.

build/, dist/ and tmp/ are Git-ignored. All previews, binary layers, SMX metadata,
thumbnail and empty placeholders are produced by code.
Rebuilding removes obsolete SMX files only from our generated graphics directory.

## Checks

~~~powershell
uv run python -m unittest discover -s tests -v
~~~

Checks cover every filename/frame count, assembly from binary layers, uniform
shadow intensity, cube area, empty pixels and literal encodings distinguishing
drawn zero from no draw. Run normally: Python -O disables parser assertions.
