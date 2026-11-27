# Сгенерировано tools/gen_art.py — не редактировать вручную.
# Мировые координаты: x — вдоль правой стены, y — вдоль левой, z — вверх.
# Экран = ORIGIN + (x - y, (x + y) / 2 - z).
extends RefCounted

const ORIGIN := Vector2(230, 108)
const ROOM := Vector3(150, 130, 85)

const ITEMS := {
	"plates": {"anchor": Vector2(12, 12), "foot": Rect2(-5.25, -5.25, 10.5, 10.5), "h": 4.8},
	"bowl": {"anchor": Vector2(11, 13), "foot": Rect2(-4.8, -4.8, 9.6, 9.6), "h": 6.3},
	"mug_yellow": {"anchor": Vector2(9, 13), "foot": Rect2(-2.25, -2.25, 4.5, 4.5), "h": 8.25},
	"mug_blue": {"anchor": Vector2(9, 13), "foot": Rect2(-2.25, -2.25, 4.5, 4.5), "h": 8.25},
	"glass": {"anchor": Vector2(6, 11), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 7.5},
	"pot": {"anchor": Vector2(13, 15), "foot": Rect2(-5.25, -5.25, 10.5, 10.5), "h": 9.9},
	"pan": {"anchor": Vector2(12, 9), "foot": Rect2(-5.25, -5.25, 10.5, 10.5), "h": 2.4},
	"kettle": {"anchor": Vector2(12, 17), "foot": Rect2(-3.9, -3.9, 7.8, 7.8), "h": 12.45},
	"cutting_board": {"anchor": Vector2(15, 10), "foot": Rect2(-6, -3.75, 15.75, 7.5), "h": 1.95},
	"knife_block": {"anchor": Vector2(9, 17), "foot": Rect2(-1.5, -2.4, 3, 4.8), "h": 12.9},
	"soap": {"anchor": Vector2(6, 12), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.9},
	"plant": {"anchor": Vector2(8, 17), "foot": Rect2(-3, -3, 6, 6), "h": 14.85},
	"milk": {"anchor": Vector2(7, 15), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 11.4},
	"cheese": {"anchor": Vector2(8, 9), "foot": Rect2(-2.4, -1.5, 4.8, 3), "h": 3.9},
	"spices": {"anchor": Vector2(6, 10), "foot": Rect2(-1.5, -1.88, 3, 3.75), "h": 5.85},
	"toothbrush_cup": {"anchor": Vector2(5, 13), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.9},
	"toothpaste": {"anchor": Vector2(8, 7), "foot": Rect2(-3, -1.5, 7.2, 3), "h": 2.1},
	"soap_dish": {"anchor": Vector2(8, 7), "foot": Rect2(-2.1, -1.5, 4.2, 3), "h": 2.85},
	"shampoo": {"anchor": Vector2(5, 13), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.9},
	"shower_gel": {"anchor": Vector2(5, 12), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.45},
	"duck": {"anchor": Vector2(7, 9), "foot": Rect2(-1.5, -1.5, 3, 3.9), "h": 6.9},
	"sponge": {"anchor": Vector2(7, 7), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 3.15},
	"towel_blue": {"anchor": Vector2(11, 10), "foot": Rect2(-3.75, -2.25, 7.5, 4.5), "h": 3.6},
	"towel_white": {"anchor": Vector2(11, 10), "foot": Rect2(-3.75, -2.25, 7.5, 4.5), "h": 3.6},
	"toilet_paper": {"anchor": Vector2(6, 8), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 4.5},
	"perfume": {"anchor": Vector2(4, 8), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 6},
	"cream": {"anchor": Vector2(5, 7), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 3.45},
	"cactus": {"anchor": Vector2(6, 12), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 10.05},
	"hairbrush": {"anchor": Vector2(8, 6), "foot": Rect2(-3.75, -1.5, 5.25, 3), "h": 2.25},
	"bunny": {"anchor": Vector2(6, 15), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 12},
	"lamp": {"anchor": Vector2(7, 17), "foot": Rect2(-2.1, -2.1, 4.2, 4.2), "h": 12},
	"alarm_clock": {"anchor": Vector2(6, 10), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 6.45},
	"book_red": {"anchor": Vector2(8, 7), "foot": Rect2(-2.25, -1.5, 4.5, 3), "h": 1.8},
	"book_blue": {"anchor": Vector2(8, 8), "foot": Rect2(-2.25, -1.5, 5.1, 3), "h": 3.3},
	"laptop": {"anchor": Vector2(11, 14), "foot": Rect2(-3.75, -2.25, 7.5, 4.5), "h": 7.5},
	"pencil_cup": {"anchor": Vector2(5, 10), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 7.5},
	"sweater": {"anchor": Vector2(10, 9), "foot": Rect2(-3, -2.25, 6, 4.5), "h": 2.7},
	"jeans": {"anchor": Vector2(10, 8), "foot": Rect2(-3, -2.25, 6, 4.5), "h": 2.1},
	"tshirt": {"anchor": Vector2(10, 8), "foot": Rect2(-3, -2.25, 6, 4.5), "h": 1.5},
	"sneakers": {"anchor": Vector2(10, 10), "foot": Rect2(-3, -1.8, 5.25, 3.6), "h": 3.9},
	"photo_frame": {"anchor": Vector2(5, 8), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 4.8},
	"globe": {"anchor": Vector2(6, 11), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 8.4},
	"headphones": {"anchor": Vector2(7, 10), "foot": Rect2(-1.5, -3.3, 3, 6.6), "h": 6.3},
}

