#!/usr/bin/env python3
"""Generador de ejercicios: desarrollo -> figura plegada (modo a) o figura -> desarrollo (modo b).
Figuras: cubo, tetraedro, octaedro, prisma, piramide.
Temas: formas, dados, lineas, grises, colores, texturas, mixto.
"""
import argparse, itertools, math, os, random, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.path import Path

TAU = 2 * math.pi
K, W = "#151515", "#ffffff"

# ---------------------------------------------------------------- geometria 2D
def circ(cx, cy, r, n=48):
    t = np.linspace(0, TAU, n, endpoint=False)
    return np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]

def reg(n, r, rot=math.pi / 2):
    t = rot + np.arange(n) * TAU / n
    return np.c_[r * np.cos(t), r * np.sin(t)]

def star(n, R, r, rot=math.pi / 2):
    return np.array([((R if i % 2 == 0 else r) * math.cos(rot + i * math.pi / n),
                      (R if i % 2 == 0 else r) * math.sin(rot + i * math.pi / n)) for i in range(2 * n)])

def bar(x0, y0, x1, y1, w):
    p0, p1 = np.array([x0, y0], float), np.array([x1, y1], float)
    d = p1 - p0
    nrm = np.array([-d[1], d[0]]) / np.hypot(*d) * w / 2
    return np.array([p0 + nrm, p1 + nrm, p1 - nrm, p0 - nrm])

def rot2(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s], [s, c]])

# ---------------------------------------------------------------- patrones
PAT = {}      # id -> (tema, funcion -> (prims, fondo))
TEMAS = {}

def reg_pat(pid, tema, fn):
    PAT[pid] = (tema, fn)
    TEMAS.setdefault(tema, []).append(pid)

# formas
reg_pat("circulo", "formas", lambda: ([(circ(0, 0, .7), K)], W))
reg_pat("cuadrado", "formas", lambda: ([(reg(4, .62 * math.sqrt(2), math.pi / 4), K)], W))
reg_pat("triangulo", "formas", lambda: ([(reg(3, .85), K)], W))
reg_pat("hexagono", "formas", lambda: ([(reg(6, .8, 0), K)], W))
reg_pat("estrella", "formas", lambda: ([(star(5, .88, .36), K)], W))
def _flor():
    pr = [(circ(.45 * math.cos(math.pi / 2 + i * TAU / 5), .45 * math.sin(math.pi / 2 + i * TAU / 5), .27), "#555555") for i in range(5)]
    return pr + [(circ(0, 0, .22), W), (circ(0, 0, .1), K)], W
reg_pat("flor", "formas", _flor)
def _trebol():
    stem = np.array([[-.07, -.1], [.07, -.1], [.17, -.78], [-.17, -.78]])
    return [(circ(0, .4, .3), K), (circ(-.33, -.08, .3), K), (circ(.33, -.08, .3), K),
            (circ(0, .05, .24), K), (stem, K)], W
reg_pat("trebol", "formas", _trebol)
def _corazon():
    t = np.linspace(0, TAU, 80, endpoint=False)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    return [(np.c_[x, y + 2.5] / 17 * .9, K)], W
reg_pat("corazon", "formas", _corazon)
reg_pat("cruz", "formas", lambda: ([(bar(-.75, 0, .75, 0, .36), K), (bar(0, -.75, 0, .75, .36), K)], W))
reg_pat("flecha", "formas", lambda: ([(np.array([[0, .85], [.55, .1], [.22, .1], [.22, -.75], [-.22, -.75], [-.22, .1], [-.55, .1]]), K)], W))

# dados y domino
DICE = {1: [(0, 0)], 2: [(-.5, .5), (.5, -.5)], 3: [(-.5, .5), (0, 0), (.5, -.5)],
        4: [(-.5, .5), (.5, .5), (-.5, -.5), (.5, -.5)],
        5: [(-.5, .5), (.5, .5), (0, 0), (-.5, -.5), (.5, -.5)],
        6: [(-.5, .6), (-.5, 0), (-.5, -.6), (.5, .6), (.5, 0), (.5, -.6)], 0: []}
for _n in range(1, 7):
    reg_pat(f"dado{_n}", "dados", (lambda n=_n: ([(circ(x * .95, y * .95, .17), K) for x, y in DICE[n]], W)))
