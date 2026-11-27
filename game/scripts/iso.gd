# Изометрическая проекция 2:1 (та же, что в tools/iso.py).
#   экран = ORIGIN + (x - y, (x + y) / 2 - z)
# x — вдоль правой стены, y — вдоль левой, z — вверх.
class_name Iso
extends RefCounted

const Art := preload("res://scripts/art_data.gd")


static func to_screen(p: Vector3) -> Vector2:
	return Art.ORIGIN + Vector2(p.x - p.y, (p.x + p.y) * 0.5 - p.z)


# Точка на экране -> точка на горизонтальной плоскости высоты z.
static func to_world(s: Vector2, z: float) -> Vector2:
	var u := s.x - Art.ORIGIN.x
	var v := s.y - Art.ORIGIN.y
	return Vector2((u + 2.0 * (v + z)) * 0.5, (2.0 * (v + z) - u) * 0.5)


# Порядок отрисовки: дальше от зрителя — раньше.
static func depth(p: Vector3) -> int:
	return int(p.x + p.y)
