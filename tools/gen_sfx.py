"""Синтез звуков и фоновой музыки (без внешних сэмплов).

Запуск из корня репозитория:
    python3 tools/gen_sfx.py

Пишет WAV (22050 Гц, моно, 16 бит) в game/assets/sfx/.
"""
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "game", "assets", "sfx")
SR = 22050
rng = np.random.default_rng(7)


def t(dur):
    return np.arange(int(dur * SR)) / SR


def env(dur, attack=0.003, decay=0.1):
    x = t(dur)
    a = np.minimum(x / attack, 1.0)
    return a * np.exp(-x / decay)


def tone(freqs, dur, decay, amps=None, attack=0.002):
    x = t(dur)
    amps = amps or [1.0] * len(freqs)
    s = sum(a * np.sin(2 * np.pi * f * x) for f, a in zip(freqs, amps))
    return s * env(dur, attack, decay)


def noise(dur):
    return rng.uniform(-1, 1, int(dur * SR))


def lowpass(s, k):
    """Скользящее среднее по k отсчётам — мягкий фильтр низких частот."""
    if k <= 1:
        return s
    c = np.cumsum(np.concatenate([np.zeros(k), s]))
    return (c[k:] - c[:-k]) / k


def highpass(s, k):
    return s - lowpass(s, k)


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[: len(p)] += p
    return out


def delay(s, sec):
    return np.concatenate([np.zeros(int(sec * SR)), s])


