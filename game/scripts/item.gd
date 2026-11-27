# Предмет, который достают из коробки и ставят на поверхность.
class_name Item
extends PixelSprite

enum State { IN_BOX, LOOSE, DRAGGED, PLACED }

var id := ""
var allowed: Array = []
var state := State.IN_BOX
var zone: Dictionary = {}         # зона, на которой стоит (если PLACED)
var from_box: Node = null         # коробка, над которой висит (если LOOSE)
var home := Vector2.ZERO          # куда вернуть, если отпустили мимо
var home_state := State.LOOSE


func is_misplaced() -> bool:
	return state == State.PLACED and not allowed.has(zone.get("tag", ""))


func left() -> int:
	return int(position.x) - half_left


func right() -> int:
	return int(position.x) + half_right
