# Уровень 1 — кухня.
# Все координаты в пикселях вьюпорта 320×180.
# Зона (zone) — поверхность, на которую ставят вещи: x0..x1 — ширина,
# y — верхняя кромка поверхности (низ предмета встаёт на неё),
# max_h — сколько места над поверхностью, tag — тип места.
extends RefCounted

const DATA := {
	"title": "КУХНЯ",
	"done_text": "КУХНЯ ГОТОВА!",
	"background": "res://assets/sprites/kitchen_bg.png",

	"zones": [
		{"id": "sill", "tag": "sill", "x0": 26, "x1": 78, "y": 61, "max_h": 40},
		{"id": "cab_top", "tag": "cabinet", "x0": 100, "x1": 173, "y": 37, "max_h": 19},
		{"id": "cab_bottom", "tag": "cabinet", "x0": 100, "x1": 173, "y": 59, "max_h": 18},
		{"id": "wall_shelf", "tag": "shelf", "x0": 178, "x1": 214, "y": 50, "max_h": 30},
		{"id": "counter_l", "tag": "counter", "x0": 15, "x1": 119, "y": 92, "max_h": 26},
		{"id": "stove", "tag": "stove", "x0": 121, "x1": 159, "y": 90, "max_h": 26},
		{"id": "counter_r", "tag": "counter", "x0": 161, "x1": 215, "y": 92, "max_h": 38},
		{"id": "fridge_top", "tag": "fridge_top", "x0": 227, "x1": 265, "y": 28, "max_h": 28},
		{"id": "fridge_1", "tag": "fridge", "x0": 230, "x1": 262, "y": 62, "max_h": 29, "container": "fridge"},
		{"id": "fridge_2", "tag": "fridge", "x0": 230, "x1": 262, "y": 96, "max_h": 32, "container": "fridge"},
		{"id": "fridge_3", "tag": "fridge", "x0": 230, "x1": 262, "y": 125, "max_h": 27, "container": "fridge"},
	],

	"containers": [
		{
			"id": "fridge",
			"closed": "res://assets/sprites/fridge_closed.png",
			"open": "res://assets/sprites/fridge_open.png",
			# левый верхний угол спрайта (с учётом прозрачной рамки 1px)
			"closed_pos": Vector2(225, 27),
			"open_pos": Vector2(266, 27),
		},
	],

	# allowed — на какие типы мест предмет можно поставить «правильно»
	"items": {
		"plates": {"allowed": ["cabinet"]},
		"bowl": {"allowed": ["cabinet"]},
		"mug_red": {"allowed": ["cabinet", "shelf"]},
		"mug_blue": {"allowed": ["cabinet", "shelf"]},
		"glass": {"allowed": ["cabinet", "shelf"]},
		"spices": {"allowed": ["shelf", "cabinet", "counter"]},
		"pot": {"allowed": ["stove"]},
		"pan": {"allowed": ["stove"]},
		"kettle": {"allowed": ["stove", "counter"]},
		"cutting_board": {"allowed": ["counter"]},
		"knife_block": {"allowed": ["counter"]},
		"soap": {"allowed": ["counter", "sill"]},
		"plant": {"allowed": ["sill", "shelf", "counter"]},
		"milk": {"allowed": ["fridge"]},
		"cheese": {"allowed": ["fridge"]},
	},

	# x — центр коробки, низ коробки стоит на y
	"boxes": [
		{"x": 70, "y": 172, "items": ["plates", "bowl", "mug_red", "mug_blue", "glass"]},
		{"x": 160, "y": 174, "items": ["pot", "pan", "kettle", "cutting_board", "knife_block"]},
		{"x": 250, "y": 171, "items": ["soap", "plant", "milk", "cheese", "spices"]},
	],
}