def save(name, s, peak=0.7):
    s = s / (np.max(np.abs(s)) + 1e-9) * peak
    # мягкие края, чтобы не щёлкало
    fade = min(len(s) // 4, int(0.004 * SR))
    if fade > 0:
        s[:fade] *= np.linspace(0, 1, fade)
        s[-fade:] *= np.linspace(1, 0, fade)
    data = (s * 32767).astype(np.int16)
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def click(dur=0.012, k=3):
    return lowpass(noise(dur), k) * env(dur, 0.0005, dur / 4)


def thud(freq=90, dur=0.18):
    x = t(dur)
    f = freq * (1 + 0.6 * np.exp(-x / 0.02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(dur, 0.002, dur / 4)


# ---------------------------------------------------------------- эффекты

def sfx():
    # материалы: стук при постановке
    save("place_wood", mix(thud(170, 0.16) * 0.8, tone([340, 690], 0.12, 0.03, [0.4, 0.15]), click(0.01, 4) * 0.6), 0.6)
    save("place_ceramic", mix(tone([1480, 2950, 4120], 0.35, 0.07, [1, 0.45, 0.25]), click(0.008, 2) * 0.5, thud(220, 0.08) * 0.4), 0.5)
    save("place_glass", mix(tone([2630, 4410, 6080], 0.4, 0.09, [1, 0.5, 0.3]), click(0.006, 1) * 0.3), 0.4)
    save("place_metal", mix(tone([523, 1309, 2154, 3340], 0.7, 0.18, [1, 0.6, 0.35, 0.2]), thud(140, 0.1) * 0.5), 0.45)
    save("place_soft", mix(thud(95, 0.16), lowpass(noise(0.12), 12) * env(0.12, 0.005, 0.03) * 1.5), 0.55)
    save("place_paper", mix(highpass(noise(0.14), 3) * env(0.14, 0.01, 0.04), thud(130, 0.08) * 0.5), 0.45)
    save("place_plastic", mix(tone([720, 1630], 0.1, 0.025, [1, 0.5]), click(0.008, 2) * 0.6, thud(160, 0.07) * 0.5), 0.5)
    save("place_plant", mix(thud(110, 0.14), highpass(noise(0.2), 2) * env(0.2, 0.02, 0.05) * 0.4, tone([300], 0.1, 0.03, [0.3])), 0.55)

    # взять предмет
    save("pick", mix(click(0.01, 2), tone([1250], 0.05, 0.012, [0.5])), 0.35)
    # предмет «выпрыгивает» из коробки
    x = t(0.12)
    f = 380 + 700 * (x / 0.12) ** 0.7
    pop = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.12, 0.003, 0.04)
    save("pop", mix(pop, lowpass(noise(0.05), 6) * env(0.05, 0.001, 0.01) * 0.4), 0.45)
    # открыть коробку: треск скотча и хлопок створок
    rip = highpass(noise(0.28), 2) * (0.6 + 0.4 * np.sin(2 * np.pi * 37 * t(0.28)) ** 2) * env(0.28, 0.01, 0.12)
    save("box_open", mix(rip * 0.8, delay(thud(120, 0.15), 0.22), delay(lowpass(noise(0.1), 8) * env(0.1, 0.002, 0.03), 0.22)), 0.6)
    # сложить коробку
    save("box_fold", mix(thud(100, 0.15), delay(thud(140, 0.12) * 0.8, 0.1), lowpass(noise(0.25), 5) * env(0.25, 0.01, 0.06) * 0.6), 0.6)
    # коробка занята: глухой стук
    save("bump", mix(thud(80, 0.12), click(0.01, 6) * 0.3), 0.4)
    # дверцы
    swoosh = lowpass(noise(0.3), 18) * env(0.3, 0.08, 0.1)
    save("door_open", mix(click(0.012, 3) * 0.6, delay(swoosh, 0.02) * 1.2, tone([196], 0.2, 0.06, [0.2])), 0.5)
    save("door_close", mix(thud(85, 0.2), click(0.012, 3) * 0.5, lowpass(noise(0.08), 10) * env(0.08, 0.002, 0.02)), 0.6)
    # не на месте: два мягких тона вниз
    save("wrong", mix(tone([523, 1046], 0.3, 0.12, [1, 0.2], 0.01), delay(tone([392, 784], 0.4, 0.15, [1, 0.2], 0.01), 0.18)), 0.35)
    # «голос» в диалоге: короткий мягкий бип
    save("blip", mix(tone([660, 1320], 0.045, 0.014, [1, 0.25], 0.002)), 0.4)
    # уровень пройден: колокольчики
    notes = [523.25, 659.25, 783.99, 1046.5, 1318.5]
    chime = mix(*[delay(tone([f, f * 2.01, f * 3.0], 1.4, 0.4, [1, 0.3, 0.1], 0.004), i * 0.11) for i, f in enumerate(notes)])
    pad = tone([261.63, 329.63, 392.0], 1.9, 0.9, [0.3, 0.25, 0.25], 0.15)
    save("complete", mix(chime, pad), 0.55)


# ---------------------------------------------------------------- музыка

def note_hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def epiano(freq, dur, vel=1.0):
    x = t(dur)
    s = np.sin(2 * np.pi * freq * x) + 0.25 * np.sin(2 * np.pi * freq * 2 * x) * np.exp(-x / 0.3)
    s += 0.08 * np.sin(2 * np.pi * freq * 3.01 * x) * np.exp(-x / 0.15)
    return s * env(dur, 0.006, 0.9) * vel


def music():
    bpm = 72
    beat = 60 / bpm
    bars = 8
    total = int(bars * 4 * beat * SR)
    out = np.zeros(total + SR * 4)
    # Fmaj7 — Em7 — Dm7 — Cmaj7 (по два такта), спокойная прогрессия
    chords = [
        [53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59],
    ]
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]  # порядок нот арпеджио по восьмым
    for bar in range(bars):
        ch = chords[(bar // 2) % 4]
        start_bar = bar * 4 * beat
        # бас
        b = epiano(note_hz(ch[0] - 12), 3.6, 0.55)
        i0 = int(start_bar * SR)
        out[i0:i0 + len(b)] += b
        # пэд
        pad = sum(np.sin(2 * np.pi * note_hz(n) * t(4 * beat)) for n in ch) * 0.05
        pad *= np.minimum(t(4 * beat) / 0.6, 1) * np.minimum((4 * beat - t(4 * beat)) / 0.6, 1)
        out[i0:i0 + len(pad)] += pad
        # арпеджио на октаву выше, с лёгкими вариациями
        for k, idx in enumerate(pattern):
            if bar % 2 == 1 and k in (5, 7):
                continue
            n = ch[idx] + 12
            vel = 0.32 if k % 2 == 0 else 0.22
            s = epiano(note_hz(n), 1.6, vel)
            j = int((start_bar + k * beat / 2) * SR)
            out[j:j + len(s)] += s
        # мелодия: редкие ноты сверху
        if bar % 2 == 0:
            m = epiano(note_hz(ch[3] + 24), 2.5, 0.16)
            j = int((start_bar + 2.5 * beat) * SR)
            out[j:j + len(m)] += m
    # хвосты нот переносим в начало — петля без шва
    loop = out[:total].copy()
    tail = out[total:]
    loop[: len(tail)] += tail
    loop = lowpass(loop, 3)
    save("music", loop, 0.32)


if __name__ == "__main__":
    sfx()
    music()
    print("ok")