def _domino(a, b):
    pr = [(bar(-.85, 0, .85, 0, .08), K)]
    pr += [(circ(.38 * x, .5 + .38 * y, .1, 24), K) for x, y in DICE[a]]
    pr += [(circ(.38 * x, -.5 + .38 * y, .1, 24), K) for x, y in DICE[b]]
    return pr, W
for _a, _b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (0, 6), (2, 2), (3, 3), (0, 4)]:
    reg_pat(f"domino{_a}{_b}", "dados", (lambda a=_a, b=_b: _domino(a, b)))

# lineas
reg_pat("rayas_h", "lineas", lambda: ([(bar(-4, y, 4, y, .22), K) for y in (-.6, 0, .6)], W))
reg_pat("barra_v", "lineas", lambda: ([(bar(0, -4, 0, 4, .6), K)], W))
def _diag():
    n = np.array([-1, 1]) / math.sqrt(2); d = np.array([1, 1]) / math.sqrt(2)
    return [(bar(*(n * k * .45 - d * 4), *(n * k * .45 + d * 4), .16), K) for k in range(-8, 9)], W
reg_pat("rayas_diag", "lineas", _diag)
reg_pat("ejes", "lineas", lambda: ([(bar(-4, 0, 4, 0, .2), K), (bar(0, -4, 0, 4, .2), K)], W))
reg_pat("aspa", "lineas", lambda: ([(bar(-4, -4, 4, 4, .22), K), (bar(-4, 4, 4, -4, .22), K)], W))

# grises y colores
for _i, _g in enumerate(["#111111", "#444444", "#777777", "#a6a6a6", "#cfcfcf", "#ececec"]):
    reg_pat(f"gris{_i}", "grises", (lambda g=_g: ([], g)))
for _i, _c in enumerate(["#e53935", "#1e88e5", "#43a047", "#fdd835", "#fb8c00", "#8e24aa", "#00acc1", "#f06292", "#6d4c41"]):
    reg_pat(f"color{_i}", "colores", (lambda c=_c: ([], c)))

# texturas
reg_pat("puntos", "texturas", lambda: ([(circ(i * .4, j * .4, .1, 12), K) for i in range(-7, 8) for j in range(-7, 8)], W))
def _ajedrez():
    s = .5
    return [(np.array([[i * s, j * s], [(i + 1) * s, j * s], [(i + 1) * s, (j + 1) * s], [i * s, (j + 1) * s]]), K)
            for i in range(-6, 6) for j in range(-6, 6) if (i + j) % 2 == 0], W
reg_pat("ajedrez", "texturas", _ajedrez)
def _ondas():
    xs = np.linspace(-3.5, 3.5, 21); pr = []
    for k in range(-4, 5):
        ys = k * .55 + .2 * np.sin(2.4 * xs)
        pr += [(bar(xs[i], ys[i], xs[i + 1], ys[i + 1], .13), K) for i in range(len(xs) - 1)]
    return pr, W
reg_pat("ondas", "texturas", _ondas)
reg_pat("diana", "texturas", lambda: ([(circ(0, 0, .95, 64), K), (circ(0, 0, .75, 64), W), (circ(0, 0, .55, 64), K),
                                       (circ(0, 0, .35, 64), W), (circ(0, 0, .15, 64), K)], W))
def _ladrillos():
    pr = [(bar(-3.5, k * .5, 3.5, k * .5, .08), K) for k in range(-6, 7)]
    for k in range(-6, 6):
        off = (k % 2) * .5
        pr += [(bar(off + j, k * .5, off + j, (k + 1) * .5, .08), K) for j in range(-4, 5)]
    return pr, W
reg_pat("ladrillos", "texturas", _ladrillos)
def _rejilla():
    pr = [(bar(-3.5, i * .5, 3.5, i * .5, .1), K) for i in range(-6, 7)]
    return pr + [(bar(i * .5, -3.5, i * .5, 3.5, .1), K) for i in range(-6, 7)], W
reg_pat("rejilla", "texturas", _rejilla)

ALL_THEMES = ["formas", "dados", "lineas", "grises", "colores", "texturas"]
_cache_pat, _cache_lab = {}, {}
COLID = {}
rs = np.random.RandomState(3)
SAMP = rs.uniform(-1.5, 1.5, (2600, 2)); SAMP = SAMP[np.hypot(*SAMP.T) <= 1.5]

