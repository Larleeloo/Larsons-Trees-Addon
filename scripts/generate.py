#!/usr/bin/env python3
"""Generate terrain_texture.json, block JSON files, and language files for the
Larson's Trees addon. Run from repo root: python3 scripts/generate.py"""

import json
import os
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
    ("pale_oak",         "textures/blocks/pale_oak_log",             "Pale Oak"),
    ("crimson",          "textures/blocks/crimson_log_side",         "Crimson"),
    ("warped",           "textures/blocks/warped_stem",              "Warped"),
    ("stripped_oak",         "textures/blocks/stripped_oak_log",          "Stripped Oak"),
    ("stripped_spruce",      "textures/blocks/stripped_spruce_log",       "Stripped Spruce"),
    ("stripped_birch",       "textures/blocks/stripped_birch_log",        "Stripped Birch"),
    ("stripped_jungle",      "textures/blocks/stripped_jungle_log",       "Stripped Jungle"),
    ("stripped_acacia",      "textures/blocks/stripped_acacia_log",       "Stripped Acacia"),
    ("stripped_dark_oak",    "textures/blocks/stripped_dark_oak_log",     "Stripped Dark Oak"),
    ("stripped_mangrove",    "textures/blocks/stripped_mangrove_log_side","Stripped Mangrove"),
    ("stripped_cherry",      "textures/blocks/stripped_cherry_log_side",  "Stripped Cherry"),
    ("stripped_pale_oak",    "textures/blocks/stripped_pale_oak_log",     "Stripped Pale Oak"),
    ("stripped_crimson",     "textures/blocks/stripped_crimson_stem",     "Stripped Crimson"),
    ("stripped_warped",      "textures/blocks/stripped_warped_stem",      "Stripped Warped"),
]

# (suffix, geometry id, hitbox origin, hitbox size, display suffix)
# Hitbox is the AABB union of all cubes in the geometry, accounting for rotation.
GEOS = [
    ("",                    "geometry.branch",    [-3, 0, -3], [ 6, 16,  6], ""),
    ("_vertical_l",         "geometry.branch_vl", [-8, 0, -3], [11, 16,  6], " (Vertical L)"),
    ("_vertical_4way",      "geometry.branch_v4", [-8, 0, -3], [16, 16,  6], " (Vertical 4-Way)"),
    ("_horizontal_l",       "geometry.branch_hl", [-3, 0, -3], [ 6, 16, 11], " (Horizontal L)"),
    ("_horizontal_4way",    "geometry.branch_h4", [-3, 0, -8], [ 6, 16, 16], " (Horizontal 4-Way)"),
]

NAMESPACE = "larsons"


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


def build_block(wood_id: str, geo_suffix: str, geo_id: str,
                origin, size) -> dict:
    identifier = f"{NAMESPACE}:{wood_id}_branch{geo_suffix}"
    return {
        "format_version": "1.20.10",
        "minecraft:block": {
            "description": {
                "identifier": identifier,
                "menu_category": {
                    "category": "nature",
                    "group": "itemGroup.name.log",
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
                "minecraft:collision_box": {
                    "origin": origin,
                    "size": size,
                },
                "minecraft:selection_box": {
                    "origin": origin,
                    "size": size,
                },
                "minecraft:destructible_by_mining": {"seconds_to_destroy": 2.0},
                "minecraft:destructible_by_explosion": {"explosion_resistance": 2.0},
                "minecraft:light_dampening": 0,
                "minecraft:map_color": "#6B4F2A",
            },
        },
    }


def build_blocks():
    for wood_id, _tex_path, _wood_name in WOODS:
        for geo_suffix, geo_id, origin, size, _disp in GEOS:
            block = build_block(wood_id, geo_suffix, geo_id, origin, size)
            filename = f"{wood_id}_branch{geo_suffix}.json"
            write_json(BP / "blocks" / filename, block)


def build_lang():
    lines = ["## Larson's Trees Addon"]
    for wood_id, _tex, wood_name in WOODS:
        for geo_suffix, _geo_id, _o, _s, disp in GEOS:
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
