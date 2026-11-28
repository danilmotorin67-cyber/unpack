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


# ---------------------------------------------------------------- ткани
# Текстуры-модификаторы: получают уже затонированный ключ k и сдвигают его
# по рампе (shift). Их можно соединять через chain().

def chain(*texs):
    """Применяет текстуры по очереди: каждая получает результат предыдущей."""
    def tex(x, y, z, face, k, nz):
        for t in texs:
            if t is None:
                continue
            r = t(x, y, z, face, k, nz)
            if r is not None:
                k = r
        return k
    return tex


def folds(freq=0.9, strength=1, phase=0.0, faces=(FACE_LEFT, FACE_RIGHT)):
    """Вертикальные складки свисающей ткани: гребни светлее, впадины темнее."""
    def tex(x, y, z, face, k, nz):
        if face not in faces:
            return None
        u = x if face == FACE_LEFT else y
        s = math.sin(u * freq + phase + 0.7 * math.sin(z * 0.3 + u * 0.2))
        if s > 0.72:
            return shift(k, strength)
        if s < -0.5:
            return shift(k, -strength)
        return None
    return tex


def puff(x0, y0, x1, y1, z0=None, z1=None, edge=1.4):
    """Пухлая ткань (подушки, диванные подушки, матрас): края верхней грани
    темнее, ближе к свету — блик, низ боковых граней в тени."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hh = (x1 - x0) / 2, (y1 - y0) / 2

    def tex(x, y, z, face, k, nz):
        if face == FACE_TOP:
            d = min(x - x0, x1 - x, y - y0, y1 - y)
            if d < edge * 0.55:
                return shift(k, -1)
            if ((x - cx + hw * 0.25) / hw) ** 2 + ((y - cy - hh * 0.2) / hh) ** 2 < 0.22:
                return shift(k, 1)
            return None
        if z0 is not None and z1 is not None and z < z0 + (z1 - z0) * 0.35:
            return shift(k, -1)
        return None
    return tex


def wrinkles(scale=1.0, faces=(FACE_TOP,)):
    """Редкие заломы на лежащей ткани."""
    def tex(x, y, z, face, k, nz):
        if face not in faces:
            return None
        s = math.sin((x * 0.45 + y * 0.28) * scale + 2.2 * math.sin(y * 0.17 * scale))
        if s > 0.94:
            return shift(k, 1)
        if s < -0.95:
            return shift(k, -1)
        return None
    return tex


def weave(step=1.6):
    """Мелкое плетение: шахматка сдвигов в половину тона на ковре/полотенце."""
    def tex(x, y, z, face, k, nz):
        if face == FACE_TOP and (int(x / step) + int(y / step)) % 2 == 0 and (int(x * 2.3) % 3 == 0):
            return shift(k, -1)
        return None
    return tex


def curtain(y0, y1, z0, z1, mat, gap=None, d=1.6):
    """Шторы на левой стене: две полотнища по краям окна y0..y1, карниз сверху.
    Возвращает список примитивов."""
    w = 7
    out = [
        box(0, y0 - w - 2, z1 + 2, 2.2, y1 + w + 2, z1 + 3.2, M_WOOD),
        box(0, y0 - w, z0 - 6, d, y0 + 1, z1 + 2, mat, folds(1.4, 1, 0.3, faces=(FACE_RIGHT,))),
        box(0, y1 - 1, z0 - 6, d, y1 + w, z1 + 2, mat, folds(1.4, 1, 1.9, faces=(FACE_RIGHT,))),
    ]
    return out


# ---------------------------------------------------------------- фактура стен
# Узор ложится только туда, где текстура комнаты ничего не нарисовала
# (окна, плитка, розетки остаются как есть). u — координата вдоль стены.

def under(tex, pattern):
    def t(x, y, z, face, k, nz):
        r = tex(x, y, z, face, k, nz) if tex else None
        if r is not None:
            return r
        if face == FACE_TOP or z < 3.2 or z > RH - 1.5:
            return None
        u = y if face == FACE_RIGHT else x
        return pattern(u, z, k)
    return t


def paper_dots(u, z, k):
    """Обои в мелкий горошек, точки в шахматном порядке."""
    row = int(z // 6)
    cu = (u + (row % 2) * 4) % 8 - 4
    cz = z % 6 - 3
    if cu * cu + cz * cz < 0.9:
        return shift(k, -1)
    return None


def plaster(u, z, k):
    """Штукатурка: редкие мягкие пятнышки на ступень темнее и светлее."""
    h = _hash(int(u * 1.4), int(z * 1.4))
    if h % 29 == 0 or (h % 29 == 1 and _hash(int(u * 1.4) + 1, int(z * 1.4)) % 3 == 0):
        return shift(k, -1)
    if h % 41 == 2:
        return shift(k, 1)
    return None


def sprigs(u, z, k):
    """Веточки между полосами обоев: стебелёк и два листика."""
    cu = u % 10 - 5
    cz = (z + (int(u // 10) % 2) * 6) % 12 - 6
    if abs(cu) < 0.45 and -2.2 < cz < 1.6:
        return shift(k, -1)
    if (abs(cu - 1) < 0.6 and abs(cz - 0.6) < 0.6) or (abs(cu + 1) < 0.6 and abs(cz + 0.8) < 0.6):
        return shift(k, -1)
    return None


def damask(u, z, k):
    """Дамаск: крестики-цветки в шахматном порядке (выше стеновых панелей)."""
    if z < 31.5:
        return None
    row = int(z // 9)
    cu = (u + (row % 2) * 6) % 12 - 6
    cz = z % 9 - 4.5
    if (abs(cu) < 0.5 and abs(cz) < 2.2) or (abs(cz) < 0.5 and abs(cu) < 2.2):
        return shift(k, -1)
    if abs(cu) + abs(cz) < 0.9:
        return shift(k, -2)
    return None