def pat(pid):
    if pid not in _cache_pat:
        _cache_pat[pid] = PAT[pid][1]()
    return _cache_pat[pid]

def label(pid, P):
    prims, bg = pat(pid)
    L = np.full(len(P), COLID.setdefault(bg, len(COLID)))
    for pts, col in prims:
        L[Path(pts).contains_points(P)] = COLID.setdefault(col, len(COLID))
    return L

def lab(pid, ang):
    key = (pid, round(ang % TAU, 4))
    if key not in _cache_lab:
        _cache_lab[key] = label(pid, SAMP @ rot2(ang).T)
    return _cache_lab[key]

def same(p, q, ang, tol=.006):
    return np.mean(lab(p, 0) != lab(q, ang)) < tol

_sym = {}
def sym(pid):
    """orden de simetria rotacional (0 = simetria total)."""
    if pid not in _sym:
        if same(pid, pid, TAU / 36):
            _sym[pid] = 0
        else:
            _sym[pid] = max(m for m in range(1, 13) if same(pid, pid, TAU / m))
    return _sym[pid]

EQ_ANGLES = sorted(set([i * math.radians(15) for i in range(24)] + [i * TAU / 5 for i in range(1, 5)]))
def equivalentes(p, q):
    return any(same(p, q, a) for a in EQ_ANGLES)

def choose(theme, n, rng):
    for _ in range(400):
        if theme == "mixto":
            cand = []
            while len(cand) < n:
                t = rng.choice(ALL_THEMES); p = rng.choice(TEMAS[t])
                if p not in cand: cand.append(p)
        else:
            pool = list(TEMAS[theme])
            extra = [p for t in ("texturas", "formas", "dados", "lineas") for p in TEMAS[t] if p not in pool]
            cand = rng.sample(pool, n) if len(pool) >= n else pool + rng.sample(extra, n - len(pool))
        if all(not equivalentes(a, b) for a, b in itertools.combinations(cand, 2)):
            rng.shuffle(cand)
            return cand
    raise RuntimeError("no se pudo elegir un conjunto de patrones distinguibles")

# ---------------------------------------------------------------- solidos
class Solid:
    def __init__(self, name, verts, faces, view, nombre):
        V = np.array(verts, float); self.center = V.mean(0); V = V - self.center
        self.V, self.name, self.nombre = V, name, nombre
        d = np.array(view, float); self.d = d / np.linalg.norm(d)
        self.faces = []
        for idx in faces:
            pts = V[idx]; c = pts.mean(0)
            n = np.cross(pts[1] - pts[0], pts[2] - pts[0]); n /= np.linalg.norm(n)
            if n @ c < 0: n = -n
            u = (pts[0] - c) / np.linalg.norm(pts[0] - c); v = np.cross(n, u)
            ang = [math.atan2((p - c) @ v, (p - c) @ u) for p in pts]
            order = list(np.argsort(ang)); k = order.index(0); order = order[k:] + order[:k]
            idx = [idx[i] for i in order]; pts = V[idx]
            loc = np.array([[(p - c) @ u, (p - c) @ v] for p in pts])
            cr = lambda a, b: a[0] * b[1] - a[1] * b[0]
            rin = min(abs(cr(loc[(i + 1) % len(loc)] - loc[i], -loc[i])) / np.linalg.norm(loc[(i + 1) % len(loc)] - loc[i])
                      for i in range(len(loc)))
            self.faces.append(dict(idx=idx, c=c, n=n, u=u, v=v, loc=loc, rin=rin))
        nf = len(self.faces)
        self.adj = {f: [g for g in range(nf) if g != f and len(set(self.faces[f]["idx"]) & set(self.faces[g]["idx"])) == 2]
                    for f in range(nf)}
        for f in self.faces:
            loc = f["loc"]; steps = []
            for m in range(2, 9):
                for j in range(1, m):
                    a = TAU * j / m; r = loc @ rot2(a).T
                    if all(np.min(np.hypot(*(loc - p).T)) < 1e-6 for p in r) and not any(abs(a - s) < 1e-6 for s in steps):
                        steps.append(a)
            f["steps"] = sorted(steps)
        self.group = self._group()

    def _group(self):
        V = self.V; n = len(V)
        basis = next((i, j, k) for i, j, k in itertools.permutations(range(n), 3)
                     if abs(np.linalg.det(np.array([V[i], V[j], V[k]]))) > 1e-6)
        Binv = np.linalg.inv(np.array([V[i] for i in basis]).T)
        mats = []
        for t in itertools.permutations(range(n), 3):
            M = np.array([V[i] for i in t]).T @ Binv
            if abs(np.linalg.det(M) - 1) > 1e-6 or not np.allclose(M @ M.T, np.eye(3), atol=1e-6): continue
            if not all(np.min(np.linalg.norm(V - M @ p, axis=1)) < 1e-6 for p in V): continue
            if not any(np.allclose(M, X, atol=1e-6) for X in mats): mats.append(M)
        group = []
        for M in mats:
            perm, alpha = [], []
            for f in self.faces:
                F = next(i for i, g in enumerate(self.faces) if np.linalg.norm(M @ f["c"] - g["c"]) < 1e-6)
                gu = M @ f["u"]; G = self.faces[F]
                perm.append(F); alpha.append(math.atan2(gu @ G["v"], gu @ G["u"]) % TAU)
            group.append((perm, alpha))
        return group

    def cam(self):
        d = self.d; up0 = np.array([0, 0, 1.]) if abs(d[2]) < .95 else np.array([0, 1., 0])
        right = np.cross(up0, d); right /= np.linalg.norm(right); up = np.cross(d, right)
        return right, up

