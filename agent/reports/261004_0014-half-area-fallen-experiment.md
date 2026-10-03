# Half-area fallen tree experiment

Branch: experiment/half-area-fallen, based on main.

Current result: standing trees retain the original small cube; fallen trees have half the base area and unchanged height, with no marking. The sections below preserve the experiment history.

Standing trees use a wide, shallow green block that nearly fills the shadow; fallen trees retain the previous small cube and have no hatch marking. Right faces remain lighter than left faces.

The standing block keeps the previous vertical thickness (4 standard pixels, 10 UHD pixels). Its radius and projected depth are computed from the shadow dimensions with a 2/4-pixel nominal inset and extra horizontal room for the side faces, ensuring all visible pixels lie within the shadow. Standing visible bounds are 83x43 and 163x87. Fallen bounds remain 41x25 and 79x49.

Both states retain the padded main canvas (96x59 or 192x119), center hotspot, and original uniform shadow. Stumps are still empty. Thus this experiment changes the visible size distinction while preserving the click canvas.

Seven tests pass, including containment within the shadow, narrow border gaps, three-color fallen cubes, all 110 files and 1914 frames, and seamless shadow tiling. All outputs were regenerated. See build/preview_tree_placement.png and build/preview_main_states.png for standard/UHD previews.

## Revised border: one third of fallen margin

The latest revision narrows the standing block. Its nominal horizontal margin is round((shadow_width - fallen_cube_width) / 6): one third of the fallen cube's average horizontal gap to the shadow bounds. This is 9 standard pixels and 19 UHD pixels. The two horizontal gaps differ by at most one pixel because the shadow width is even and the cube width is odd. Vertical margins use half this inset for the 2:1 diamond.

Standing visible bounds are now 77x39 and 153x77; this supersedes the original dimensions above. Standard horizontal gaps are 9/10 pixels, UHD 19/20. Fallen PNGs and encoded binary layers were checked byte-for-byte against the prior output and are unchanged. Seven tests pass, including the revised border and full containment within the shadow. All mod outputs and previews were regenerated.

## Latest revision: one half of fallen margin

Standing margins now use round((shadow_width - fallen_cube_width) / 4), half the fallen horizontal margin. Nominal insets are 14 standard pixels and 28 UHD pixels; vertical inset is half the horizontal value for the 2:1 projection. Visible standing bounds are 67x33 and 135x67. Fallen PNG and binary layers remain byte-identical. Seven tests pass and the mod/previews were regenerated. This replaces the one-third rule above.

## Latest revision: former fallen size for standing trees

Standing trees now use the previous fallen cube exactly: visible bounds 41x25 / 79x49, confirmed by byte-identical encoded layers against the prior fallen output. Fallen cubes halve the ground-plane edge lengths with integer pixel rounding, keeping vertical thickness unchanged (4 / 10). New fallen bounds are 21x15 / 41x31. Both states remain centered, with the same padded canvas, hotspot, colors and shadow and no markings. The former border-fraction rules are removed. Seven tests pass and all outputs have been regenerated.

## Latest revision: half base area for fallen trees

Fallen base dimensions now use sqrt(0.5) scaling on both projected axes, separately rounded to integer pixels. Height is unchanged. Geometric base-area ratios are 49.0% standard and approximately 49.1% UHD; visible fallen bounds are 29x19 and 57x37. Standing trees remain the prior small cube. Common padded canvas, hotspot, shadow and colors are unchanged. Seven tests pass and all outputs/previews have been regenerated. This replaces the half-edge-length rule above.
