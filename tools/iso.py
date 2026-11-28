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

from palette import PALETTE, RAMP_OF, rgba, shift

KEYS = list(PALETTE.keys())
KEY_INDEX = {k: i for i, k in enumerate(KEYS)}
RGBA = np.array([rgba(k) for k in KEYS], dtype=np.uint8)

FACE_RIGHT, FACE_LEFT, FACE_TOP = 0, 1, 2  # +x, +y, +z


# Пикселей экрана на единицу мира по оси экрана (детализация арта).
PX = 4.0 / 3.0


def project(x, y, z):
    return PX * (x - y), PX * ((x + y) / 2.0 - z)


class Mat:
    """Тона материала: hi — блик на ребре, top/left/right — грани, edge — контур."""

    def __init__(self, top, left, right, edge="o", hi=None, gloss=False):
        self.top, self.left, self.right, self.edge, self.hi = top, left, right, edge, hi
        self.gloss = gloss  # глянец: блик на круглых поверхностях


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


# ------------------------------------------------------------------ свет

def _norm(v):
    v = np.array(v, dtype=float)
    return v / np.linalg.norm(v)


LIGHT_DIFFUSE = _norm((-0.3, 0.7, 0.9))   # для плавного освещения круглых форм
LIGHT_SHADOW = _norm((-0.22, 0.4, 1.0))   # откуда падают тени (сверху, чуть слева)
VIEW = _norm((1, 1, 1))
HALF = _norm(LIGHT_DIFFUSE + VIEW)
AO_RADIUS = 7.0
# направления для AO: равномерно по сфере, лишние отбрасываются по нормали
_g = (1 + 5 ** 0.5) / 2
AO_DIRS = []
for _i in range(24):
    _z = 1 - (2 * _i + 1) / 24
    _r = (1 - _z * _z) ** 0.5
    _a = 2 * np.pi * _i / _g
    AO_DIRS.append((_r * np.cos(_a), _r * np.sin(_a), _z))
AO_DIRS = np.array(AO_DIRS)


