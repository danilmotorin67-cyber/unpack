# Базовый спрайт: точка опоры (anchor) задаётся генератором арта,
# попадание мыши — попиксельное, обводка — шейдером.
class_name PixelSprite
extends Sprite2D

const OUTLINE_SHADER := preload("res://shaders/outline.gdshader")
const COLOR_HOVER := Color("fbf5e9")
const COLOR_WRONG := Color("c8664f")

var _image: Image
var _tween: Tween


func _init() -> void:
	centered = false
	material = ShaderMaterial.new()
	material.shader = OUTLINE_SHADER


# anchor — пиксель спрайта, который совпадает с position
func set_tex(tex: Texture2D, anchor: Vector2) -> void:
	texture = tex
	_image = tex.get_image()
	offset = -anchor


func hit(global_point: Vector2) -> bool:
	if not visible or _image == null or scale.x == 0.0 or scale.y == 0.0:
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
