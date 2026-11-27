"""Мини-рендерер изометрического пиксель-арта.

Сцена — набор примитивов (короб, вертикальный цилиндр, сфера) в мировых
координатах: x — вдоль правой стены (на экране вправо-вниз), y — вдоль левой
стены (влево-вниз), z — вверх. Проекция 2:1:

    sx = x - y
    sy = (x + y) / 2 - z

Луч зрения идёт вдоль (1, 1, 1), «глубина» (ближе к зрителю) = x + y + z.
Каждый пиксель трассируется до ближайшего примитива. Цвет выбирается из
палитры по ориентации грани (верх / левая / правая) и текстуре примитива,
потом добавляются контуры (силуэт) и блики на рёбрах.
"""
import numpy as np
from PIL import Image

from palette import PALETTE, rgba

KEYS = list(PALETTE.keys())
KEY_INDEX = {k: i for i, k in enumerate(KEYS)}
RGBA = np.array([rgba(k) for k in KEYS], dtype=np.uint8)

FACE_RIGHT, FACE_LEFT, FACE_TOP = 0, 1, 2  # +x, +y, +z


def project(x, y, z):
    return x - y, (x + y) / 2.0 - z


class Mat:
    """Тона материала: hi — блик на ребре, top/left/right — грани, edge — контур."""

    def __init__(self, top, left, right, edge="o", hi=None):
        self.top, self.left, self.right, self.edge, self.hi = top, left, right, edge, hi


class Prim:
    def __init__(self, kind, mat, tex=None, **p):
        self.kind, self.mat, self.tex, self.p = kind, mat, tex, p

    def bounds(self):
        p = self.p
        if self.kind == "box":
            return p["x0"], p["y0"], p["z0"], p["x1"], p["y1"], p["z1"]
        if self.kind == "cyl":
            r = p["r"]
            return p["cx"] - r, p["cy"] - r, p["z0"], p["cx"] + r, p["cy"] + r, p["z1"]
        r = p["r"]
        return p["cx"] - r, p["cy"] - r, p["cz"] - r, p["cx"] + r, p["cy"] + r, p["cz"] + r


def box(x0, y0, z0, x1, y1, z1, mat, tex=None):
    return Prim("box", mat, tex, x0=x0, y0=y0, z0=z0, x1=x1, y1=y1, z1=z1)


def cyl(cx, cy, r, z0, z1, mat, tex=None):
    return Prim("cyl", mat, tex, cx=cx, cy=cy, r=r, z0=z0, z1=z1)


def sphere(cx, cy, cz, r, mat, tex=None, zmax=None, cap=None):
    return Prim("sph", mat, tex, cx=cx, cy=cy, cz=cz, r=r, zmax=zmax, cap=cap)


# ------------------------------------------------------------------ trace

