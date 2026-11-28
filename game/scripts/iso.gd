# Изометрическая проекция 2:1 (та же, что в tools/iso.py).
#   экран = ORIGIN + PX * (x - y, (x + y) / 2 - z)
# x — вдоль правой стены, y — вдоль левой, z — вверх.
class_name Iso
extends RefCounted

const Art := preload("res://scripts/art_data.gd")


static func to_screen(p: Vector3) -> Vector2:
	return Art.ORIGIN + Art.PX * Vector2(p.x - p.y, (p.x + p.y) * 0.5 - p.z)


# Точка на экране -> точка на горизонтальной плоскости высоты z.
static func to_world(s: Vector2, z: float) -> Vector2:
	var u := (s.x - Art.ORIGIN.x) / Art.PX
	var v := (s.y - Art.ORIGIN.y) / Art.PX
	return Vector2((u + 2.0 * (v + z)) * 0.5, (2.0 * (v + z) - u) * 0.5)


# Точка на экране -> точка на стене. side "L" — плоскость x=0, вернёт (y, z);
# "R" — плоскость y=0, вернёт (x, z).
static func to_wall(s: Vector2, side: String) -> Vector2:
	var u := (s.x - Art.ORIGIN.x) / Art.PX
	var v := (s.y - Art.ORIGIN.y) / Art.PX
	if side == "L":
		var y := -u
		return Vector2(y, y * 0.5 - v)
	return Vector2(u, u * 0.5 - v)


# Порядок отрисовки: дальше от зрителя — раньше.
static func depth(p: Vector3) -> int:
	return int(p.x + p.y)
