"""Уровень 5 — детская: кровать, вигвам, сундук для игрушек, стеллаж-кубики,
детский столик, ковёр-радуга."""
import math

from common import *  # noqa: F401,F403
from palette import shift

NAME = "kids"

M_LIGHT_WOOD = Mat(top="q", left="f", right="F", edge="p", hi="W")
M_BED = Mat(top="W", left="c", right="C", edge="K", hi="W")
M_PINK = Mat(top="_", left="*", right="^", edge="~", hi="_")
M_CURTAIN = Mat(top="X", left="y", right="y", edge="Y")
M_TENT = Mat(top="W", left="c", right="C", edge="K")
M_CHEST = Mat(top="l", left="L", right="z", edge="Z", hi="I")
M_SAGE_K = Mat(top="g", left="G", right="h", edge="H", hi="D")

WIN = (52, 86, 46, 76)


def floor_tex(x, y, z, face, k, nz):
    if face != FACE_TOP or z < -0.5:
        return None
    # круглый ковёр-радуга
    d = math.hypot((x - 72) / 1.0, (y - 82) / 1.0)
    if d < 22:
        rings = ("y", "*", "l", "a", "*", "W")
        if d > 21:
            return "^"
        return rings[int(d // 3.6) % len(rings)]
    lit = x > 32 and (WIN[0] - 4 + 0.3 * x) < y < (WIN[1] + 0.3 * x)
    return planks(x, y, lit)


def wall_left_tex(x, y, z, face, k, nz):
    if face != FACE_RIGHT:
        return None
    w = window(y, z, *WIN)
    if w:
        return w
    if z < 3:
        return "k"
    return None


def wall_right_tex(x, y, z, face, k, nz):
    if face != FACE_LEFT:
        return None
    if z < 3:
        return "k"
    return None


def blanket_tex(x, y, z, face, k, nz):
    # звёздочки на одеяле
    cu = (x + int(y // 6) * 3) % 6 - 3
    cv = y % 6 - 3
    if face == FACE_TOP and ((abs(cu) < 0.4 and abs(cv) < 1.3) or (abs(cv) < 0.4 and abs(cu) < 1.3)):
        return "X"
    return None


def headboard_tex(x, y, z, face, k, nz):
    # сердечко на изголовье
    if face == FACE_RIGHT:
        u, v = y - 93, z - 17
        if (u * u + (v - abs(u) * 0.6) ** 2) < 9 and v > -3.5:
            return "*"
    return None


def tent_tex(x, y, z, face, k, nz):
    # полоски по высоте и вход, обращённый в комнату
    a = math.atan2(y - 16, x - 16)
    if z < 22 and abs(a - math.pi / 4) < 0.42 - z * 0.012:
        return shift(k, -3)
    if int(z // 3) % 2 == 0:
        return tint(k, "*")
    return None


def chest_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT:
        if abs(z - 7) < 2.2 and abs(x - 52) < 2.2 and (abs(x - 52) < 0.6 or abs(z - 7) < 0.6):
            return "X"
        if z < 1.6 or z > 12.6:
            return shift(k, -1)
    return None


def prims():
    p = shell(floor_tex, under(wall_left_tex, stars), under(wall_right_tex, stars))
    # шторы
    p += curtain(52, 86, 46, 76, M_CURTAIN)
    # кровать вдоль левой стены: изголовье у дальнего края
    p += [
        box(0, 62, 0, 31, 64.5, 26, M_LIGHT_WOOD, headboard_tex),
        box(0, 64.5, 0, 30, 122, 9, M_LIGHT_WOOD),
        box(0, 120, 9, 31, 122.5, 17, M_LIGHT_WOOD),
        box(1, 64.5, 9, 29, 120, 14, M_BED, puff(1, 64.5, 29, 120, 9, 14, edge=1.2)),
        box(9, 64.5, 14, 30, 120, 15.6, M_PINK, chain(blanket_tex, wrinkles(1.2))),
        box(30, 64.5, 6, 31.2, 120, 15.6, M_PINK, folds(1.2, 1, 0.3, faces=(FACE_RIGHT,))),
        box(2, 67, 14, 9, 82, 17.6, M_BED, puff(2, 67, 9, 82, 14, 17.6, edge=1.8)),
    ]
    # вигвам в углу: ткань полосками, кольца сужаются кверху, жерди торчат
    for i in range(26):
        z0 = i * 1.6
        r = 12 * (1 - z0 / 44)
        p.append(cyl(16, 16, r, z0, z0 + 1.6, M_TENT, tent_tex))
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        p.append(box(16 + dx * 0.6 - 0.4, 16 + dy * 0.6 - 0.4, 41, 16 + dx * 0.6 + 0.4, 16 + dy * 0.6 + 0.4, 47, M_WOOD))
    # сундук для игрушек (крышка — отдельный спрайт)
    p += [
        box(40, 0, 0, 64, 14, 1.5, M_CHEST),
        box(40, 0, 1.5, 64, 1, 14, M_CHEST),
        box(40, 13, 1.5, 64, 14, 14, M_CHEST, chest_tex),
        box(40, 1, 1.5, 41, 13, 14, M_CHEST),
        box(63, 1, 1.5, 64, 13, 14, M_CHEST),
    ]
    # стеллаж-кубики 3×2 и полка над ним
    p += [
        box(72, 0, 0, 108, 15, 1.2, M_LIGHT_WOOD),
        box(72, 0, 14, 108, 15, 15.2, M_LIGHT_WOOD),
        box(72, 0, 29, 108, 15, 30.2, M_LIGHT_WOOD),
        box(72, 0, 0, 73, 15, 30.2, M_LIGHT_WOOD),
        box(107, 0, 0, 108, 15, 30.2, M_LIGHT_WOOD),
        box(84, 0, 1.2, 85, 15, 29, M_LIGHT_WOOD),
        box(96, 0, 1.2, 97, 15, 29, M_LIGHT_WOOD),
        box(73, 0, 1.2, 107, 0.6, 29, M_SAGE_K),
        box(72, 0, 50, 108, 11, 52.4, M_WOOD),
        box(76, 0, 45, 77.6, 8, 50, M_WOOD),
        box(102.4, 0, 45, 104, 8, 50, M_WOOD),
    ]
    # детский столик и два стульчика
    p += [
        box(100, 60, 15, 120, 80, 17, M_LIGHT_WOOD),
        box(101, 61, 0, 102.6, 62.6, 15, M_LIGHT_WOOD),
        box(117.4, 61, 0, 119, 62.6, 15, M_LIGHT_WOOD),
        box(101, 77.4, 0, 102.6, 79, 15, M_LIGHT_WOOD),
        box(117.4, 77.4, 0, 119, 79, 15, M_LIGHT_WOOD),
        # стульчик спереди
        box(105, 84, 8, 115, 92, 9.5, M_PINK),
        box(105, 92, 8, 115, 93.5, 19, M_PINK),
        box(105.6, 84.6, 0, 106.8, 85.8, 8, M_LIGHT_WOOD),
        box(113.2, 84.6, 0, 114.4, 85.8, 8, M_LIGHT_WOOD),
        box(105.6, 91, 0, 106.8, 92.2, 8, M_LIGHT_WOOD),
        box(113.2, 91, 0, 114.4, 92.2, 8, M_LIGHT_WOOD),
        # стульчик сбоку
        box(124, 65, 8, 132, 75, 9.5, M_SAGE_K),
        box(132, 65, 8, 133.5, 75, 19, M_SAGE_K),
        box(124.6, 65.6, 0, 125.8, 66.8, 8, M_LIGHT_WOOD),
        box(130.2, 65.6, 0, 131.4, 66.8, 8, M_LIGHT_WOOD),
        box(124.6, 73.2, 0, 125.8, 74.4, 8, M_LIGHT_WOOD),
        box(130.2, 73.2, 0, 131.4, 74.4, 8, M_LIGHT_WOOD),
    ]
    return p


DOORS = [
    {
        "id": "chest",
        "closed": [box(39.6, 0, 14, 64.4, 14.4, 16.6, M_CHEST, lambda x, y, z, f, k, nz: "X" if f == FACE_TOP and math.hypot(x - 52, y - 7) < 1.6 else None)],
        "open": [box(39.6, 0, 14, 64.4, 2.6, 38.4, M_CHEST)],
        "closed_depth": 64.4 + 14.4,
        "open_depth": 64.4 + 2.6,
    },
]

CUBBY = {"y0": 0.6, "y1": 15, "tag": "cubby"}
ZONES = [
    {"id": "wall_l1", "tag": "wall", "wall": "L", "u0": -42, "u1": -4, "z0": 48, "z1": 82},
    {"id": "wall_l2", "tag": "wall", "wall": "L", "u0": -128, "u1": -96, "z0": 30, "z1": 82},
    {"id": "wall_r1", "tag": "wall", "wall": "R", "u0": 30, "u1": 68, "z0": 42, "z1": 82},
    {"id": "wall_r2", "tag": "wall", "wall": "R", "u0": 112, "u1": 146, "z0": 28, "z1": 82},
    {"id": "bed", "tag": "bed", "x0": 10, "y0": 84, "x1": 29, "y1": 118, "z": 15.6, "max_h": 40},
    {"id": "chest", "tag": "chest", "x0": 42, "y0": 2, "x1": 62, "y1": 12, "z": 1.5, "max_h": 12, "container": "chest"},
    {"id": "cubby_00", "x0": 73, "x1": 84, "z": 1.2, "max_h": 12.5, **CUBBY},
    {"id": "cubby_01", "x0": 85, "x1": 96, "z": 1.2, "max_h": 12.5, **CUBBY},
    {"id": "cubby_02", "x0": 97, "x1": 107, "z": 1.2, "max_h": 12.5, **CUBBY},
    {"id": "cubby_10", "x0": 73, "x1": 84, "z": 15.2, "max_h": 13.5, **CUBBY},
    {"id": "cubby_11", "x0": 85, "x1": 96, "z": 15.2, "max_h": 13.5, **CUBBY},
    {"id": "cubby_12", "x0": 97, "x1": 107, "z": 15.2, "max_h": 13.5, **CUBBY},
    {"id": "shelf", "tag": "shelf", "x0": 72, "y0": 0, "x1": 108, "y1": 11, "z": 52.4, "max_h": 28},
    {"id": "table", "tag": "table", "x0": 100, "y0": 60, "x1": 120, "y1": 80, "z": 17, "max_h": 40},
]
