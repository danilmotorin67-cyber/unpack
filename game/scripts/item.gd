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
var zpos := Vector2.ZERO          # позиция в координатах зоны (см. main.zone_area)
var home_zpos := Vector2.ZERO

# вещи на стенах: два спрайта — для левой и правой стены
var is_wall := false
var wall_side := "R"
var home_side := "R"
var _wall_tex := {}


func setup_wall(tex_l: Texture2D, anchor_l: Vector2, tex_r: Texture2D, anchor_r: Vector2) -> void:
	is_wall = true
	_wall_tex = {"L": [tex_l, anchor_l], "R": [tex_r, anchor_r]}
	set_wall_side("R")


func set_wall_side(side: String) -> void:
	wall_side = side
	set_tex(_wall_tex[side][0], _wall_tex[side][1])


func is_misplaced() -> bool:
	return state == State.PLACED and not allowed.has(zone.get("tag", ""))


func foot_at(p: Vector2) -> Rect2:
	return Rect2(foot.position + p, foot.size)
