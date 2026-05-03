#!/usr/bin/env python3
"""Generate terrain_texture.json, block JSON files, and language files for the
Larson's Trees addon. Run from repo root: python3 scripts/generate.py"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RP = ROOT / "resource_pack"
BP = ROOT / "behavior_pack"

# (id, vanilla side texture path, display name)
WOODS = [
    ("oak",              "textures/blocks/log_oak",                  "Oak"),
    ("spruce",           "textures/blocks/log_spruce",               "Spruce"),
    ("birch",            "textures/blocks/log_birch",                "Birch"),
    ("jungle",           "textures/blocks/log_jungle",               "Jungle"),
    ("acacia",           "textures/blocks/log_acacia",               "Acacia"),
    ("dark_oak",         "textures/blocks/log_big_oak",              "Dark Oak"),
    ("mangrove",         "textures/blocks/mangrove_log_side",        "Mangrove"),
    ("cherry",           "textures/blocks/cherry_log_side",          "Cherry"),
    ("pale_oak",         "textures/blocks/pale_oak_log_side",        "Pale Oak"),
    ("crimson",          "textures/blocks/huge_fungus/crimson_log_side",     "Crimson"),
    ("warped",           "textures/blocks/huge_fungus/warped_stem_side",     "Warped"),
    ("stripped_oak",         "textures/blocks/stripped_oak_log",          "Stripped Oak"),
    ("stripped_spruce",      "textures/blocks/stripped_spruce_log",       "Stripped Spruce"),
    ("stripped_birch",       "textures/blocks/stripped_birch_log",        "Stripped Birch"),
    ("stripped_jungle",      "textures/blocks/stripped_jungle_log",       "Stripped Jungle"),
    ("stripped_acacia",      "textures/blocks/stripped_acacia_log",       "Stripped Acacia"),
    ("stripped_dark_oak",    "textures/blocks/stripped_dark_oak_log",     "Stripped Dark Oak"),
    ("stripped_mangrove",    "textures/blocks/stripped_mangrove_log_side","Stripped Mangrove"),
    ("stripped_cherry",      "textures/blocks/stripped_cherry_log_side",  "Stripped Cherry"),
    ("stripped_pale_oak",    "textures/blocks/stripped_pale_oak_log_side",        "Stripped Pale Oak"),
    ("stripped_crimson",     "textures/blocks/huge_fungus/stripped_crimson_stem_side", "Stripped Crimson"),
    ("stripped_warped",      "textures/blocks/huge_fungus/stripped_warped_stem_side",  "Stripped Warped"),
]

# Each geometry has three pillar-axis hitboxes (Y default, plus X and Z rotated
# variants). Origin/size are AABB unions of all cubes after applying the
# corresponding minecraft:transformation rotation around the block center
# [0, 8, 0]. Coordinates are in 1/16-block units, X/Z centered at 0, Y in 0..16.
#
# Rotation map:
#   y axis: no rotation
#   z axis: rotation [90, 0, 0]   -> (x, y, z) -> (x, 8 - z, y - 8)
#   x axis: rotation [0, 0, 90]   -> (x, y, z) -> (8 - y, x + 8, z)
#
# (suffix, geometry id, display suffix, hitboxes_by_axis)
GEOS = [
    (
        "", "geometry.branch", "",
        {
            "y": ([-3, 0, -3], [ 6, 16,  6]),
            "z": ([-3, 5, -8], [ 6,  6, 16]),
            "x": ([-8, 5, -3], [16,  6,  6]),
        },
    ),
    (
        "_vertical_l", "geometry.branch_vl", " (Vertical L)",
        {
            "y": ([-8, 0, -3], [11, 16,  6]),
            "z": ([-8, 5, -8], [11,  6, 16]),
            "x": ([-8, 0, -3], [16, 11,  6]),
        },
    ),
    (
        "_vertical_4way", "geometry.branch_v4", " (Vertical 4-Way)",
        {
            "y": ([-8, 0, -3], [16, 16,  6]),
            "z": ([-8, 5, -8], [16,  6, 16]),
            "x": ([-8, 0, -3], [16, 16,  6]),
        },
    ),
    (
        "_horizontal_l", "geometry.branch_hl", " (Horizontal L)",
        {
            "y": ([-3, 0, -3], [ 6, 16, 11]),
            "z": ([-3, 0, -8], [ 6, 11, 16]),
            "x": ([-8, 5, -3], [16,  6, 11]),
        },
    ),
    (
        "_horizontal_4way", "geometry.branch_h4", " (Horizontal 4-Way)",
        {
            "y": ([-3, 0, -8], [ 6, 16, 16]),
            "z": ([-3, 0, -8], [ 6, 16, 16]),
            "x": ([-8, 5, -8], [16,  6, 16]),
        },
    ),
]

NAMESPACE = "larsons"

# Mapping from clicked block_face to placement axis (matches vanilla pillar
# logs: clicking the top/bottom places vertical, clicking a side places
# horizontal along that face's axis).
AXIS_BY_FACE = {
    "up":    "y",
    "down":  "y",
    "north": "z",
    "south": "z",
    "east":  "x",
    "west":  "x",
}

# Rotation applied via minecraft:transformation for each axis.
ROTATION_BY_AXIS = {
    "y": [0, 0,  0],
    "z": [90, 0, 0],
    "x": [0, 0, 90],
}


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def texture_short_name(wood_id: str) -> str:
    return f"larsons_{wood_id}_log_side"


def build_terrain_texture():
    data = {
        "resource_pack_name": "larsons_trees",
        "texture_name": "atlas.terrain",
        "padding": 8,
        "num_mip_levels": 4,
        "texture_data": {
            texture_short_name(w[0]): {"textures": w[1]}
            for w in WOODS
        },
    }
    write_json(RP / "textures" / "terrain_texture.json", data)


def build_axis_permutations(hitboxes):
    """Return one permutation per pillar axis. Faces sharing an axis are OR'd
    together so a single permutation covers both clicked-face values."""
    faces_by_axis = {}
    for face, axis in AXIS_BY_FACE.items():
        faces_by_axis.setdefault(axis, []).append(face)

    permutations = []
    for axis in ("y", "z", "x"):
        faces = faces_by_axis[axis]
        condition = " || ".join(
            f"q.block_state('minecraft:block_face') == '{f}'" for f in faces
        )
        origin, size = hitboxes[axis]
        components = {
            "minecraft:transformation": {
                "rotation": ROTATION_BY_AXIS[axis],
            },
            "minecraft:collision_box": {"origin": origin, "size": size},
            "minecraft:selection_box": {"origin": origin, "size": size},
        }
        permutations.append({"condition": condition, "components": components})
    return permutations


def build_block(wood_id: str, geo_suffix: str, geo_id: str, hitboxes) -> dict:
    identifier = f"{NAMESPACE}:{wood_id}_branch{geo_suffix}"
    return {
        "format_version": "1.21.40",
        "minecraft:block": {
            "description": {
                "identifier": identifier,
                "menu_category": {
                    "category": "nature",
                    "group": "itemGroup.name.log",
                },
                "traits": {
                    "minecraft:placement_position": {
                        "enabled_states": ["minecraft:block_face"],
                    },
                },
            },
            "components": {
                "minecraft:geometry": geo_id,
                "minecraft:material_instances": {
                    "*": {
                        "texture": texture_short_name(wood_id),
                        "render_method": "alpha_test",
                        "ambient_occlusion": True,
                        "face_dimming": True,
                    }
                },
                "minecraft:destructible_by_mining": {"seconds_to_destroy": 2.0},
                "minecraft:destructible_by_explosion": {"explosion_resistance": 2.0},
                "minecraft:light_dampening": 0,
                "minecraft:map_color": "#6B4F2A",
            },
            "permutations": build_axis_permutations(hitboxes),
        },
    }


def build_blocks():
    for wood_id, _tex_path, _wood_name in WOODS:
        for geo_suffix, geo_id, _disp, hitboxes in GEOS:
            block = build_block(wood_id, geo_suffix, geo_id, hitboxes)
            filename = f"{wood_id}_branch{geo_suffix}.json"
            write_json(BP / "blocks" / filename, block)


def build_lang():
    lines = ["## Larson's Trees Addon"]
    for wood_id, _tex, wood_name in WOODS:
        for geo_suffix, _geo_id, disp, _hitboxes in GEOS:
            ident = f"{NAMESPACE}:{wood_id}_branch{geo_suffix}"
            label = f"{wood_name} Branch{disp}"
            lines.append(f"tile.{ident}.name={label}")
    text = "\n".join(lines) + "\n"
    (RP / "texts").mkdir(parents=True, exist_ok=True)
    (BP / "texts").mkdir(parents=True, exist_ok=True)
    (RP / "texts" / "en_US.lang").write_text(text, encoding="utf-8")
    (BP / "texts" / "en_US.lang").write_text(text, encoding="utf-8")
    langs = ["en_US"]
    write_json(RP / "texts" / "languages.json", langs)
    write_json(BP / "texts" / "languages.json", langs)


def main():
    build_terrain_texture()
    build_blocks()
    build_lang()
    n = len(WOODS) * len(GEOS)
    print(f"Generated {n} block files, terrain_texture.json, and lang files.")


if __name__ == "__main__":
    main()
