# Главная сцена: строит уровень из данных, обрабатывает мышь,
# раскладывает предметы по поверхностям и проверяет, всё ли на месте.
extends Node2D

const Level := preload("res://scripts/levels/level_01.gd")
const CURSOR_ARROW := preload("res://assets/sprites/cursor_arrow.png")
const CURSOR_HAND := preload("res://assets/sprites/cursor_hand.png")
const CURSOR_GRAB := preload("res://assets/sprites/cursor_grab.png")

const Z_BG := 0
const Z_BOX := 5
const Z_ITEM := 10
const Z_DOOR := 20
const Z_LOOSE := 30
const Z_DRAG := 50
const Z_UI := 90
const Z_CURSOR := 100

# Насколько далеко (по вертикали) от поверхности можно отпустить предмет,
# чтобы он на неё «сел». Отрицательное — низ предмета ниже поверхности.
const SNAP_ABOVE := 22
const SNAP_BELOW := 8
const MAX_NUDGE := 24   # насколько можно сдвинуть вбок, чтобы не перекрыть соседа

var data: Dictionary = Level.DATA
var zones: Array = []
var containers := {}        # id -> {data, sprite, open}
var items: Array[Item] = []
var boxes: Array[Box] = []

var dragging: Item = null
var drag_offset := Vector2.ZERO
var hovered: Node = null
var level_done := false
var showing_wrong := false
var first_item_taken := false
var first_item_placed := false

var cursor: Sprite2D
var hint: PixelText
var banner: Node2D


func _ready() -> void:
	randomize()
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
	_build_level()
	_build_ui()
	_show_title()


# ------------------------------------------------------------------ сборка

func _build_level() -> void:
	var bg := Sprite2D.new()
	bg.texture = load(data["background"])
	bg.centered = false
	bg.z_index = Z_BG
	add_child(bg)

	zones = data["zones"]

	for c in data["containers"]:
		var s := PixelSprite.new()
		s.set_tex(load(c["closed"]))
		s.offset = Vector2.ZERO  # у дверей точка опоры — левый верхний угол
		s.position = c["closed_pos"]
		s.z_index = Z_DOOR
		add_child(s)
		containers[c["id"]] = {"data": c, "sprite": s, "open": false}

	var item_defs: Dictionary = data["items"]
	for b in data["boxes"]:
		var box := Box.new()
		box.position = Vector2(b["x"], b["y"])
		box.z_index = Z_BOX
		add_child(box)
		var ids: Array = b["items"].duplicate()
		ids.shuffle()
		box.contents = ids
		boxes.append(box)
		for id in ids:
			var it := Item.new()
			it.id = id
			it.allowed = item_defs[id]["allowed"]
			it.set_tex(load("res://assets/sprites/item_%s.png" % id))
			it.visible = false
			it.z_index = Z_ITEM
			add_child(it)
			items.append(it)


func _build_ui() -> void:
	hint = PixelText.new()
	hint.position = Vector2(160, 3)
	hint.color = Color("2e2430")
	hint.shadow_color = Color("e2cfb0")
	hint.z_index = Z_UI
	add_child(hint)

	cursor = Sprite2D.new()
	cursor.centered = false
	cursor.texture = CURSOR_ARROW
	cursor.z_index = Z_CURSOR
	add_child(cursor)


func _make_banner(title: String, subtitle: String) -> Node2D:
	var root := Node2D.new()
	root.z_index = Z_UI
	var band := ColorRect.new()
	band.color = Color("2e2430")
	band.position = Vector2(0, 70)
	band.size = Vector2(320, 38 if subtitle != "" else 30)
	band.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(band)
	var line := ColorRect.new()
	line.color = Color("e6be6e")
	line.position = Vector2(0, 71)
	line.size = Vector2(320, 1)
	line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(line)
	var line2 := line.duplicate() as ColorRect
	line2.position = Vector2(0, band.position.y + band.size.y - 2)
	root.add_child(line2)
	var t := PixelText.new()
	t.text = title
	t.scale = Vector2(2, 2)
	t.position = Vector2(160, 77)
	t.shadow = false
	root.add_child(t)
	if subtitle != "":
		var s := PixelText.new()
		s.text = subtitle
		s.position = Vector2(160, 95)
		s.color = Color("c9b08e")
		s.shadow = false
		root.add_child(s)
	add_child(root)
	return root


func _show_title() -> void:
	banner = _make_banner(data["title"], "")
	var t := create_tween()
	t.tween_interval(1.6)
	t.tween_property(banner, "modulate:a", 0.0, 0.5)
	t.tween_callback(banner.queue_free)
	t.tween_callback(_show_first_hint)


