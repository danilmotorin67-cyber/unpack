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
I_SPONGE = Mat(top="y", left="Y", right="$", edge="o")
I_SILVER = Mat(top="s", left="S", right="x", edge="o", hi="W", gloss=True)


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
    "towel_blue": [box(-3.5, -2.5, 0, 3.5, 2.5, 2.4, I_BLUE, chain(fold_tex("z"), puff(-3.5, -2.5, 3.5, 2.5, 0, 2.4, edge=1.2)))],
    "towel_white": [box(-3.5, -2.5, 0, 3.5, 2.5, 2.4, I_CREAM, chain(fold_tex("k"), puff(-3.5, -2.5, 3.5, 2.5, 0, 2.4, edge=1.2)))],
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
    "sweater": [box(-3, -2.5, 0, 3, 2.5, 1.8, I_TERRA, chain(knit_tex, puff(-3, -2.5, 3, 2.5, 0, 1.8, edge=1.0)))],
    "jeans": [box(-3, -2.5, 0, 3, 2.5, 1.4, I_BLUE, chain(fold_tex("z"), puff(-3, -2.5, 3, 2.5, 0, 1.4, edge=1.0), wrinkles(2.5)))],
    "tshirt": [box(-3, -2.5, 0, 3, 2.5, 1, I_CREAM, chain(tshirt_tex, puff(-3, -2.5, 3, 2.5, 0, 1, edge=1.0), wrinkles(2.5)))],
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


ITEM_SCALE = 1.7
# мелкие вещи рисуем крупнее, иначе на них не хватает пикселей
SMALL_SCALE = 2.3
SMALL_ITEMS = {
    "remote", "candles", "spices", "soap", "perfume", "cream", "toothpaste",
    "pencil_cup", "photo_frame", "headphones", "alarm_clock", "cheese", "duck",
    "sponge", "cactus", "hairbrush", "soap_dish", "shower_gel", "shampoo", "glass",
}


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


# ---------------------------------------------------------------- вещи на стенах
#
# Модель задаётся в координатах стены: u — вдоль стены (слева направо, как
# видит игрок), v — вверх, d — от стены в комнату. Начало координат — центр
# задней стороны предмета. Для левой стены (плоскость x=0) u = -y, d = x;
# для правой (y=0) u = x, d = y. Текстура рисует лицевую сторону tex(u, v).

def wall_box(u0, u1, v0, v1, d0, d1, mat, tex, side):
    if side == "L":
        def wrap(x, y, z, face, k, nz):
            return tex(-y, z) if tex and face == FACE_RIGHT and x > d1 - 0.3 else None
        return box(d0, -u1, v0, d1, -u0, v1, mat, wrap)

    def wrap(x, y, z, face, k, nz):
        return tex(x, z) if tex and face == FACE_LEFT and y > d1 - 0.3 else None
    return box(u0, d0, v0, u1, d1, v1, mat, wrap)


def wall_disc(r, d0, d1, mat, tex, side, step=0.3):
    out = []
    v = -r
    while v < r:
        vc = v + step / 2
        half = math.sqrt(max(r * r - vc * vc, 0))
        if half > 0.2:
            out.append(wall_box(-half, half, v, v + step, d0, d1, mat, tex, side))
        v += step
    return out


def landscape_tex(u, v):
    if abs(u) > 5.2 or abs(v) > 3.7:
        return None  # рама
    if v < -1.5 + 1.2 * math.sin(u * 0.8):
        return "E" if v < -2.6 else "e"
    if math.hypot(u - 2.6, v - 1.6) < 1.1:
        return "y"
    if v < 0.6 - abs(u + 1.5) * 0.9:
        return "L"
    return "t"


def flowers_tex(u, v):
    if abs(u) > 2.8 or abs(v) > 4.3:
        return None
    if -1.1 < u < 1.1 and -4.3 < v < -1.6:
        return "l" if u < 0.3 else "L"
    for fu, fv, c in ((-1.2, 1.4, "r"), (0.6, 2.3, "y"), (1.4, 0.6, "i"), (-0.2, 0.2, "r")):
        if math.hypot(u - fu, v - fv) < 0.8:
            return c
    if abs(u - (v + 1.6) * 0.2) < 0.25 and -1.6 < v < 1.8:
        return "E"
    return "c"


def clock_face_tex(u, v):
    d = math.hypot(u, v)
    if d > 3.1:
        return "o"
    if (abs(u) < 0.3 and 0 < v < 2.2) or (abs(v) < 0.3 and 0 < u < 1.6):
        return "o"
    for a in range(12):
        ang = a * math.pi / 6
        if math.hypot(u - 2.5 * math.cos(ang), v - 2.5 * math.sin(ang)) < 0.3:
            return "m"
    return "W"


