"""Модели предметов и коробки."""
import math

from common import *  # noqa: F401,F403
from iso import Prim


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


# ---------------------------------------------------------------- ванная и спальня

I_CREAM = Mat(top="W", left="c", right="k", edge="K")
I_SPONGE = Mat(top="y", left="Y", right="n", edge="o")
I_SILVER = Mat(top="s", left="S", right="x", edge="o", hi="W")


def band_tex(z0, z1, left, right):
    def tex(x, y, z, face, k, nz):
        if face != FACE_TOP and z0 < z < z1:
            return left if face == FACE_LEFT else right
        return None
    return tex


def tube_tex(x, y, z, face, k, nz):
    if x > 1.6:
        return {FACE_TOP: "i", FACE_LEFT: "r", FACE_RIGHT: "R"}[face]
    return None


def sponge_tex(x, y, z, face, k, nz):
    if face != FACE_TOP and (int(x * 1.7) * 3 + int(z * 2.3) * 5 + int(y * 1.3)) % 7 == 0:
        return "n"
    return None


def fold_tex(dark):
    def tex(x, y, z, face, k, nz):
        if face == FACE_LEFT and (z % 0.8) < 0.25:
            return dark
        if face == FACE_TOP and abs(x - 1) < 0.25:
            return dark
        return None
    return tex


def knit_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and (int(x * 2) + int(y)) % 3 == 0:
        return "r"
    if face == FACE_LEFT and (z % 0.6) < 0.2:
        return "R"
    return None


def tshirt_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and math.hypot(x - 0.3, y) < 1.3:
        return "y"
    return None


def pages_tex(x, y, z, face, k, nz):
    if face == FACE_RIGHT and 0.2 < z < (z % 100) + 1 and y < 1.6:
        return "c" if (z % 0.5) < 0.3 else "C"
    return None


def book(mat, z0=0.0, h=1.2, dx=0.0):
    def tex(x, y, z, face, k, nz):
        if face == FACE_RIGHT and z0 + 0.25 < z < z0 + h - 0.25 and y < 1.5:
            return "c"
        if face == FACE_LEFT and z0 + 0.25 < z < z0 + h - 0.25 and x > -2.2 + dx:
            return "W"
        return None
    return [box(-2.5 + dx, -1.8, z0, 2.5 + dx, 1.8, z0 + h, mat, tex)]


def screen_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT and -3 < x < 3 and 1.1 < z < 4.5:
        return "L" if (x - z) % 3 > 0.6 else "l"
    return None


def clock_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT:
        d = math.hypot(x, z - 1.7)
        if d < 1.3:
            if (abs(x) < 0.25 and 1.7 < z < 2.7) or (abs(z - 1.7) < 0.25 and 0 < x < 0.8):
                return "o"
            return "W"
    return None


def frame_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT and -1.3 < x < 1.3 and 0.5 < z < 2.7:
        return "e" if z < 1.1 + 0.4 * math.sin(x * 2) else "t"
    return None


def globe_tex(x, y, z, face, k, nz):
    if math.sin(x * 1.6) + math.cos(y * 1.4 + z * 0.9) > 0.9:
        return "e" if face != FACE_RIGHT else "E"
    return None


