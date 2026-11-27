# Предмет, который достают из коробки и ставят на поверхность.
class_name Item
extends PixelSprite

enum State { IN_BOX, LOOSE, DRAGGED, PLACED }

var id := ""
var allowed: Array = []
var snd := "wood"             # материал для звука
var foot := Rect2()               # след на поверхности относительно wpos (мировые единицы)
var height := 0.0
var state := State.IN_BOX
var wpos := Vector3.ZERO          # мировая позиция (центр следа, низ)
var zone: Dictionary = {}         # зона, на которой стоит (если PLACED)
var from_box: Node = null         # коробка, над которой висит (если LOOSE)
var home := Vector3.ZERO          # куда вернуть, если отпустили мимо
var home_state := State.LOOSE
var home_zone: Dictionary = {}


func is_misplaced() -> bool:
	return state == State.PLACED and not allowed.has(zone.get("tag", ""))


func foot_at(p: Vector2) -> Rect2:
	return Rect2(foot.position + p, foot.size)
