# Уровень 4 — гостиная. См. комментарии в level_01.gd.
# Тег "wall" — вещь вешается на стену (зоны стен описаны в tools/room_living.py).
extends RefCounted

const DATA := {
	"room": "living",
	"title": "ГОСТИНАЯ",
	"done_text": "ГОСТИНАЯ ГОТОВА!",
	"items": {
		"painting_landscape": {"allowed": ["wall"], "snd": "wood"},
		"painting_flowers": {"allowed": ["wall"], "snd": "wood"},
		"wall_clock": {"allowed": ["wall"], "snd": "plastic"},
		"mirror_round": {"allowed": ["wall"], "snd": "glass"},
		"cushion_terra": {"allowed": ["sofa"], "snd": "soft"},
		"cushion_blue": {"allowed": ["sofa"], "snd": "soft"},
		"throw_blanket": {"allowed": ["sofa"], "snd": "soft"},
		"teapot": {"allowed": ["table"], "snd": "ceramic"},
		"remote": {"allowed": ["table", "sofa", "tvstand"], "snd": "plastic"},
		"vase": {"allowed": ["table", "tvstand", "cabinet_top", "bookshelf"], "snd": "ceramic"},
		"books_row": {"allowed": ["bookshelf"], "snd": "paper"},
		"vinyl_stack": {"allowed": ["sideboard", "bookshelf"], "snd": "paper"},
		"board_game": {"allowed": ["sideboard", "bookshelf"], "snd": "paper"},
		"candles": {"allowed": ["table", "cabinet_top", "bookshelf", "tvstand"], "snd": "soft"},
		"cactus": {"allowed": ["bookshelf", "cabinet_top", "tvstand"], "snd": "plant"},
	},
	"boxes": [
		{"x": 112, "y": 50, "items": ["painting_landscape", "painting_flowers", "wall_clock", "mirror_round", "remote"]},
		{"x": 118, "y": 94, "items": ["cushion_terra", "cushion_blue", "throw_blanket", "teapot", "candles"]},
		{"x": 66, "y": 104, "items": ["books_row", "vinyl_stack", "board_game", "vase", "cactus"]},
	],
}
