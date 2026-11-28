# Автоплейтест: проходит все уровни настоящими событиями мыши и делает скриншоты.
# Цели для предметов подбирает через логику игры (_free_pos), поэтому заодно
# проверяет, что на каждом уровне всё помещается. Первую вещь уровня кладёт
# не туда — проверяет подсветку ошибки.
# Запуск (нужен дисплей, например xvfb-run):
#   godot --path game res://tests/autoplay.tscn -- <папка_для_скриншотов>
extends Node

const SCALE := 2.0  # окно 1280×720 при вьюпорте 640×360

var main: Node
var out_dir := "user://"
var failed := false


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		out_dir = args[0]
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for level in main.LEVELS.size():
		await play_level(level)
		if failed:
			get_tree().quit(1)
			return
	print("ALL OK")
	get_tree().quit()


func fail(msg: String) -> void:
	print("FAIL: ", msg)
	failed = true


func play_level(level: int) -> void:
	await wait(2.4)
	var name: String = main.data["room"]
	if main.level_index != level:
		return fail("ожидался уровень %d, а сейчас %d" % [level, main.level_index])
	await snap("%d_%s_1_start" % [level + 1, name])
	for id in main.containers:
		var s: Sprite2D = main.containers[id]["sprite"]
		await click(find_opaque_rect(s))
		await wait(0.2)
		if not main.containers[id]["open"]:
			return fail("не открылся контейнер " + id)
	var wrong_item = null
	var shot_item := true
	for box in main.boxes:
		var bp := Iso.to_screen(box.wpos + Vector3(0, 0, 6))
		await click(bp)
		await wait(0.3)
		while not box.contents.is_empty():
			await click(bp)
			await wait(0.35)
			if shot_item:
				await snap("%d_%s_2_item" % [level + 1, name])
				shot_item = false
			var it = box.loose_item
			if it == null:
				return fail("нет предмета над коробкой")
			var target = null
			if wrong_item == null:
				target = find_target(it, false)
				if target != null:
					wrong_item = it
			if target == null:
				target = find_target(it, true)
			if target == null:
				for o in main.items:
					if o.state == Item.State.PLACED:
						print("   placed ", o.id, " ", o.zone["id"], " ", o.wpos, " foot ", o.foot)
				print("   item foot ", it.foot, " h ", it.height, " allowed ", it.allowed)
				return fail("некуда поставить " + it.id)
			await drag(it, Iso.to_screen(target))
			if it.state == Item.State.PLACED and it.wpos.distance_to(target) > 2.5:
				print("   TARGET ", it.id, " хотели ", target, " встал ", it.zone["id"], " ", it.wpos)
			if it.state != Item.State.PLACED:
				return fail("не встал %s (цель %s)" % [it.id, target])
		await click(bp)  # убрать пустую коробку
		await wait(0.3)
	await wait(0.3)
	if wrong_item == null:
		return fail("не нашлось неправильного места для проверки")
	if not main.showing_wrong:
		return fail("не показана подсветка ошибки")
	await snap("%d_%s_3_wrong" % [level + 1, name])
	var fix = find_target(wrong_item, true)
	await drag(wrong_item, Iso.to_screen(fix))
	await wait(1.2)
	if not main.level_done:
		var bad := []
		for it in main.items:
			if it.is_misplaced():
				bad.append(it.id)
		return fail("уровень не пройден, не на месте: %s" % [bad])
	await snap("%d_%s_4_done" % [level + 1, name])
	for it in main.items:
		print("  ", it.id, " -> ", it.zone.get("id", "?"), " ", it.wpos)
	print("level %d (%s) OK" % [level + 1, name])
	if level < main.LEVELS.size() - 1:
		await click(Vector2(320, 300))  # «нажми, чтобы продолжить»
		await wait(0.2)


# Свободное место на подходящей (correct=true) или неподходящей поверхности.
func find_target(it, correct: bool):
	for z in main.zones:
		if main.containers.has(z.get("container", "")) and not main.containers[z["container"]]["open"]:
			continue
		if main.is_wall_zone(z) != it.is_wall:
			continue
		if it.allowed.has(z["tag"]) != correct or (not it.is_wall and it.height > z["max_h"]):
			continue
		var area: Rect2 = main.zone_area(z)
		for fx in [0.25, 0.75, 0.5]:
			for fy in [0.25, 0.75, 0.5]:
				var c := area.position + area.size * Vector2(fx, fy)
				var p = main._free_pos(it, z, c)
				if p != null:
					return main.zone_to_world(z, p)
	return null


func drag(it, target_screen: Vector2) -> void:
	var grab := find_opaque(it)
	var off: Vector2 = it.position - grab
	await press(grab, true)
	var to := target_screen - off
	for i in range(1, 7):
		await move(grab.lerp(to, i / 6.0))
	await press(to, false)
	await wait(0.25)


func find_opaque(it) -> Vector2:
	var c: Vector2 = it.position + Vector2(0, -3)
	for r in range(0, 8):
		for dx in range(-r, r + 1):
			for dy in range(-r, r + 1):
				var p := (c + Vector2(dx, dy)).floor() + Vector2(0.5, 0.5)
				if it.hit(p) and main._object_at(p.floor()) == it:
					return p
	return c


func find_opaque_rect(s: Sprite2D) -> Vector2:
	var size := s.texture.get_size()
	return (s.position + size / 2).floor() + Vector2(0.5, 0.5)


func move(p: Vector2) -> void:
	var e := InputEventMouseMotion.new()
	e.position = p * SCALE
	e.global_position = e.position
	Input.warp_mouse(e.position)
	Input.parse_input_event(e)
	await wait(0.02)


func press(p: Vector2, down: bool) -> void:
	await move(p)
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = down
	e.position = p * SCALE
	e.global_position = e.position
	Input.parse_input_event(e)
	await wait(0.03)


func click(p: Vector2) -> void:
	await press(p, true)
	await press(p, false)


func wait(t: float) -> void:
	await get_tree().create_timer(t).timeout


func snap(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(out_dir.path_join("%s.png" % name))
