# Сгенерировано tools/gen_art.py — не редактировать вручную.
# Мировые координаты: x — вдоль правой стены, y — вдоль левой, z — вверх.
# Экран = ORIGIN + (x - y, (x + y) / 2 - z).
extends RefCounted

const ORIGIN := Vector2(230, 108)
const ROOM := Vector3(150, 130, 85)

const ITEMS := {
	"plates": {"anchor": Vector2(12, 12), "foot": Rect2(-5.25, -5.25, 10.5, 10.5), "h": 4.8},
	"bowl": {"anchor": Vector2(11, 13), "foot": Rect2(-4.8, -4.8, 9.6, 9.6), "h": 6.3},
	"mug_yellow": {"anchor": Vector2(9, 13), "foot": Rect2(-2.25, -2.25, 4.5, 6.6), "h": 8.25},
	"mug_blue": {"anchor": Vector2(9, 13), "foot": Rect2(-2.25, -2.25, 4.5, 6.6), "h": 8.25},
	"glass": {"anchor": Vector2(6, 11), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 7.5},
	"pot": {"anchor": Vector2(13, 15), "foot": Rect2(-5.55, -5.55, 13.35, 13.35), "h": 9.9},
	"pan": {"anchor": Vector2(12, 9), "foot": Rect2(-5.25, -5.25, 20.25, 10.5), "h": 2.4},
	"kettle": {"anchor": Vector2(12, 17), "foot": Rect2(-3.9, -3.9, 7.8, 11.4), "h": 12.45},
	"cutting_board": {"anchor": Vector2(15, 10), "foot": Rect2(-6, -3.75, 15.75, 7.5), "h": 1.95},
	"knife_block": {"anchor": Vector2(9, 17), "foot": Rect2(-1.5, -2.4, 3, 4.8), "h": 12.9},
	"soap": {"anchor": Vector2(6, 12), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.9},
	"plant": {"anchor": Vector2(8, 17), "foot": Rect2(-3, -3, 6, 6), "h": 14.85},
	"milk": {"anchor": Vector2(7, 15), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 11.4},
	"cheese": {"anchor": Vector2(8, 9), "foot": Rect2(-2.4, -1.5, 4.8, 3), "h": 3.9},
	"spices": {"anchor": Vector2(6, 10), "foot": Rect2(-1.5, -1.88, 3, 3.75), "h": 5.85},
}

const BOX := {
	"anchor_closed": Vector2(22, 27),
	"anchor_open": Vector2(28, 35),
	"foot": Rect2(-11, -9, 22, 18),
	"h": 15,
}

# двери: левый верхний угол спрайта на экране; depth — для сортировки
const DOORS := {
	"fridge": {"closed_pos": Vector2(310, 98), "open_pos": Vector2(279, 98), "closed_depth": 173, "open_depth": 171},
}

# поверхности: прямоугольник x0..x1, y0..y1 на высоте z
const ZONES := [
	{"id": "sill", "tag": "sill", "x0": 0, "y0": 43, "x1": 9, "y1": 93, "z": 50.5, "max_h": 30},
	{"id": "shelf", "tag": "shelf", "x0": 25, "y0": 0, "x1": 100, "y1": 15, "z": 73, "max_h": 12},
	{"id": "counter_r", "tag": "counter", "x0": 0, "y0": 0, "x1": 60, "y1": 30, "z": 39, "max_h": 24},
	{"id": "stove", "tag": "stove", "x0": 60, "y0": 0, "x1": 86, "y1": 30, "z": 39, "max_h": 24},
	{"id": "counter_r2", "tag": "counter", "x0": 86, "y0": 0, "x1": 108, "y1": 30, "z": 39, "max_h": 24},
	{"id": "counter_l", "tag": "counter", "x0": 0, "y0": 30, "x1": 30, "y1": 108, "z": 39, "max_h": 30},
	{"id": "fridge_top", "tag": "fridge_top", "x0": 112, "y0": 0, "x1": 142, "y1": 28, "z": 80, "max_h": 20},
	{"id": "fridge_0", "tag": "fridge", "x0": 116, "y0": 4, "x1": 138, "y1": 26, "z": 6, "max_h": 21, "container": "fridge"},
	{"id": "fridge_1", "tag": "fridge", "x0": 116, "y0": 4, "x1": 138, "y1": 26, "z": 31, "max_h": 20, "container": "fridge"},
	{"id": "fridge_2", "tag": "fridge", "x0": 116, "y0": 4, "x1": 138, "y1": 26, "z": 55, "max_h": 20, "container": "fridge"},
]