def mirror_tex(u, v):
    if math.hypot(u, v) > 3.5:
        return None
    if 0 < (u + v) + 1.5 < 0.9 or 0 < (u + v) + 0.3 < 0.4:
        return "W"
    return "t"


def poster_tex(u, v):
    if abs(u) > 4.0 or abs(v) > 5.5:
        return None
    if math.hypot(u + 1, v - 2.5) < 1.4:
        return "y"
    if v < -1 + 2 * math.sin(u * 0.7):
        return "z" if v < -3 else "L"
    if -3.5 < u < 3.5 and -5 < v < -4.2:
        return "o"
    return "c"


def small_picture_tex(u, v):
    if abs(u) > 2.3 or abs(v) > 2.8:
        return None
    if v < -0.6 + 0.8 * math.sin(u * 1.2):
        return "e"
    if math.hypot(u - 1, v - 1.2) < 0.7:
        return "y"
    return "T"


WALL_ITEMS = {
    "painting_landscape": lambda s: [wall_box(-6, 6, -4.5, 4.5, 0, 0.8, I_WOOD, landscape_tex, s)],
    "painting_flowers": lambda s: [wall_box(-3.5, 3.5, -5, 5, 0, 0.8, I_OCHRE, flowers_tex, s)],
    "wall_clock": lambda s: wall_disc(3.8, 0, 0.9, I_WHITE, clock_face_tex, s),
    "mirror_round": lambda s: wall_disc(4.2, 0, 0.7, I_OCHRE, mirror_tex, s),
    "poster": lambda s: [wall_box(-4.5, 4.5, -6, 6, 0, 0.3, I_CREAM, poster_tex, s)],
    "painting_small": lambda s: [wall_box(-3, 3, -3.5, 3.5, 0, 0.7, I_WOOD, small_picture_tex, s)],
}

# размер на стене (u0, v0, u1, v1) — для раскладки без наложений
WALL_FOOT = {
    "painting_landscape": (-6, -4.5, 6, 4.5),
    "painting_flowers": (-3.5, -5, 3.5, 5),
    "wall_clock": (-3.8, -3.8, 3.8, 3.8),
    "mirror_round": (-4.2, -4.2, 4.2, 4.2),
    "poster": (-4.5, -6, 4.5, 6),
    "painting_small": (-3, -3.5, 3, 3.5),
}


# ---------------------------------------------------------------- гостиная

def cushion_tex(edge):
    def tex(x, y, z, face, k, nz):
        if face == FACE_TOP and (abs(x) > 2.75 or abs(y) > 2.75):
            return edge
        if face == FACE_TOP and math.hypot(x, y) < 0.5:
            return edge
        return None
    return tex


