"""Уровень 4 — гостиная: диван, журнальный стол, ТВ, стеллаж, комод, стены под картины."""
import math

from common import *  # noqa: F401,F403

NAME = "living"

M_SOFA = Mat(top="l", left="L", right="z", edge="Z", hi="t")
M_LIGHT_WOOD = Mat(top="q", left="f", right="F", edge="p", hi="W")
M_INNER = Mat(top="c", left="C", right="k", edge="K", hi="W")
M_TV = Mat(top="d", left="o", right="o", edge="o", hi="m")
M_SHADE = Mat(top="W", left="c", right="C", edge="K", hi="W")
M_POT = Mat(top="i", left="r", right="R", edge="o")
M_LEAF = Mat(top="a", left="e", right="E", edge="E")

WIN = (62, 98, 44, 76)


def floor_tex(x, y, z, face, k, nz):
    if face != FACE_TOP or z < -0.5:
        return None
    # ковёр под журнальным столом
    if 40 <= x <= 96 and 34 <= y <= 82:
        if x < 41.5 or x > 94.5 or y < 35.5 or y > 80.5:
            return "R"
        d = abs(x - 68) / 28 + abs(y - 58) / 24
        if 0.62 < d < 0.7 or 0.3 < d < 0.36:
            return "y"
        return "r" if d < 0.3 else "i" if d < 0.66 else "r"
    lit = x > 20 and (WIN[0] - 4 + 0.3 * x) < y < (WIN[1] + 0.3 * x)
    return planks(x, y, lit)


def wall_left_tex(x, y, z, face, k, nz):
    if face != FACE_RIGHT:
        return None
    w = window(y, z, *WIN)
    if w:
        return w
    if z < 3:
        return "k"
    if abs(z - 30) < 0.6:
        return "C"
    if z < 30 and (y % 6) < 0.7:
        return "C"
    return None


def wall_right_tex(x, y, z, face, k, nz):
    if face != FACE_LEFT:
        return None
    if z < 3:
        return "k"
    if abs(z - 30) < 0.6:
        return "k"
    if z < 30 and (x % 6) < 0.7:
        return "k"
    return None


def tv_tex(x, y, z, face, k, nz):
    if face == FACE_RIGHT and 25 < y < 51 and 20 < z < 38.5:
        if 0 < (y - 30) - (z - 22) * 0.8 < 1.5:
            return "z"
        return "Z"
    return None


def stand_tex(x, y, z, face, k, nz):
    if face == FACE_RIGHT:
        if abs(y - 38) < 0.5 or z < 2.5:
            return "H"
        if 7 < z < 12 and (abs(y - 35.5) < 0.6 or abs(y - 40.5) < 0.6):
            return "s"
    return None


def sideboard_door_tex(x, y, z, face, k, nz):
    if face == FACE_RIGHT:
        if abs(z - 15) < 0.5:
            return "H"
        if 17 < z < 24 and abs(y - 124.5) < 0.6:
            return "s"
        if 5 < z < 12 and abs(y - 124.5) < 0.6:
            return "s"
    return None


def sideboard_inner_tex(x, y, z, face, k, nz):
    if face == FACE_LEFT and 21 < x < 42 and 2 < z < 28:
        return "G"
    return None


def sofa_tex(x, y, z, face, k, nz):
    if face == FACE_TOP and 10 < z < 16.5 and abs(x - 60) < 0.5:
        return "L"
    if face == FACE_LEFT and z < 10 and (x % 8) < 0.5:
        return "z"
    return None