def _intersect(pr, x0, y0):
    """Возвращает t (глубина вдоль луча, z = t), маску попадания и
    нормаль (nx, ny, nz) для лучей P(t) = (x0 + t, y0 + t, t)."""
    p = pr.p
    n = x0.shape
    if pr.kind == "box":
        ex = p["x1"] - x0
        ey = p["y1"] - y0
        ez = np.full(n, float(p["z1"]))
        t_hi = np.minimum(np.minimum(ex, ey), ez)
        t_lo = np.maximum(np.maximum(p["x0"] - x0, p["y0"] - y0), float(p["z0"]))
        hit = t_lo <= t_hi
        face = np.argmin(np.stack([ex, ey, ez]), axis=0)
        nx = (face == 0).astype(float)
        ny = (face == 1).astype(float)
        nz = (face == 2).astype(float)
        return t_hi, hit, (nx, ny, nz)
    if pr.kind == "cyl":
        a = x0 - p["cx"]
        b = y0 - p["cy"]
        r = p["r"]
        # верхняя крышка
        tt = float(p["z1"])
        top = (a + tt) ** 2 + (b + tt) ** 2 <= r * r
        # боковая поверхность
        disc = (a + b) ** 2 - 2 * (a * a + b * b - r * r)
        side_ok = disc >= 0
        ts = (-(a + b) + np.sqrt(np.maximum(disc, 0))) / 2
        side = side_ok & (ts >= p["z0"]) & (ts <= p["z1"])
        t = np.where(top, tt, ts)
        hit = top | side
        nx = np.where(top, 0.0, (a + ts) / r)
        ny = np.where(top, 0.0, (b + ts) / r)
        nz = np.where(top, 1.0, 0.0)
        return t, hit, (nx, ny, nz)
    # сфера
    dx = x0 - p["cx"]
    dy = y0 - p["cy"]
    dz = -float(p["cz"])
    r = p["r"]
    s = dx + dy + dz
    c = dx * dx + dy * dy + dz * dz - r * r
    disc = s * s - 3 * c
    ok = disc >= 0
    t = (-s + np.sqrt(np.maximum(disc, 0))) / 3
    hit = ok.copy()
    nx, ny, nz = (dx + t) / r, (dy + t) / r, (dz + t) / r
    if p.get("zmax") is not None:
        zm = p["zmax"]
        above = t > zm
        # срез: видим «крышку» (внутренность) на плоскости z = zmax
        rc2 = r * r - (zm - p["cz"]) ** 2
        capin = (dx + zm) ** 2 + (dy + zm) ** 2 <= rc2
        cap = above & capin
        hit = (ok & ~above) | cap
        t = np.where(cap, zm, t)
        nz = np.where(cap, 2.0, nz)  # 2.0 — маркер «внутренности»
        nx = np.where(cap, 0.0, nx)
        ny = np.where(cap, 0.0, ny)
    return t, hit, (nx, ny, nz)


def _shade(mat, nx, ny, nz, curved):
    """Тон по нормали: верх светлый, левая грань средняя, правая тёмная.
    У круглых предметов слева добавляется светлая полоса-блик."""
    out = np.empty(nx.shape, dtype=object)
    top = nz > 0.6
    s = ny - nx
    out[:] = mat.left
    out[s <= -0.45] = mat.right
    if curved:
        out[(s > 0.8) & ~top] = mat.top
    out[top] = mat.top
    face = np.where(top, FACE_TOP, np.where(s > 0.05, FACE_LEFT, FACE_RIGHT))
    return out, face