const BOX := {
	"anchor_closed": Vector2(22, 27),
	"anchor_open": Vector2(28, 35),
	"foot": Rect2(-11, -9, 22, 18),
	"h": 15,
}

# комнаты: фон, двери (левый верхний угол спрайта, глубина для сортировки),
# поверхности (прямоугольник x0..x1, y0..y1 на высоте z)
const ROOMS := {
	"kitchen": {
		"bg": "res://assets/sprites/kitchen_bg.png",
		"doors": {
			"fridge": {"closed": "res://assets/sprites/kitchen_fridge_closed.png", "open": "res://assets/sprites/kitchen_fridge_open.png", "closed_pos": Vector2(310, 98), "open_pos": Vector2(279, 98), "closed_depth": 173, "open_depth": 171},
		},
		"zones": [
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
		],
	},
	"bathroom": {
		"bg": "res://assets/sprites/bathroom_bg.png",
		"doors": {
			"mirror": {"closed": "res://assets/sprites/bathroom_mirror_closed.png", "open": "res://assets/sprites/bathroom_mirror_open.png", "closed_pos": Vector2(241, 48), "open_pos": Vector2(204, 48), "closed_depth": 67.5, "open_depth": 67.5},
		},
		"zones": [
			{"id": "bath", "tag": "bath", "x0": 3, "y0": 69, "x1": 27, "y1": 125, "z": 4, "max_h": 30},
			{"id": "sink", "tag": "sink", "x0": 17, "y0": 0, "x1": 63, "y1": 26, "z": 33, "max_h": 14},
			{"id": "mirror_0", "tag": "mirror", "x0": 24, "y0": 1, "x1": 56, "y1": 7.5, "z": 50, "max_h": 9.5, "container": "mirror"},
			{"id": "mirror_1", "tag": "mirror", "x0": 24, "y0": 1, "x1": 56, "y1": 7.5, "z": 61.5, "max_h": 10, "container": "mirror"},
			{"id": "tank", "tag": "toilet", "x0": 72, "y0": 0, "x1": 90, "y1": 7, "z": 36, "max_h": 30},
			{"id": "shelf_0", "tag": "shelf", "x0": 106, "y0": 1, "x1": 142, "y1": 18, "z": 3, "max_h": 19},
			{"id": "shelf_1", "tag": "shelf", "x0": 106, "y0": 1, "x1": 142, "y1": 18, "z": 24, "max_h": 19},
			{"id": "shelf_2", "tag": "shelf", "x0": 106, "y0": 1, "x1": 142, "y1": 18, "z": 45, "max_h": 17},
			{"id": "shelf_top", "tag": "shelf", "x0": 104, "y0": 0, "x1": 144, "y1": 18, "z": 64, "max_h": 20},
		],
	},
	"bedroom": {
		"bg": "res://assets/sprites/bedroom_bg.png",
		"doors": {
			"wardrobe": {"closed": "res://assets/sprites/bedroom_wardrobe_closed.png", "open": "res://assets/sprites/bedroom_wardrobe_open.png", "closed_pos": Vector2(261, 69), "open_pos": Vector2(218, 68), "closed_depth": 124, "open_depth": 124},
		},
		"zones": [
			{"id": "bed", "tag": "bed", "x0": 18, "y0": 37, "x1": 46, "y1": 97, "z": 21, "max_h": 40},
			{"id": "nightstand", "tag": "nightstand", "x0": 0, "y0": 104, "x1": 18, "y1": 122, "z": 22, "max_h": 40},
			{"id": "wardrobe_0", "tag": "wardrobe", "x0": 60, "y0": 1, "x1": 96, "y1": 23, "container": "wardrobe", "z": 4, "max_h": 24},
			{"id": "wardrobe_1", "tag": "wardrobe", "x0": 60, "y0": 1, "x1": 96, "y1": 23, "container": "wardrobe", "z": 30, "max_h": 22},
			{"id": "wardrobe_2", "tag": "wardrobe", "x0": 60, "y0": 1, "x1": 96, "y1": 23, "container": "wardrobe", "z": 54, "max_h": 22},
			{"id": "desk", "tag": "desk", "x0": 106, "y0": 0, "x1": 146, "y1": 26, "z": 31, "max_h": 25},
			{"id": "shelf", "tag": "shelf", "x0": 108, "y0": 0, "x1": 144, "y1": 12, "z": 59, "max_h": 24},
		],
	},
}