def make_solids():
    s = {}
    cube_v = list(itertools.product((-1, 1), repeat=3))
    cube_f = [[i for i, v in enumerate(cube_v) if v[a] == sg] for a in range(3) for sg in (-1, 1)]
    s["cubo"] = Solid("cubo", cube_v, cube_f, (.62, .78, .9), "cubo")
    tv = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    s["tetraedro"] = Solid("tetraedro", tv, [list(c) for c in itertools.combinations(range(4), 3)], (1.1, .8, .9), "tetraedro")
    ov = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    of = [[0 if sx > 0 else 1, 2 if sy > 0 else 3, 4 if sz > 0 else 5] for sx, sy, sz in itertools.product((1, -1), repeat=3)]
    s["octaedro"] = Solid("octaedro", ov, of, (.5, .7, .9), "octaedro")
    h = .85; tri = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in (90, 210, 330)]
    pv = [(x, y, -h) for x, y in tri] + [(x, y, h) for x, y in tri]
    pf = [[0, 1, 2], [3, 4, 5], [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]]
    s["prisma"] = Solid("prisma", pv, pf, (.25, 1, .55), "prisma triangular")
    yv = [(-1, -1, -.8), (1, -1, -.8), (1, 1, -.8), (-1, 1, -.8), (0, 0, 1.1)]
    yf = [[0, 1, 2, 3], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]
    s["piramide"] = Solid("piramide", yv, yf, (.6, .8, -.5), "pirámide cuadrada")
    return s

# ---------------------------------------------------------------- desarrollos
def polys_overlap(A, B, shrink=.97):
    def sh(P): c = P.mean(0); return c + (P - c) * shrink
    A, B = sh(A), sh(B)
    for P in (A, B):
        for i in range(len(P)):
            e = P[(i + 1) % len(P)] - P[i]; n = np.array([-e[1], e[0]])
            a, b = A @ n, B @ n
            if a.max() < b.min() or b.max() < a.min(): return False
    return True

def random_net(S, rng, tries=300):
    nf = len(S.faces)
    for _ in range(tries):
        root = rng.randrange(nf); parent = {root: None}; order = [root]
        fr = [(root, g) for g in S.adj[root]]
        while len(order) < nf:
            p, c = fr.pop(rng.randrange(len(fr)))
            if c in parent: continue
            parent[c] = p; order.append(c); fr += [(c, g) for g in S.adj[c] if g not in parent]
        loc0 = S.faces[root]["loc"]; e = loc0[1] - loc0[0]
        T = {root: (-math.atan2(e[1], e[0]), np.zeros(2))}
        def place(f, q): th, t = T[f]; return rot2(th) @ q + t
        for f in order[1:]:
            p = parent[f]; fi, pi = S.faces[f]["idx"], S.faces[p]["idx"]
            a, b = [v for v in fi if v in pi]
            la = {v: S.faces[f]["loc"][i] for i, v in enumerate(fi)}
            lp = {v: S.faces[p]["loc"][i] for i, v in enumerate(pi)}
            Pa, Pb = place(p, lp[a]), place(p, lp[b]); Ca, Cb = la[a], la[b]
            th = math.atan2(*(Pb - Pa)[::-1]) - math.atan2(*(Cb - Ca)[::-1])
            T[f] = (th, Pa - rot2(th) @ Ca)
        polys = {f: S.faces[f]["loc"] @ rot2(T[f][0]).T + T[f][1] for f in range(nf)}
        if all(not polys_overlap(polys[i], polys[j]) for i, j in itertools.combinations(range(nf), 2)):
            return dict(T=T, polys=polys, key=tuple(sorted((k, -1 if v is None else v) for k, v in parent.items())))
    raise RuntimeError("no hay desarrollo valido")

