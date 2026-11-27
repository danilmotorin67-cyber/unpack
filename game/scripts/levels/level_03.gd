# Уровень 3 — спальня. См. комментарии в level_01.gd.
extends RefCounted

const DATA := {
	"room": "bedroom",
	"title": "СПАЛЬНЯ",
	"done_text": "СПАЛЬНЯ ГОТОВА!",
	"items": {
		"bunny": {"allowed": ["bed"], "snd": "soft"},
		"lamp": {"allowed": ["nightstand", "desk"], "snd": "ceramic"},
		"alarm_clock": {"allowed": ["nightstand", "desk"], "snd": "metal"},
		"book_red": {"allowed": ["shelf", "nightstand", "desk"], "snd": "paper"},
		"book_blue": {"allowed": ["shelf", "nightstand", "desk"], "snd": "paper"},
		"laptop": {"allowed": ["desk"], "snd": "plastic"},
		"pencil_cup": {"allowed": ["desk"], "snd": "wood"},
		"sweater": {"allowed": ["wardrobe"], "snd": "soft"},
		"jeans": {"allowed": ["wardrobe"], "snd": "soft"},
		"tshirt": {"allowed": ["wardrobe"], "snd": "soft"},
		"sneakers": {"allowed": ["wardrobe"], "snd": "soft"},
		"photo_frame": {"allowed": ["shelf", "desk", "nightstand"], "snd": "wood"},
		"plant": {"allowed": ["shelf", "desk", "nightstand"], "snd": "plant"},
		"globe": {"allowed": ["shelf", "desk"], "snd": "plastic"},
		"headphones": {"allowed": ["desk", "nightstand"], "snd": "plastic"},
	},
	"boxes": [
		{"x": 84, "y": 66, "items": ["sweater", "jeans", "tshirt", "sneakers", "bunny"]},
		{"x": 114, "y": 98, "items": ["laptop", "pencil_cup", "headphones", "lamp", "alarm_clock"]},
		{"x": 60, "y": 118, "items": ["book_red", "book_blue", "photo_frame", "plant", "globe"]},
	],
}
