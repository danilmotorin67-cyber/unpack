# Уровень 2 — ванная. См. комментарии в level_01.gd.
extends RefCounted

const DATA := {
	"room": "bathroom",
	"title": "ВАННАЯ",
	"done_text": "ВАННАЯ ГОТОВА!",
	"items": {
		"toothbrush_cup": {"allowed": ["sink", "mirror"], "snd": "ceramic"},
		"toothpaste": {"allowed": ["sink", "mirror"], "snd": "plastic"},
		"soap_dish": {"allowed": ["sink", "bath"], "snd": "glass"},
		"shampoo": {"allowed": ["bath"], "snd": "plastic"},
		"shower_gel": {"allowed": ["bath"], "snd": "plastic"},
		"duck": {"allowed": ["bath"], "snd": "plastic"},
		"sponge": {"allowed": ["bath"], "snd": "soft"},
		"towel_blue": {"allowed": ["shelf"], "snd": "soft"},
		"towel_white": {"allowed": ["shelf"], "snd": "soft"},
		"toilet_paper": {"allowed": ["shelf", "toilet"], "snd": "paper"},
		"perfume": {"allowed": ["mirror", "sink"], "snd": "glass"},
		"cream": {"allowed": ["mirror", "sink"], "snd": "plastic"},
		"cactus": {"allowed": ["toilet", "shelf"], "snd": "plant"},
		"hairbrush": {"allowed": ["mirror", "sink"], "snd": "wood"},
	},
	"boxes": [
		{"x": 60, "y": 58, "items": ["toothbrush_cup", "toothpaste", "perfume", "cream", "hairbrush"]},
		{"x": 95, "y": 94, "items": ["shampoo", "shower_gel", "duck", "sponge", "soap_dish"]},
		{"x": 128, "y": 60, "items": ["towel_blue", "towel_white", "toilet_paper", "cactus"]},
	],
}
