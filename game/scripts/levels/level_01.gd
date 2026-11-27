# Уровень 1 — кухня.
# Геометрия комнаты и поверхности (зоны) генерируются вместе с артом:
# см. tools/gen_art.py и scripts/art_data.gd. Здесь — правила и содержимое коробок.
extends RefCounted

const DATA := {
	"title": "КУХНЯ",
	"done_text": "КУХНЯ ГОТОВА!",
	"background": "res://assets/sprites/kitchen_bg.png",

	"containers": [
		{
			"id": "fridge",
			"closed": "res://assets/sprites/fridge_closed.png",
			"open": "res://assets/sprites/fridge_open.png",
		},
	],

	# allowed — на какие типы мест (tag зоны) предмет ставить правильно
	"items": {
		"plates": {"allowed": ["shelf"]},
		"bowl": {"allowed": ["shelf"]},
		"mug_yellow": {"allowed": ["shelf"]},
		"mug_blue": {"allowed": ["shelf"]},
		"glass": {"allowed": ["shelf"]},
		"spices": {"allowed": ["shelf", "counter"]},
		"pot": {"allowed": ["stove"]},
		"pan": {"allowed": ["stove"]},
		"kettle": {"allowed": ["stove", "counter"]},
		"cutting_board": {"allowed": ["counter"]},
		"knife_block": {"allowed": ["counter"]},
		"soap": {"allowed": ["counter", "sill"]},
		"plant": {"allowed": ["sill", "counter"]},
		"milk": {"allowed": ["fridge"]},
		"cheese": {"allowed": ["fridge"]},
	},

	# x, y — мировые координаты центра коробки на полу
	"boxes": [
		{"x": 62, "y": 64, "items": ["plates", "bowl", "mug_yellow", "mug_blue", "glass"]},
		{"x": 92, "y": 102, "items": ["pot", "pan", "kettle", "cutting_board", "knife_block"]},
		{"x": 126, "y": 78, "items": ["soap", "plant", "milk", "cheese", "spices"]},
	],
}
