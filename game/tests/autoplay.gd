# Автоплейтест: проходит уровень настоящими событиями мыши и делает скриншоты.
# Запуск (нужен дисплей, например xvfb-run):
#   godot --path game res://tests/autoplay.tscn -- <папка_для_скриншотов>
extends Node

const SCALE := 3.0  # окно 1440×810 при вьюпорте 480×270

# id -> [зона, мировые x, y]
const PLAN := {
	"plates": ["shelf", 35, 8], "bowl": ["shelf", 50, 8],
	"mug_yellow": ["shelf", 63, 6], "mug_blue": ["shelf", 73, 6], "glass": ["shelf", 83, 8],
	"spices": ["shelf", 94, 8],
	"pot": ["stove", 74, 7], "pan": ["stove", 66, 24], "kettle": ["counter_r2", 97, 15],
	"cutting_board": ["counter_r", 15, 14], "knife_block": ["counter_r", 40, 8],
	"soap": ["counter_l", 8, 90], "plant": ["sill", 4.5, 60], "milk": ["fridge_1", 124, 14],
	"cheese": ["counter_l", 18, 100],  # специально не туда — проверим подсветку
}

var main: Node
var out_dir := "user://"
var shot := 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		out_dir = args[0]
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await wait(2.4)
	await snap("01_start")
	await click(Iso.to_screen(Vector3(127, 31, 40)))  # открыть холодильник
	await wait(0.2)
	var first := true
	for box in main.boxes:
		var bp := Iso.to_screen(box.wpos + Vector3(0, 0, 6))
		await click(bp)  # открыть
		await wait(0.3)
		while not box.contents.is_empty():
			await click(bp)
			await wait(0.35)
			if first:
				await snap("02_item_out")
				first = false
			var it = box.loose_item
			if it == null:
				print("FAIL: нет предмета над коробкой")
				get_tree().quit(1)
				return
			await drag_to_plan(it)
			if it.state != Item.State.PLACED:
				print("FAIL: не встал ", it.id, " pos=", it.position)
				get_tree().quit(1)
				return
		await click(bp)  # убрать пустую коробку
		await wait(0.3)
	await wait(0.3)
	await snap("03_wrong_item")
	print("misplaced shown: ", main.showing_wrong)
	# переносим сыр в холодильник
	var cheese = main._find_item("cheese")
	await drag(cheese, Iso.to_screen(Vector3(126, 14, 6)))
	await wait(0.6)
	await snap("04_done")
	print("level done: ", main.level_done)
	for it in main.items:
		print("  ", it.id, " -> ", it.zone.get("id", "?"), " at ", it.wpos, " wrong=", it.is_misplaced())
	get_tree().quit()


func drag_to_plan(it) -> void:
	var p: Array = PLAN[it.id]
	var z: Dictionary = {}
	for zz in main.zones:
		if zz["id"] == p[0]:
			z = zz
	await drag(it, Iso.to_screen(Vector3(p[1], p[2], z["z"])))


func drag(it, target_bottom: Vector2) -> void:
	var grab := find_opaque(it)
	var off: Vector2 = it.position - grab
	await press(grab, true)
	var to := target_bottom - off
	for i in range(1, 7):
		await move(grab.lerp(to, i / 6.0))
	await press(to, false)
	await wait(0.25)


func find_opaque(it) -> Vector2:
	var c: Vector2 = it.position + Vector2(0, -3)
	for r in range(0, 6):
		for dx in range(-r, r + 1):
			for dy in range(-r, r + 1):
				var p := (c + Vector2(dx, dy)).floor() + Vector2(0.5, 0.5)
				if it.hit(p):
					return p
	return c


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
	shot += 1