def stripes_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and int((x + 4) // 1.3) % 2 == 0:
        return "Y"
    if face != FACE_TOP and (z % 0.55) < 0.18:
        return "n"
    return None


def remote_tex(x, y, z, face, k, nz):
    if face == FACE_TOP:
        if math.hypot(x - 1.4, y) < 0.35:
            return "r"
        if -1 < x < 0.8 and abs(y) < 0.35 and (x % 0.6) < 0.3:
            return "S"
    return None


def record_tex(x, y, z, face, k, nz):
    if face == FACE_TOP:
        d = math.hypot(x, y)
        if d < 0.9:
            return "y" if d > 0.3 else "o"
        if 1.5 < d < 1.7 or 2.1 < d < 2.25:
            return "m"
    if face != FACE_TOP and (z % 0.4) < 0.15:
        return "m"
    return None


def game_tex(x, y, z, face, k, nz):
    if face == FACE_TOP:
        if abs(x) < 2.6 and abs(y) < 1.6:
            return "y" if (int((x + 3) // 1.2) + int((y + 2) // 1.2)) % 2 else "c"
    if face == FACE_LEFT and 0.4 < z < 1.2 and abs(x) < 2.5:
        return "c"
    return None


def teapot_tex(x, y, z, face, k, nz):
    if 1.8 < z < 2.6 and nz < 0.6:
        return "l" if face != FACE_RIGHT else "L"
    return None


def books_row():
    out = []
    x = -3.2
    for w, h, mat in ((1.0, 5.2, I_TERRA), (0.8, 4.6, I_BLUE), (1.2, 5.6, I_GREEN), (0.9, 4.2, I_OCHRE), (1.1, 5.0, I_CREAM), (0.8, 4.8, I_TERRA)):
        def tex(xx, yy, zz, face, k, nz, x0=x, w=w, h=h):
            if face == FACE_LEFT and (abs(zz - h * 0.75) < 0.25 or abs(zz - h * 0.25) < 0.2):
                return "y"
            return None
        out.append(box(x, -1.6, 0, x + w, 1.6, h, mat, tex))
        x += w
    return out


ITEMS.update({
    "cushion_terra": [box(-3, -3, 0, 3, 3, 2.2, I_TERRA, chain(puff(-3, -3, 3, 3, 0, 2.2, edge=1.6), cushion_tex("R")))],
    "cushion_blue": [box(-3, -3, 0, 3, 3, 2.2, I_BLUE, chain(puff(-3, -3, 3, 3, 0, 2.2, edge=1.6), cushion_tex("z")))],
    "throw_blanket": [box(-4, -2.5, 0, 4, 2.5, 1.8, I_OCHRE, chain(stripes_tex, puff(-4, -2.5, 4, 2.5, 0, 1.8, edge=1.0)))],
    "teapot": [
        sphere(0, 0, 2.2, 2.3, I_WHITE, teapot_tex),
        cyl(0, 0, 1.4, 0, 0.6, I_WHITE),
        cyl(0, 0, 1, 4.2, 4.7, I_WHITE),
        sphere(0, 0, 5, 0.5, I_BLUE),
        box(-0.4, 1.8, 2, 0.4, 3.8, 2.8, I_WHITE),
        box(-0.4, 3.2, 2.8, 0.4, 3.9, 3.6, I_WHITE),
    ] + handle(-3.6, -2, 1.4, 3.8, I_WHITE),
    "remote": [box(-2.2, -0.7, 0, 2.2, 0.7, 0.6, I_DARK, remote_tex)],
    "vase": [
        cyl(0, 0, 1.4, 0, 4.2, I_BLUE),
        cyl(0, 0, 0.8, 4.2, 4.8, I_BLUE),
        box(-0.15, -0.15, 4.8, 0.15, 0.15, 7, I_GREEN),
        box(0.6, -0.3, 4.8, 0.9, 0, 6.4, I_GREEN),
        sphere(0, 0, 7.3, 0.8, I_TERRA),
        sphere(0.8, -0.2, 6.6, 0.7, I_OCHRE),
        sphere(-0.7, 0.3, 6.4, 0.7, I_CREAM),
    ],
    "books_row": books_row(),
    "vinyl_stack": [box(-2.8, -2.8, 0, 2.8, 2.8, 1.6, I_DARK, record_tex)],
    "board_game": [box(-3.5, -2.5, 0, 3.5, 2.5, 1.6, I_TERRA, game_tex)],
    "candles": [
        cyl(-0.9, -0.4, 0.6, 0, 2.6, I_CREAM), box(-1, -0.5, 2.6, -0.8, -0.3, 3.2, I_OCHRE),
        cyl(0.6, -0.6, 0.6, 0, 3.6, I_CREAM), box(0.5, -0.7, 3.6, 0.7, -0.5, 4.2, I_OCHRE),
        cyl(0, 0.9, 0.6, 0, 2, I_CREAM), box(-0.1, 0.8, 2, 0.1, 1, 2.6, I_OCHRE),
    ],
})


# ---------------------------------------------------------------- детская

I_TEDDY = Mat(top="A", left="w", right="v", edge="u")
I_PINK = Mat(top="_", left="*", right="^", edge="~", gloss=True)
I_MOON = Mat(top="X", left="y", right="Y", edge="$", gloss=True)
I_PAPER = Mat(top="W", left="c", right="C", edge="K")


def teddy_head_tex(x, y, z, face, k, nz):
    # глаза и нос на морде мишки
    for ex in (-0.65, 0.65):
        if (x - ex) ** 2 + (z - 5.35) ** 2 < 0.09 and y > 0.8:
            return "o"
    return None


def block_tex(color):
    def tex(x, y, z, face, k, nz):
        k = tint(k, color)
        # светлая вставка-квадрат с буквой-точкой на каждой грани
        u = x if face != FACE_RIGHT else y
        v = z if face != FACE_TOP else y
        fu, fv = (u + 10) % 2.4 - 1.2, (v + 10) % 2.4 - 1.2
        if abs(fu) < 0.75 and abs(fv) < 0.75:
            return "o" if abs(fu) < 0.28 and abs(fv) < 0.28 else shift(k, 1)
        return k
    return tex


def ball_tex(x, y, z, face, k, nz):
    if z > 2.55:
        return tint(k, "r")
    if abs(z - 2.1) < 0.4:
        return tint(k, "W")
    return None


def drum_tex(x, y, z, face, k, nz):
    if face != FACE_TOP and 0.5 < z < 2.2:
        a = math.atan2(y, x)
        if abs(((a * 4 / math.pi) % 2) - 1 - (z - 1.35) * 1.1) < 0.28:
            return tint(k, "W")
    return None


def crayon_box_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT and 0.3 < z < 0.9 and abs(x) < 1.4:
        return "W"
    return None


def sketch_tex(x, y, z, face, k, nz):
    if face == FACE_TOP:
        if y < -1.6 and (x % 0.8) < 0.35:
            return "x"
        if math.hypot(x - 0.8, y - 0.2) < 0.9:
            return "y"
        if y > 0.8 and abs(x + 0.5) < 1.6:
            return "e"
    return None


def piggy_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and abs(x) < 0.7 and abs(y + 0.2) < 0.18:
        return "~"
    if y > 1.4 and (x - 0.5) ** 2 + (z - 2.9) ** 2 < 0.07:
        return "o"
    if y > 1.4 and (x + 0.5) ** 2 + (z - 2.9) ** 2 < 0.07:
        return "o"
    return None


def robot_head_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT and abs(z - 5.4) < 0.35 and (abs(x - 0.45) < 0.3 or abs(x + 0.45) < 0.3):
        return "l"
    if face == FACE_LEFT and abs(z - 4.8) < 0.15 and abs(x) < 0.6:
        return "x"
    return None


def rocket_tex(x, y, z, face, k, nz):
    if nz < 0.6 and math.hypot(math.atan2(y, x) - math.pi / 4, (z - 4.2) * 0.9) < 0.75:
        return "L"
    if 1.2 < z < 1.8:
        return tint(k, "r")
    return None


def kid_drawing_tex(u, v):
    if abs(u) > 3.8 or abs(v) > 2.8:
        return None
    if v < -1.7:
        return "e"
    if -1.7 <= v < 0.3 and -2.4 < u < 0.2:
        if -1.5 < u < -0.7 and v < -0.6:
            return "u"
        return "r"
    if 0.3 <= v < 1.6 and abs(u + 1.1) < (1.6 - v) * 1.15:
        return "R"
    if math.hypot(u - 2.3, v - 1.5) < 0.9:
        return "y"
    return "W"


def star_poster_tex(u, v):
    if abs(u) > 3.2 or abs(v) > 4.7:
        return None
    if math.hypot(u + 0.8, v - 1.5) < 1.6 and math.hypot(u - 0.0, v - 2.1) > 1.3:
        return "X"
    for su, sv in ((1.8, 3.4), (2.2, -0.4), (-2.2, -1.8), (0.6, -3.2), (-1.5, -3.8), (2.6, 1.6)):
        if abs(u - su) + abs(v - sv) < 0.5:
            return "y"
    return "Z"


ITEMS.update({
    "teddy_bear": [
        sphere(0, 0, 2.2, 2.2, I_TEDDY),
        sphere(-1.2, 1.6, 0.9, 0.9, I_TEDDY), sphere(1.2, 1.6, 0.9, 0.9, I_TEDDY),
        sphere(-2, 0.6, 2.8, 0.8, I_TEDDY), sphere(2, 0.6, 2.8, 0.8, I_TEDDY),
        sphere(0, 0.3, 5, 1.7, I_TEDDY, teddy_head_tex),
        sphere(-1.2, 0, 6.4, 0.6, I_TEDDY), sphere(1.2, 0, 6.4, 0.6, I_TEDDY),
        sphere(0, 1.7, 4.6, 0.6, Mat(top="Q", left="q", right="f", edge="p")),
    ],
    "blocks": [
        box(-2.6, -1.2, 0, -0.2, 1.2, 2.4, I_TERRA, block_tex("r")),
        box(0.2, -1.2, 0, 2.6, 1.2, 2.4, I_BLUE, block_tex("L")),
        box(-1.2, -1.2, 2.4, 1.2, 1.2, 4.8, I_OCHRE, block_tex("Y")),
    ],
    "toy_car": [
        box(-2.6, -1.2, 0.7, 2.6, 1.2, 1.9, I_TERRA),
        box(-1.2, -1.0, 1.9, 1.1, 1.0, 2.9, I_GLASS),
        box(-2.1, -1.45, 0, -0.9, -1.2, 1.1, I_DARK), box(0.9, -1.45, 0, 2.1, -1.2, 1.1, I_DARK),
        box(-2.1, 1.2, 0, -0.9, 1.45, 1.1, I_DARK), box(0.9, 1.2, 0, 2.1, 1.45, 1.1, I_DARK),
    ],
    "ball": [sphere(0, 0, 2.1, 2.1, I_BLUE, ball_tex)],
    "crayons": [
        box(-2, -1.4, 0, 2, 1.4, 1.2, I_OCHRE, crayon_box_tex),
        box(-1.6, -0.8, 1.2, -1.0, -0.2, 2.8, I_TERRA), box(-0.8, -0.8, 1.2, -0.2, -0.2, 2.4, I_BLUE),
        box(0.0, -0.8, 1.2, 0.6, -0.2, 2.6, I_GREEN), box(0.8, -0.8, 1.2, 1.4, -0.2, 2.2, I_PINK),
    ],
    "sketchbook": [box(-3, -2.2, 0, 3, 2.2, 0.7, I_PAPER, sketch_tex)],
    "picture_books": book(I_GREEN) + book(I_PINK, 1.2, 1.0, 0.5) + book(I_OCHRE, 2.2, 1.1, -0.3),
    "night_light": [
        cyl(0, 0, 1.4, 0, 0.8, I_WOOD),
        cyl(0, 0, 0.3, 0.8, 1.4, I_WOOD),
        sphere(0, 0, 3.1, 1.9, I_MOON),
    ],
    "piggy_bank": [
        sphere(0, 0, 2.3, 2.1, I_PINK, piggy_tex),
        sphere(0, 1.9, 2.4, 0.75, I_PINK),
        box(-1.2, -0.4, 3.9, -0.6, 0.2, 4.6, I_PINK), box(0.6, -0.4, 3.9, 1.2, 0.2, 4.6, I_PINK),
        box(-1.2, -1.0, 0, -0.6, -0.4, 0.8, I_PINK), box(0.6, -1.0, 0, 1.2, -0.4, 0.8, I_PINK),
        box(-1.2, 0.6, 0, -0.6, 1.2, 0.8, I_PINK), box(0.6, 0.6, 0, 1.2, 1.2, 0.8, I_PINK),
    ],
    "robot": [
        box(-1.0, -0.6, 0, -0.3, 0.6, 1.4, I_DARK), box(0.3, -0.6, 0, 1.0, 0.6, 1.4, I_DARK),
        box(-1.5, -1.0, 1.4, 1.5, 1.0, 4.2, I_SILVER),
        box(-0.6, 1.0, 2.2, 0.6, 1.2, 3.4, I_TERRA),
        box(-1.1, -0.9, 4.2, 1.1, 0.9, 6.0, I_SILVER, robot_head_tex),
        box(-0.15, -0.15, 6.0, 0.15, 0.15, 7.0, I_DARK),
        sphere(0, 0, 7.2, 0.4, I_TERRA),
    ],
    "ring_pyramid": [
        cyl(0, 0, 2.4, 0, 0.6, I_WOOD),
        cyl(0, 0, 2.2, 0.6, 1.4, I_TERRA), cyl(0, 0, 1.9, 1.4, 2.2, I_OCHRE),
        cyl(0, 0, 1.6, 2.2, 3.0, I_GREEN), cyl(0, 0, 1.3, 3.0, 3.8, I_BLUE),
        cyl(0, 0, 1.0, 3.8, 4.5, I_PINK), sphere(0, 0, 5.0, 0.7, I_TERRA),
    ],
    "drum": [
        cyl(0, 0, 2.4, 0, 2.6, I_TERRA, drum_tex),
        cyl(0, 0, 2.5, 2.6, 2.95, I_WHITE),
        box(-0.15, 1.6, 2.95, 0.15, 3.6, 3.25, I_WOOD),
    ],
    "toy_rocket": [
        cyl(0, 0, 1.1, 0.8, 5.6, I_WHITE, rocket_tex),
        cyl(0, 0, 0.8, 5.6, 6.4, I_TERRA), cyl(0, 0, 0.45, 6.4, 7.1, I_TERRA),
        box(-1.9, -0.15, 0, -0.9, 0.15, 2.2, I_TERRA), box(0.9, -0.15, 0, 1.9, 0.15, 2.2, I_TERRA),
        box(-0.15, 0.9, 0, 0.15, 1.9, 2.2, I_TERRA),
    ],
})

WALL_ITEMS.update({
    "kid_drawing": lambda s: [wall_box(-4, 4, -3, 3, 0, 0.2, I_PAPER, kid_drawing_tex, s)],
    "star_poster": lambda s: [wall_box(-3.5, 3.5, -5, 5, 0, 0.3, I_WOOD, star_poster_tex, s)],
})
WALL_FOOT.update({
    "kid_drawing": (-4, -3, 4, 3),
    "star_poster": (-3.5, -5, 3.5, 5),
})
