# Palette pin and adjacent shadow seams

2026-10-03. Current implementation notes; supersedes the reference-palette path and WIDTH/HEIGHT examples in earlier reports.

## Pinned external submodule

SMX-Workshop is a Git submodule at external/SMX-Workshop, declared in .gitmodules. The parent repository records only the gitlink; upstream files remain separate.

- Upstream: https://github.com/ImWG/SMX-Workshop.git
- Default branch: master.
- Latest upstream HEAD checked on 2026-10-03: 7e2b5bcf4314ebef60fe1bc164a9eeb169ab968f.
- Submodule is checked out at that exact commit with detached HEAD.
- Initialize after cloning: git submodule update --init.
- Required file: external/SMX-Workshop/palettes/n_trees.pal (15,615 bytes).
- SHA-256: b4eb13f5652b2f4a7dc7ff3850da833ca613f2d68a5ed9e77bb0801d965ba51b. The upstream palette matches the prior local snapshot; the checksum test is unchanged.
- The former single-file copy is saved under ignored tmp/SMX-Workshop-vendored-palette.
- Correction to older research notes: reference/SMX-Workshop is not a separate Git checkout. Its earlier reported commit belonged to the parent workspace. The commit above was verified directly against upstream.

The build reads the external palette and its own code, without reference/. Main model records contain literal width=96, height=48 or width=192, height=96, with explicit frame counts and empty flags. All six tests pass using the submodule, and all 110 mod files were regenerated.

## Seam cause and fix

The old PIL polygon used (width-1, cy) and (cx, height-1), shrinking and skewing the right/bottom edges. At integer tile offsets (width/2, height/2) and (-width/2, height/2), its raster edges did not complement adjacent tiles. This was a coverage problem, not just an edge that needed smoothing.

The replacement evaluates each pixel center against the full centered diamond:

~~~python
abs(2*x + 1 - width) * height + abs(2*y + 1 - height) * width < width*height
~~~

For our two even 2:1 dimensions, no pixel center lies exactly on the boundary. Each shared boundary partitions the pixel lattice without drawing the same pixel twice or leaving holes. No blur or alpha feathering is added. Shadow strength remains uniformly 96, preserving the simple gray base.

The test tiles a 7x7 neighborhood using the actual encoded .bin mask, and examines the central rectangle of 2*width by 2*height:

| Canvas | Old occupied pixels per tile | Old gaps | Old overlaps | New occupied pixels | New gaps | New overlaps |
|---|---:|---:|---:|---:|---:|---:|
| 96x48 | 2280 | 240 | 48 | 2304 | 0 | 0 |
| 192x96 | 9168 | 480 | 96 | 9216 | 0 | 0 |

Comparison previews: build/preview_shadow_tiling_96x48.png and build/preview_shadow_tiling_192x96.png. These are generated local artifacts, not Git-tracked assets.

Scope: verified native integer placement on the configured flat grids. This does not verify the game's actual tile transforms, zoom filtering or terrain elevation handling. In-game testing remains with the user.

## Validation

Six unittest checks pass, including checksum pinning, binary-layer tessellation, exact literal no-draw encodings, all 110 output files and 1914 frame counts, uniform alpha and cube area. All mod files and previews were regenerated. Preview saves use temporary-file replacement because an open Windows preview prevented overwriting one PNG in place.
