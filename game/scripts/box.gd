# Коробка: первый клик открывает, следующие достают по одному предмету,
# пустую коробку кликом складываем и убираем.
class_name Box
extends PixelSprite

const TEX_CLOSED := preload("res://assets/sprites/box_closed.png")
const TEX_OPEN := preload("res://assets/sprites/box_open.png")

var contents: Array = []   # id предметов, последний достаётся первым
var opened := false
var loose_item: Item = null
var removed := false


func _ready() -> void:
	set_tex(TEX_CLOSED)


func open() -> void:
	opened = true
	set_tex(TEX_OPEN)
	squash(0.25)


func top_y() -> int:
	# верх проёма открытой коробки (створки не считаем)
	return int(position.y) - 26 + 1


func is_empty() -> bool:
	return contents.is_empty() and loose_item == null


func shake() -> void:
	var t := create_tween()
	var x := position.x
	for dx in [2, -2, 1, -1, 0]:
		t.tween_property(self, "position:x", x + dx, 0.04)


func fold_away() -> void:
	removed = true
	set_outline(false)
	var t := create_tween()
	t.tween_property(self, "scale", Vector2(1.3, 0.2), 0.12)
	t.tween_property(self, "scale", Vector2(0.0, 0.0), 0.1)
	t.tween_callback(hide)