ITEMS.update({
    # ванная
    "toothbrush_cup": [
        cyl(0, 0, 1.6, 0, 3.5, I_BLUE, cup_top(1.1, "z")),
        box(-0.7, -0.4, 3, -0.1, 0.2, 6.5, I_WHITE),
        box(-0.9, -0.5, 5.6, 0.1, 0.3, 6.6, I_WHITE),
        box(0.2, -0.1, 3, 0.8, 0.5, 6, I_TERRA),
    ],
    "toothpaste": [
        box(-3, -0.9, 0, 3, 0.9, 1.4, I_WHITE, tube_tex),
        box(3, -0.6, 0.2, 3.8, 0.6, 1.2, I_DARK),
    ],
    "soap_dish": [
        box(-2.4, -1.7, 0, 2.4, 1.7, 0.7, I_GLASS),
        box(-1.6, -1.1, 0.7, 1.6, 1.1, 1.9, I_GREEN),
    ],
    "shampoo": [
        box(-1.3, -1, 0, 1.3, 1, 5.5, I_BLUE, band_tex(2, 3.8, "W", "c")),
        cyl(0, 0, 0.8, 5.5, 6.6, I_WHITE),
    ],
    "shower_gel": [
        cyl(0, 0, 1.3, 0, 5, I_OCHRE, band_tex(1.5, 3.2, "W", "c")),
        cyl(0, 0, 0.9, 5, 6.3, I_DARK),
    ],
    "duck": [
        sphere(0, 0, 1.6, 1.7, I_OCHRE),
        sphere(0, 0.9, 3.5, 1.1, I_OCHRE),
        box(-0.4, 1.7, 3.1, 0.4, 2.6, 3.6, I_TERRA),
    ],
    "sponge": [
        box(-2, -1.3, 0, 2, 1.3, 1.6, I_SPONGE, sponge_tex),
        box(-2, -1.3, 1.6, 2, 1.3, 2.1, I_GREEN),
    ],
    "towel_blue": [box(-3.5, -2.5, 0, 3.5, 2.5, 2.4, I_BLUE, fold_tex("z"))],
    "towel_white": [box(-3.5, -2.5, 0, 3.5, 2.5, 2.4, I_CREAM, fold_tex("k"))],
    "toilet_paper": [cyl(0, 0, 1.7, 0, 3, I_CREAM, cup_top(0.6, "k"))],
    "perfume": [
        box(-1, -0.6, 0, 1, 0.6, 3, I_GLASS),
        box(-0.4, -0.3, 3, 0.4, 0.3, 4, I_OCHRE),
    ],
    "cream": [
        cyl(0, 0, 1.5, 0, 1.6, I_WHITE),
        cyl(0, 0, 1.55, 1.6, 2.3, I_BLUE),
    ],
    "cactus": [
        cyl(0, 0, 1.8, 0, 2.4, I_TERRA, cup_top(1.4, "u")),
        cyl(0, 0, 1.1, 2.4, 5.6, I_GREEN),
        sphere(0, 0, 5.6, 1.1, I_GREEN),
        box(-0.5, 0.9, 3.4, 0.5, 2, 4.2, I_GREEN),
        box(-0.5, 1.4, 4.2, 0.5, 2, 5.4, I_GREEN),
    ],
    "hairbrush": [
        box(-3.5, -0.6, 0, 0.5, 0.6, 0.8, I_WOOD),
        box(0.5, -1.3, 0, 3.5, 1.3, 1, I_WOOD),
        box(0.8, -1, 1, 3.2, 1, 1.5, I_DARK),
    ],
    # спальня
    "bunny": [
        sphere(0, 0, 2, 2, I_CREAM),
        sphere(0, 0.3, 4.6, 1.5, I_CREAM),
        box(-0.9, -0.1, 5.6, -0.2, 0.5, 8, I_CREAM),
        box(0.2, -0.1, 5.6, 0.9, 0.5, 8, I_CREAM),
    ],
    "lamp": [
        cyl(0, 0, 1.5, 0, 0.8, I_WOOD),
        cyl(0, 0, 0.35, 0.8, 5, I_DARK),
        cyl(0, 0, 2.4, 5, 8, I_CREAM),
    ],
    "alarm_clock": [
        box(-1.8, -1, 0, 1.8, 1, 3.4, I_TERRA, clock_tex),
        sphere(-1.1, 0, 3.6, 0.7, I_SILVER),
        sphere(1.1, 0, 3.6, 0.7, I_SILVER),
    ],
    "book_red": book(I_TERRA),
    "book_blue": book(I_BLUE) + book(I_GREEN, 1.2, 1.0, 0.4),
    "laptop": [
        box(-3.5, -2.5, 0, 3.5, 2.5, 0.6, I_SILVER),
        box(-3.5, -2.5, 0.6, 3.5, -2, 5, I_SILVER, screen_tex),
    ],
    "pencil_cup": [
        cyl(0, 0, 1.2, 0, 3, I_TERRA),
        box(-0.5, -0.3, 3, -0.1, 0.1, 5, I_OCHRE),
        box(0.1, 0, 3, 0.5, 0.4, 4.6, I_BLUE),
        box(-0.2, 0.3, 3, 0.2, 0.7, 4.3, I_GREEN),
    ],
    "sweater": [box(-3, -2.5, 0, 3, 2.5, 1.8, I_TERRA, knit_tex)],
    "jeans": [box(-3, -2.5, 0, 3, 2.5, 1.4, I_BLUE, fold_tex("z"))],
    "tshirt": [box(-3, -2.5, 0, 3, 2.5, 1, I_CREAM, tshirt_tex)],
    "sneakers": [
        box(-3, -2.2, 0, 2.5, -0.4, 1.5, I_CREAM, band_tex(-1, 0.4, "k", "K")),
        box(-3, 0.4, 0, 2.5, 2.2, 1.5, I_CREAM, band_tex(-1, 0.4, "k", "K")),
        box(-3, -2.2, 1.5, -0.5, -0.4, 2.6, I_CREAM),
        box(-3, 0.4, 1.5, -0.5, 2.2, 2.6, I_CREAM),
    ],
    "photo_frame": [
        box(-1.8, -0.4, 0, 1.8, 0.4, 3.2, I_WOOD, frame_tex),
        box(-0.4, -1.4, 0, 0.4, -0.4, 1.8, I_WOOD),
    ],
    "globe": [
        cyl(0, 0, 1.2, 0, 0.6, I_WOOD),
        cyl(0, 0, 0.3, 0.6, 1.8, I_DARK),
        sphere(0, 0, 3.6, 2, I_BLUE, globe_tex),
    ],
    "headphones": [
        cyl(0, -2.1, 1.1, 0, 1.6, I_DARK),
        cyl(0, 2.1, 1.1, 0, 1.6, I_DARK),
        box(-0.4, -2.4, 1.6, 0.4, -1.8, 3.6, I_DARK),
        box(-0.4, 1.8, 1.6, 0.4, 2.4, 3.6, I_DARK),
        box(-0.4, -2.4, 3.6, 0.4, 2.4, 4.2, I_TERRA),
    ],
})


ITEM_SCALE = 1.5


def scaled(prims, k):
    """Масштабирует модель предмета (текстуры остаются в исходных единицах)."""
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
