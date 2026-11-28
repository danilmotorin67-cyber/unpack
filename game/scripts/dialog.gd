# Диалог с портретом: печать по буквам, живая мимика (рот двигается,
# пока идёт текст, портрет моргает), смена эмоций по репликам.
class_name Dialog
extends Node2D

signal finished

const FontData := preload("res://scripts/font_data.gd")
const DIR := "res://assets/portrait/"
const EMOTIONS := {
	# эмоция: [брови, глаза, рот, рот во время речи, эффекты]
	"happy": ["happy", "happy", "grin", "talk", []],
	"smile": ["normal", "open", "smile", "talk", []],
	"wink": ["happy", "wink", "grin", "talk", []],
	"shy": ["soft", "aside", "soft", "talk", ["blush"]],
	"excited": ["raised", "open", "grin", "oh", ["sparkle"]],
	"love": ["soft", "happy", "smile", "talk", ["blush", "heart"]],
}
const CHARS_PER_SEC := 32.0
const TEXT_W := 420
const LINE_H := 11

var lines: Array = []
var sfx: Sfx
var _i := -1
var _shown := 0.0
var _full := ""
var _wrapped: Array[String] = []
var _emo: Array = []
var _talk_t := 0.0
var _blink_t := 3.0
var _blinking := 0.0
var _done_line := false

var portrait: Node2D
var _brows: Sprite2D
var _eyes: Sprite2D
var _mouth: Sprite2D
var _extras: Array[Sprite2D] = []
var _texts: Array[PixelText] = []
var _next: Sprite2D
var _base_pos := Vector2.ZERO


func _ready() -> void:
	# карточка портрета
	var card := _nine(Rect2(44, 236, 104, 108))
	add_child(card)
	portrait = Node2D.new()
	portrait.scale = Vector2(2, 2)
	_base_pos = Vector2(56, 254)
	portrait.position = _base_pos
	add_child(portrait)
	_add_layer(portrait, "base")
	_brows = _add_layer(portrait, "brows_normal")
	_eyes = _add_layer(portrait, "eyes_open")
	_mouth = _add_layer(portrait, "mouth_smile")
	# окно текста
	add_child(_nine(Rect2(152, 262, 452, 82)))
	for k in 4:
		var t := PixelText.new()
		t.centered = false
		t.shadow = false
		t.color = Color("2e2430")
		t.position = Vector2(170, 276 + k * LINE_H)
		add_child(t)
		_texts.append(t)
	_next = Sprite2D.new()
	_next.texture = load(DIR + "next.png")
	_next.centered = false
	_next.position = Vector2(584, 330)
	_next.visible = false
	add_child(_next)
	# появление снизу
	modulate.a = 0.0
	position.y = 30
	var t := create_tween().set_parallel()
	t.tween_property(self, "modulate:a", 1.0, 0.35)
	t.tween_property(self, "position:y", 0.0, 0.45).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	_advance()


func _nine(r: Rect2) -> NinePatchRect:
	var n := NinePatchRect.new()
	n.texture = load(DIR + "frame.png")
	n.patch_margin_left = 4
	n.patch_margin_top = 4
	n.patch_margin_right = 4
	n.patch_margin_bottom = 4
	n.position = r.position
	n.size = r.size
	n.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return n


func _add_layer(parent: Node, name: String) -> Sprite2D:
	var s := Sprite2D.new()
	s.centered = false
	s.texture = load(DIR + name + ".png")
	parent.add_child(s)
	return s


func _set_emotion(name: String) -> void:
	_emo = EMOTIONS[name]
	_brows.texture = load(DIR + "brows_" + _emo[0] + ".png")
	_eyes.texture = load(DIR + "eyes_" + _emo[1] + ".png")
	_mouth.texture = load(DIR + "mouth_" + _emo[2] + ".png")
	for s in _extras:
		s.queue_free()
	_extras.clear()
	for e in _emo[4]:
		_extras.append(_add_layer(portrait, "extra_" + e))
	# лёгкий подскок при смене эмоции
	var t := create_tween()
	portrait.position = _base_pos + Vector2(0, 3)
	t.tween_property(portrait, "position", _base_pos, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _advance() -> void:
	_i += 1
	if _i >= lines.size():
		_close()
		return
	_set_emotion(lines[_i]["emo"])
	_full = lines[_i]["text"]
	_wrapped = _wrap(_full)
	_shown = 0.0
	_done_line = false
	_next.visible = false
	_render()


func _close() -> void:
	set_process(false)
	var t := create_tween().set_parallel()
	t.tween_property(self, "modulate:a", 0.0, 0.3)
	t.tween_property(self, "position:y", 20.0, 0.3)
	t.chain().tween_callback(func():
		finished.emit()
		queue_free())


# Клик или пробел: сначала допечатать реплику, потом — следующая.
func next() -> void:
	if _i >= lines.size():
		return
	if not _done_line:
		_shown = _full.length()
		_render()
		_finish_line()
	else:
		_advance()


func _finish_line() -> void:
	_done_line = true
	_next.visible = true
	_mouth.texture = load(DIR + "mouth_" + _emo[2] + ".png")


func _wrap(text: String) -> Array[String]:
	var out: Array[String] = []
	var cur := ""
	for word in text.split(" "):
		var test := word if cur == "" else cur + " " + word
		if _width(test) > TEXT_W and cur != "":
			out.append(cur)
			cur = word
		else:
			cur = test
	if cur != "":
		out.append(cur)
	return out


func _width(s: String) -> int:
	var w := 0
	for ch in s:
		var g: Vector2i = FontData.GLYPHS.get(ch, FontData.GLYPHS["?"])
		w += g.y + 1
	return w


func _render() -> void:
	var left := int(_shown)
	for k in _texts.size():
		var line: String = _wrapped[k] if k < _wrapped.size() else ""
		var n := clampi(left, 0, line.length())
		_texts[k].text = line.substr(0, n)
		left -= line.length() + 1


func _process(delta: float) -> void:
	if _i < 0 or _i >= lines.size():
		return
	if not _done_line:
		var before := int(_shown)
		_shown += delta * CHARS_PER_SEC
		var now := int(_shown)
		if now != before:
			_render()
			var ch := _full.substr(min(now, _full.length()) - 1, 1)
			if now % 2 == 0 and ch != " " and sfx:
				sfx.play("blip", -12.0, 0.12)
		if _shown >= _full.length():
			_finish_line()
		else:
			# рот: открыт/закрыт в такт печати
			_talk_t += delta
			var open := int(_talk_t / 0.09) % 2 == 0
			_mouth.texture = load(DIR + "mouth_" + (_emo[3] if open else _emo[2]) + ".png")
	# моргание, если глаза открыты
	if _emo[1] in ["open", "aside"]:
		_blink_t -= delta
		if _blinking > 0.0:
			_blinking -= delta
			if _blinking <= 0.0:
				_eyes.texture = load(DIR + "eyes_" + _emo[1] + ".png")
		elif _blink_t <= 0.0:
			_eyes.texture = load(DIR + "eyes_blink.png")
			_blinking = 0.12
			_blink_t = randf_range(2.0, 4.0)
	# стрелка «дальше» мигает
	if _next.visible:
		_next.position.y = 330 + (1 if int(Time.get_ticks_msec() / 350) % 2 == 0 else 0)
