# Базовый спрайт с точкой опоры внизу по центру и попиксельным попаданием мыши.
# Все PNG сгенерированы с прозрачной рамкой 1px (для обводки), её учитываем.
class_name PixelSprite
extends Sprite2D

const OUTLINE_SHADER := preload("res://shaders/outline.gdshader")
const COLOR_HOVER := Color("fbf5e9")
const COLOR_WRONG := Color("c8664f")

var _image: Image
var art_w := 0   # ширина рисунка без рамки
var art_h := 0
var half_left := 0
var half_right := 0


func _init() -> void:
	centered = false
	material = ShaderMaterial.new()
	material.shader = OUTLINE_SHADER


func set_tex(tex: Texture2D) -> void:
	texture = tex
	_image = tex.get_image()
	art_w = tex.get_width() - 2
	art_h = tex.get_height() - 2
	half_left = art_w / 2
	half_right = art_w - half_left
	# position = низ-центр рисунка; нижний ряд рисунка на строке position.y - 1
	offset = Vector2(-1 - half_left, 1 - tex.get_height())


func hit(global_point: Vector2) -> bool:
	if not visible or _image == null:
		return false
	var local := (global_point - global_position) / scale - offset
	var px := int(floor(local.x))
	var py := int(floor(local.y))
	if px < 0 or py < 0 or px >= _image.get_width() or py >= _image.get_height():
		return false
	return _image.get_pixel(px, py).a > 0.5


func set_outline(on: bool, color: Color = COLOR_HOVER) -> void:
	var m := material as ShaderMaterial
	m.set_shader_parameter("enabled", on)
	m.set_shader_parameter("outline_color", color)


var _tween: Tween


func new_tween() -> Tween:
	stop_tween()
	_tween = create_tween()
	return _tween


func stop_tween() -> void:
	if _tween and _tween.is_valid():
		_tween.kill()


func squash(strength := 0.2, time := 0.18) -> void:
	var t := create_tween()
	scale = Vector2(1.0 + strength, 1.0 - strength)
	t.tween_property(self, "scale", Vector2.ONE, time).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
