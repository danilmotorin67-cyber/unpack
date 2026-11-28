# Сгенерировано tools/gen_art.py — не редактировать вручную.
# Мировые координаты: x — вдоль правой стены, y — вдоль левой, z — вверх.
# Экран = ORIGIN + PX * (x - y, (x + y) / 2 - z).
extends RefCounted

const ORIGIN := Vector2(306, 143)
const PX := 1.3333333333333333  # пикселей на единицу мира
const ROOM := Vector3(150, 130, 85)

const ITEMS := {
	"plates": {"anchor": Vector2(12, 12), "foot": Rect2(-5.25, -5.25, 10.5, 10.5), "h": 4.8},
	"bowl": {"anchor": Vector2(14, 16), "foot": Rect2(-4.8, -4.8, 9.6, 9.6), "h": 6.3},
	"mug_yellow": {"anchor": Vector2(11, 14), "foot": Rect2(-2.25, -2.25, 4.5, 4.5), "h": 8.25},
	"mug_blue": {"anchor": Vector2(11, 14), "foot": Rect2(-2.25, -2.25, 4.5, 4.5), "h": 8.25},
	"glass": {"anchor": Vector2(7, 15), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 7.5},
	"pot": {"anchor": Vector2(13, 15), "foot": Rect2(-5.25, -5.25, 10.5, 10.5), "h": 9.9},
	"pan": {"anchor": Vector2(15, 12), "foot": Rect2(-5.25, -5.25, 10.5, 10.5), "h": 2.4},
	"kettle": {"anchor": Vector2(15, 22), "foot": Rect2(-3.9, -3.9, 7.8, 7.8), "h": 12.45},
	"cutting_board": {"anchor": Vector2(19, 13), "foot": Rect2(-6, -3.75, 15.75, 7.5), "h": 1.95},
	"knife_block": {"anchor": Vector2(11, 22), "foot": Rect2(-1.5, -2.4, 3, 4.8), "h": 12.9},
	"soap": {"anchor": Vector2(7, 16), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.9},
	"plant": {"anchor": Vector2(10, 17), "foot": Rect2(-3, -3, 6, 6), "h": 14.85},
	"milk": {"anchor": Vector2(8, 19), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 11.4},
	"cheese": {"anchor": Vector2(10, 11), "foot": Rect2(-2.4, -1.5, 4.8, 3), "h": 3.9},
	"spices": {"anchor": Vector2(7, 12), "foot": Rect2(-1.5, -1.88, 3, 3.75), "h": 5.85},
	"toothbrush_cup": {"anchor": Vector2(7, 16), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.9},
	"toothpaste": {"anchor": Vector2(10, 9), "foot": Rect2(-3, -1.5, 7.2, 3), "h": 2.1},
	"soap_dish": {"anchor": Vector2(10, 8), "foot": Rect2(-2.1, -1.5, 4.2, 3), "h": 2.85},
	"shampoo": {"anchor": Vector2(7, 16), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.9},
	"shower_gel": {"anchor": Vector2(6, 16), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 9.45},
	"duck": {"anchor": Vector2(8, 11), "foot": Rect2(-1.5, -1.5, 3, 3.9), "h": 6.9},
	"sponge": {"anchor": Vector2(9, 9), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 3.15},
	"towel_blue": {"anchor": Vector2(14, 13), "foot": Rect2(-3.75, -2.25, 7.5, 4.5), "h": 3.6},
	"towel_white": {"anchor": Vector2(14, 13), "foot": Rect2(-3.75, -2.25, 7.5, 4.5), "h": 3.6},
	"toilet_paper": {"anchor": Vector2(7, 10), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 4.5},
	"perfume": {"anchor": Vector2(5, 11), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 6},
	"cream": {"anchor": Vector2(6, 9), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 3.45},
	"cactus": {"anchor": Vector2(7, 16), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 10.05},
	"hairbrush": {"anchor": Vector2(10, 8), "foot": Rect2(-3.75, -1.5, 5.25, 3), "h": 2.25},
	"bunny": {"anchor": Vector2(8, 19), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 12},
	"lamp": {"anchor": Vector2(9, 21), "foot": Rect2(-2.1, -2.1, 4.2, 4.2), "h": 12},
	"alarm_clock": {"anchor": Vector2(8, 12), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 6.45},
	"book_red": {"anchor": Vector2(11, 9), "foot": Rect2(-2.25, -1.5, 4.5, 3), "h": 1.8},
	"book_blue": {"anchor": Vector2(11, 10), "foot": Rect2(-2.25, -1.5, 5.1, 3), "h": 3.3},
	"laptop": {"anchor": Vector2(14, 18), "foot": Rect2(-3.75, -2.25, 7.5, 4.5), "h": 7.5},
	"pencil_cup": {"anchor": Vector2(5, 13), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 7.5},
	"sweater": {"anchor": Vector2(13, 11), "foot": Rect2(-3, -2.25, 6, 4.5), "h": 2.7},
	"jeans": {"anchor": Vector2(13, 10), "foot": Rect2(-3, -2.25, 6, 4.5), "h": 2.1},
	"tshirt": {"anchor": Vector2(13, 9), "foot": Rect2(-3, -2.25, 6, 4.5), "h": 1.5},
	"sneakers": {"anchor": Vector2(12, 12), "foot": Rect2(-3, -1.8, 5.25, 3.6), "h": 3.9},
	"photo_frame": {"anchor": Vector2(6, 10), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 4.8},
	"globe": {"anchor": Vector2(8, 14), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 8.4},
	"headphones": {"anchor": Vector2(9, 13), "foot": Rect2(-1.5, -3.3, 3, 6.6), "h": 6.3},
	"cushion_terra": {"anchor": Vector2(14, 12), "foot": Rect2(-3, -3, 6, 6), "h": 3.3},
	"cushion_blue": {"anchor": Vector2(14, 12), "foot": Rect2(-3, -3, 6, 6), "h": 3.3},
	"throw_blanket": {"anchor": Vector2(15, 12), "foot": Rect2(-4.5, -2.25, 9, 4.5), "h": 2.7},
	"teapot": {"anchor": Vector2(11, 14), "foot": Rect2(-1.95, -3.9, 3.9, 8.25), "h": 8.25},
	"remote": {"anchor": Vector2(8, 6), "foot": Rect2(-1.8, -1.5, 3.6, 3), "h": 0.9},
	"vase": {"anchor": Vector2(6, 19), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 12.15},
	"books_row": {"anchor": Vector2(12, 17), "foot": Rect2(-3.3, -1.5, 5.7, 3), "h": 8.4},
	"vinyl_stack": {"anchor": Vector2(13, 11), "foot": Rect2(-2.7, -2.7, 5.4, 5.4), "h": 2.4},
	"board_game": {"anchor": Vector2(14, 11), "foot": Rect2(-3.75, -2.25, 7.5, 4.5), "h": 2.4},
	"candles": {"anchor": Vector2(5, 11), "foot": Rect2(-1.5, -1.5, 3, 3), "h": 6.3},
	"painting_landscape": {"wall": true, "anchor_l": Vector2(14, 17), "anchor_r": Vector2(16, 17), "foot": Rect2(-9, -6.75, 18, 13.5), "h": 0},
	"painting_flowers": {"wall": true, "anchor_l": Vector2(9, 15), "anchor_r": Vector2(11, 15), "foot": Rect2(-5.25, -7.5, 10.5, 15), "h": 0},
	"wall_clock": {"wall": true, "anchor_l": Vector2(10, 11), "anchor_r": Vector2(11, 11), "foot": Rect2(-5.7, -5.7, 11.4, 11.4), "h": 0},
	"mirror_round": {"wall": true, "anchor_l": Vector2(10, 12), "anchor_r": Vector2(12, 12), "foot": Rect2(-6.3, -6.3, 12.6, 12.6), "h": 0},
	"poster": {"wall": true, "anchor_l": Vector2(11, 18), "anchor_r": Vector2(12, 18), "foot": Rect2(-6.75, -9, 13.5, 18), "h": 0},
	"painting_small": {"wall": true, "anchor_l": Vector2(8, 12), "anchor_r": Vector2(9, 12), "foot": Rect2(-4.5, -5.25, 9, 10.5), "h": 0},
}

