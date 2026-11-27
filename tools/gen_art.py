"""Генератор пиксель-арта для игры (изометрия).

Запуск из корня репозитория:
    python3 tools/gen_art.py

Пишет PNG в game/assets/, а геометрию уровня (зоны, якоря спрайтов) —
в game/scripts/art_data.gd. Каждый спрайт проверяется на палитру.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

from glyphs import CURSORS, GLYPHS
from iso import FACE_LEFT, FACE_RIGHT, FACE_TOP, Canvas, Mat, box, cyl, render_sprite, sphere
from palette import ALLOWED, rgba

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES = os.path.join(ROOT, "game", "assets", "sprites")
FONT_DIR = os.path.join(ROOT, "game", "assets", "font")
SCRIPTS = os.path.join(ROOT, "game", "scripts")

VIEW_W, VIEW_H = 480, 270
ORIGIN = (230, 108)

# Комната
RW, RD, RH, WALL, SLAB = 150, 130, 85, 6, 6
COUNTER_H, TOP_H = 36, 39

# ---------------------------------------------------------------- materials

M_WALL_L = Mat(top="C", left="K", right="c", edge="K", hi="W")
M_WALL_R = Mat(top="C", left="C", right="K", edge="K", hi="W")
M_FLOOR = Mat(top="f", left="p", right="P", edge="u", hi="q")
M_SAGE = Mat(top="g", left="G", right="h", edge="H", hi="g")
M_STOVE = Mat(top="L", left="z", right="Z", edge="o", hi="l")
M_TOP = Mat(top="j", left="J", right="J", edge="K", hi="W")
M_WOOD = Mat(top="w", left="v", right="u", edge="o", hi="q")
M_CREAM = Mat(top="c", left="C", right="k", edge="K", hi="W")
M_CREAM_IN = Mat(top="c", left="C", right="T", edge="K", hi="W")
M_FRIDGE_IN = Mat(top="t", left="T", right="T", edge="K")
M_SHELF_IN = Mat(top="t", left="T", right="T", edge="S", hi="W")
M_METAL = Mat(top="s", left="S", right="x", edge="d", hi="W")

I_WHITE = Mat(top="W", left="c", right="C", edge="K")
I_METAL = Mat(top="s", left="S", right="x", edge="d", hi="W")
I_DARK = Mat(top="m", left="d", right="o", edge="o")
I_TERRA = Mat(top="i", left="r", right="R", edge="o")
I_OCHRE = Mat(top="y", left="Y", right="n", edge="o")
I_BLUE = Mat(top="l", left="L", right="z", edge="o")
I_GREEN = Mat(top="a", left="e", right="E", edge="o")
I_WOOD = Mat(top="f", left="w", right="v", edge="u", hi="q")
I_GLASS = Mat(top="W", left="t", right="T", edge="S")
I_CARD = Mat(top="b", left="B", right="n", edge="N", hi="y")
I_CARD_BACK = Mat(top="b", left="n", right="n", edge="N", hi="y")
I_CARD_SIDE = Mat(top="b", left="B", right="N", edge="N", hi="y")
I_CARD_FLOOR = Mat(top="N", left="N", right="N", edge="N")


# ---------------------------------------------------------------- helpers

def check_palette(name, img):
    bad = {p for p in list(img.getdata()) if p[3] != 0 and p not in ALLOWED}
    if bad:
        sys.exit(f"{name}: цвета вне палитры: {sorted(bad)[:5]}")


def save(name, img, folder=SPRITES):
    check_palette(name, img)
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, name + ".png"))


def from_map(rows):
    w = max(len(r) for r in rows)
    img = Image.new("RGBA", (w, len(rows)), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch not in ". ":
                img.putpixel((x, y), rgba(ch))
    return img


# ---------------------------------------------------------------- kitchen textures

def floor_tex(x, y, z, face, k, nz):
    if face != FACE_TOP or z < -0.5:
        return None
    # коврик
    if 52 <= x <= 100 and 100 <= y <= 124:
        if x < 53.5 or x > 98.5:
            return "c" if int(y) % 2 else "C"
        if y < 101.5 or y > 122.5:
            return "H"
        return "G" if int((x - 52) // 4) % 2 else "h"
    row = math.floor(y / 7)
    seam = (y % 7) < 1
    joint = ((x + row * 17) % 36) < 1
    seg = math.floor((x + row * 17) / 36)
    alt = (row * 7 + seg * 3) % 3 == 0
    lit = x > 30 and (40 + 0.3 * x) < y < (93 + 0.3 * x)
    if seam or joint:
        return "F" if lit else "p"
    if lit:
        return "f" if alt else "q"
    return "F" if alt else "f"


def wall_left_tex(x, y, z, face, k, nz):
    if face != FACE_RIGHT:
        return None
    if z < 3:
        return "k"
    # окно
    if 44 <= y <= 92 and 50 <= z <= 80:
        if y < 46 or y > 90 or z < 52 or z > 78 or abs(y - 68) < 1 or abs(z - 65) < 0.8:
            return "W"
        hill = 58 + 3 * math.sin(y / 4.0) + (y - 44) * 0.05
        if z < hill - 3:
            return "E"
        if z < hill:
            return "e"
        if (y - 81) ** 2 + (z - 72) ** 2 < 10:
            return "y"
        return "t" if z > 66 else "T"
    # плитка под окном, над столешницей
    if 28 <= y <= 108 and TOP_H <= z <= 48:
        row = int((z - TOP_H) // 4.5)
        if (z - TOP_H) % 4.5 < 0.8 or ((y + (row % 2) * 4) % 8) < 0.9:
            return "C"
        return "W"
    # часы
    d = math.hypot(y - 16, z - 68)
    if d < 6.3:
        if d > 5.2:
            return "o"
        if (abs(y - 16) < 0.6 and 68 <= z < 72.5) or (abs(z - 68) < 0.6 and 16 <= y < 19.5):
            return "o"
        return "W"
    return None


def wall_right_tex(x, y, z, face, k, nz):
    if face != FACE_LEFT:
        return None
    if z < 3:
        return "k"
    # плитка над столешницей
    if 0 <= x <= 108 and TOP_H <= z <= 62:
        row = int((z - TOP_H) // 4.5)
        if (z - TOP_H) % 4.5 < 0.8 or ((x + (row % 2) * 4.5) % 9) < 0.9:
            return "k"
        return "c"
    # картина
    if 6 <= x <= 22 and 62 <= z <= 80:
        if x < 7.5 or x > 20.5 or z < 63.5 or z > 78.5:
            return "w"
        if z < 66 + 4 * math.sin((x - 6) / 3):
            return "e"
        return "T"
    return None


def door_fronts(u, z, x_mode):
    """Общий рисунок фасадов: цоколь, ящики, дверцы, ручки. u — координата вдоль фасада."""
    if z < 3:
        return "H"
    if abs(z - 27) < 0.6:
        return "H"
    if (u % 20) < 0.9 and u > 1:
        return "H"
    if z > 27:
        if 29.8 < z < 31.4 and abs((u % 20) - 10) < 3:
            return "s"
        return None
    if 15 < z < 22 and abs((u % 20) - 16.5) < 0.7:
        return "s"
    if abs(z - 5.5) < 0.5 or abs(z - 24.5) < 0.5:
        return "h" if x_mode else "h"
    return None


def cab_r_tex(x, y, z, face, k, nz):
    if face != FACE_LEFT:
        return None
    if x > 86:
        if z < 3 or abs(z - 27) < 0.6 or abs(x - 96.5) < 0.5:
            return "H"
        if 29.8 < z < 31.4 and (abs(x - 91.5) < 3 or abs(x - 102) < 3):
            return "s"
        if 15 < z < 22 and (abs(x - 94.5) < 0.7 or abs(x - 99) < 0.7):
            return "s"
        return None
    return door_fronts(x, z, False)


def cab_l_tex(x, y, z, face, k, nz):
    if face != FACE_RIGHT:
        return None
    return door_fronts(y - 28, z, True)


def stove_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT:
        if z < 3:
            return "Z"
        if 63 <= x <= 83 and 7 <= z <= 22:
            if x < 64 or x > 82 or z < 8 or z > 21:
                return "o"
            return "Z" if (x - z) % 9 > 2 else "z"
        if 64 <= x <= 82 and 24 <= z <= 25.2:
            return "s"
        for kx in (65.5, 71.5, 77.5, 83):
            if (x - kx) ** 2 + (z - 31.5) ** 2 < 1.6:
                return "S"
    return None


def counter_r_tex(x, y, z, face, k, nz):
    if face != FACE_TOP:
        return None
    if 60.5 <= x <= 85.5 and 1 <= y <= 28:
        for cx, cy in ((67, 8), (79, 8), (67, 21), (79, 21)):
            d = math.hypot(x - cx, y - cy)
            if d < 3.8:
                return "Z" if d > 2.6 or d < 0.9 else "z"
        return "L"
    return None


def counter_l_tex(x, y, z, face, k, nz):
    if face != FACE_TOP:
        return None
    if 5 <= x <= 24 and 54 <= y <= 82:
        if x < 6.2 or x > 22.8 or y < 55.2 or y > 80.8:
            return "s"
        if math.hypot(x - 15, y - 70) < 1:
            return "x"
        if x < 8 or y < 57.5:
            return "x"
        return "S"
    return None


def fridge_base_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT and 1.5 < z < 4.5 and (x % 2) < 0.8 and 116 < x < 138:
        return "k"
    return None


def fridge_door_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT:
        if abs(z - 52) < 0.6:
            return "K"
        if 137.4 <= x <= 139 and (55 < z < 66 or 38 < z < 49):
            return "s"
    return None


def fridge_door_inner_tex(x, y, z, face, k, nz):
    # внутренняя сторона открытой дверцы: полочки
    if face == FACE_RIGHT and 32.5 < y < 57.5:
        for bz in (18, 42, 64):
            if bz <= z <= bz + 4:
                return "s" if z > bz + 3.2 else "T"
        if 3 < z < 77:
            return "t"
    return None


def kitchen_prims():
    p = []
    # пол
    p.append(box(-WALL, -WALL, -SLAB, RW, RD, 0, M_FLOOR, floor_tex))
    # стены
    p.append(box(-WALL, -WALL, 0, RW, 0, RH, M_WALL_R, wall_right_tex))
    p.append(box(-WALL, 0, 0, 0, RD, RH, M_WALL_L, wall_left_tex))
    # шкафы
    p.append(box(0, 0, 0, 107, 28, COUNTER_H, M_SAGE, cab_r_tex))
    p.append(box(0, 28, 0, 28, 107, COUNTER_H, M_SAGE, cab_l_tex))
    p.append(box(60, 0, 0, 86, 28.6, COUNTER_H, M_STOVE, stove_tex))
    # столешницы
    p.append(box(0, 0, COUNTER_H, 108, 30, TOP_H, M_TOP, counter_r_tex))
    p.append(box(0, 30, COUNTER_H, 30, 108, TOP_H, M_TOP, counter_l_tex))
    # кран
    p.append(cyl(3.5, 68, 1, TOP_H, 49, M_METAL))
    p.append(box(3, 67.3, 47, 10, 68.7, 49, M_METAL))
    p.append(box(8.6, 67.3, 45, 10, 68.7, 47, M_METAL))
    # подоконник
    p.append(box(0, 42, 48, 9, 94, 50.5, M_TOP))
    # полка и кронштейны
    p.append(box(25, 0, 70, 100, 15, 73, M_WOOD))
    p.append(box(30, 0, 63, 32, 11, 70, M_WOOD))
    p.append(box(93, 0, 63, 95, 11, 70, M_WOOD))
    # холодильник (корпус, внутри полки; дверь — отдельный спрайт)
    p.append(box(112, 0, 0, 142, 28, 6, M_CREAM, fridge_base_tex))
    p.append(box(112, 0, 77, 142, 28, 80, M_CREAM))
    p.append(box(112, 0, 6, 142, 2, 77, M_FRIDGE_IN))
    p.append(box(112, 0, 6, 114, 28, 77, M_CREAM_IN))
    p.append(box(140, 0, 6, 142, 28, 77, M_CREAM))
    p.append(box(114, 2, 29, 140, 27, 31, M_SHELF_IN))
    p.append(box(114, 2, 53, 140, 27, 55, M_SHELF_IN))
    return p


FRIDGE_DOOR_CLOSED = [box(112, 28, 0.5, 142, 31, 79.5, M_CREAM, fridge_door_tex)]
FRIDGE_DOOR_OPEN = [box(109, 31, 0.5, 112, 59, 79.5, M_CREAM, fridge_door_inner_tex)]

ZONES = [
    {"id": "sill", "tag": "sill", "x0": 0, "y0": 43, "x1": 9, "y1": 93, "z": 50.5, "max_h": 30},
    {"id": "shelf", "tag": "shelf", "x0": 25, "y0": 0, "x1": 100, "y1": 15, "z": 73, "max_h": 12},
    {"id": "counter_r", "tag": "counter", "x0": 0, "y0": 0, "x1": 60, "y1": 30, "z": TOP_H, "max_h": 24},
    {"id": "stove", "tag": "stove", "x0": 60, "y0": 0, "x1": 86, "y1": 30, "z": TOP_H, "max_h": 24},
    {"id": "counter_r2", "tag": "counter", "x0": 86, "y0": 0, "x1": 108, "y1": 30, "z": TOP_H, "max_h": 24},
    {"id": "counter_l", "tag": "counter", "x0": 0, "y0": 30, "x1": 30, "y1": 108, "z": TOP_H, "max_h": 30},
    {"id": "fridge_top", "tag": "fridge_top", "x0": 112, "y0": 0, "x1": 142, "y1": 28, "z": 80, "max_h": 20},
    {"id": "fridge_0", "tag": "fridge", "x0": 116, "y0": 4, "x1": 138, "y1": 26, "z": 6, "max_h": 21, "container": "fridge"},
    {"id": "fridge_1", "tag": "fridge", "x0": 116, "y0": 4, "x1": 138, "y1": 26, "z": 31, "max_h": 20, "container": "fridge"},
    {"id": "fridge_2", "tag": "fridge", "x0": 116, "y0": 4, "x1": 138, "y1": 26, "z": 55, "max_h": 20, "container": "fridge"},
]


def render_kitchen():
    cv = Canvas(VIEW_W, VIEW_H, ORIGIN)
    cv.add(kitchen_prims())
    cv.finish()
    img = cv.image()
    # фон вокруг комнаты + мягкая тень под полом
    a = np.array(img)
    empty = a[..., 3] == 0
    shadow = np.zeros_like(empty)
    shadow[4:] = ~empty[:-4]
    a[empty] = rgba("W")
    a[empty & shadow] = rgba("c")
    return Image.fromarray(a, "RGBA")


def render_door(prims):
    cv = Canvas(VIEW_W, VIEW_H, ORIGIN)
    cv.add(prims)
    cv.finish()
    img = cv.image()
    bb = img.getbbox()
    x0, y0, x1, y1 = bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1
    return img.crop((x0, y0, x1, y1)), (x0, y0)


# ---------------------------------------------------------------- items

def plates_tex(x, y, z, face, k, nz):
    if face == FACE_TOP:
        return "c" if math.hypot(x, y) < 2.8 else "W"
    if (z % 1.07) < 0.3:
        return "k"
    return None


def cup_top(inner_r, inner, rim=None):
    def tex(x, y, z, face, k, nz):
        if face == FACE_TOP and nz < 1.5:
            return inner if math.hypot(x, y) < inner_r else rim
        return None
    return tex


def bowl_tex(x, y, z, face, k, nz):
    if nz > 1.5:
        return "l" if math.hypot(x, y) > 3.4 else "z"
    return None


def board_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and math.hypot(x - 6.4, y) < 0.6:
        return "u"
    if face == FACE_TOP and (y % 2.5) < 0.4 and x < 4.5:
        return "w"
    return None


def soap_tex(x, y, z, face, k, nz):
    if face != FACE_TOP and 1.5 < z < 3.6:
        return "W" if face == FACE_LEFT else "c"
    return None


def milk_tex(x, y, z, face, k, nz):
    if face != FACE_TOP and 2.2 < z < 4.4:
        return "l" if face == FACE_LEFT else "L"
    return None


def cheese_tex(x, y, z, face, k, nz):
    for hx, hy, hz in ((1, 1.6, 1.2), (-1.4, 1.6, 1.8), (2.6, -0.4, 1), (0.2, -0.2, 2.6), (2.6, 1, 2)):
        if (x - hx) ** 2 + (y - hy) ** 2 + (z - hz) ** 2 < 0.45:
            return "Y" if face == FACE_TOP else "n"
    return None


def handle(y0, y1, z0, z1, mat, t=0.5):
    return [
        box(-t, y0, z1 - 0.7, t, y1, z1, mat),
        box(-t, y0, z0, t, y1, z0 + 0.7, mat),
        box(-t, y1 - 0.7, z0, t, y1, z1, mat),
    ]


ITEMS = {
    "plates": [cyl(0, 0, 4.5, 0, 3.2, I_WHITE, plates_tex)],
    "bowl": [sphere(0, 0, 4.2, 4.2, I_BLUE, bowl_tex, zmax=4.2)],
    "mug_yellow": [cyl(0, 0, 2.5, 0, 5.5, I_OCHRE, cup_top(1.8, "u"))] + handle(2.4, 3.9, 1.5, 4.5, I_OCHRE),
    "mug_blue": [cyl(0, 0, 2.5, 0, 5.5, I_BLUE, cup_top(1.8, "u"))] + handle(2.4, 3.9, 1.5, 4.5, I_BLUE),
    "glass": [cyl(0, 0, 1.9, 0, 5, I_GLASS, cup_top(1.3, "t"))],
    "pot": [
        cyl(0, 0, 4.5, 0, 5, I_METAL),
        cyl(0, 0, 4.7, 5, 5.6, I_METAL),
        cyl(0, 0, 1, 5.6, 6.6, I_DARK),
        box(4.2, -0.8, 3.6, 6.2, 0.8, 4.6, I_DARK),
        box(-0.8, 4.2, 3.6, 0.8, 6.2, 4.6, I_DARK),
    ],
    "pan": [
        cyl(0, 0, 4.5, 0, 1.6, I_DARK, cup_top(3.6, "d", "m")),
        box(4, -0.7, 0.6, 11, 0.7, 1.6, I_WOOD),
    ],
    "kettle": [
        cyl(0, 0, 3.6, 0, 5.5, I_TERRA),
        cyl(0, 0, 2, 5.5, 6.3, I_TERRA),
        sphere(0, 0, 6.8, 0.8, I_DARK),
        box(-0.6, 3.3, 2, 0.6, 6, 3.2, I_TERRA),
        box(-0.6, 5.2, 3.2, 0.6, 6, 4.4, I_TERRA),
        box(-0.5, -2.6, 5.5, 0.5, -1.8, 8.3, I_DARK),
        box(-0.5, 1.8, 5.5, 0.5, 2.6, 8.3, I_DARK),
        box(-0.5, -2.6, 7.6, 0.5, 2.6, 8.3, I_DARK),
    ],
    "cutting_board": [box(-5, -3.5, 0, 5, 3.5, 1.3, I_WOOD, board_tex), box(5, -1.2, 0, 7.5, 1.2, 1.3, I_WOOD, board_tex)],
    "knife_block": [
        box(-2, -2.6, 0, 2, 2.6, 6, I_WOOD),
        box(-1.6, -1.6, 6, -0.6, -0.6, 8.6, I_DARK),
        box(-0.5, -0.5, 6, 0.5, 0.5, 8.1, I_DARK),
        box(0.6, 0.6, 6, 1.6, 1.6, 7.6, I_DARK),
    ],
    "soap": [
        box(-1.2, -1.2, 0, 1.2, 1.2, 5, I_GREEN, soap_tex),
        cyl(0, 0, 0.5, 5, 6.5, I_DARK),
        box(-0.3, 0, 6, 0.3, 1.8, 6.6, I_DARK),
    ],
    "plant": [
        cyl(0, 0, 2.6, 0, 3.4, I_TERRA),
        cyl(0, 0, 3, 3.2, 4.2, I_TERRA, cup_top(2.4, "u")),
        sphere(0.8, 1.4, 5.4, 1.3, I_GREEN),
        sphere(-1.4, -1.1, 5.6, 1.3, I_GREEN),
        sphere(0, 0, 6, 1.9, I_GREEN),
        sphere(1.2, -0.8, 7.6, 1.4, I_GREEN),
        sphere(-1, 1, 7.2, 1.4, I_GREEN),
        sphere(0.2, 0.2, 8.8, 1.1, I_GREEN),
    ],
    "milk": [
        box(-1.6, -1.6, 0, 1.6, 1.6, 6.5, I_WHITE, milk_tex),
        box(-1.6, -0.5, 6.5, 1.6, 0.5, 7.6, I_WHITE),
        cyl(0.7, 1.0, 0.5, 6.4, 7.2, I_BLUE),
    ],
    "cheese": [box(-2.6, -1.6, 0, 2.6, 1.6, 2.6, I_OCHRE, cheese_tex)],
    "spices": [
        cyl(0, -1.2, 1, 0, 3.2, I_OCHRE),
        cyl(0, -1.2, 1.05, 3.2, 3.9, I_DARK),
        cyl(0, 1.2, 1, 0, 3.2, I_TERRA),
        cyl(0, 1.2, 1.05, 3.2, 3.9, I_DARK),
    ],
}


ITEM_SCALE = 1.5


def scaled(prims, k):
    """Масштабирует модель предмета (текстуры остаются в исходных единицах)."""
    from iso import Prim
    out = []
    for pr in prims:
        q = {key: (v * k if isinstance(v, (int, float)) and v is not None else v) for key, v in pr.p.items()}
        tex = pr.tex
        if tex is not None:
            tex = (lambda t: lambda x, y, z, f, key, nz: t(x / k, y / k, z / k, f, key, nz))(tex)
        out.append(Prim(pr.kind, pr.mat, tex, **q))
    return out


def footprint(prims):
    xs0, ys0, xs1, ys1, zs1 = [], [], [], [], []
    for pr in prims:
        x0, y0, z0, x1, y1, z1 = pr.bounds()
        if pr.p.get("zmax") is not None:
            z1 = min(z1, pr.p["zmax"])
        xs0.append(x0); ys0.append(y0); xs1.append(x1); ys1.append(y1); zs1.append(z1)
    return min(xs0), min(ys0), max(xs1), max(ys1), max(zs1)


# ---------------------------------------------------------------- cardboard box

BOX_X, BOX_Y, BOX_H = 11, 9, 15


def box_side_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT and y > BOX_Y - 0.5:
        if -8 <= x <= -1 and 6 <= z <= 10.5 and (z % 1.8) < 0.6:
            return "N"
        if 4.5 <= x <= 5.5 and 5 <= z <= 10:
            return "N"
        if 3 <= x <= 7 and 10 - abs(x - 5) * 0.8 <= z <= 10.6 - abs(x - 5) * 0.8 + 0.6:
            return "N"
    return None


def box_closed_tex(x, y, z, face, k, nz):
    if abs(y) < 1.6 and (face == FACE_TOP or (face == FACE_RIGHT and z > 11)):
        return "C" if face == FACE_TOP else "k"
    return box_side_tex(x, y, z, face, k, nz)


BOX_CLOSED = [box(-BOX_X, -BOX_Y, 0, BOX_X, BOX_Y, BOX_H, I_CARD, box_closed_tex)]
BOX_OPEN = [
    box(-BOX_X, -BOX_Y, 0, BOX_X, -BOX_Y + 1, BOX_H, I_CARD_BACK),
    box(-BOX_X, -BOX_Y + 1, 0, -BOX_X + 1, BOX_Y, BOX_H, I_CARD_SIDE),
    box(-BOX_X + 1, BOX_Y - 1, 0, BOX_X, BOX_Y, BOX_H, I_CARD, box_side_tex),
    box(BOX_X - 1, -BOX_Y + 1, 0, BOX_X, BOX_Y - 1, BOX_H, I_CARD),
    box(-BOX_X + 1, -BOX_Y + 1, 0, BOX_X - 1, BOX_Y - 1, 1, I_CARD_FLOOR),
    # створки
    box(-BOX_X, -BOX_Y - 1.4, BOX_H, BOX_X, -BOX_Y, BOX_H + 7, I_CARD),
    box(-BOX_X - 1.4, -BOX_Y, BOX_H, -BOX_X, BOX_Y, BOX_H + 7, I_CARD),
    box(-BOX_X, BOX_Y, BOX_H - 0.8, BOX_X, BOX_Y + 6, BOX_H, I_CARD),
    box(BOX_X, -BOX_Y, BOX_H - 0.8, BOX_X + 6, BOX_Y, BOX_H, I_CARD),
]


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


def main():
    for old in os.listdir(SPRITES) if os.path.isdir(SPRITES) else []:
        if old.endswith(".png") or old.endswith(".png.import"):
            os.remove(os.path.join(SPRITES, old))

    out = [
        "# Сгенерировано tools/gen_art.py — не редактировать вручную.",
        "# Мировые координаты: x — вдоль правой стены, y — вдоль левой, z — вверх.",
        "# Экран = ORIGIN + (x - y, (x + y) / 2 - z).",
        "extends RefCounted",
        "",
        f"const ORIGIN := {v2(ORIGIN)}",
        f"const ROOM := Vector3({RW}, {RD}, {RH})",
        "",
        "const ITEMS := {",
    ]
    for name, prims in ITEMS.items():
        prims = scaled(prims, ITEM_SCALE)
        img, anchor = render_sprite(prims)
        save("item_" + name, img)
        x0, y0, x1, y1, h = footprint(prims)
        # след чуть меньше габарита: ручки и края могут нависать
        sh = 1.5
        x0, y0 = min(x0 + sh, -1.5), min(y0 + sh, -1.5)
        x1, y1 = max(x1 - sh, 1.5), max(y1 - sh, 1.5)
        out.append(
            f'\t"{name}": {{"anchor": {v2(anchor)}, '
            f'"foot": Rect2({num(x0)}, {num(y0)}, {num(x1 - x0)}, {num(y1 - y0)}), "h": {num(h)}}},'
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
    ]

    save("kitchen_bg", render_kitchen())
    img, pos_c = render_door(FRIDGE_DOOR_CLOSED)
    save("fridge_closed", img)
    img, pos_o = render_door(FRIDGE_DOOR_OPEN)
    save("fridge_open", img)
    out += [
        "",
        "# двери: левый верхний угол спрайта на экране; depth — для сортировки",
        "const DOORS := {",
        f'\t"fridge": {{"closed_pos": {v2(pos_c)}, "open_pos": {v2(pos_o)}, "closed_depth": {142 + 31}, "open_depth": {112 + 59}}},',
        "}",
        "",
        "# поверхности: прямоугольник x0..x1, y0..y1 на высоте z",
        "const ZONES := [",
    ]
    for z in ZONES:
        fields = ", ".join(
            f'"{k}": "{v}"' if isinstance(v, str) else f'"{k}": {num(v)}' for k, v in z.items()
        )
        out.append(f"\t{{{fields}}},")
    out.append("]")
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
