"""Портрет для приветственного диалога — нарисован попиксельно.

Основа (голова, стрижка кроп, футболка) задаётся рядами пикселей. Эмоции
собираются из слоёв: брови, глаза, рот и эффекты (румянец, сердечко,
искорка). Каждый слой — PNG размером с портрет, прозрачный вне своей зоны;
в игре они накладываются друг на друга.

Запуск из корня репозитория: python3 tools/portrait.py
"""
import os

from PIL import Image

from palette import ALLOWED, rgba

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "game", "assets", "portrait")
W, H = 40, 44

# Ключи: 5 — контур (тёмный орех), { } < > — тёмно-коричневые волосы,
# ( ) [ ] — кожа, W — белки/зубы, E % — тёмно-зелёные глаза, o — зрачки/ресницы,
# R r — рот, g G h H — футболка (шалфей).
SKIN = set("()[]")

BASE_ROWS = {
    1: (14, "5" * 10),
    2: (11, "555<<>>>><<<<555"),
    3: (9, "55<<<>>>>><<<<<<}}55"),
    4: (8, "5<<<>>>>><<<<<<<}}}}}5"),
    5: (7, "5<<<<>>>><<<<<<<<}}}}}}5"),
    6: (7, "5<<<<<<<<<<>><<<<<}}}}}5"),
    7: (7, "5}<<<<<<<<<>>><<<<}}}}}5"),
    8: (7, "5}<<<<>><<<<<<>><<<}}}}5"),
    9: (7, "5}}<<<}<<<<}<<<<}<<}}}}5"),
    10: (7, "5}}{[}<<{[[}<<{][}<{}}}5"),
    11: (7, "5{}" + ")" * 19 + "}5"),
    12: (7, "5{}" + "]]]" + "[" * 12 + "))))" + "}5"),
    13: (8, "5{" + "]]]" + "[" * 12 + "))))" + "{5"),
    14: (8, "5{" + "]]]" + "}{{{}" + "[[[[" + "}{{{}" + "))" + "{5"),
    15: (8, "5{" + "]]" + "[" * 13 + "))))" + "{5"),
    16: (7, "5)[" + "]]" + "[" + "oooo[" + "[[[[" + "[oooo" + "))" + "))5"),
    17: (7, "5)[" + "]]" + "[" + "WEoEW" + "[[[[" + "WEoEW" + "))" + "))5"),
    18: (7, "5([" + "]]" + "[[" + "%E%" + "[" + "[[[[" + "[" + "%E%" + "[" + "))" + "()5"),
    19: (7, "5)[" + "]]" + "[[" + ")))" + "[" + "[[[[" + "[" + ")))" + "[" + "))" + "))5"),
    20: (7, "5)[" + "]]]" + "[" * 12 + "))))" + "))5"),
    21: (8, "5)" + "]]]" + "[" * 6 + ")" + "[" * 5 + "))))" + ")5"),
    22: (9, "5" + "]]]" + "[" * 5 + ")" + "[" + ")" + "[" * 4 + "))))" + "5"),
    23: (9, "5" + "]]" + "[" * 13 + "))))" + "5"),
    24: (9, "5" + "]]" + "[" * 13 + "))))" + "5"),
    25: (9, "5" + "]]" + "[" * 13 + "))))" + "5"),
    26: (10, "5" + "[" * 13 + "))))" + "5"),
    27: (11, "5" + "[" * 11 + "))))" + "5"),
    28: (12, "5" + "[" * 9 + "))))" + "5"),
    29: (13, "5" + "[" * 7 + "))))" + "5"),
    30: (14, "5" * 11),
    31: (15, "5" + "(" * 8 + "5"),
    32: (15, "5" + ")" + "[" * 5 + "))" + "5"),
    33: (15, "5" + ")" + "[" * 5 + "))" + "5"),
}


def base_grid():
    g = [["." for _ in range(W)] for _ in range(H)]
    for y, (x0, s) in BASE_ROWS.items():
        for i, ch in enumerate(s):
            g[y][x0 + i] = ch
    # футболка: плечи расходятся вниз, свет слева, складки у рук
    for i, y in enumerate(range(34, H)):
        L = max(1, 9 - 2 * i)
        R = min(W - 2, 30 + 2 * i)
        for x in range(L, R + 1):
            if x in (L, R):
                c = "H"
            elif x < 14:
                c = "g"
            elif x > 26:
                c = "h"
            else:
                c = "G"
            if i >= 4 and x in (L + 4, R - 4):
                c = "h" if x < 20 else "H"
            g[y][x] = c
    # горловина: шея уходит в ворот
    for x in range(16, 24):
        g[34][x] = ")"
    g[34][15] = g[34][24] = "h"
    for x in range(15, 25):
        g[35][x] = "h"
    for x in range(16, 24):
        g[36][x] = "G"
    return g