const BOX := {
	"anchor_closed": Vector2(29, 35),
	"anchor_open": Vector2(37, 46),
	"foot": Rect2(-11, -9, 22, 18),
	"h": 15,
}

# комнаты: фон, двери (левый верхний угол спрайта, глубина для сортировки),
# поверхности: горизонтальные — прямоугольник x0..x1, y0..y1 на высоте z;
# на стенах (wall = L: плоскость x=0, R: y=0) — u0..u1 вдоль стены, z0..z1 по высоте
const ROOMS := {
	"kitchen": {
		"bg": "res://assets/sprites/kitchen_bg.png",
		"doors": {
			"fridge": {"closed": "res://assets/sprites/kitchen_fridge_closed.png", "open": "res://assets/sprites/kitchen_fridge_open.png", "closed_pos": Vector2(413, 130), "open_pos": Vector2(372, 130), "closed_depth": 173, "open_depth": 171},
		},
		"zones": [
			{"id": "wall_l", "tag": "wall", "wall": "L", "u0": -40, "u1": -6, "z0": 50, "z1": 82},
			{"id": "wall_r", "tag": "wall", "wall": "R", "u0": 2, "u1": 24, "z0": 63, "z1": 82},
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
			"mirror": {"closed": "res://assets/sprites/bathroom_mirror_closed.png", "open": "res://assets/sprites/bathroom_mirror_open.png", "closed_pos": Vector2(322, 63), "open_pos": Vector2(272, 63), "closed_depth": 67.5, "open_depth": 67.5},
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
			"wardrobe": {"closed": "res://assets/sprites/bedroom_wardrobe_closed.png", "open": "res://assets/sprites/bedroom_wardrobe_open.png", "closed_pos": Vector2(348, 91), "open_pos": Vector2(291, 90), "closed_depth": 124, "open_depth": 124},
		},
		"zones": [
			{"id": "wall_r", "tag": "wall", "wall": "R", "u0": 4, "u1": 55, "z0": 36, "z1": 82},
			{"id": "wall_l", "tag": "wall", "wall": "L", "u0": -128, "u1": -96, "z0": 34, "z1": 82},
			{"id": "bed", "tag": "bed", "x0": 18, "y0": 37, "x1": 46, "y1": 97, "z": 21, "max_h": 40},
			{"id": "nightstand", "tag": "nightstand", "x0": 0, "y0": 104, "x1": 18, "y1": 122, "z": 22, "max_h": 40},
			{"id": "wardrobe_0", "tag": "wardrobe", "x0": 60, "y0": 1, "x1": 96, "y1": 23, "container": "wardrobe", "z": 4, "max_h": 24},
			{"id": "wardrobe_1", "tag": "wardrobe", "x0": 60, "y0": 1, "x1": 96, "y1": 23, "container": "wardrobe", "z": 30, "max_h": 22},
			{"id": "wardrobe_2", "tag": "wardrobe", "x0": 60, "y0": 1, "x1": 96, "y1": 23, "container": "wardrobe", "z": 54, "max_h": 22},
			{"id": "desk", "tag": "desk", "x0": 106, "y0": 0, "x1": 146, "y1": 26, "z": 31, "max_h": 25},
			{"id": "shelf", "tag": "shelf", "x0": 108, "y0": 0, "x1": 144, "y1": 12, "z": 59, "max_h": 24},
		],
	},
	"living": {
		"bg": "res://assets/sprites/living_bg.png",
		"doors": {
			"sideboard": {"closed": "res://assets/sprites/living_sideboard_closed.png", "open": "res://assets/sprites/living_sideboard_open.png", "closed_pos": Vector2(158, 183), "open_pos": Vector2(195, 183), "closed_depth": 147.5, "open_depth": 145.5},
		},
		"zones": [
			{"id": "wall_l1", "tag": "wall", "wall": "L", "u0": -58, "u1": -20, "z0": 44, "z1": 82},
			{"id": "wall_l2", "tag": "wall", "wall": "L", "u0": -128, "u1": -102, "z0": 36, "z1": 82},
			{"id": "wall_r", "tag": "wall", "wall": "R", "u0": 30, "u1": 88, "z0": 34, "z1": 82},
			{"id": "sofa", "tag": "sofa", "x0": 36, "y0": 6, "x1": 84, "y1": 24, "z": 16, "max_h": 30},
			{"id": "table", "tag": "table", "x0": 50, "y0": 44, "x1": 84, "y1": 70, "z": 14, "max_h": 40},
			{"id": "tvstand", "tag": "tvstand", "x0": 5, "y0": 20, "x1": 18, "y1": 56, "z": 18, "max_h": 30},
			{"id": "sideboard_top", "tag": "cabinet_top", "x0": 0, "y0": 102, "x1": 18, "y1": 128, "z": 30, "max_h": 40},
			{"id": "sideboard_0", "tag": "sideboard", "x0": 1, "y0": 104, "x1": 17, "y1": 126, "container": "sideboard", "z": 2, "max_h": 12},
			{"id": "sideboard_1", "tag": "sideboard", "x0": 1, "y0": 104, "x1": 17, "y1": 126, "container": "sideboard", "z": 15.5, "max_h": 12},
			{"id": "bookshelf_0", "tag": "bookshelf", "x0": 102, "y0": 1, "x1": 138, "y1": 16, "z": 3, "max_h": 20},
			{"id": "bookshelf_1", "tag": "bookshelf", "x0": 102, "y0": 1, "x1": 138, "y1": 16, "z": 26, "max_h": 20},
			{"id": "bookshelf_2", "tag": "bookshelf", "x0": 102, "y0": 1, "x1": 138, "y1": 16, "z": 49, "max_h": 18},
			{"id": "bookshelf_top", "tag": "bookshelf", "x0": 100, "y0": 0, "x1": 140, "y1": 16, "z": 70, "max_h": 14},
		],
	},
}
