// Обводка в 1 пиксель вокруг непрозрачных пикселей спрайта.
// Спрайты сгенерированы с прозрачной рамкой в 1px, поэтому обводка помещается.
shader_type canvas_item;

uniform bool enabled = false;
uniform vec4 outline_color : source_color = vec4(0.984, 0.961, 0.914, 1.0);

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (enabled && c.a < 0.5) {
		vec2 p = TEXTURE_PIXEL_SIZE;
		float a = texture(TEXTURE, UV + vec2(p.x, 0.0)).a
			+ texture(TEXTURE, UV - vec2(p.x, 0.0)).a
			+ texture(TEXTURE, UV + vec2(0.0, p.y)).a
			+ texture(TEXTURE, UV - vec2(0.0, p.y)).a;
		if (a > 0.5) {
			c = outline_color;
		}
	}
	COLOR = c;
}
