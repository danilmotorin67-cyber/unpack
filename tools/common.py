"""Общие части генератора: пути, комната, материалы, сохранение.

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

from iso import FACE_LEFT, FACE_RIGHT, FACE_TOP, Canvas, Mat, box, cyl, sphere
from palette import ALLOWED, rgba, shift
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES = os.path.join(ROOT, "game", "assets", "sprites")
FONT_DIR = os.path.join(ROOT, "game", "assets", "font")
SCRIPTS = os.path.join(ROOT, "game", "scripts")

VIEW_W, VIEW_H = 640, 360
ORIGIN = (306, 143)

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
M_METAL = Mat(top="s", left="S", right="x", edge="d", hi="W", gloss=True)

I_WHITE = Mat(top="W", left="c", right="C", edge="K", gloss=True)
I_METAL = Mat(top="s", left="S", right="x", edge="d", hi="W", gloss=True)
I_DARK = Mat(top="m", left="d", right="o", edge="o")
I_TERRA = Mat(top="i", left="r", right="R", edge="o", gloss=True)
I_OCHRE = Mat(top="y", left="Y", right="$", edge="o", gloss=True)
I_BLUE = Mat(top="l", left="L", right="z", edge="o", gloss=True)
I_GREEN = Mat(top="a", left="e", right="E", edge="o")
I_WOOD = Mat(top="A", left="w", right="v", edge="u", hi="q")
I_GLASS = Mat(top="O", left="t", right="T", edge="S", gloss=True)
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



# ---------------------------------------------------------------- room shell

def shell(floor_tex, wall_l_tex, wall_r_tex, m_floor=None, m_wall_l=None, m_wall_r=None):
    """Пол и две стены комнаты в разрезе."""
    return [
        box(-WALL, -WALL, -SLAB, RW, RD, 0, m_floor or M_FLOOR, floor_tex),
        box(-WALL, -WALL, 0, RW, 0, RH, m_wall_r or M_WALL_R, wall_r_tex),
        box(-WALL, 0, 0, 0, RD, RH, m_wall_l or M_WALL_L, wall_l_tex),
    ]


def _hash(*v):
    h = 0
    for x in v:
        h = (h * 1103515245 + int(x) * 2654435761 + 12345) & 0x7FFFFFFF
    return h


def planks(x, y, lit, width=7.0, length=36.0):
    """Доски пола вдоль оси x: у каждой доски свой тон, волокна, редкие сучки,
    тёмные швы. lit — пятно света из окна (на ступень светлее)."""
    row = math.floor(y / width)
    off = (row * 17) % length
    seg = math.floor((x + off) / length)
    h = _hash(row, seg)
    v = y - row * width
    u = (x + off) % length
    if v < 0.9 or u < 0.9:
        k = "p"
    else:
        k = ("f", "f", "F", "f", "f")[h % 5]
        # волокна: тонкие длинные полосы, у каждой доски свои
        g = (v * 1.9 + math.sin(u * 0.21 + h % 7) * 1.3 + (h % 5)) % 3.1
        if g < 0.28:
            k = shift(k, -1)
        # сучок
        if h % 9 == 0 and (u - 9 - h % 17) ** 2 + ((v - width / 2) * 2.2) ** 2 < 1.4:
            k = shift(k, -2)
    return shift(k, 1) if lit else k


def window(y, z, y0, y1, z0, z1, frame="W"):
    """Окно на левой стене: рама, переплёт, небо, холмы, солнце. None — не окно."""
    if not (y0 <= y <= y1 and z0 <= z <= z1):
        return None
    ym, zm = (y0 + y1) / 2, (z0 + z1) / 2
    if y < y0 + 2 or y > y1 - 2 or z < z0 + 2 or z > z1 - 2 or abs(y - ym) < 1 or abs(z - zm) < 0.8:
        return frame
    hill = z0 + (z1 - z0) * 0.27 + 3 * math.sin(y / 4.0)
    if z < hill - 3:
        return "E"
    if z < hill:
        return "e"
    if (y - (y1 - 11)) ** 2 + (z - (z1 - 8)) ** 2 < 10:
        return "y"
    return "t" if z > zm + 1 else "T"


def render_room(prims):
    cv = Canvas(VIEW_W, VIEW_H, ORIGIN)
    cv.add(prims)
    cv.light()
    cv.finish()
    img = cv.image()
    a = np.array(img)
    empty = a[..., 3] == 0
    shadow = np.zeros_like(empty)
    shadow[4:] = ~empty[:-4]
    a[empty] = rgba("W")
    a[empty & shadow] = rgba("c")
    return Image.fromarray(a, "RGBA")


def render_door(prims, room=()):
    cv = Canvas(VIEW_W, VIEW_H, ORIGIN)
    cv.add(prims)
    cv.light(extra=room)
    cv.finish()
    img = cv.image()
    bb = img.getbbox()
    x0, y0, x1, y1 = bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1
    return img.crop((x0, y0, x1, y1)), (x0, y0)