def _ray_hits(pr, O, D, tmax, eps=0.05):
    """Попадает ли луч O + tD (t в (eps, tmax)) в примитив. O, D — (n, 3)."""
    p = pr.p
    ox, oy, oz = O[:, 0], O[:, 1], O[:, 2]
    dx, dy, dz = D[:, 0], D[:, 1], D[:, 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        if pr.kind == "box":
            tn = np.full(len(O), -np.inf)
            tf = np.full(len(O), np.inf)
            for o, d, lo, hi in ((ox, dx, p["x0"], p["x1"]), (oy, dy, p["y0"], p["y1"]), (oz, dz, p["z0"], p["z1"])):
                inv = 1.0 / np.where(np.abs(d) < 1e-9, 1e-9, d)
                t1 = (lo - o) * inv
                t2 = (hi - o) * inv
                tn = np.maximum(tn, np.minimum(t1, t2))
                tf = np.minimum(tf, np.maximum(t1, t2))
            return (tn <= tf) & (tf > eps) & (tn < tmax)
        if pr.kind == "cyl":
            ax = ox - p["cx"]
            ay = oy - p["cy"]
            r = p["r"]
            a = dx * dx + dy * dy
            b = 2 * (ax * dx + ay * dy)
            c = ax * ax + ay * ay - r * r
            disc = b * b - 4 * a * c
            ok = (disc >= 0) & (a > 1e-9)
            sq = np.sqrt(np.maximum(disc, 0))
            hit = np.zeros(len(O), dtype=bool)
            for t in ((-b - sq) / (2 * a), (-b + sq) / (2 * a)):
                z = oz + t * dz
                hit |= ok & (t > eps) & (t < tmax) & (z >= p["z0"]) & (z <= p["z1"])
            for zc in (p["z0"], p["z1"]):
                t = (zc - oz) / np.where(np.abs(dz) < 1e-9, 1e-9, dz)
                xx = ax + t * dx
                yy = ay + t * dy
                hit |= (t > eps) & (t < tmax) & (xx * xx + yy * yy <= r * r)
            return hit
        cx, cy, cz = O[:, 0] - p["cx"], O[:, 1] - p["cy"], O[:, 2] - p["cz"]
        b = cx * dx + cy * dy + cz * dz
        c = cx * cx + cy * cy + cz * cz - p["r"] ** 2
        disc = b * b - c
        sq = np.sqrt(np.maximum(disc, 0))
        hit = np.zeros(len(O), dtype=bool)
        for t in (-b - sq, -b + sq):
            hit |= (disc >= 0) & (t > eps) & (t < tmax)
        return hit


def _occluded(prims, O, D, tmax):
    """Маска: луч упирается хоть во что-то. Примитивы далеко от точек пропускаем."""
    out = np.zeros(len(O), dtype=bool)
    lo = O.min(axis=0) - tmax
    hi = O.max(axis=0) + tmax
    for pr in prims:
        b = pr.bounds()
        if b[0] > hi[0] or b[3] < lo[0] or b[1] > hi[1] or b[4] < lo[1] or b[2] > hi[2] or b[5] < lo[2]:
            continue
        todo = ~out
        if not todo.any():
            break
        out[todo] |= _ray_hits(pr, O[todo], D[todo], tmax)
    return out


def _curved_keys(mat, nx, ny, nz):
    """Плавный тон по нормали вдоль рампы материала (вместо трёх полос)."""
    if mat.left not in RAMP_OF:
        return None
    ramp, il = RAMP_OF[mat.left]
    rt = RAMP_OF.get(mat.top)
    rr = RAMP_OF.get(mat.right)
    if rt is None or rr is None or rt[0] is not ramp or rr[0] is not ramp:
        return None
    it, ir = rt[1], rr[1]
    L = LIGHT_DIFFUSE
    dT, dL, dR = L[2], L[1], L[0]
    d = nx * L[0] + ny * L[1] + nz * L[2]
    up = il + (d - dL) / (dT - dL) * (it - il)
    down = ir + (d - dR) / (dL - dR) * (il - ir)
    idx = np.where(d >= dL, up, down)
    idx = np.clip(np.round(idx), max(ir - 1, 0), min(it + 1, len(ramp) - 1)).astype(int)
    if mat.gloss:
        spec = (nx * HALF[0] + ny * HALF[1] + nz * HALF[2]) > 0.93
        idx = np.where(spec, len(ramp) - 1, idx)
    out = np.empty(nx.shape, dtype=object)
    for i, k in enumerate(ramp):
        out[idx == i] = k
    return out


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
        self.pos = np.zeros((h, w, 3))
        self.nrm = np.zeros((h, w, 3))
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
        sx = (gx + 0.5 - self.ox) / PX
        sy = (gy + 0.5 - self.oy) / PX
        rx = sy + sx / 2
        ry = sy - sx / 2
        t, hit, (nx, ny, nz) = _intersect(pr, rx, ry)
        depth = rx + ry + 3 * t
        cur = self.depth[py0:py1, px0:px1]
        win = hit & (depth > cur)
        if not win.any():
            return
        keys, face = _shade(pr.mat, nx, ny, nz, pr.kind != "box")
        if pr.kind != "box":
            smooth = _curved_keys(pr.mat, nx, ny, np.where(nz > 1.5, 1.0, nz))
            if smooth is not None:
                keys = np.where(nz > 1.5, keys, smooth)
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
        P = np.stack([rx + t, ry + t, t], axis=-1)
        N = np.stack([nx, ny, np.where(nz > 1.5, 1.0, nz)], axis=-1)
        self.pos[sl] = np.where(win[..., None], P, self.pos[sl])
        self.nrm[sl] = np.where(win[..., None], N, self.nrm[sl])

    # -------------------------------------------------------------- post

    def light(self, ao=True, shadows=True, extra=()):
        """Тени и AO: сдвигают тон пикселя вниз по его рампе.
        extra — дополнительные примитивы, которые отбрасывают тень, но не рисуются."""
        ys, xs = np.nonzero(self.pid >= 0)
        if len(ys) == 0:
            return self
        P = self.pos[ys, xs]
        N = self.nrm[ys, xs]
        O = P + N * 0.08
        prims = list(self.prims) + list(extra)
        dark = np.zeros(len(ys), dtype=int)
        if shadows:
            Ls = np.broadcast_to(LIGHT_SHADOW, P.shape)
            facing = (N @ LIGHT_SHADOW) > 0.05
            sh = np.zeros(len(ys), dtype=bool)
            sh[facing] = _occluded(prims, O[facing], Ls[facing], 120.0)
            dark += sh.astype(int)
        if ao:
            hits = np.zeros(len(ys))
            count = np.zeros(len(ys))
            for d in AO_DIRS:
                cosn = N @ d
                use = cosn > 0.15
                if not use.any():
                    continue
                D = np.broadcast_to(d, P.shape)
                h = _occluded(prims, O[use], D[use], AO_RADIUS)
                hits[use] += h * cosn[use]
                count[use] += cosn[use]
            occ = hits / np.maximum(count, 1e-6)
            dark += (occ > 0.28).astype(int) + (occ > 0.55).astype(int)
        dark = np.minimum(dark, 2)
        for y, x, n in zip(ys[dark > 0], xs[dark > 0], dark[dark > 0]):
            self.key[y, x] = KEY_INDEX[shift(KEYS[self.key[y, x]], -int(n))]
        return self

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
                if self.prims[pid[y, x]].mat.hi:
                    key[y, x] = KEY_INDEX[shift(KEYS[self.key[y, x]], 1)]
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
                if self.prims[pid[y, x]].mat.edge:
                    k = KEYS[self.key[y, x]]
                    # контур — на два тона темнее; если тон уже самый тёмный
                    # в рампе, темнее некуда — берём общий тёмный контур
                    _, idx = RAMP_OF[k]
                    key[y, x] = KEY_INDEX["o" if idx == 0 and k != "o" else shift(k, -2)]
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
    cv.light(shadows=False)
    cv.finish()
    img = cv.image()
    a = np.array(img)
    alpha = a[..., 3] > 0
    if outline:
        # цветной контур: самый тёмный тон рампы соседнего пикселя
        # (снизу и справа — ещё и тёмный общий контур, чтобы вещь «стояла»)
        fin = cv.final
        H, W = alpha.shape
        ring = np.zeros_like(alpha)
        src = np.full(alpha.shape, -1)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.full(alpha.shape, -1)
            ys = slice(max(dy, 0), H + min(dy, 0))
            yd = slice(max(-dy, 0), H + min(-dy, 0))
            xs = slice(max(dx, 0), W + min(dx, 0))
            xd = slice(max(-dx, 0), W + min(-dx, 0))
            sh[yd, xd] = fin[ys, xs]
            take = (~alpha) & (sh >= 0) & (src < 0)
            src[take] = sh[take]
            ring |= take
        below = np.zeros_like(alpha)
        below[:-1] = alpha[1:]
        left = np.zeros_like(alpha)
        left[:, 1:] = alpha[:, :-1]
        for y, x in zip(*np.nonzero(ring)):
            k = KEYS[src[y, x]]
            ramp, _ = RAMP_OF[k]
            # сверху-слева — тёмный тон материала, снизу-справа — общий тёмный контур
            a[y, x] = rgba(ramp[0]) if (below[y, x] and not left[y, x]) else rgba(outline)
        alpha = alpha | ring
    ys, xs = np.nonzero(alpha)
    x0, x1, y0, y1 = xs.min() - 1, xs.max() + 2, ys.min() - 1, ys.max() + 2  # +1px рамка для шейдера
    crop = Image.fromarray(a, "RGBA").crop((x0, y0, x1, y1))
    anchor = (size // 2 - x0, size // 2 + size // 4 - y0)
    return crop, anchor