func _show_first_hint() -> void:
	if not first_item_taken:
		hint.text = "НАЖМИ НА КОРОБКУ"


# ------------------------------------------------------------------ ввод

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_ESCAPE:
				get_tree().quit()
			KEY_F11:
				var full := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
				DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if full else DisplayServer.WINDOW_MODE_FULLSCREEN)
			KEY_R:
				if level_done:
					get_tree().reload_current_scene()
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		var mp := get_global_mouse_position().floor()
		if event.pressed:
			_press(mp)
		else:
			_release(mp)


func _press(mp: Vector2) -> void:
	var it := _item_at(mp)
	if it:
		_start_drag(it, mp)
		return
	for id in containers:
		var c: Dictionary = containers[id]
		if (c["sprite"] as PixelSprite).hit(mp):
			_toggle_container(id)
			return
	var box := _box_at(mp)
	if box:
		_click_box(box)


func _release(_mp: Vector2) -> void:
	if dragging:
		_drop(dragging)
		dragging = null


func _process(_delta: float) -> void:
	var mp := get_global_mouse_position().floor()
	cursor.position = mp
	if dragging:
		dragging.position = (mp + drag_offset).round()
	_update_hover(mp)
	_update_wrong_blink()


func _update_hover(mp: Vector2) -> void:
	var h: Node = null
	if not dragging and not level_done:
		h = _item_at(mp)
		if h == null:
			for id in containers:
				if containers[id]["sprite"].hit(mp):
					h = containers[id]["sprite"]
			if h == null:
				h = _box_at(mp)
	if h != hovered:
		if hovered and is_instance_valid(hovered):
			hovered.set_outline(false)
		hovered = h
		if hovered:
			hovered.set_outline(true)
	if dragging:
		cursor.texture = CURSOR_GRAB
		cursor.offset = Vector2(-4, -3)
	elif hovered:
		cursor.texture = CURSOR_HAND
		cursor.offset = Vector2(-4, -1)
	else:
		cursor.texture = CURSOR_ARROW
		cursor.offset = Vector2.ZERO


# ------------------------------------------------------------------ поиск под мышью

func _item_at(mp: Vector2) -> Item:
	var best: Item = null
	for it in items:
		if it.state == Item.State.IN_BOX or not it.visible:
			continue
		if _hidden_in_container(it):
			continue
		if it.hit(mp):
			if best == null or it.z_index > best.z_index or (it.z_index == best.z_index and it.get_index() > best.get_index()):
				best = it
	return best


func _box_at(mp: Vector2) -> Box:
	for box in boxes:
		if not box.removed and box.hit(mp):
			return box
	return null


func _hidden_in_container(it: Item) -> bool:
	if it.state != Item.State.PLACED:
		return false
	var cid: String = it.zone.get("container", "")
	return cid != "" and not containers[cid]["open"]


# ------------------------------------------------------------------ коробки и контейнеры

