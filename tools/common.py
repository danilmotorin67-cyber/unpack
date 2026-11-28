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
from palette import ALLOWED, rgba
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



# ---------------------------------------------------------------- room shell

def shell(floor_tex, wall_l_tex, wall_r_tex, m_floor=None, m_wall_l=None, m_wall_r=None):
    """Пол и две стены комнаты в разрезе."""
    return [
        box(-WALL, -WALL, -SLAB, RW, RD, 0, m_floor or M_FLOOR, floor_tex),
        box(-WALL, -WALL, 0, RW, 0, RH, m_wall_r or M_WALL_R, wall_r_tex),
        box(-WALL, 0, 0, 0, RD, RH, m_wall_l or M_WALL_L, wall_l_tex),
    ]


def planks(x, y, lit, light="q", base="f", alt_c="F", seam="p", seam_lit="F"):
    """Доски пола вдоль оси x."""
    row = math.floor(y / 7)
    seg = math.floor((x + row * 17) / 36)
    alt = (row * 7 + seg * 3) % 3 == 0
    if (y % 7) < 1 or ((x + row * 17) % 36) < 1:
        return seam_lit if lit else seam
    if lit:
        return base if alt else light
    return alt_c if alt else base


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


# на тон темнее — для теней
DARKER = {
    "q": "f", "f": "F", "F": "p", "p": "P", "W": "c", "c": "C", "C": "k", "k": "K",
    "t": "T", "T": "S", "l": "L", "L": "z", "z": "Z", "g": "G", "G": "h", "h": "H",
    "j": "J", "J": "k", "w": "v", "v": "u", "b": "B", "B": "n", "i": "r", "r": "R",
    "y": "Y", "a": "e", "e": "E", "s": "S", "S": "x",
}


def shadow_rects(prims, grow=1.5, shift=3.0):
    """Тени от мебели, стоящей на полу: след, чуть расширенный и сдвинутый от окна (+x)."""
    rects = []
    for pr in prims[3:]:  # первые три — пол и стены
        x0, y0, z0, x1, y1, z1 = pr.bounds()
        if z0 <= 0.5 and x1 - x0 > 1.5 and y1 - y0 > 1.5:
            rects.append((x0 - grow, y0 - grow, x1 + grow + shift, y1 + grow + shift * 0.4))
    return rects


def render_room(prims):
    cv = Canvas(VIEW_W, VIEW_H, ORIGIN)
    cv.add(prims)
    cv.floor_shadow(0, shadow_rects(prims), DARKER)
    cv.finish()
    img = cv.image()
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
