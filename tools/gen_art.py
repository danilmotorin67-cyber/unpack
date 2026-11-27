"""Генератор пиксель-арта для игры.

Запуск из корня репозитория:
    python3 tools/gen_art.py

Пишет PNG в game/assets/ и шрифт в game/scripts/font_data.gd.
Каждый спрайт проверяется на соответствие палитре (tools/palette.py).
"""
import os
import sys

from PIL import Image

from palette import ALLOWED, rgba

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES = os.path.join(ROOT, "game", "assets", "sprites")
FONT_DIR = os.path.join(ROOT, "game", "assets", "font")
SCRIPTS = os.path.join(ROOT, "game", "scripts")


# ---------------------------------------------------------------- helpers

def from_map(rows, pad=1):
    """Спрайт из текстовой карты. '.' — прозрачный. pad — прозрачная рамка
    (нужна шейдеру обводки)."""
    w = max(len(r) for r in rows)
    img = Image.new("RGBA", (w + pad * 2, len(rows) + pad * 2), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch not in ". ":
                img.putpixel((x + pad, y + pad), rgba(ch))
    return img


class Canvas:
    def __init__(self, w, h, fill=None):
        self.img = Image.new("RGBA", (w, h), rgba(fill) if fill else (0, 0, 0, 0))
        self.w, self.h = w, h

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((x, y), rgba(c))

    def rect(self, x0, y0, x1, y1, c):
        """Заливка, границы включительно."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def frame(self, x0, y0, x1, y1, c):
        self.hline(x0, x1, y0, c)
        self.hline(x0, x1, y1, c)
        self.vline(x0, y0, y1, c)
        self.vline(x1, y0, y1, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def blit(self, sprite, x, y):
        self.img.alpha_composite(sprite, (x, y))


def check_palette(name, img):
    bad = {p for p in list(img.getdata()) if p[3] != 0 and p not in ALLOWED}
    if bad:
        sys.exit(f"{name}: цвета вне палитры: {sorted(bad)[:5]}")


def save(name, img, folder=SPRITES):
    check_palette(name, img)
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, name + ".png"))


# ---------------------------------------------------------------- items

ITEMS = {
    "plates": [
        ".oooooooooooo.",
        "oWWWWWWWWWWWWo",
        ".oCCCCCCCCCCo.",
        "oWWWWWWWWWWWWo",
        ".oCCCCCCCCCCo.",
        "oWWWWWWWWWWWWo",
        ".oCCCCCCCCCCo.",
        "..oooooooooo..",
    ],
    "bowl": [
        "oooooooooo",
        "oLLLLLLLLo",
        "olWllllllo",
        ".ollllllo.",
        "..oLLLLo..",
        "...oooo...",
    ],
    "mug_red": [
        "ooooooo..",
        "oWrrrro..",
        "orrrrrooo",
        "orrrrro.o",
        "orrrrro.o",
        "orrrrrooo",
        "oRRRRRo..",
        "ooooooo..",
    ],
    "mug_blue": [
        "ooooooo..",
        "oWllllo..",
        "olllllooo",
        "olllllo.o",
        "olllllo.o",
        "olllllooo",
        "oLLLLLo..",
        "ooooooo..",
    ],
    "glass": [
        "oooooo",
        "oWtTto",
        "otttTo",
        "otttTo",
        "otttTo",
        "otttTo",
        "oTTTTo",
        "oooooo",
    ],
    "pot": [
        "......oooo......",
        ".....oxxxxo.....",
        "..oooooooooooo..",
        ".oSssssssssssSo.",
        "oooooooooooooooo",
        "ooosssssssssSooo",
        "o.osssssssssSo.o",
        "ooosssssssssSooo",
        "..oSssssssssSo..",
        "..oSSSSSSSSSSo..",
        "...oooooooooo...",
    ],
    "pan": [
        "oooooooooo........",
        "oSSSSSSSSoooooooo.",
        "oddddddddovvvvvvvo",
        ".oddddddo.oooooooo",
        "..oooooo..........",
    ],
    "kettle": [
        "......oo.....",
        ".....oxxo....",
        "...ooooooo...",
        "o.oWyyyyyyoo.",
        "ooyyyyyyyyo.o",
        ".oyyyyyyyyo.o",
        "..oyyyyyyyo.o",
        "..oyyyyyyyooo",
        "..oRyyyyyRo..",
        "..oRRRRRRRo..",
        "..ooooooooo..",
    ],
    "cutting_board": [
        "....oooooo....",
        "...owwwwwwo...",
        "...owwoowwo...",
        "...owwwwwwo...",
        ".oooooooooooo.",
        "owwwwwwwwwwwvo",
        "owwwwwwwwwwwvo",
        "owwwwwwwwwwwvo",
        "ovvvvvvvvvvvvo",
        ".oooooooooooo.",
    ],
    "knife_block": [
        ".oo.oo.oo.",
        ".od.od.do.",
        ".od.od.do.",
        "oooooooooo",
        "owwwwwwwvo",
        "owwwwwwwvo",
        "owwwwwwwvo",
        "owwwwwwwvo",
        "ovvvvvvvvo",
        "oooooooooo",
    ],
    "soap": [
        "..o..",
        ".oxo.",
        ".ooo.",
        "oWeeo",
        "oeeeo",
        "oWWWo",
        "oWWWo",
        "oeeeo",
        "oEEEo",
        "ooooo",
    ],
    "plant": [
        "....o.o....",
        "...oeoeo...",
        ".o.oeoeo.o.",
        "oeooEoEooeo",
        "oEeoEeEoeEo",
        ".oEeoEoeEo.",
        "..oEeEeEo..",
        "...oEEEo...",
        ".ooooooooo.",
        ".oWrrrrrro.",
        "..orrrrro..",
        "..oRrrrRo..",
        "..oRRRRRo..",
        "...ooooo...",
    ],
    "milk": [
        "..ooo..",
        ".oWWWo.",
        "oWWWWWo",
        "ooooooo",
        "oWWWWSo",
        "olllllo",
        "olWWllo",
        "olllllo",
        "oWWWWSo",
        "oWWWWSo",
        "oSSSSSo",
        "ooooooo",
    ],
    "cheese": [
        ".....ooo.",
        "...ooyyyo",
        ".ooyyyyyo",
        "oyyyyoyyo",
        "oyoyyyyRo",
        "ooooooooo",
    ],
    "spices": [
        "oooo.oooo",
        "oxxo.oxxo",
        "oooo.oooo",
        "oyWo.orWo",
        "oyyo.orro",
        "oyyo.orro",
        "oooo.oooo",
    ],
}


# ---------------------------------------------------------------- boxes

def box_closed():
    w, h = 36, 26
    c = Canvas(w, h)
    c.rect(0, 0, w - 1, h - 1, "o")
    # верхняя грань
    c.rect(1, 1, w - 2, 5, "b")
    c.hline(1, w - 2, 5, "B")
    c.vline(w // 2 - 1, 1, 4, "n")  # шов между створками
    # передняя грань
    c.rect(1, 6, w - 2, h - 2, "b")
    c.vline(w - 2, 6, h - 2, "B")
    c.hline(1, w - 2, h - 2, "B")
    # скотч
    c.rect(w // 2 - 3, 1, w // 2 + 2, 9, "C")
    c.hline(w // 2 - 3, w // 2 + 2, 5, "k")
    c.vline(w // 2 - 1, 1, 4, "k")
    # надпись маркером
    for x in range(5, 13):
        c.px(x, 14 + (x % 2), "n")
    for x in range(6, 11):
        c.px(x, 18, "n")
    # подпись "стекло" — кружок-стрелка
    c.rect(26, 15, 29, 15, "n")
    c.rect(27, 14, 28, 14, "n")
    c.rect(27, 16, 28, 19, "n")
    return pad(c.img)


def box_open():
    w, h = 36, 32  # +6 сверху на раскрытые створки
    c = Canvas(w, h)
    top = 6
    # передняя грань (как у закрытой)
    c.rect(0, top + 5, w - 1, h - 1, "o")
    c.rect(1, top + 6, w - 2, h - 2, "b")
    c.vline(w - 2, top + 6, h - 2, "B")
    c.hline(1, w - 2, h - 2, "B")
    # проём
    c.rect(0, top, w - 1, top + 5, "o")
    c.rect(2, top + 1, w - 3, top + 4, "n")
    c.hline(2, w - 3, top + 1, "u")
    # створки
    for i in range(6):
        # левая
        c.hline(0 + i // 2, 9 + i // 2, top - 6 + i, "o" if i == 0 else ("b" if i < 5 else "B"))
        c.px(0 + i // 2, top - 6 + i, "o")
        c.px(9 + i // 2, top - 6 + i, "o")
        # правая
        c.hline(w - 10 - i // 2, w - 1 - i // 2, top - 6 + i, "o" if i == 0 else ("b" if i < 5 else "B"))
        c.px(w - 10 - i // 2, top - 6 + i, "o")
        c.px(w - 1 - i // 2, top - 6 + i, "o")
    # край скотча на передней грани
    c.rect(w // 2 - 3, top + 6, w // 2 + 2, top + 9, "C")
    for x in range(5, 13):
        c.px(x, 14 + top - 0 + (x % 2), "n")
    for x in range(6, 11):
        c.px(x, 18 + top, "n")
    c.rect(26, 15 + top, 29, 15 + top, "n")
    c.rect(27, 14 + top, 28, 14 + top, "n")
    c.rect(27, 16 + top, 28, 19 + top, "n")
    return pad(c.img)


def pad(img, p=1):
    out = Image.new("RGBA", (img.width + 2 * p, img.height + 2 * p), (0, 0, 0, 0))
    out.paste(img, (p, p))
    return out


# ---------------------------------------------------------------- kitchen

def kitchen_bg():
    W, H = 320, 180
    c = Canvas(W, H, "c")

    # --- обои: мелкий ромбик
    for y in range(4, 128, 8):
        for x in range(4 + (y // 8 % 2) * 6, W, 12):
            c.px(x, y, "C")
    c.rect(0, 0, W - 1, 1, "C")

    # --- пол
    FLOOR = 132
    c.rect(0, FLOOR, W - 1, H - 1, "w")
    for i, y in enumerate(range(FLOOR, H, 8)):
        c.hline(0, W - 1, y, "v")
        off = (i * 23) % 40
        for x in range(off, W, 40):
            c.vline(x, y + 1, min(y + 7, H - 1), "v")
        # блик доски
        for x in range(off + 3, W, 40):
            c.hline(x, x + 6, y + 2, "b")
    c.hline(0, W - 1, FLOOR, "u")
    c.hline(0, W - 1, FLOOR + 1, "v")

    # --- плинтус
    c.rect(0, 126, W - 1, 131, "C")
    c.hline(0, W - 1, 126, "W")
    c.hline(0, W - 1, 131, "k")

    # --- фартук (плитка)
    c.rect(14, 66, 216, 91, "t")
    for y in range(66, 92, 6):
        c.hline(14, 216, y, "T")
    for row, y in enumerate(range(66, 92, 6)):
        for x in range(14 + (row % 2) * 6, 217, 12):
            c.vline(x, y, min(y + 5, 91), "T")

    # --- окно
    c.rect(28, 16, 76, 60, "o")
    c.rect(29, 17, 75, 59, "W")
    c.rect(31, 19, 73, 57, "l")
    # небо светлее сверху
    c.rect(31, 19, 73, 30, "t")
    for x in range(31, 74, 2):
        c.px(x, 31, "t")
    # дерево за окном
    for (cx, cy, r) in [(40, 50, 9), (52, 54, 7), (66, 52, 8)]:
        for y in range(cy - r, 58):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and 31 <= x <= 73 and 19 <= y <= 57:
                    c.px(x, y, "e" if (x + y) % 5 else "E")
    # блики стекла
    for i in range(6):
        c.px(34 + i, 28 - i, "W")
        c.px(36 + i, 28 - i, "W")
    # переплёт
    c.rect(51, 17, 53, 59, "W")
    c.rect(29, 37, 75, 38, "W")
    c.vline(51, 19, 57, "C")
    c.hline(31, 73, 38, "C")
    # подоконник
    c.rect(24, 61, 80, 65, "o")
    c.rect(25, 61, 79, 64, "C")
    c.hline(25, 79, 61, "W")
    c.hline(25, 79, 64, "k")
    c.hline(26, 78, 66, "C")  # тень

    # --- верхний шкаф (открытые полки)
    c.rect(94, 11, 178, 14, "o")
    c.rect(95, 12, 177, 13, "G")
    c.hline(95, 177, 12, "g")
    c.rect(96, 14, 176, 62, "o")
    c.rect(97, 15, 175, 61, "g")
    c.rect(99, 17, 173, 58, "k")
    c.rect(99, 17, 173, 18, "C")  # тень сверху внутри
    c.vline(99, 17, 58, "C")
    # средняя полка: верх доски = 37
    c.rect(99, 37, 173, 39, "G")
    c.hline(99, 173, 37, "g")
    c.hline(99, 173, 39, "h")
    c.hline(99, 173, 40, "C")  # тень под полкой
    # нижняя доска: верх = 59
    c.rect(97, 59, 175, 61, "g")
    c.hline(97, 175, 59, "g")
    c.hline(97, 175, 61, "G")
    c.vline(175, 15, 61, "G")
    c.hline(97, 175, 62, "o")
    c.hline(96, 176, 63, "C")  # тень на стене

    # --- настенная полка
    c.rect(177, 49, 215, 52, "o")
    c.rect(178, 50, 214, 51, "w")
    c.hline(178, 214, 50, "b")
    c.hline(178, 214, 51, "v")
    for bx in (183, 209):
        c.rect(bx, 53, bx + 1, 57, "o")
        c.px(bx + 2, 53, "o")
        c.px(bx + 2, 54, "o")
    c.hline(178, 214, 53, "C")

    # --- нижние шкафы
    c.rect(14, 97, 216, 131, "o")
    c.rect(15, 98, 215, 126, "g")
    c.rect(15, 127, 215, 131, "d")  # цоколь
    # ящики сверху (левая и правая секции)
    def section(x0, x1, doors):
        c.hline(x0, x1, 104, "h")
        c.hline(x0, x1, 98, "g")
        n = doors
        step = (x1 - x0 + 1) / n
        for i in range(n):
            dx0 = int(x0 + i * step)
            dx1 = int(x0 + (i + 1) * step) - 1
            c.vline(dx1, 98, 126, "h")
            c.vline(dx0, 98, 126, "g")
            # ручка ящика
            mid = (dx0 + dx1) // 2
            c.rect(mid - 2, 101, mid + 2, 101, "S")
            # дверца: рамка-филёнка
            c.frame(dx0 + 3, 107, dx1 - 3, 123, "G")
            c.hline(dx0 + 3, dx1 - 3, 107, "h")
            # ручка дверцы
            hx = dx1 - 5 if i % 2 == 0 else dx0 + 5
            c.rect(hx, 110, hx, 113, "S")
    section(15, 119, 4)
    section(161, 215, 2)
    # плита
    c.rect(120, 97, 160, 126, "o")
    c.rect(121, 98, 159, 126, "s")
    c.hline(121, 159, 98, "W")
    for kx in range(125, 158, 7):
        c.rect(kx, 100, kx + 1, 101, "x")
    c.rect(124, 105, 156, 123, "x")
    c.rect(126, 108, 154, 121, "d")
    c.hline(126, 154, 108, "m")
    c.rect(130, 106, 150, 106, "S")  # ручка духовки
    c.vline(159, 98, 126, "S")

    # столешница: верх = 92
    c.rect(13, 92, 217, 96, "o")
    c.rect(14, 92, 216, 95, "w")
    c.hline(14, 216, 92, "b")
    c.hline(14, 216, 95, "v")
    # варочная поверхность
    c.rect(120, 92, 160, 95, "S")
    c.hline(120, 160, 92, "s")
    for gx0 in (124, 142):
        c.rect(gx0, 90, gx0 + 14, 91, "o")
        c.rect(gx0 + 1, 90, gx0 + 13, 90, "x")
    # мойка: бортик и кран
    c.hline(34, 70, 92, "s")
    c.hline(34, 70, 93, "S")
    c.rect(49, 80, 51, 91, "o")
    c.vline(50, 81, 91, "s")
    c.rect(49, 78, 58, 80, "o")
    c.hline(50, 57, 79, "s")
    c.rect(57, 80, 59, 83, "o")
    c.vline(58, 80, 82, "S")
    c.rect(46, 89, 54, 91, "o")
    c.rect(47, 90, 53, 90, "S")

    # --- холодильник (корпус и внутренности; дверь — отдельный спрайт)
    c.rect(226, 28, 266, 131, "o")
    c.rect(227, 29, 265, 130, "W")
    c.vline(265, 29, 130, "C")
    c.rect(229, 31, 263, 127, "t")
    c.rect(229, 31, 263, 32, "T")
    c.vline(263, 31, 127, "T")
    for sy in (62, 96):
        c.rect(229, sy, 263, sy + 1, "S")
        c.hline(229, 263, sy, "s")
    c.rect(229, 125, 263, 127, "T")
    c.hline(229, 263, 125, "s")
    c.rect(227, 128, 265, 130, "C")
    # лампочка
    c.rect(244, 33, 247, 34, "W")
    # тень от холодильника на стене
    c.vline(267, 30, 125, "C")
    c.vline(268, 32, 125, "C")

    # --- часы
    cx, cy, r = 298, 40, 7
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= (r + 1) ** 2:
                c.px(x, y, "o")
            if d <= r * r:
                c.px(x, y, "W")
    c.vline(cx, cy - 5, cy, "o")
    c.hline(cx, cx + 3, cy, "o")
    for (dx, dy) in [(0, -6), (6, 0), (0, 6), (-6, 0)]:
        c.px(cx + dx, cy + dy, "m")
    c.hline(cx - 6, cx + 6, cy + r + 2, "C")

    # --- полотенце на крючке справа от плиты? — нет: акцент только на предметах.
    return c.img


def fridge_door_closed():
    w, h = 41, 104  # x 226..266, y 28..131
    c = Canvas(w, h)
    c.rect(0, 0, w - 1, h - 1, "o")
    c.rect(1, 1, w - 2, h - 2, "W")
    c.vline(w - 2, 1, h - 2, "C")
    c.hline(1, w - 2, h - 2, "C")
    # морозилка / основная камера
    c.hline(1, w - 2, 30, "m")
    c.hline(1, w - 2, 31, "C")
    # ручки
    c.rect(3, 10, 5, 24, "o")
    c.vline(4, 11, 23, "s")
    c.rect(3, 36, 5, 64, "o")
    c.vline(4, 37, 63, "s")
    # блик
    c.vline(1, 2, 28, "W")
    # магнитики? — нет, только мебель
    c.rect(1, h - 5, w - 2, h - 2, "C")
    c.hline(1, w - 2, h - 5, "k")
    return pad(c.img)


def fridge_door_open():
    w, h = 12, 104  # x 267..278
    c = Canvas(w, h)
    c.rect(0, 0, w - 1, h - 1, "o")
    c.rect(1, 1, w - 2, h - 2, "C")
    c.vline(1, 1, h - 2, "W")
    c.vline(w - 2, 1, h - 2, "k")
    for by in (20, 44, 70, 92):
        c.rect(1, by, w - 2, by + 3, "T")
        c.hline(1, w - 2, by, "s")
    c.hline(1, w - 2, 30, "m")
    return pad(c.img)


# ---------------------------------------------------------------- cursors

CURSORS = {
    "cursor_arrow": [
        "o......",
        "oo.....",
        "oWo....",
        "oWWo...",
        "oWWWo..",
        "oWWWWo.",
        "oWWWWWo",
        "oWWoooo",
        "ooo....",
    ],
    "cursor_hand": [
        "...oo....",
        "..oWWo...",
        "..oWWoo..",
        "..oWWWWoo",
        "ooWWWWWWo",
        "oWoWWWWWo",
        ".oWWWWWWo",
        "..oWWWWo.",
        "...oWWWo.",
        "...ooooo.",
    ],
    "cursor_grab": [
        "..oooooo.",
        ".oWWWWWWo",
        "ooWWWWWWo",
        "oWWWWWWWo",
        ".oWWWWWWo",
        "..oWWWWo.",
        "...ooooo.",
    ],
}


# ---------------------------------------------------------------- font 5x7

GLYPHS = {
    "А": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "Б": ["#####", "#....", "#....", "####.", "#...#", "#...#", "####."],
    "В": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "Г": ["#####", "#....", "#....", "#....", "#....", "#....", "#...."],
    "Д": [".###.", ".#.#.", ".#.#.", ".#.#.", ".#.#.", "#####", "#...#"],
    "Е": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "Ж": ["#.#.#", "#.#.#", ".###.", "..#..", ".###.", "#.#.#", "#.#.#"],
    "З": [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    "И": ["#...#", "#...#", "#..##", "#.#.#", "##..#", "#...#", "#...#"],
    "Й": ["..#..", "#...#", "#..##", "#.#.#", "##..#", "#...#", "#...#"],
    "К": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "Л": ["..###", ".#..#", ".#..#", ".#..#", ".#..#", "#...#", "#...#"],
    "М": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "Н": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "О": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "П": ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#"],
    "Р": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "С": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "Т": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "У": ["#...#", "#...#", "#...#", ".####", "....#", "#...#", ".###."],
    "Ф": ["..#..", ".###.", "#.#.#", "#.#.#", ".###.", "..#..", "..#.."],
    "Х": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Ц": ["#..#.", "#..#.", "#..#.", "#..#.", "#..#.", "#####", "....#"],
    "Ч": ["#...#", "#...#", "#...#", ".####", "....#", "....#", "....#"],
    "Ш": ["#.#.#", "#.#.#", "#.#.#", "#.#.#", "#.#.#", "#.#.#", "#####"],
    "Щ": ["#.#.#", "#.#.#", "#.#.#", "#.#.#", "#.#.#", "#####", "....#"],
    "Ъ": ["##...", ".#...", ".#...", ".###.", ".#..#", ".#..#", ".###."],
    "Ы": ["#...#", "#...#", "#...#", "##..#", "#.#.#", "#.#.#", "##..#"],
    "Ь": ["#....", "#....", "#....", "####.", "#...#", "#...#", "####."],
    "Э": [".###.", "#...#", "....#", "..###", "....#", "#...#", ".###."],
    "Ю": ["#..#.", "#.#.#", "#.#.#", "###.#", "#.#.#", "#.#.#", "#..#."],
    "Я": [".####", "#...#", "#...#", ".####", "..#.#", ".#..#", "#...#"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    ",": ["..", "..", "..", "..", "..", ".#", "#."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "-": ["...", "...", "...", "###", "...", "...", "..."],
    ":": [".", ".", "#", ".", ".", "#", "."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
}
GLYPHS["Ё"] = GLYPHS["Е"]
# латиница: свои глифы для R S F I, остальное — как у похожих кириллических
GLYPHS["R"] = ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"]
GLYPHS["S"] = [".####", "#....", "#....", ".###.", "....#", "....#", "####."]
GLYPHS["F"] = GLYPHS["Г"][:3] + ["####."] + GLYPHS["Г"][4:]
GLYPHS["I"] = ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"]
for lat, cyr in zip("ABCEHKMOPTXY", "АВСЕНКМОРТХУ"):
    GLYPHS[lat] = GLYPHS[cyr]


def font():
    chars = list(GLYPHS.keys())
    total = sum(len(GLYPHS[ch][0]) for ch in chars)
    img = Image.new("RGBA", (total, 7), (0, 0, 0, 0))
    entries = []
    x = 0
    white = rgba("W")
    for ch in chars:
        g = GLYPHS[ch]
        w = len(g[0])
        assert all(len(r) == w for r in g), ch
        for y, row in enumerate(g):
            for i, p in enumerate(row):
                if p == "#":
                    img.putpixel((x + i, y), white)
        entries.append((ch, x, w))
        x += w
    save("font", img, FONT_DIR)
    lines = [
        "# Сгенерировано tools/gen_art.py — не редактировать вручную.",
        "extends RefCounted",
        "",
        "const HEIGHT := 7",
        "const GLYPHS := {",
    ]
    for ch, gx, w in entries:
        lines.append(f'\t"{ch}": Vector2i({gx}, {w}),')
    lines.append("}")
    with open(os.path.join(SCRIPTS, "font_data.gd"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- main

def main():
    for name, rows in ITEMS.items():
        widths = {len(r) for r in rows}
        if len(widths) != 1:
            sys.exit(f"{name}: строки разной длины {widths}")
        save("item_" + name, from_map(rows))
    for name, rows in CURSORS.items():
        save(name, from_map(rows, pad=0))
    save("box_closed", box_closed())
    save("box_open", box_open())
    save("kitchen_bg", kitchen_bg())
    save("fridge_closed", fridge_door_closed())
    save("fridge_open", fridge_door_open())
    font()
    # иконка приложения: закрытая коробка ×4
    icon = box_closed().resize((38 * 4, 28 * 4), Image.NEAREST)
    canvas = Image.new("RGBA", (152, 152), (0, 0, 0, 0))
    canvas.alpha_composite(icon, (0, 20))
    canvas.save(os.path.join(ROOT, "game", "icon.png"))
    print("ok")


if __name__ == "__main__":
    main()
