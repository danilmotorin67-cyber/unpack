# Главная сцена: строит изометрическую комнату, обрабатывает мышь,
# раскладывает предметы по поверхностям и проверяет, всё ли на месте.
extends Node2D

const LEVELS := [
	preload("res://scripts/levels/level_01.gd"),
	preload("res://scripts/levels/level_02.gd"),
	preload("res://scripts/levels/level_03.gd"),
	preload("res://scripts/levels/level_04.gd"),
]
const Art := preload("res://scripts/art_data.gd")
const CURSOR_ARROW := preload("res://assets/sprites/cursor_arrow.png")
const CURSOR_HAND := preload("res://assets/sprites/cursor_hand.png")
const CURSOR_GRAB := preload("res://assets/sprites/cursor_grab.png")

const VIEW := Vector2(640, 360)

# Слои: фон -> объекты в комнате (сортируются по глубине) -> висящие/тащимые вещи -> UI
const Z_BG := -100
const Z_WORLD := 0           # + глубина (x + y), до ~300
const Z_LOOSE := 1000
const Z_DRAG := 1100
const Z_UI := 2000
const Z_CURSOR := 3000

const SNAP_TOLERANCE := 3.0  # насколько можно промахнуться мимо края поверхности (мировые ед.)
const MAX_NUDGE := 12        # насколько можно сдвинуть вещь, чтобы не перекрыть соседей
const GAP := 0.5             # минимальный зазор между вещами

var level_index := 0
var data: Dictionary
var zones: Array
var containers := {}        # id -> {data, sprite, open}
var items: Array[Item] = []
var boxes: Array[Box] = []

var dragging: Item = null
var drag_offset := Vector2.ZERO
var hovered: Node = null
var level_done := false
var waiting_next := false
var showing_wrong := false
var first_item_taken := false
var first_item_placed := false

var cursor: Sprite2D
var hint: PixelText
var banner: Node2D
var world: Node2D           # всё, что относится к текущему уровню
var sfx: Sfx
var _nudges: Array[Vector2] = []


func _ready() -> void:
	randomize()
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
	_prepare_nudges()
	sfx = Sfx.new()
	add_child(sfx)
	_build_ui()
	load_level(0)


# Сбрасывает состояние и строит уровень с номером index (с нуля).
func load_level(index: int) -> void:
	level_index = index
	data = LEVELS[index].DATA
	zones = Art.ROOMS[data["room"]]["zones"]
	if world:
		world.queue_free()
	if banner and is_instance_valid(banner):
		banner.queue_free()
	world = Node2D.new()
	add_child(world)
	containers.clear()
	items.clear()
	boxes.clear()
	dragging = null
	hovered = null
	level_done = false
	waiting_next = false
	showing_wrong = false
	first_item_taken = false
	first_item_placed = false
	hint.text = ""
	_build_level()
	_show_title()


# ------------------------------------------------------------------ сборка

func _build_level() -> void:
	var room: Dictionary = Art.ROOMS[data["room"]]
	var bg := Sprite2D.new()
	bg.texture = load(room["bg"])
	bg.centered = false
	bg.z_index = Z_BG
	world.add_child(bg)

	for id in room["doors"]:
		var s := PixelSprite.new()
		world.add_child(s)
		containers[id] = {"sprite": s, "open": false, "art": room["doors"][id]}
		_apply_container(id)

	var item_defs: Dictionary = data["items"]
	for b in data["boxes"]:
		var box := Box.new()
		box.wpos = Vector3(b["x"], b["y"], 0)
		box.position = Iso.to_screen(box.wpos)
		box.z_index = Z_WORLD + Iso.depth(box.wpos)
		world.add_child(box)
		var ids: Array = b["items"].duplicate()
		ids.shuffle()
		box.contents = ids
		boxes.append(box)
		for id in ids:
			var info: Dictionary = Art.ITEMS[id]
			var it := Item.new()
			it.id = id
			it.allowed = item_defs[id]["allowed"]
			it.snd = item_defs[id].get("snd", "wood")
			it.foot = info["foot"]
			it.height = info["h"]
			if info.get("wall", false):
				it.setup_wall(
					load("res://assets/sprites/item_%s_l.png" % id), info["anchor_l"],
					load("res://assets/sprites/item_%s_r.png" % id), info["anchor_r"])
			else:
				it.set_tex(load("res://assets/sprites/item_%s.png" % id), info["anchor"])
			it.visible = false
			world.add_child(it)
			items.append(it)


