# Larson's Trees Addon

A Minecraft Bedrock addon adding decorative branch blocks for every vanilla wood
type, including stripped variants.

## Contents

- 5 branch shapes per wood type:
  - `<wood>_branch` — single vertical pole
  - `<wood>_branch_vertical_l` — vertical pole with one horizontal stub
  - `<wood>_branch_vertical_4way` — vertical pole with stubs on +X / -X
  - `<wood>_branch_horizontal_l` — vertical pole with one stub on +Z
  - `<wood>_branch_horizontal_4way` — vertical pole with stubs on +Z / -Z
- 22 wood types (11 base + 11 stripped): oak, spruce, birch, jungle, acacia,
  dark oak, mangrove, cherry, pale oak, crimson, warped.
- Total: **110 blocks**, all using the side log texture on every face.

## Layout

```
resource_pack/
  manifest.json
  models/blocks/*.geo.json     # the 5 BlockBench geometries
  textures/terrain_texture.json
  texts/en_US.lang
behavior_pack/
  manifest.json
  blocks/*.json                # 110 block definitions
  texts/en_US.lang
scripts/
  generate.py                  # regenerates blocks/textures/lang
```

To regenerate everything after editing `scripts/generate.py`:

```
python3 scripts/generate.py
```

## Pillar rotation

Every branch block rotates like a vanilla pillar/log: clicking the top or
bottom of a block places the branch on the Y axis, clicking a north/south
face places it on the Z axis, and clicking an east/west face places it on the
X axis. This is wired up via the `minecraft:placement_position` trait, which
exposes `minecraft:block_face`, plus three permutations that apply a
`minecraft:transformation` rotation and the matching axis-aligned hitbox.

| clicked face   | axis | rotation        |
|----------------|------|-----------------|
| up / down      | y    | `[ 0, 0,  0]`   |
| north / south  | z    | `[90, 0,  0]`   |
| east / west    | x    | `[ 0, 0, 90]`   |

## Hitbox alignment

Bedrock blocks only support a single axis-aligned `collision_box` and
`selection_box` per permutation, so each axis gets its own AABB union of every
cube in the geometry after the permutation's rotation is applied around the
block centre `[0, 8, 0]`. Coordinates are in the same 1/16-block units
BlockBench uses, but with X and Z shifted so the block's centre column is at 0
(BlockBench `from`/`to` runs 0–16; block components run −8 to +8 on X/Z and
0–16 on Y).

| Geometry                  | y origin / size            | z origin / size            | x origin / size            |
|---------------------------|----------------------------|----------------------------|----------------------------|
| `branch`                  | `[-3, 0, -3]` / `[ 6,16, 6]` | `[-3, 5,-8]` / `[ 6, 6,16]` | `[-8, 5,-3]` / `[16, 6, 6]` |
| `branch_vertical_l`       | `[-8, 0,-3]` / `[11,16, 6]` | `[-8, 5,-8]` / `[11, 6,16]` | `[-8, 0,-3]` / `[16,11, 6]` |
| `branch_vertical_4way`    | `[-8, 0,-3]` / `[16,16, 6]` | `[-8, 5,-8]` / `[16, 6,16]` | `[-8, 0,-3]` / `[16,16, 6]` |
| `branch_horizontal_l`     | `[-3, 0,-3]` / `[ 6,16,11]` | `[-3, 0,-8]` / `[ 6,11,16]` | `[-8, 5,-3]` / `[16, 6,11]` |
| `branch_horizontal_4way`  | `[-3, 0,-8]` / `[ 6,16,16]` | `[-3, 0,-8]` / `[ 6,16,16]` | `[-8, 5,-8]` / `[16, 6,16]` |

For the horizontal variants the side cubes also have `rotation: [0, -90, 0]`
in the geometry around their pivot; the rotated corners were computed before
taking the union.

## Texture references

`terrain_texture.json` defines short names like `larsons_oak_log_side` that
resolve to the vanilla side-log file paths (e.g. `textures/blocks/log_oak`).
No texture files are shipped — the engine resolves them against the vanilla
resource pack at runtime.
