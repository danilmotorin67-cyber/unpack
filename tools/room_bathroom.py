"""Уровень 2 — ванная: ванна, раковина с зеркальным шкафчиком, унитаз, стеллаж."""
import math

from common import *  # noqa: F401,F403
from palette import shift

NAME = "bathroom"

M_TILE_FLOOR = Mat(top="W", left="k", right="K", edge="K", hi="W")
M_TUB = Mat(top="W", left="c", right="C", edge="K", hi="W")
M_TUB_IN = Mat(top="c", left="c", right="C", edge="k", hi="W")
M_MIRROR_IN = Mat(top="c", left="C", right="k", edge="K", hi="W")
M_LIGHT_WOOD = Mat(top="q", left="f", right="F", edge="p", hi="W")

WIN = (72, 104, 52, 76)  # окно на левой стене: y0, y1, z0, z1


def floor_tex(x, y, z, face, k, nz):
    if face != FACE_TOP or z < -0.5:
        return None
    # коврик у ванны
    if 34 <= x <= 52 and 78 <= y <= 116:
        if x < 35.5 or x > 50.5 or y < 79.5 or y > 114.5:
            return "L"
        return "l" if int((y - 78) // 3) % 2 else "t"
    if (x % 10) < 0.8 or (y % 10) < 0.8:
        return "T"
    lit = x > 30 and (WIN[0] - 4 + 0.3 * x) < y < (WIN[1] + 0.3 * x)
    checker = (int(x // 10) + int(y // 10)) % 2
    if lit:
        return "W"
    return "t" if checker else "W"


def tiles(u, z, tile="t", grout="T"):
    row = int(z // 4.5)
    if (z % 4.5) < 0.7 or ((u + (row % 2) * 3) % 6) < 0.7:
        return grout
    return tile


def wall_left_tex(x, y, z, face, k, nz):
    if face != FACE_RIGHT:
        return None
    w = window(y, z, *WIN)
    if w:
        return w
    if z < 44:
        return tiles(y, z)
    if z < 45.5:
        return "T"
    return None


def wall_right_tex(x, y, z, face, k, nz):
    if face != FACE_LEFT:
        return None
    if z < 44:
        return tiles(x, z)
    if z < 45.5:
        return "T"
    return None


def vanity_tex(x, y, z, face, k, nz):
    if face != FACE_LEFT:
        return None
    if z < 3 or abs(x - 40) < 0.5:
        return "H"
    if 14 < z < 21 and (abs(x - 37) < 0.7 or abs(x - 43) < 0.7):
        return "s"
    if abs(z - 4.5) < 0.5 or abs(z - 26.5) < 0.5:
        return "h"
    return None


def vanity_top_tex(x, y, z, face, k, nz):
    if face != FACE_TOP:
        return None
    d = ((x - 40) / 10) ** 2 + ((y - 14) / 7) ** 2
    if d < 1:
        if math.hypot(x - 40, y - 14) < 1:
            return "x"
        return "C" if d > 0.75 else "k"
    return None


def toilet_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and z > 14.5:
        r = math.hypot(x - 81, y - 15)
        if r < 4.5:
            return "T"
        if r < 5.5:
            return "C"
    return None


def tank_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and math.hypot(x - 81, y - 3.5) < 1.4:
        return "s"
    return None


def mirror_tex(x, y, z, face, k, nz):
    if face != FACE_LEFT:
        return None
    if x < 23.2 or x > 56.8 or z < 49.2 or z > 72.8:
        return "W"
    if 0 < (x - 26) - (z - 52) * 1.2 < 2.5 or 0 < (x - 32) - (z - 52) * 1.2 < 1:
        return "W"
    return "t"


def mirror_inner_tex(x, y, z, face, k, nz):
    if face == FACE_RIGHT:
        if y < 11 or y > 44 or z < 49.5 or z > 72.5:
            return "C"
        return "T"
    return None


def prims():
    p = shell(floor_tex, under(wall_left_tex, plaster), under(wall_right_tex, plaster), m_floor=M_TILE_FLOOR)
    # ванна вдоль левой стены
    p += [
        box(0, 66, 0, 30, 128, 4, M_TUB),
        box(27, 66, 4, 30, 128, 22, M_TUB),
        box(0, 66, 4, 27, 69, 22, M_TUB),
        box(0, 125, 4, 27, 128, 22, M_TUB),
        box(0, 69, 4, 3, 125, 22, M_TUB_IN),
        box(0, 95, 24, 4, 98, 26, M_METAL),
        box(3, 95.8, 22.5, 4, 97.2, 24, M_METAL),
    ]
    # тумба с раковиной
    p += [
        box(18, 0, 0, 62, 24, 30, M_SAGE, vanity_tex),
        box(17, 0, 30, 63, 26, 33, M_TUB, vanity_top_tex),
        cyl(40, 2.5, 0.8, 33, 38, M_METAL),
        box(39.3, 2.5, 36.5, 40.7, 7, 38, M_METAL),
    ]
    # зеркальный шкафчик (дверца — отдельный спрайт)
    p += [
        box(22, 0, 48, 58, 8, 50, M_LIGHT_WOOD),
        box(22, 0, 72, 58, 8, 74, M_LIGHT_WOOD),
        box(22, 0, 50, 24, 8, 72, M_LIGHT_WOOD),
        box(56, 0, 50, 58, 8, 72, M_LIGHT_WOOD),
        box(24, 0, 50, 56, 1, 72, M_MIRROR_IN),
        box(24, 1, 60, 56, 7.5, 61.5, M_LIGHT_WOOD),
    ]
    # унитаз
    p += [
        box(72, 0, 18, 90, 7, 36, M_TUB, tank_tex),
        cyl(81, 13, 4.5, 0, 8, M_TUB),
        cyl(81, 15, 7.5, 8, 15, M_TUB, toilet_tex),
    ]
    # стеллаж
    p += [
        box(104, 0, 0, 106, 18, 64, M_LIGHT_WOOD),
        box(142, 0, 0, 144, 18, 64, M_LIGHT_WOOD),
        box(106, 0, 0, 142, 1, 62, M_MIRROR_IN),
        box(106, 0, 1, 142, 18, 3, M_LIGHT_WOOD),
        box(106, 0, 22, 142, 18, 24, M_LIGHT_WOOD),
        box(106, 0, 43, 142, 18, 45, M_LIGHT_WOOD),
        box(104, 0, 62, 144, 18, 64, M_LIGHT_WOOD),
    ]
    # шторка у ванны (сдвинута к дальнему краю), карниз
    M_SHOWER = Mat(top="O", left="t", right="t", edge="T")
    p.append(box(27, 66, 72, 28.2, 128, 73.2, M_METAL))
    p.append(box(26.4, 104, 24, 28.8, 128, 72, M_SHOWER, folds(1.6, 1, 0.2, faces=(FACE_RIGHT,))))
    # полотенце на крючке у ванны (левая стена)
    M_TOWEL = Mat(top="l", left="L", right="L", edge="z")
    p.append(box(0, 32, 45, 2.2, 48, 46, M_METAL))
    p.append(box(0.3, 34, 28, 1.8, 46, 45, M_TOWEL, chain(folds(1.3, 1, 0.8, faces=(FACE_RIGHT,)),
             lambda x, y, z, f, k, nz: "W" if f == FACE_RIGHT and 30.5 < z < 31.6 else None)))
    # весы на полу
    p.append(box(56, 104, 0, 66, 113, 1.3, M_TUB, lambda x, y, z, f, k, nz: "z" if f == FACE_TOP and 59 < x < 63 and 105.5 < y < 107.5 else None))
    # декор: корзина для мусора и ёршик у унитаза
    p.append(cyl(97, 8, 3, 0, 7, M_METAL))
    p.append(cyl(97, 8, 3.3, 7, 7.8, M_METAL))
    p.append(cyl(66, 6, 1.6, 0, 3.5, M_TUB))
    p.append(cyl(66, 6, 0.4, 3.5, 10, M_METAL))
    return p


DOORS = [
    {
        "id": "mirror",
        "closed": [box(22, 8, 48, 58, 9.5, 74, M_LIGHT_WOOD, mirror_tex)],
        "open": [box(20.5, 9.5, 48, 22, 45.5, 74, M_LIGHT_WOOD, mirror_inner_tex)],
        "closed_depth": 58 + 9.5,
        "open_depth": 22 + 45.5,
    },
]

SHELF = {"x0": 106, "y0": 1, "x1": 142, "y1": 18}
ZONES = [
    {"id": "bath", "tag": "bath", "x0": 3, "y0": 69, "x1": 27, "y1": 102, "z": 4, "max_h": 30},
    {"id": "sink", "tag": "sink", "x0": 17, "y0": 0, "x1": 63, "y1": 26, "z": 33, "max_h": 14},
    {"id": "mirror_0", "tag": "mirror", "x0": 24, "y0": 1, "x1": 56, "y1": 7.5, "z": 50, "max_h": 9.5, "container": "mirror"},
    {"id": "mirror_1", "tag": "mirror", "x0": 24, "y0": 1, "x1": 56, "y1": 7.5, "z": 61.5, "max_h": 10, "container": "mirror"},
    {"id": "tank", "tag": "toilet", "x0": 72, "y0": 0, "x1": 90, "y1": 7, "z": 36, "max_h": 30},
    {"id": "shelf_0", "tag": "shelf", **SHELF, "z": 3, "max_h": 19},
    {"id": "shelf_1", "tag": "shelf", **SHELF, "z": 24, "max_h": 19},
    {"id": "shelf_2", "tag": "shelf", **SHELF, "z": 45, "max_h": 17},
    {"id": "shelf_top", "tag": "shelf", "x0": 104, "y0": 0, "x1": 144, "y1": 18, "z": 64, "max_h": 20},
]