func _click_box(box: Box) -> void:
	if not box.opened:
		box.open()
		return
	if box.loose_item:
		box.shake()
		return
	if box.contents.is_empty():
		box.fold_away()
		return
	var it: Item = _find_item(box.contents.pop_back())
	it.visible = true
	it.state = Item.State.LOOSE
	it.from_box = box
	it.z_index = Z_LOOSE
	box.loose_item = it
	var target := Vector2(box.position.x, box.top_y() - 3)
	it.home = target
	it.home_state = Item.State.LOOSE
	it.position = Vector2(target.x, box.top_y() + it.art_h / 2)
	it.scale = Vector2(0.6, 0.6)
	var t := it.new_tween().set_parallel()
	t.tween_property(it, "position", target, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	t.tween_property(it, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	box.squash(0.12, 0.15)
	if not first_item_taken:
		first_item_taken = true
		hint.text = "ПЕРЕТАЩИ ВЕЩЬ НА ЕЁ МЕСТО"


func _find_item(id: String) -> Item:
	for it in items:
		if it.id == id:
			return it
	return null


func _toggle_container(id: String) -> void:
	var c: Dictionary = containers[id]
	c["open"] = not c["open"]
	var s: PixelSprite = c["sprite"]
	var d: Dictionary = c["data"]
	s.texture = load(d["open"] if c["open"] else d["closed"])
	s.position = d["open_pos"] if c["open"] else d["closed_pos"]
	# hit() нужен свежий Image
	s.set_tex(s.texture)
	s.offset = Vector2.ZERO
	s.set_outline(false)
	hovered = null


# ------------------------------------------------------------------ перетаскивание

func _start_drag(it: Item, mp: Vector2) -> void:
	dragging = it
	it.stop_tween()
	it.scale = Vector2.ONE
	if it.state == Item.State.PLACED:
		it.home = it.position
		it.home_state = Item.State.PLACED
	it.state = Item.State.DRAGGED
	it.z_index = Z_DRAG
	it.set_outline(false)
	drag_offset = it.position - mp
	it.squash(-0.1, 0.12)


func _drop(it: Item) -> void:
	var spot := _find_spot(it)
	if spot.is_empty():
		_return_home(it)
		return
	var z: Dictionary = spot["zone"]
	var target: Vector2 = spot["pos"]
	if it.from_box:
		it.from_box.loose_item = null
		it.from_box = null
	it.state = Item.State.PLACED
	it.zone = z
	it.z_index = Z_ITEM
	var t := it.new_tween()
	t.tween_property(it, "position", target, 0.06)
	t.tween_callback(it.squash.bind(0.2, 0.2))
	if not first_item_placed:
		first_item_placed = true
		hint.text = ""
	_check_level()


func _return_home(it: Item) -> void:
	it.state = it.home_state
	it.z_index = Z_LOOSE if it.home_state == Item.State.LOOSE else Z_ITEM
	var t := it.new_tween()
	t.tween_property(it, "position", it.home, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	t.tween_callback(it.squash.bind(0.15, 0.15))


# Ищет поверхность под предметом и свободное место на ней.
func _find_spot(it: Item) -> Dictionary:
	var p := it.position
	var candidates: Array = []
	for z in zones:
		var cid: String = z.get("container", "")
		if cid != "" and not containers[cid]["open"]:
			continue
		if p.x < z["x0"] - 4 or p.x > z["x1"] + 4:
			continue
		var dy: float = z["y"] - p.y
		if dy < -SNAP_BELOW or dy > SNAP_ABOVE:
			continue
		if it.art_h > z["max_h"]:
			continue
		candidates.append({"zone": z, "dy": abs(dy)})
	candidates.sort_custom(func(a, b): return a["dy"] < b["dy"])
	for c in candidates:
		var x = _free_x(it, c["zone"], int(p.x))
		if x != null:
			return {"zone": c["zone"], "pos": Vector2(x, c["zone"]["y"])}
	return {}


# Ближайшая к желаемой x-позиция, где предмет не перекрывает соседей.
func _free_x(it: Item, z: Dictionary, want: int) -> Variant:
	var lo: int = z["x0"] + it.half_left
	var hi: int = z["x1"] + 1 - it.half_right
	if lo > hi:
		return null
	want = clampi(want, lo, hi)
	var others: Array[Item] = []
	for o in items:
		if o != it and o.state == Item.State.PLACED and o.zone.get("id") == z["id"]:
			others.append(o)
	var options: Array[int] = [want]
	for o in others:
		options.append(o.left() - it.half_right)   # вплотную слева
		options.append(o.right() + it.half_left)   # вплотную справа
	options.sort_custom(func(a, b): return abs(a - want) < abs(b - want))
	for x in options:
		if x < lo or x > hi or abs(x - want) > MAX_NUDGE:
			continue
		var ok := true
		for o in others:
			if x - it.half_left < o.right() and o.left() < x + it.half_right:
				ok = false
				break
		if ok:
			return x
	return null


# ------------------------------------------------------------------ проверка уровня

func _check_level() -> void:
	for box in boxes:
		if not box.contents.is_empty():
			return
	for it in items:
		if it.state != Item.State.PLACED:
			return
	var wrong := 0
	for it in items:
		if it.is_misplaced():
			wrong += 1
	if wrong > 0:
		showing_wrong = true
		hint.text = "КОЕ-ЧТО ЛЕЖИТ НЕ НА СВОЁМ МЕСТЕ"
	else:
		showing_wrong = false
		_finish()


func _update_wrong_blink() -> void:
	if not showing_wrong:
		return
	var on := int(Time.get_ticks_msec() / 400) % 2 == 0
	for it in items:
		if it == hovered or it == dragging:
			continue
		if it.is_misplaced():
			it.set_outline(on, PixelSprite.COLOR_WRONG)
		else:
			it.set_outline(false)


func _finish() -> void:
	level_done = true
	hint.text = ""
	for it in items:
		it.set_outline(false)
	if hovered:
		hovered.set_outline(false)
		hovered = null
	banner = _make_banner(data["done_text"], "R - ЕЩЁ РАЗ   ESC - ВЫХОД")
	banner.modulate.a = 0.0
	create_tween().tween_property(banner, "modulate:a", 1.0, 0.4)
