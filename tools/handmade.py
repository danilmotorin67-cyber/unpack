"""Предметы, нарисованные вручную попиксельно.

Каждый спрайт — текстовая карта: один символ = один пиксель, '.' — прозрачный,
остальные символы — ключи палитры (tools/palette.py). Шаблоны с буквами
A/B/C/D перекрашиваются через RAMPS (A — светлый, B — средний, C — тёмный,
D — самый тёмный тон материала).

anchor — пиксель, который стоит на поверхности (центр «дна» предмета).
Если предмет есть здесь, gen_art.py берёт эту картинку вместо рендера.
"""

RAMPS = {
    "ochre": {"A": "y", "B": "Y", "C": "n", "D": "u"},
    "blue": {"A": "l", "B": "L", "C": "z", "D": "Z"},
}

MUG = [
    ".......oooooo....",
    ".....ooAAAAAAoo..",
    "....oAuuuuuuuuAo.",
    "....oBuuvvvvuuBo.",
    "....oBAuuuuuuABo.",
    "....oAAAAAAAABBo.",
    "....oAWBBBBBBBCo.",
    ".ooooAABBBBBBCCo.",
    "oABooAABBBBBBCCo.",
    "oB.ooAABBBBBBCCo.",
    "oB.ooAABBBBBBCCo.",
    "oCCooAABBBBBBCCo.",
    ".ooooAABBBBBBCCo.",
    "....oCBBBBBBBCDo.",
    ".....oCCCCCCCDo..",
    ".......oooooo....",
]

PLATES = [
    "........ooooooo........",
    ".....oooWWWWWWWooo.....",
    "...ooWWWWWWWWWWWWWoo...",
    "..oWWWWccccccccWWWWWo..",
    ".oWWWccCCCCCCCCccWWWWo.",
    ".oWWWcCCCCCCCCCCcWWWCo.",
    ".oWWWWccccccccccWWWCCo.",
    "..oWWWWWWWWWWWWWWWCCo..",
    ".okkCCCCCCCCCCCCCCCkkm.",
    ".oWWWWWWWWWWWWWWWWCCCm.",
    ".mkkCCCCCCCCCCCCCCkkKm.",
    "..oWWWWWWWWWWWWWWCCCm..",
    "..mkkCCCCCCCCCCCCkkKm..",
    "....mmkkkkkkkkkkkKmm...",
    "......mmmmmmmmmmm......",
]

PLANT = [
    "........oo........",
    "...oo..oao..oo....",
    "..oaeo.oaeo.oaeo..",
    "..oaeEooaeEooeEo..",
    ".ooaeEoaeeEoaeEoo.",
    "oaeeaEoaeEEoaeeeEo",
    "oaeeEEEoaEoEeeEEEo",
    ".oaeeEEEoEEEeEEEo.",
    "..ooEEEEEEEEEEoo..",
    "...oooooooooooo...",
    "..oiiiiiiiiiiiRo..",
    "..oRrrrrrrrrrRRo..",
    "...oirrrrrrrrRo...",
    "...oirrrrrrrrRo...",
    "...oirrrrrrrRRo...",
    "....oirrrrrrRo....",
    "....oRRRRRRRRo....",
    ".....oooooooo.....",
]

POT = [
    "..........oooo..........",
    ".........omddmo.........",
    ".......oooommooooo......",
    ".....oosssssssssSSoo....",
    "...oosWWssssssssSSSSoo..",
    "..osssssssssssSSSSSSxxo.",
    "..oSsssssssssSSSSSSxxxo.",
    "...oSSssssSSSSSSSxxxxo..",
    "....ooxxxxxxxxxxxxoo....",
    "...osssSSSSSSSSSxxxxo...",
    "oooosWsSSSSSSSSSxxxxoooo",
    "oddossssSSSSSSSSxxxxoddo",
    "oooossssSSSSSSSSxxxxoooo",
    "...osssSSSSSSSSSxxxxo...",
    "...ossSSSSSSSSSxxxxxo...",
    "....oxSSSSSSSSxxxxxo....",
    "......oooooooooooo......",
]


def _recolor(rows, ramp):
    m = RAMPS[ramp]
    return ["".join(m.get(ch, ch) for ch in r) for r in rows]


HANDMADE = {
    "mug_yellow": (_recolor(MUG, "ochre"), (10, 13)),
    "mug_blue": (_recolor(MUG, "blue"), (10, 13)),
    "plates": (PLATES, (11, 11)),
    "plant": (PLANT, (9, 16)),
    "pot": (POT, (12, 14)),
}