# ---------------------------------------------------------------- dibujo
def draw_face(ax, poly, face, pid, ang, mapper, z=1):
    prims, bg = pat(pid)
    base = Polygon(poly, closed=True, fc=bg, ec="none", zorder=z); ax.add_patch(base)
    R = rot2(ang)
    for pts, col in prims:
        q = (pts * face["rin"]) @ R.T
        pp = Polygon(mapper(q), closed=True, fc=col, ec="none", zorder=z + .1); ax.add_patch(pp)
        pp.set_clip_path(base)
    ax.add_patch(Polygon(poly, closed=True, fc="none", ec="#222222", lw=2.2, joinstyle="round", zorder=z + .5))

def draw_net(ax, S, layout, A, half=None):
    T = layout["T"]
    for f, (pid, beta) in A.items():
        th, t = T[f]; R = rot2(th)
        draw_face(ax, layout["polys"][f], S.faces[f], pid, beta, lambda q, R=R, t=t: q @ R.T + t)
    allp = np.vstack(list(layout["polys"].values())); lo, hi = allp.min(0), allp.max(0)
    return lo, hi

def fit(ax, lo, hi, half=None):
    c = (lo + hi) / 2; h = half if half else max(hi - lo) / 2
    ax.set_xlim(c[0] - h * 1.08, c[0] + h * 1.08); ax.set_ylim(c[1] - h * 1.08, c[1] + h * 1.08)
    ax.set_aspect("equal"); ax.axis("off")

def net_extent(S, layout):
    allp = np.vstack(list(layout["polys"].values())); return allp.min(0), allp.max(0)

def vis_faces(S):
    return [f for f, fc in enumerate(S.faces) if fc["n"] @ S.d > .12]

def draw_view(ax, S, view):
    right, up = S.cam(); pts = []
    for F, (pid, ang) in view.items():
        fc = S.faces[F]; proj = lambda P: np.c_[P @ right, P @ up]
        poly = proj(S.V[fc["idx"]])
        draw_face(ax, poly, fc, pid, ang, lambda q, fc=fc: proj(fc["c"] + q[:, :1] * fc["u"] + q[:, 1:] * fc["v"]))
        pts.append(poly)
    allv = np.c_[S.V @ right, S.V @ up]; lo, hi = allv.min(0), allv.max(0)
    fit(ax, lo, hi, half=max(hi - lo) / 2)

# ---------------------------------------------------------------- logica
def display(S, A, g):
    perm, alpha = g
    return {perm[f]: (p, (b + alpha[f]) % TAU) for f, (p, b) in A.items()}

def match(opt, view, vis):
    for F in vis:
        p, a = opt[F]; q, b = view[F]
        if p != q: return False
        m = sym(p)
        if m:
            d = (a - b) % (TAU / m)
            if min(d, TAU / m - d) > 2e-3: return False
    return True

def vkey(view):
    out = []
    for F, (p, a) in sorted(view.items()):
        m = sym(p); out.append((F, p, 0 if not m else round((a % (TAU / m)) % (TAU / m) * 100) % round(TAU / m * 100)))
    return tuple(out)

def perturb_view(S, true_pats, view, rng):
    """cambia una cara de la vista: intercambia dos, gira una o pone un patron que no es visible."""
    v = dict(view); vis = list(v); kind = rng.choice(["swap", "rot", "rot", "replace"])
    if kind == "swap" and len(vis) >= 2:
        a, b = rng.sample(vis, 2); v[a], v[b] = v[b], v[a]
    elif kind == "replace":
        hidden = [p for f, p in true_pats.items() if f not in vis]
        if not hidden: return None
        F = rng.choice(vis); st = [0] + S.faces[F]["steps"]
        v[F] = (rng.choice(hidden), rng.choice(st))
    else:
        F = rng.choice(vis); st = S.faces[F]["steps"]
        if not st: return None
        v[F] = (v[F][0], (v[F][1] + rng.choice(st)) % TAU)
    return v