class Canvas:
    def __init__(self, w, h, origin):
        self.w, self.h = w, h
        self.ox, self.oy = origin
        self.depth = np.full((h, w), -np.inf)
        self.key = np.full((h, w), -1, dtype=int)
        self.pid = np.full((h, w), -1, dtype=int)
        self.face = np.full((h, w), -1, dtype=int)
        self.prims = []

    def add(self, prims):
        for pr in prims if isinstance(prims, list) else [prims]:
            self._draw(pr)

    def _draw(self, pr):
        pid = len(self.prims)
        self.prims.append(pr)
        x0, y0, z0, x1, y1, z1 = pr.bounds()
        xs, ys = [], []
        for X in (x0, x1):
            for Y in (y0, y1):
                for Z in (z0, z1):
                    a, b = project(X, Y, Z)
                    xs.append(a)
                    ys.append(b)
        px0 = max(int(np.floor(min(xs) + self.ox)) - 1, 0)
        px1 = min(int(np.ceil(max(xs) + self.ox)) + 1, self.w)
        py0 = max(int(np.floor(min(ys) + self.oy)) - 1, 0)
        py1 = min(int(np.ceil(max(ys) + self.oy)) + 1, self.h)
        if px0 >= px1 or py0 >= py1:
            return
        gy, gx = np.mgrid[py0:py1, px0:px1]
        sx = gx + 0.5 - self.ox
        sy = gy + 0.5 - self.oy
        rx = sy + sx / 2
        ry = sy - sx / 2
        t, hit, (nx, ny, nz) = _intersect(pr, rx, ry)
        depth = rx + ry + 3 * t
        cur = self.depth[py0:py1, px0:px1]
        win = hit & (depth > cur)
        if not win.any():
            return
        keys, face = _shade(pr.mat, nx, ny, nz, pr.kind != "box")
        if pr.tex is not None:
            X = rx + t
            Y = ry + t
            Z = t
            for idx in zip(*np.nonzero(win)):
                k = pr.tex(X[idx], Y[idx], Z[idx], int(face[idx]), keys[idx], nz[idx])
                if k is not None:
                    keys[idx] = k
        kidx = np.vectorize(KEY_INDEX.get)(keys)
        sl = (slice(py0, py1), slice(px0, px1))
        self.depth[sl] = np.where(win, depth, cur)
        self.key[sl] = np.where(win, kidx, self.key[sl])
        self.pid[sl] = np.where(win, pid, self.pid[sl])
        self.face[sl] = np.where(win, face, self.face[sl])

    # -------------------------------------------------------------- post

    def finish(self, edges=True, creases=True, edge_t=4.0):
        key = self.key.copy()
        d, pid, face = self.depth, self.pid, self.face
        H, W = d.shape
        filled = pid >= 0
        if creases:
            # верхняя грань над боковой гранью того же примитива — светлое ребро
            below_pid = np.full_like(pid, -1)
            below_pid[:-1] = pid[1:]
            below_face = np.full_like(face, -1)
            below_face[:-1] = face[1:]
            mask = filled & (face == FACE_TOP) & (below_pid == pid) & (below_face != FACE_TOP)
            for y, x in zip(*np.nonzero(mask)):
                hi = self.prims[pid[y, x]].mat.hi
                if hi:
                    key[y, x] = KEY_INDEX[hi]
        if edges:
            far = np.zeros_like(filled)
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nd = np.full_like(d, -np.inf)
                ys = slice(max(dy, 0), H + min(dy, 0))
                yd = slice(max(-dy, 0), H + min(-dy, 0))
                xs = slice(max(dx, 0), W + min(dx, 0))
                xd = slice(max(-dx, 0), W + min(-dx, 0))
                nd[yd, xd] = d[ys, xs]
                far |= nd < d - edge_t
            mask = filled & far
            for y, x in zip(*np.nonzero(mask)):
                e = self.prims[pid[y, x]].mat.edge
                if e:
                    key[y, x] = KEY_INDEX[e]
        self.final = key
        return self

    def image(self):
        img = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        m = self.final >= 0
        img[m] = RGBA[self.final[m]]
        return Image.fromarray(img, "RGBA")


def render_sprite(prims, outline="o", size=160):
    """Рендерит объект вокруг мирового начала координат в спрайт.
    Возвращает (image, anchor) — anchor = пиксель проекции точки (0,0,0)."""
    cv = Canvas(size, size, (size // 2, size // 2 + size // 4))
    cv.add(prims)
    cv.finish()
    img = cv.image()
    a = np.array(img)
    alpha = a[..., 3] > 0
    if outline:
        grown = alpha.copy()
        grown[1:] |= alpha[:-1]
        grown[:-1] |= alpha[1:]
        grown[:, 1:] |= alpha[:, :-1]
        grown[:, :-1] |= alpha[:, 1:]
        ring = grown & ~alpha
        a[ring] = rgba(outline)
        alpha = grown
    ys, xs = np.nonzero(alpha)
    x0, x1, y0, y1 = xs.min() - 1, xs.max() + 2, ys.min() - 1, ys.max() + 2  # +1px рамка для шейдера
    crop = Image.fromarray(a, "RGBA").crop((x0, y0, x1, y1))
    anchor = (size // 2 - x0, size // 2 + size // 4 - y0)
    return crop, anchor
