"""Уровень 1 — кухня: мебель, поверхности, холодильник."""
import math

from common import *  # noqa: F401,F403
from palette import shift

NAME = "kitchen"


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
    lit = x > 30 and (40 + 0.3 * x) < y < (93 + 0.3 * x)
    return planks(x, y, lit)


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


M_CURTAIN = Mat(top="V", left="i", right="i", edge="r")


def prims():
    p = shell(floor_tex, under(wall_left_tex, paper_dots), under(wall_right_tex, paper_dots))
    # шкафы
    p.append(box(0, 0, 0, 107, 28, COUNTER_H, M_SAGE, cab_r_tex))
    p.append(box(0, 28, 0, 28, 107, COUNTER_H, M_SAGE, cab_l_tex))
    p.append(box(60, 0, 0, 86, 28.6, COUNTER_H, M_STOVE, stove_tex))
    # столешницы
    p.append(box(0, 0, COUNTER_H, 108, 30, TOP_H, M_TOP, counter_r_tex))
    p.append(box(0, 30, COUNTER_H, 30, 108, TOP_H, M_TOP, counter_l_tex))
    # кран
    p.append(cyl(3.5, 68, 2, TOP_H, TOP_H + 1, M_METAL))
    p.append(cyl(3.5, 68, 1.3, TOP_H, 49, M_METAL))
    p.append(box(3, 66.8, 47, 11, 69.2, 49.4, M_METAL))
    p.append(box(9, 66.8, 44.5, 11, 69.2, 47, M_METAL))
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
    # шторы на окне
    p += curtain(44, 92, 50, 80, M_CURTAIN)
    # рейлинг под полкой: половник, лопатка, венчик
    p.append(box(32, 0.4, 61.5, 92, 1.4, 62.5, M_METAL))
    p.append(box(40, 0.8, 52, 40.8, 1.8, 61.5, M_METAL))
    p.append(cyl(40.4, 2.6, 1.6, 50.5, 52.2, M_METAL))
    p.append(box(52, 0.8, 50, 52.8, 1.8, 61.5, M_WOOD))
    p.append(box(50.8, 0.8, 47, 54, 2.2, 50.5, M_WOOD))
    p.append(box(64, 0.8, 54, 64.8, 1.8, 61.5, M_METAL))
    p.append(sphere(64.4, 1.8, 52.5, 1.6, M_METAL))
    # мусорное ведро и выключатель
    p.append(cyl(38, 38, 4.2, 0, 13, M_CREAM))
    p.append(cyl(38, 38, 4.5, 13, 14.4, M_METAL))
    p.append(box(104, 0, 50, 107, 0.6, 55, M_CREAM))
    # декор: розетки на фартуке, полотенце на ручке духовки
    M_TOWEL = Mat(top="i", left="r", right="R", edge="o")
    p.append(box(36, 0, 46, 42, 0.8, 50, M_CREAM))
    p.append(box(92, 0, 46, 98, 0.8, 50, M_CREAM))
    p.append(box(66, 28.6, 13, 72, 29.6, 26, M_TOWEL, lambda x, y, z, f, k, nz: "W" if f == FACE_LEFT and int(z) % 3 == 0 else None))
    return p


DOORS = [
    {
        "id": "fridge",
        "closed": [box(112, 28, 0.5, 142, 31, 79.5, M_CREAM, fridge_door_tex)],
        "open": [box(109, 31, 0.5, 112, 59, 79.5, M_CREAM, fridge_door_inner_tex)],
        "closed_depth": 142 + 31,
        "open_depth": 112 + 59,
    },
]

ZONES = [
    # на стенах: левая — u вдоль стены (u = -y), правая — u = x
    {"id": "wall_l", "tag": "wall", "wall": "L", "u0": -36, "u1": -6, "z0": 50, "z1": 82},
    {"id": "wall_r", "tag": "wall", "wall": "R", "u0": 2, "u1": 24, "z0": 63, "z1": 82},
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
