"""Генератор пиксель-арта для игры (изометрия).

Запуск из корня репозитория:
    python3 tools/gen_art.py

Рендерит комнаты всех уровней, предметы, коробки, курсоры и шрифт в
game/assets/, а геометрию (поверхности, якоря спрайтов, двери) пишет в
game/scripts/art_data.gd. Каждый спрайт проверяется на палитру.
"""
import os

from PIL import Image

import room_bathroom
import room_bedroom
import room_kitchen
import room_living
from common import FONT_DIR, ORIGIN, RD, RH, ROOT, RW, SCRIPTS, SPRITES, from_map, render_door, render_room, save
from glyphs import CURSORS, GLYPHS
from iso import PX, render_sprite
from items import BOX_CLOSED, BOX_H, BOX_OPEN, BOX_X, BOX_Y, ITEM_SCALE, ITEMS, SMALL_ITEMS, SMALL_SCALE, WALL_FOOT, WALL_ITEMS, footprint, scaled
from palette import rgba

ROOMS = [room_kitchen, room_bathroom, room_bedroom, room_living]
BODY_FOOT = {"pan", "pot", "kettle", "mug_yellow", "mug_blue", "hairbrush"}


# ---------------------------------------------------------------- font

def font():
    chars = list(GLYPHS.keys())
    total = sum(len(GLYPHS[ch][0]) for ch in chars)
    img = Image.new("RGBA", (total, 7), (0, 0, 0, 0))
    entries = []
    x = 0
    white = rgba("W")
    for ch in chars:
        g = GLYPHS[ch]
        w = len(g[0])
        assert all(len(r) == w for r in g), ch
        for y, row in enumerate(g):
            for i, p in enumerate(row):
                if p == "#":
                    img.putpixel((x + i, y), white)
        entries.append((ch, x, w))
        x += w
    save("font", img, FONT_DIR)
    lines = [
        "# Сгенерировано tools/gen_art.py — не редактировать вручную.",
        "extends RefCounted",
        "",
        "const HEIGHT := 7",
        "const GLYPHS := {",
    ]
    for ch, gx, w in entries:
        lines.append(f'\t"{ch}": Vector2i({gx}, {w}),')
    lines.append("}")
    with open(os.path.join(SCRIPTS, "font_data.gd"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- main

def v2(p):
    return f"Vector2({p[0]}, {p[1]})"


def num(v):
    return f"{float(v):.2f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))


def gd_dict(d):
    return "{" + ", ".join(
        f'"{k}": "{v}"' if isinstance(v, str) else f'"{k}": {num(v)}' for k, v in d.items()
    ) + "}"


def main():
    for old in os.listdir(SPRITES) if os.path.isdir(SPRITES) else []:
        if old.endswith(".png") or old.endswith(".png.import"):
            os.remove(os.path.join(SPRITES, old))

    out = [
        "# Сгенерировано tools/gen_art.py — не редактировать вручную.",
        "# Мировые координаты: x — вдоль правой стены, y — вдоль левой, z — вверх.",
        "# Экран = ORIGIN + PX * (x - y, (x + y) / 2 - z).",
        "extends RefCounted",
        "",
        f"const ORIGIN := {v2(ORIGIN)}",
        f"const PX := {PX!r}  # пикселей на единицу мира",
        f"const ROOM := Vector3({RW}, {RD}, {RH})",
        "",
        "const ITEMS := {",
    ]
    for name, prims in ITEMS.items():
        prims = scaled(prims, SMALL_SCALE if name in SMALL_ITEMS else ITEM_SCALE)
        img, anchor = render_sprite(prims)
        save("item_" + name, img)
        x0, y0, x1, y1, h = footprint(prims)
        if name in BODY_FOOT:
            # ручки не занимают место на поверхности: след — только корпус
            x0, y0, x1, y1, _ = footprint(prims[:1])
        # след чуть меньше габарита: ручки и края могут нависать
        sh = 1.5
        x0, y0 = min(x0 + sh, -1.5), min(y0 + sh, -1.5)
        x1, y1 = max(x1 - sh, 1.5), max(y1 - sh, 1.5)
        out.append(
            f'\t"{name}": {{"anchor": {v2(anchor)}, '
            f'"foot": Rect2({num(x0)}, {num(y0)}, {num(x1 - x0)}, {num(y1 - y0)}), "h": {num(h)}}},'
        )
    # вещи на стенах: два варианта спрайта — для левой (L) и правой (R) стены
    for name, make in WALL_ITEMS.items():
        anchors = {}
        for side in ("L", "R"):
            img, anchors[side] = render_sprite(scaled(make(side), ITEM_SCALE))
            save(f"item_{name}_{side.lower()}", img)
        u0, v0, u1, v1 = (c * ITEM_SCALE for c in WALL_FOOT[name])
        out.append(
            f'\t"{name}": {{"wall": true, "anchor_l": {v2(anchors["L"])}, "anchor_r": {v2(anchors["R"])}, '
            f'"foot": Rect2({num(u0)}, {num(v0)}, {num(u1 - u0)}, {num(v1 - v0)}), "h": 0}},'
        )
    out.append("}")

    img, a_closed = render_sprite(BOX_CLOSED, outline="N")
    save("box_closed", img)
    img, a_open = render_sprite(BOX_OPEN, outline="N")
    save("box_open", img)
    out += [
        "",
        "const BOX := {",
        f'\t"anchor_closed": {v2(a_closed)},',
        f'\t"anchor_open": {v2(a_open)},',
        f'\t"foot": Rect2({-BOX_X}, {-BOX_Y}, {2 * BOX_X}, {2 * BOX_Y}),',
        f'\t"h": {BOX_H},',
        "}",
        "",
        "# комнаты: фон, двери (левый верхний угол спрайта, глубина для сортировки),",
        "# поверхности: горизонтальные — прямоугольник x0..x1, y0..y1 на высоте z;",
        "# на стенах (wall = L: плоскость x=0, R: y=0) — u0..u1 вдоль стены, z0..z1 по высоте",
        "const ROOMS := {",
    ]
    for room in ROOMS:
        n = room.NAME
        save(f"{n}_bg", render_room(room.prims()))
        out.append(f'\t"{n}": {{')
        out.append(f'\t\t"bg": "res://assets/sprites/{n}_bg.png",')
        out.append('\t\t"doors": {')
        for d in room.DOORS:
            room_prims = room.prims()
            img, pos_c = render_door(d["closed"], room_prims)
            save(f"{n}_{d['id']}_closed", img)
            img, pos_o = render_door(d["open"], room_prims)
            save(f"{n}_{d['id']}_open", img)
            out.append(
                f'\t\t\t"{d["id"]}": {{"closed": "res://assets/sprites/{n}_{d["id"]}_closed.png", '
                f'"open": "res://assets/sprites/{n}_{d["id"]}_open.png", '
                f'"closed_pos": {v2(pos_c)}, "open_pos": {v2(pos_o)}, '
                f'"closed_depth": {num(d["closed_depth"])}, "open_depth": {num(d["open_depth"])}}},'
            )
        out.append("\t\t},")
        out.append('\t\t"zones": [')
        for z in room.ZONES:
            out.append(f"\t\t\t{gd_dict(z)},")
        out.append("\t\t],")
        out.append("\t},")
    out.append("}")
    with open(os.path.join(SCRIPTS, "art_data.gd"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    for name, rows in CURSORS.items():
        save(name, from_map(rows))
    font()

    icon = Image.open(os.path.join(SPRITES, "box_closed.png"))
    s = 128 // max(icon.size)
    icon = icon.resize((icon.width * s, icon.height * s), Image.NEAREST)
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    canvas.alpha_composite(icon, ((128 - icon.width) // 2, (128 - icon.height) // 2))
    canvas.save(os.path.join(ROOT, "game", "icon.png"))
    print("ok")


if __name__ == "__main__":
    main()
