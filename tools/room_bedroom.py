"""Уровень 3 — спальня: кровать, тумбочка, шкаф, стол с полкой."""
import math

from common import *  # noqa: F401,F403
from palette import shift

NAME = "bedroom"

M_BED = Mat(top="W", left="c", right="C", edge="K", hi="W")
M_BLANKET = Mat(top="l", left="L", right="z", edge="Z", hi="t")
M_LIGHT_WOOD = Mat(top="q", left="f", right="F", edge="p", hi="W")
M_WARDROBE_IN = Mat(top="c", left="C", right="k", edge="K", hi="W")

WIN = (44, 90, 48, 76)


def floor_tex(x, y, z, face, k, nz):
    if face != FACE_TOP or z < -0.5:
        return None
    # большой ковёр у кровати
    if 30 <= x <= 76 and 30 <= y <= 112:
        if x < 32 or x > 74 or y < 32 or y > 110:
            return "z"
        if abs(((x - 53) + (y - 71)) % 12 - 6) < 0.8 or abs(((x - 53) - (y - 71)) % 12 - 6) < 0.8:
            return "t"
        return "l"
    lit = x > 46 and (WIN[0] - 4 + 0.3 * x) < y < (WIN[1] + 0.3 * x)
    return planks(x, y, lit)


def wall_left_tex(x, y, z, face, k, nz):
    if face != FACE_RIGHT:
        return None
    w = window(y, z, *WIN)
    if w:
        return w
    if z < 3:
        return "k"
    if (y % 10) < 1:
        return "C"
    return None


def wall_right_tex(x, y, z, face, k, nz):
    if face != FACE_LEFT:
        return None
    if z < 3:
        return "k"
    if (x % 10) < 1:
        return "k"
    return None


def blanket_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and (int(x // 4) + int(y // 4)) % 2 == 0:
        return "t"
    return None


def drawer_tex(x, y, z, face, k, nz):
    if face == FACE_RIGHT:
        if abs(z - 12) < 0.5:
            return "u"
        if abs(y - 113) < 1.5 and (abs(z - 16.5) < 0.7 or abs(z - 7) < 0.7):
            return "s"
    return None


def wardrobe_door_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT:
        if abs(x - 78) < 0.5:
            return "p"
        if 40 < z < 46 and (abs(x - 75.5) < 0.7 or abs(x - 80.5) < 0.7):
            return "s"
        if abs(z - 5) < 0.5 or abs(z - 75) < 0.5:
            return "F"
    return None


def wardrobe_inner_tex(x, y, z, face, k, nz):
    if face == FACE_RIGHT and 30 < y < 64 and 4 < z < 76:
        return "f"
    return None


def prims():
    p = shell(floor_tex, wall_left_tex, wall_right_tex)
    # кровать
    p += [
        box(0, 32, 0, 4, 102, 34, M_WOOD),
        box(4, 34, 0, 46, 100, 12, M_WOOD),
        box(4, 36, 12, 46, 98, 19, M_BED),
        box(18, 35, 19, 47, 99, 21, M_BLANKET, blanket_tex),
        box(5, 40, 19, 15, 62, 23, M_BED),
        box(5, 68, 19, 15, 90, 23, M_BED),
    ]
    # тумбочка
    p.append(box(0, 104, 0, 18, 122, 22, M_LIGHT_WOOD, drawer_tex))
    # шкаф (дверца — отдельный спрайт)
    p += [
        box(58, 0, 0, 98, 24, 4, M_LIGHT_WOOD),
        box(58, 0, 76, 98, 24, 80, M_LIGHT_WOOD),
        box(58, 0, 4, 60, 24, 76, M_LIGHT_WOOD),
        box(96, 0, 4, 98, 24, 76, M_LIGHT_WOOD),
        box(60, 0, 4, 96, 1, 76, M_WARDROBE_IN),
        box(60, 1, 28, 96, 23, 30, M_LIGHT_WOOD),
        box(60, 1, 52, 96, 23, 54, M_LIGHT_WOOD),
    ]
    # стол, полка, табурет
    p += [
        box(106, 0, 28, 146, 26, 31, M_WOOD),
        box(107, 23, 0, 109, 25, 28, M_WOOD),
        box(107, 1, 0, 109, 3, 28, M_WOOD),
        box(131, 1, 6, 145, 25, 28, M_WOOD),
        box(108, 0, 56, 144, 12, 59, M_WOOD),
        box(112, 0, 50, 114, 9, 56, M_WOOD),
        box(138, 0, 50, 140, 9, 56, M_WOOD),
        cyl(122, 40, 4.5, 12, 15, M_LIGHT_WOOD),
        cyl(122, 40, 1.2, 0, 12, M_WOOD),
    ]
    # декор: корзина для белья и тапочки у кровати
    M_BASKET = Mat(top="b", left="B", right="n", edge="N", hi="U")
    p.append(cyl(140, 44, 5, 0, 12, M_BASKET, lambda x, y, z, f, k, nz: shift(k, -1) if (z % 2) < 0.6 else None))
    p.append(cyl(140, 44, 4.3, 12, 13.5, M_BED))
    p.append(box(50, 92, 0, 56, 95, 1.6, M_BLANKET))
    p.append(box(50, 97, 0, 56, 100, 1.6, M_BLANKET))
    return p


DOORS = [
    {
        "id": "wardrobe",
        "closed": [box(58, 24, 0.5, 98, 26, 79.5, M_LIGHT_WOOD, wardrobe_door_tex)],
        "open": [box(55.5, 26, 0.5, 58, 66, 79.5, M_LIGHT_WOOD, wardrobe_inner_tex)],
        "closed_depth": 98 + 26,
        "open_depth": 58 + 66,
    },
]

WARDROBE = {"x0": 60, "y0": 1, "x1": 96, "y1": 23, "container": "wardrobe"}
ZONES = [
    {"id": "wall_r", "tag": "wall", "wall": "R", "u0": 4, "u1": 55, "z0": 36, "z1": 82},
    {"id": "wall_l", "tag": "wall", "wall": "L", "u0": -128, "u1": -96, "z0": 34, "z1": 82},
    {"id": "bed", "tag": "bed", "x0": 18, "y0": 37, "x1": 46, "y1": 97, "z": 21, "max_h": 40},
    {"id": "nightstand", "tag": "nightstand", "x0": 0, "y0": 104, "x1": 18, "y1": 122, "z": 22, "max_h": 40},
    {"id": "wardrobe_0", "tag": "wardrobe", **WARDROBE, "z": 4, "max_h": 24},
    {"id": "wardrobe_1", "tag": "wardrobe", **WARDROBE, "z": 30, "max_h": 22},
    {"id": "wardrobe_2", "tag": "wardrobe", **WARDROBE, "z": 54, "max_h": 22},
    {"id": "desk", "tag": "desk", "x0": 106, "y0": 0, "x1": 146, "y1": 26, "z": 31, "max_h": 25},
    {"id": "shelf", "tag": "shelf", "x0": 108, "y0": 0, "x1": 144, "y1": 12, "z": 59, "max_h": 24},
]
