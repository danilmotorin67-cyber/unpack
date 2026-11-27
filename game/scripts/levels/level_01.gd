# Уровень 1 — кухня.
# Геометрия комнаты, поверхности и дверцы генерируются вместе с артом
# (tools/room_kitchen.py -> scripts/art_data.gd). Здесь — правила и коробки.
#   allowed — на какие типы мест (tag зоны) предмет ставить правильно
#   snd     — материал: звук, когда предмет ставят
extends RefCounted

const DATA := {
	"room": "kitchen",
	"title": "КУХНЯ",
	"done_text": "КУХНЯ ГОТОВА!",
	"items": {
		"plates": {"allowed": ["shelf"], "snd": "ceramic"},
		"bowl": {"allowed": ["shelf"], "snd": "ceramic"},
		"mug_yellow": {"allowed": ["shelf"], "snd": "ceramic"},
		"mug_blue": {"allowed": ["shelf"], "snd": "ceramic"},
		"glass": {"allowed": ["shelf"], "snd": "glass"},
		"spices": {"allowed": ["shelf", "counter"], "snd": "glass"},
		"pot": {"allowed": ["stove"], "snd": "metal"},
		"pan": {"allowed": ["stove"], "snd": "metal"},
		"kettle": {"allowed": ["stove", "counter"], "snd": "metal"},
		"cutting_board": {"allowed": ["counter"], "snd": "wood"},
		"knife_block": {"allowed": ["counter"], "snd": "wood"},
		"soap": {"allowed": ["counter", "sill"], "snd": "plastic"},
		"plant": {"allowed": ["sill", "counter"], "snd": "plant"},
		"milk": {"allowed": ["fridge"], "snd": "paper"},
		"cheese": {"allowed": ["fridge"], "snd": "soft"},
	},
	# x, y — мировые координаты центра коробки на полу
	"boxes": [
		{"x": 62, "y": 64, "items": ["plates", "bowl", "mug_yellow", "mug_blue", "glass"]},
		{"x": 92, "y": 102, "items": ["pot", "pan", "kettle", "cutting_board", "knife_block"]},
		{"x": 126, "y": 78, "items": ["soap", "plant", "milk", "cheese", "spices"]},
	],
}
