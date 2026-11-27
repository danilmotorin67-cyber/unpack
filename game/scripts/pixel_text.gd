# Текст пиксельным шрифтом 5×7 (кириллица заглавными).
# Рисует строку по центру относительно своей позиции (или от левого края).
class_name PixelText
extends Node2D

const FontData := preload("res://scripts/font_data.gd")
const FONT_TEX := preload("res://assets/font/font.png")
const SPACING := 1

@export var text := "":
	set(value):
		text = value.to_upper()
		queue_redraw()
@export var color := Color("fbf5e9")
@export var shadow_color := Color("2e2430")
@export var shadow := true
@export var centered := true


func text_width() -> int:
	var w := 0
	for ch in text:
		var g: Vector2i = FontData.GLYPHS.get(ch, FontData.GLYPHS["?"])
		w += g.y + SPACING
	return max(w - SPACING, 0)


func _draw() -> void:
	var x := -text_width() / 2 if centered else 0
	for ch in text:
		var g: Vector2i = FontData.GLYPHS.get(ch, FontData.GLYPHS["?"])
		var src := Rect2(g.x, 0, g.y, FontData.HEIGHT)
		if shadow:
			draw_texture_rect_region(FONT_TEX, Rect2(x, 1, g.y, FontData.HEIGHT), src, shadow_color)
		draw_texture_rect_region(FONT_TEX, Rect2(x, 0, g.y, FontData.HEIGHT), src, color)
		x += g.y + SPACING