def prims():
    p = shell(floor_tex, wall_left_tex, wall_right_tex)
    # большое растение в углу
    p += [
        cyl(8, 8, 5, 0, 9, M_POT),
        sphere(8, 8, 14, 5, M_LEAF),
        sphere(5, 11, 19, 4, M_LEAF),
        sphere(11, 6, 20, 3.6, M_LEAF),
        sphere(8, 8, 24, 3, M_LEAF),
    ]
    # тумба под ТВ и телевизор
    p += [
        box(0, 20, 0, 18, 56, 18, M_SAGE, stand_tex),
        box(1, 30, 18, 4, 46, 20, M_TV),
        box(2, 24, 20, 5, 52, 40, M_TV, tv_tex),
    ]
    # диван вдоль правой стены
    p += [
        box(30, 0, 0, 90, 24, 10, M_SOFA, sofa_tex),
        box(36, 6, 10, 84, 24, 16, M_SOFA, sofa_tex),
        box(30, 0, 10, 90, 6, 30, M_SOFA),
        box(30, 6, 10, 36, 24, 22, M_SOFA),
        box(84, 6, 10, 90, 24, 22, M_SOFA),
    ]
    # торшер
    p += [
        cyl(22, 9, 2.5, 0, 1.5, M_WOOD),
        cyl(22, 9, 0.8, 1.5, 48, M_TV),
        cyl(22, 9, 5, 48, 58, M_SHADE),
    ]
    # стеллаж
    p += [
        box(100, 0, 0, 102, 16, 70, M_LIGHT_WOOD),
        box(138, 0, 0, 140, 16, 70, M_LIGHT_WOOD),
        box(102, 0, 0, 138, 1, 68, M_INNER),
        box(102, 0, 1, 138, 16, 3, M_LIGHT_WOOD),
        box(102, 0, 24, 138, 16, 26, M_LIGHT_WOOD),
        box(102, 0, 47, 138, 16, 49, M_LIGHT_WOOD),
        box(100, 0, 68, 140, 16, 70, M_LIGHT_WOOD),
    ]
    # журнальный стол
    p += [
        box(50, 44, 12, 84, 70, 14, M_WOOD),
        box(52, 46, 0, 54, 48, 12, M_WOOD),
        box(80, 46, 0, 82, 48, 12, M_WOOD),
        box(52, 66, 0, 54, 68, 12, M_WOOD),
        box(80, 66, 0, 82, 68, 12, M_WOOD),
        box(53, 47, 4, 81, 67, 5, M_LIGHT_WOOD),
    ]
    # комод (дверца — отдельный спрайт)
    p += [
        box(0, 102, 0, 18, 128, 2, M_SAGE),
        box(0, 102, 28, 18, 128, 30, M_SAGE),
        box(0, 102, 2, 1, 128, 28, M_INNER),
        box(0, 102, 2, 18, 104, 28, M_SAGE),
        box(0, 126, 2, 18, 128, 28, M_SAGE),
        box(1, 104, 14, 17, 126, 15.5, M_SAGE),
    ]
    # декор: стопка журналов под столом, напольная подушка
    M_MAG = Mat(top="W", left="c", right="C", edge="K", hi="W")
    p.append(box(58, 52, 5, 70, 60, 6, M_MAG))
    p.append(box(59, 53, 6, 69, 59, 7, Mat(top="l", left="L", right="z", edge="Z")))
    p.append(box(126, 38, 0, 140, 52, 4, Mat(top="g", left="G", right="h", edge="H", hi="D")))
    return p


DOORS = [
    {
        "id": "sideboard",
        "closed": [box(18, 102, 0.5, 19.5, 128, 29.5, M_SAGE, sideboard_door_tex)],
        "open": [box(19.5, 100.5, 0.5, 43.5, 102, 29.5, M_SAGE, sideboard_inner_tex)],
        "closed_depth": 19.5 + 128,
        "open_depth": 43.5 + 102,
    },
]

SIDEBOARD = {"x0": 1, "y0": 104, "x1": 17, "y1": 126, "container": "sideboard"}
BOOKSHELF = {"x0": 102, "y0": 1, "x1": 138, "y1": 16}
ZONES = [
    {"id": "wall_l1", "tag": "wall", "wall": "L", "u0": -58, "u1": -20, "z0": 44, "z1": 82},
    {"id": "wall_l2", "tag": "wall", "wall": "L", "u0": -128, "u1": -102, "z0": 36, "z1": 82},
    {"id": "wall_r", "tag": "wall", "wall": "R", "u0": 30, "u1": 88, "z0": 34, "z1": 82},
    {"id": "sofa", "tag": "sofa", "x0": 36, "y0": 6, "x1": 84, "y1": 24, "z": 16, "max_h": 30},
    {"id": "table", "tag": "table", "x0": 50, "y0": 44, "x1": 84, "y1": 70, "z": 14, "max_h": 40},
    {"id": "tvstand", "tag": "tvstand", "x0": 5, "y0": 20, "x1": 18, "y1": 56, "z": 18, "max_h": 30},
    {"id": "sideboard_top", "tag": "cabinet_top", "x0": 0, "y0": 102, "x1": 18, "y1": 128, "z": 30, "max_h": 40},
    {"id": "sideboard_0", "tag": "sideboard", **SIDEBOARD, "z": 2, "max_h": 12},
    {"id": "sideboard_1", "tag": "sideboard", **SIDEBOARD, "z": 15.5, "max_h": 12},
    {"id": "bookshelf_0", "tag": "bookshelf", **BOOKSHELF, "z": 3, "max_h": 20},
    {"id": "bookshelf_1", "tag": "bookshelf", **BOOKSHELF, "z": 26, "max_h": 20},
    {"id": "bookshelf_2", "tag": "bookshelf", **BOOKSHELF, "z": 49, "max_h": 18},
    {"id": "bookshelf_top", "tag": "bookshelf", "x0": 100, "y0": 0, "x1": 140, "y1": 16, "z": 70, "max_h": 14},
]