def perturb_net(S, A, rng):
    B = dict(A); fs = list(B)
    if rng.random() < .5:
        a, b = rng.sample(fs, 2); B[a], B[b] = B[b], B[a]
    else:
        f = rng.choice(fs); st = S.faces[f]["steps"]
        if not st: return None
        B[f] = (B[f][0], (B[f][1] + rng.choice(st)) % TAU)
    return B

def generate(figura, tema, modo, seed, path, dpi=105, titulo=True):
    S = SOLIDS[figura]; rng = random.Random(seed); nf = len(S.faces)
    pats = choose(tema, nf, rng)
    A = {f: (pats[f], 0.0) for f in range(nf)}
    vis = vis_faces(S); g0 = rng.choice(S.group)
    view = {F: v for F, v in display(S, A, g0).items() if F in vis}
    ans = rng.randrange(4); L = "ABCD"
    fig = plt.figure(figsize=(11, 9) if modo == "a" else (10, 12.2), facecolor="white")
    if modo == "a":
        if titulo: fig.text(.5, .955, f"¿Qué figura se forma al plegar este desarrollo? ({S.nombre})", ha="center", fontsize=17, weight="bold")
        lay = random_net(S, rng)
        ax = fig.add_axes([.12, .5, .76, .4]); lo, hi = draw_net(ax, S, lay, A); fit(ax, lo, hi)
        valid = lambda o: any(match(display(S, A, g), o, vis) for g in S.group)
        wrong, seen = [], {vkey(view)}
        for _ in range(3000):
            if len(wrong) == 3: break
            w = perturb_view(S, dict(enumerate(pats)), view, rng)
            if w is None or valid(w) or vkey(w) in seen: continue
            seen.add(vkey(w)); wrong.append(w)
        opts = wrong[:]; opts.insert(ans, view)
        for i, o in enumerate(opts):
            ax = fig.add_axes([.02 + i * .245, .07, .235, .33]); draw_view(ax, S, o)
            ax.set_title(L[i], fontsize=20, weight="bold")
    else:
        if titulo: fig.text(.5, .965, f"¿Qué desarrollo forma esta figura? ({S.nombre})", ha="center", fontsize=17, weight="bold")
        ax = fig.add_axes([.3, .71, .4, .22]); draw_view(ax, S, view)
        lay0 = random_net(S, rng)
        valid = lambda B: any(match(display(S, B, g), view, vis) for g in S.group)
        wrong = []
        for _ in range(4000):
            if len(wrong) == 3: break
            B = perturb_net(S, A, rng)
            if B is None: continue
            if rng.random() < .3:
                B2 = perturb_net(S, B, rng)
                if B2 is not None: B = B2
            if valid(B): continue
            lay = lay0 if len(wrong) < 2 else random_net(S, rng)
            if lay["key"] == lay0["key"] and len(wrong) >= 2: continue
            wrong.append((lay, B))
        opts = wrong[:]; opts.insert(ans, (lay0, A))
        ext = [net_extent(S, l) for l, _ in opts]; half = max(max(hi - lo) for lo, hi in ext) / 2
        for i, (l, B) in enumerate(opts):
            ax = fig.add_axes([.03 + (i % 2) * .49, .33 - (i // 2) * .32, .46, .25]); lo, hi = draw_net(ax, S, l, B)
            fit(ax, lo, hi, half); ax.set_title(L[i], fontsize=20, weight="bold")
    if titulo: fig.savefig(path, dpi=dpi)
    else: fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=.12)
    plt.close(fig)
    return L[ans]

SOLIDS = make_solids()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--figura", default="cubo", choices=list(SOLIDS))
    ap.add_argument("--tema", default="mixto", choices=ALL_THEMES + ["mixto"])
    ap.add_argument("--modo", default="a", choices=["a", "b"])
    ap.add_argument("--semilla", type=int, default=1)
    ap.add_argument("--salida", default="ejercicio.png")
    a = ap.parse_args()
    print("respuesta:", generate(a.figura, a.tema, a.modo, a.semilla, a.salida))