func _build_ui() -> void:
	hint = PixelText.new()
	hint.position = Vector2(VIEW.x / 2, 5)
	hint.color = Color("2e2430")
	hint.shadow_color = Color("e3d3b3")
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
	var top := VIEW.y / 2 - 22
	var h := 38.0 if subtitle != "" else 30.0
	var band := ColorRect.new()
	band.color = Color("2e2430")
	band.position = Vector2(0, top)
	band.size = Vector2(VIEW.x, h)
	band.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(band)
	for y in [top + 1, top + h - 2]:
		var line := ColorRect.new()
		line.color = Color("ecc97a")
		line.position = Vector2(0, y)
		line.size = Vector2(VIEW.x, 1)
		line.mouse_filter = Control.MOUSE_FILTER_IGNORE
		root.add_child(line)
	var t := PixelText.new()
	t.text = title
	t.scale = Vector2(2, 2)
	t.position = Vector2(VIEW.x / 2, top + 7)
	t.shadow = false
	root.add_child(t)
	if subtitle != "":
		var s := PixelText.new()
		s.text = subtitle
		s.position = Vector2(VIEW.x / 2, top + 25)
		s.color = Color("cdb995")
		s.shadow = false
		root.add_child(s)
	add_child(root)
	return root


func _show_title() -> void:
	banner = _make_banner(data["title"], "КОМНАТА %d ИЗ %d" % [level_index + 1, LEVELS.size()])
	var b := banner
	var t := create_tween()
	t.tween_interval(1.6)
	t.tween_property(b, "modulate:a", 0.0, 0.5)
	t.tween_callback(b.queue_free)
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
			KEY_M:
				sfx.toggle_music()
			KEY_R:
				if level_done:
					load_level(level_index)
			KEY_SPACE, KEY_ENTER:
				if waiting_next:
					_next_level()
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		var mp := get_global_mouse_position().floor()
		if event.pressed:
			_press(mp)
		elif dragging:
			_drop(dragging)
			dragging = null


func _press(mp: Vector2) -> void:
	if waiting_next:
		_next_level()
		return
	if level_done:
		return
	var target := _object_at(mp)
	if target is Item:
		_start_drag(target, mp)
	elif target is Box:
		_click_box(target)
	elif target != null:
		for id in containers:
			if containers[id]["sprite"] == target:
				_toggle_container(id)


func _process(_delta: float) -> void:
	var mp := get_global_mouse_position().floor()
	cursor.position = mp
	if dragging:
		dragging.position = (mp + drag_offset).round()
		_update_drag_side(dragging)
	_update_hover(mp)
	_update_wrong_blink()


func _update_hover(mp: Vector2) -> void:
	var h: Node = null
	if not dragging and not level_done:
		h = _object_at(mp)
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


# ------------------------------------------------------------------ что под мышью

# Самый верхний (по z_index) интерактивный объект под курсором.
func _object_at(mp: Vector2) -> Node:
	var best: PixelSprite = null
	var candidates: Array = []
	for it in items:
		if it.state != Item.State.IN_BOX and it.visible and not _hidden_in_container(it):
			candidates.append(it)
	for box in boxes:
		if not box.removed:
			candidates.append(box)
	for id in containers:
		candidates.append(containers[id]["sprite"])
	for c in candidates:
		var s: PixelSprite = c
		if s.hit(mp) and (best == null or s.z_index > best.z_index or (s.z_index == best.z_index and s.get_index() > best.get_index())):
			best = s
	return best


func _hidden_in_container(it: Item) -> bool:
	if it.state != Item.State.PLACED:
		return false
	var cid: String = it.zone.get("container", "")
	return cid != "" and not containers[cid]["open"]


# ------------------------------------------------------------------ коробки и контейнеры

