# Звуки и фоновая музыка. Пул плееров, лёгкий разброс высоты тона,
# чтобы одинаковые звуки не звучали механически.
class_name Sfx
extends Node

const NAMES := [
	"place_wood", "place_ceramic", "place_glass", "place_metal", "place_soft",
	"place_paper", "place_plastic", "place_plant", "pick", "pop", "box_open",
	"box_fold", "bump", "door_open", "door_close", "wrong", "complete", "blip",
]
const POOL := 8

var _streams := {}
var _players: Array[AudioStreamPlayer] = []
var _next := 0
var music: AudioStreamPlayer


func _ready() -> void:
	for n in NAMES:
		_streams[n] = load("res://assets/sfx/%s.wav" % n)
	for i in POOL:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_players.append(p)
	music = AudioStreamPlayer.new()
	var m: AudioStreamWAV = load("res://assets/sfx/music.wav")
	m.loop_mode = AudioStreamWAV.LOOP_FORWARD
	m.loop_begin = 0
	m.loop_end = int(m.get_length() * m.mix_rate)
	music.stream = m
	music.volume_db = -8.0
	add_child(music)
	music.play()


func play(name: String, volume_db := 0.0, pitch_var := 0.06) -> void:
	if not _streams.has(name):
		return
	var p := _players[_next]
	_next = (_next + 1) % POOL
	p.stream = _streams[name]
	p.volume_db = volume_db
	p.pitch_scale = 1.0 + randf_range(-pitch_var, pitch_var)
	p.play()


func toggle_music() -> void:
	music.stream_paused = not music.stream_paused