def skin_at(g, x, y):
    c = g[y][x]
    if c in SKIN:
        return c
    return "]" if x <= 12 else (")" if x >= 25 else "[")


# ------------------------------------------------------------------ слои

BROW_L, BROW_R = 13, 22   # левые колонки бровей (по 5 пикселей)
EYE_L, EYE_R = 13, 22


def layer(region, draw):
    """region: список (x0, y0, x1, y1) — зона слоя (включительно), её фон — кожа.
    draw(put) — рисует черты поверх."""
    g = base_grid()
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cells = {}
    for x0, y0, x1, y1 in region:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                cells[(x, y)] = skin_at(g, x, y)

    def put(x, y, c):
        cells[(x, y)] = c

    draw(put)
    for (x, y), c in cells.items():
        img.putpixel((x, y), rgba(c))
    return img


BROWS_REGION = [(BROW_L, 13, BROW_L + 4, 15), (BROW_R, 13, BROW_R + 4, 15)]
EYES_REGION = [(EYE_L, 16, EYE_L + 4, 19), (EYE_R, 16, EYE_R + 4, 19)]
MOUTH_REGION = [(15, 23, 24, 27)]


def row(put, x0, y, s):
    for i, c in enumerate(s):
        if c != " ":
            put(x0 + i, y, c)


def brows(kind):
    def d(put):
        for side, x0 in (("L", BROW_L), ("R", BROW_R)):
            if kind == "normal":
                row(put, x0, 14, "}{{{}")
            elif kind == "raised":
                row(put, x0, 13, "}{{{}")
            elif kind == "happy":
                row(put, x0 + 1, 13, "{{{")
                put(x0, 14, "}")
                put(x0 + 4, 14, "}")
            elif kind == "soft":  # внутренние концы приподняты — нежно, чуть смущённо
                if side == "L":
                    row(put, x0, 14, "}{{")
                    row(put, x0 + 3, 13, "{}")
                else:
                    row(put, x0, 13, "}{")
                    row(put, x0 + 2, 14, "{{}")
    return d


def eye(put, x0, kind, side="L"):
    # ресницы гуще к внешнему уголку глаза
    lash = "oooo " if side == "L" else " oooo"
    if kind == "open":
        row(put, x0, 16, lash)
        row(put, x0, 17, "WEoEW")
        row(put, x0 + 1, 18, "%E%")
        row(put, x0 + 1, 19, ")))")
    elif kind == "happy":  # закрытые от улыбки глаза-дуги
        row(put, x0 + 1, 17, "ooo")
        put(x0, 18, "o")
        put(x0 + 4, 18, "o")
    elif kind == "blink":
        row(put, x0, 18, "ooooo")
        row(put, x0 + 1, 19, ")))")
    elif kind == "aside":  # взгляд в сторону
        row(put, x0, 16, lash)
        row(put, x0, 17, "EoEWW")
        row(put, x0, 18, "%E%")
        row(put, x0 + 1, 19, ")))")


def eyes(kind):
    def d(put):
        if kind == "wink":
            eye(put, EYE_L, "open", "L")
            eye(put, EYE_R, "happy", "R")
        else:
            eye(put, EYE_L, kind, "L")
            eye(put, EYE_R, kind, "R")
    return d


def mouth(kind):
    def d(put):
        if kind == "grin":  # широкая улыбка с зубами
            put(15, 23, "R")
            put(24, 23, "R")
            row(put, 16, 24, "RWWWWWWR")
            row(put, 17, 25, "RrrrrR")
            row(put, 18, 26, "RRRR")
        elif kind == "smile":
            put(15, 23, "R")
            put(24, 23, "R")
            put(16, 24, "R")
            put(23, 24, "R")
            row(put, 17, 25, "RRRRRR")
        elif kind == "soft":
            put(17, 24, "R")
            put(22, 24, "R")
            row(put, 18, 25, "RRRR")
        elif kind == "talk":
            row(put, 17, 24, "RRRRRR")
            row(put, 17, 25, "RrrrrR")
            row(put, 18, 26, "RRRR")
        elif kind == "oh":
            row(put, 18, 24, "RRRR")
            row(put, 17, 25, "RrrrrR")
            row(put, 17, 26, "RrrrrR")
            row(put, 18, 27, "RRRR")
    return d