func _click_box(box: Box) -> void:
	if not box.opened:
		box.open()
		sfx.play("box_open")
		return
	if box.loose_item:
		box.shake()
		sfx.play("bump")
		return
	if box.contents.is_empty():
		box.fold_away()
		sfx.play("box_fold")
		hovered = null
		return
	var it: Item = _find_item(box.contents.pop_back())
	it.visible = true
	it.state = Item.State.LOOSE
	it.from_box = box
	it.z_index = Z_LOOSE
	box.loose_item = it
	it.wpos = box.hover_point()
	it.home = it.wpos
	it.home_state = Item.State.LOOSE
	it.home_zone = {}
	if it.is_wall:
		it.set_wall_side("R")
		it.home_side = "R"
	var target := Iso.to_screen(it.wpos).round()
	it.position = Iso.to_screen(box.wpos + Vector3(0, 0, 8)).round()
	it.scale = Vector2(0.5, 0.5)
	var t := it.new_tween().set_parallel()
	t.tween_property(it, "position", target, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	t.tween_property(it, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	box.squash(0.1, 0.15)
	sfx.play("pop")
	if not first_item_taken:
		first_item_taken = true
		hint.text = "ПЕРЕТАЩИ ВЕЩЬ НА ЕЁ МЕСТО"


func _find_item(id: String) -> Item:
	for it in items:
		if it.id == id:
			return it
	return null


func _apply_container(id: String) -> void:
	var c: Dictionary = containers[id]
	var art: Dictionary = c["art"]
	var s: PixelSprite = c["sprite"]
	s.set_tex(load(art["open"] if c["open"] else art["closed"]), Vector2.ZERO)
	s.position = art["open_pos"] if c["open"] else art["closed_pos"]
	s.z_index = Z_WORLD + int(art["open_depth"] if c["open"] else art["closed_depth"])


func _toggle_container(id: String) -> void:
	containers[id]["open"] = not containers[id]["open"]
	_apply_container(id)
	sfx.play("door_open" if containers[id]["open"] else "door_close")
	var s: PixelSprite = containers[id]["sprite"]
	s.set_outline(false)
	s.squash(0.05, 0.12)
	hovered = null


# ------------------------------------------------------------------ перетаскивание

func _start_drag(it: Item, mp: Vector2) -> void:
	dragging = it
	it.stop_tween()
	it.scale = Vector2.ONE
	if it.state == Item.State.PLACED:
		it.home = it.wpos
		it.home_state = Item.State.PLACED
		it.home_zone = it.zone
		it.home_zpos = it.zpos
		it.home_side = it.wall_side
	it.state = Item.State.DRAGGED
	it.zone = {}
	it.z_index = Z_DRAG
	it.set_outline(false)
	drag_offset = it.position - mp
	it.squash(-0.1, 0.12)
	sfx.play("pick")


# Пока тащим настенную вещь, разворачиваем её к той стене, над которой она.
func _update_drag_side(it: Item) -> void:
	if not it.is_wall:
		return
	for c in _spot_candidates(it):
		var side: String = c["zone"]["wall"]
		if side != it.wall_side:
			var before := it.position
			it.set_wall_side(side)
			it.position = before
		return


func _drop(it: Item) -> void:
	var spot := _find_spot(it)
	if spot.is_empty():
		_return_home(it)
		return
	if it.from_box:
		it.from_box.loose_item = null
		it.from_box = null
	_place(it, spot["zone"], spot["zpos"])
	if not first_item_placed:
		first_item_placed = true
		hint.text = ""
	_check_level()


func _place(it: Item, z: Dictionary, zpos: Vector2) -> void:
	it.state = Item.State.PLACED
	it.zone = z
	it.zpos = zpos
	it.wpos = zone_to_world(z, zpos)
	if it.is_wall:
		it.set_wall_side(z["wall"])
	it.z_index = Z_WORLD + Iso.depth(it.wpos)
	var t := it.new_tween()
	t.tween_property(it, "position", Iso.to_screen(it.wpos).round(), 0.06)
	t.tween_callback(it.squash.bind(0.2, 0.2))
	sfx.play("place_" + it.snd)


func _return_home(it: Item) -> void:
	it.state = it.home_state
	it.zone = it.home_zone
	it.zpos = it.home_zpos
	it.wpos = it.home
	if it.is_wall:
		it.set_wall_side(it.home_side)
	it.z_index = Z_LOOSE if it.home_state == Item.State.LOOSE else Z_WORLD + Iso.depth(it.home)
	sfx.play("bump", -6.0)
	var t := it.new_tween()
	t.tween_property(it, "position", Iso.to_screen(it.home).round(), 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	t.tween_callback(it.squash.bind(0.15, 0.15))


# ------------------------------------------------------------------ поверхности
# У каждой зоны свои 2D-координаты: на горизонтальной поверхности (x, y),
# на стене (u, z), где u — вдоль стены (левая: u = -y, правая: u = x).

func is_wall_zone(z: Dictionary) -> bool:
	return z.has("wall")


func zone_area(z: Dictionary) -> Rect2:
	if is_wall_zone(z):
		return Rect2(z["u0"], z["z0"], z["u1"] - z["u0"], z["z1"] - z["z0"])
	return Rect2(z["x0"], z["y0"], z["x1"] - z["x0"], z["y1"] - z["y0"])


func zone_to_world(z: Dictionary, p: Vector2) -> Vector3:
	if not is_wall_zone(z):
		return Vector3(p.x, p.y, z["z"])
	if z["wall"] == "L":
		return Vector3(0, -p.x, p.y)
	return Vector3(p.x, 0, p.y)


# Точка экрана -> координаты зоны (на её плоскости).
func screen_to_zone(z: Dictionary, s: Vector2) -> Vector2:
	if not is_wall_zone(z):
		return Iso.to_world(s, z["z"])
	var w := Iso.to_wall(s, z["wall"])
	return Vector2(-w.x if z["wall"] == "L" else w.x, w.y)


# Зоны под точкой опоры предмета, ближайшие к зрителю — первыми.
func _spot_candidates(it: Item) -> Array:
	var candidates: Array = []
	for z in zones:
		if is_wall_zone(z) != it.is_wall:
			continue
		var cid: String = z.get("container", "")
		if cid != "" and not containers[cid]["open"]:
			continue
		if not it.is_wall and it.height > z["max_h"]:
			continue
		var p := screen_to_zone(z, it.position)
		if not zone_area(z).grow(SNAP_TOLERANCE).has_point(p):
			continue
		var w := zone_to_world(z, p)
		candidates.append({"zone": z, "p": p, "depth": w.x + w.y + w.z})
	candidates.sort_custom(func(a, b): return a["depth"] > b["depth"])
	return candidates


# Ищет поверхность под предметом и свободное место на ней.
func _find_spot(it: Item) -> Dictionary:
	for c in _spot_candidates(it):
		var p = _free_pos(it, c["zone"], c["p"])
		if p != null:
			return {"zone": c["zone"], "zpos": p}
	return {}


func _prepare_nudges() -> void:
	for dx in range(-MAX_NUDGE, MAX_NUDGE + 1):
		for dy in range(-MAX_NUDGE, MAX_NUDGE + 1):
			if dx * dx + dy * dy <= MAX_NUDGE * MAX_NUDGE:
				_nudges.append(Vector2(dx, dy))
	_nudges.sort_custom(func(a, b): return a.length_squared() < b.length_squared())


# Ближайшая к желаемой позиция (в координатах зоны), где след предмета
# целиком в зоне и не пересекается со следами соседей.
func _free_pos(it: Item, z: Dictionary, want: Vector2) -> Variant:
	var area := zone_area(z)
	var lo := area.position - it.foot.position
	var hi := area.end - it.foot.end
	if lo.x > hi.x or lo.y > hi.y:
		return null
	want = want.clamp(lo, hi).round()
	var others: Array[Rect2] = []
	for o in items:
		if o != it and o.state == Item.State.PLACED and o.zone.get("id") == z["id"]:
			others.append(o.foot_at(o.zpos).grow(GAP))
	for d in _nudges:
		var p: Vector2 = want + d
		if p.x < lo.x or p.y < lo.y or p.x > hi.x or p.y > hi.y:
			continue
		var r := it.foot_at(p)
		var ok := true
		for o in others:
			if r.intersects(o):
				ok = false
				break
		if ok:
			return p
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
		if not showing_wrong:
			sfx.play("wrong")
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
	sfx.play("complete", 0.0, 0.0)
	var last := level_index == LEVELS.size() - 1
	if last:
		banner = _make_banner("ВСЁ РАСПАКОВАНО!", "СПАСИБО ЗА ИГРУ   R - ЕЩЁ РАЗ   ESC - ВЫХОД")
	else:
		banner = _make_banner(data["done_text"], "НАЖМИ, ЧТОБЫ ПРОДОЛЖИТЬ")
	banner.modulate.a = 0.0
	var t := create_tween()
	t.tween_interval(0.5)
	t.tween_property(banner, "modulate:a", 1.0, 0.4)
	t.tween_callback(func(): waiting_next = not last)


func _next_level() -> void:
	waiting_next = false
	load_level((level_index + 1) % LEVELS.size())
