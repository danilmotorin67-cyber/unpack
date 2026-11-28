# Уровень 5 — детская. См. комментарии в level_01.gd.
extends RefCounted

const DATA := {
	"room": "kids",
	"title": "ДЕТСКАЯ",
	"done_text": "ДЕТСКАЯ ГОТОВА!",
	"items": {
		"teddy_bear": {"allowed": ["bed", "chest", "cubby"], "snd": "soft"},
		"blocks": {"allowed": ["cubby", "chest", "table"], "snd": "wood"},
		"toy_car": {"allowed": ["chest", "cubby"], "snd": "plastic"},
		"ball": {"allowed": ["chest"], "snd": "soft"},
		"crayons": {"allowed": ["table"], "snd": "paper"},
		"sketchbook": {"allowed": ["table", "cubby"], "snd": "paper"},
		"picture_books": {"allowed": ["cubby", "shelf"], "snd": "paper"},
		"night_light": {"allowed": ["shelf", "table"], "snd": "glass"},
		"piggy_bank": {"allowed": ["shelf", "cubby"], "snd": "ceramic"},
		"robot": {"allowed": ["chest", "cubby", "shelf"], "snd": "metal"},
		"ring_pyramid": {"allowed": ["chest", "cubby"], "snd": "wood"},
		"drum": {"allowed": ["chest"], "snd": "wood"},
		"toy_rocket": {"allowed": ["shelf", "cubby"], "snd": "plastic"},
		"kid_drawing": {"allowed": ["wall"], "snd": "paper"},
		"star_poster": {"allowed": ["wall"], "snd": "paper"},
	},
	"boxes": [
		{"x": 58, "y": 52, "items": ["teddy_bear", "ball", "drum", "toy_car", "robot"]},
		{"x": 84, "y": 108, "items": ["blocks", "ring_pyramid", "toy_rocket", "piggy_bank", "night_light"]},
		{"x": 132, "y": 40, "items": ["crayons", "sketchbook", "picture_books", "kid_drawing", "star_poster"]},
	],
}