def extra(kind):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def put(x, y, c):
        img.putpixel((x, y), rgba(c))
    if kind == "blush":
        for x in (11, 12, 13, 25, 26, 27):
            put(x, 21, "i")
        put(12, 22, "i")
        put(26, 22, "i")
    elif kind == "heart":
        rows = {
            1: (33, "RR RR"),
            2: (32, "RVrRrrR"),
            3: (32, "RrrrrrR"),
            4: (33, "RrrrR"),
            5: (34, "RrR"),
            6: (35, "R"),
        }
        for y, (x0, s) in rows.items():
            for i, c in enumerate(s):
                if c != " ":
                    put(x0 + i, y, c)
    elif kind == "sparkle":
        for y, x0, s in ((8, 35, "X"), (9, 35, "y"), (10, 33, "XyWyX"), (11, 35, "y"), (12, 35, "X"), (4, 37, "X"), (5, 36, "XWX"), (6, 37, "X")):
            for i, c in enumerate(s):
                put(x0 + i, y, c)
    return img


def base_image():
    g = base_grid()
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            if g[y][x] != ".":
                img.putpixel((x, y), rgba(g[y][x]))
    return img


# эмоция -> (брови, глаза, рот, эффекты)
EMOTIONS = {
    "happy": ("happy", "happy", "grin", []),
    "smile": ("normal", "open", "smile", []),
    "wink": ("happy", "wink", "grin", []),
    "shy": ("soft", "aside", "soft", ["blush"]),
    "excited": ("raised", "open", "grin", ["sparkle"]),
    "love": ("soft", "happy", "smile", ["blush", "heart"]),
}


def check(name, img):
    bad = {p for p in list(img.convert("RGBA").getdata()) if p[3] and p not in ALLOWED}
    assert not bad, (name, bad)


def save(name, img):
    check(name, img)
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, name + ".png"))


def ui():
    """Рамка диалога (9-slice 12×12) и стрелка «дальше»."""
    f = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
    for y in range(12):
        for x in range(12):
            corner = (x in (0, 11) and y in (0, 1, 10, 11)) or (y in (0, 11) and x in (0, 1, 10, 11))
            if corner:
                continue
            edge = x in (0, 11) or y in (0, 11) or (x in (1, 10) and y in (1, 10))
            if edge:
                c = "5"
            elif x == 1 or y == 1 or x == 10 or y == 10:
                c = "C"
            else:
                c = "W"
            f.putpixel((x, y), rgba(c))
    for (x, y) in ((1, 1), (10, 1), (1, 10), (10, 10)):
        f.putpixel((x, y), rgba("5"))
    save("frame", f)
    a = Image.new("RGBA", (7, 5), (0, 0, 0, 0))
    for y, s in enumerate(["5555555", ".5rrr5.", "..5r5..", "...5...", "......."]):
        for x, c in enumerate(s):
            if c != ".":
                a.putpixel((x, y), rgba(c))
    save("next", a)


def main():
    save("base", base_image())
    for k in ("normal", "raised", "happy", "soft"):
        save("brows_" + k, layer(BROWS_REGION, brows(k)))
    for k in ("open", "happy", "blink", "aside", "wink"):
        save("eyes_" + k, layer(EYES_REGION, eyes(k)))
    for k in ("grin", "smile", "soft", "talk", "oh"):
        save("mouth_" + k, layer(MOUTH_REGION, mouth(k)))
    for k in ("blush", "heart", "sparkle"):
        save("extra_" + k, extra(k))
    ui()
    # превью всех эмоций (PORTRAIT_PREVIEW=путь.png)
    sheet = Image.new("RGBA", (W * len(EMOTIONS) + 4 * len(EMOTIONS), H + 4), rgba("c"))
    for i, (name, (b, e, m, ex)) in enumerate(EMOTIONS.items()):
        im = base_image()
        for part in (Image.open(os.path.join(OUT, f"brows_{b}.png")), Image.open(os.path.join(OUT, f"eyes_{e}.png")),
                     Image.open(os.path.join(OUT, f"mouth_{m}.png"))):
            im.alpha_composite(part)
        for x in ex:
            im.alpha_composite(Image.open(os.path.join(OUT, f"extra_{x}.png")))
        sheet.alpha_composite(im, (2 + i * (W + 4), 2))
    preview = os.environ.get("PORTRAIT_PREVIEW")
    if preview:
        sheet.save(preview)
    print("ok")


if __name__ == "__main__":
    main()
