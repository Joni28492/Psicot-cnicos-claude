"""Series de relojes: relojes de agujas, tartas (sectores rellenos) y circulos con puntos que se mueven."""
import math
from .nucleo import ejercicio
from .dibujo import K, GRIS, Circle, Wedge, lienzo, interrogante, letras_opciones, a_uri

T = "Series de relojes"
COLORES = ["#2b6cb0", "#c05621", "#2f855a", "#805ad5", "#b83280"]

def xy(cx, cy, r, paso, n):
    """punto a `paso` posiciones (de n) desde las 12, en sentido horario."""
    a = 2 * math.pi * paso / n
    return cx + r * math.sin(a), cy + r * math.cos(a)

# ---------------------------------------------------------------- dibujo de cada tipo de esfera
def esfera_reloj(ax, cx, cy, estado):
    h, m = estado                       # posiciones en horas (0..11): la aguja corta marca h y la larga marca m
    ax.add_patch(Circle((cx, cy), 1, fc="white", ec=K, lw=2.2))
    for i in range(12):
        ax.plot(*zip(xy(cx, cy, .86, i, 12), xy(cx, cy, .97, i, 12)), color=K, lw=2 if i % 3 == 0 else 1)
    ax.plot(*zip((cx, cy), xy(cx, cy, .82, m, 12)), color=K, lw=2.4, solid_capstyle="round")      # larga y fina
    ax.plot(*zip((cx, cy), xy(cx, cy, .5, h, 12)), color="#c05621", lw=6, solid_capstyle="round")  # corta y gruesa
    ax.add_patch(Circle((cx, cy), .06, fc=K, ec=K))

def esfera_tarta(ax, cx, cy, estado, n, color):
    s, c = estado                       # sector inicial y cuantos sectores rellenos seguidos
    ax.add_patch(Circle((cx, cy), 1, fc="white", ec=K, lw=2.2))
    for i in range(c):
        a0 = 90 - 360 * ((s + i) % n + 1) / n
        ax.add_patch(Wedge((cx, cy), 1, a0, a0 + 360 / n, fc=color, ec=K, lw=1))
    for i in range(n):
        ax.plot(*zip((cx, cy), xy(cx, cy, 1, i, n)), color=K, lw=1)
    ax.add_patch(Circle((cx, cy), 1, fc="none", ec=K, lw=2.2))

def esfera_puntos(ax, cx, cy, estado, n):
    a, b = estado                       # posicion del punto negro y del punto blanco
    ax.add_patch(Circle((cx, cy), 1, fc="white", ec=K, lw=2.2))
    for i in range(n):
        x, y = xy(cx, cy, 1, i, n)
        ax.add_patch(Circle((x, y), .06, fc=GRIS, ec=GRIS))
    ax.add_patch(Circle(xy(cx, cy, 1, a, n), .2, fc=K, ec=K, zorder=3))
    ax.add_patch(Circle(xy(cx, cy, 1, b, n), .2, fc="white", ec=K, lw=2.2, zorder=3))

# ---------------------------------------------------------------- composicion
def componer(rng, serie, ops, ok, dibuja):
    paso = 2.7
    n = len(serie)
    lim_s = (-1.4, paso * n - paso + 1.4, -1.4, 1.4)
    ancho_s = paso * n + 2.8
    sep = (ancho_s - 2.8) / 3.6      # mismo ancho de dibujo en la serie y en las opciones: las esferas salen del mismo tamaño
    lim_o = (-1.4, ancho_s - 1.4, -1.4, 1.4)
    fig, ax_s, ax_o = lienzo(9.6, 1.5, 1.7, lim_s, lim_o)
    for i, st in enumerate(serie):
        dibuja(ax_s, i * paso, 0, st)
    interrogante(ax_s, n * paso, 0, 2, 2)
    ax_s.set_xlim(-1.4, n * paso + 1.4)
    for j, st in enumerate(ops):
        dibuja(ax_o, 1.2 + j * sep * 1.0, .1, st)
    letras_opciones(ax_o, [1.2 + j * sep for j in range(4)], -1.2)
    return a_uri(fig)

def elegir(rng, ok, candidatos, valido):
    rng.shuffle(candidatos)
    vistos, out = {ok}, []
    for c in candidatos:
        if c not in vistos and valido(c):
            vistos.add(c); out.append(c)
        if len(out) == 3: break
    if len(out) < 3: raise ValueError("faltan distractores")
    ops = [ok] + out
    rng.shuffle(ops)
    return ops

# ---------------------------------------------------------------- generadores
def reloj(rng):
    for _ in range(60):
        dh = rng.choice([1, 2, 3, -1, -2, -3]); dm = rng.choice([1, 2, 3, 4, -1, -2, -3, -4])
        if dh == dm: continue
        h0, m0 = rng.randint(0, 11), rng.randint(0, 11)
        s = [((h0 + i * dh) % 12, (m0 + i * dm) % 12) for i in range(6)]
        if any(h == m for h, m in s): continue        # agujas superpuestas: ambiguo
        ok = s[-1]
        c = [((ok[0] + d) % 12, ok[1]) for d in (1, -1, 2)] + [(ok[0], (ok[1] + d) % 12) for d in (1, -1, 2)] + [(ok[1], ok[0]), ((ok[0] + dh) % 12, (ok[1] + dm) % 12), s[-2]]
        try: ops = elegir(rng, ok, c, lambda e: e[0] != e[1])
        except ValueError: continue
        sentido = lambda d: f"{'avanza' if d > 0 else 'retrocede'} {abs(d)} hora{'s' if abs(d) > 1 else ''}"
        truco = (f"Sigue cada aguja por separado: la corta y gruesa {sentido(dh)} en cada reloj y la larga y fina {sentido(dm)} "
                 f"(cada marca es una hora del reloj).")
        return dict(enunciado="¿Qué reloj continúa la serie?", opciones=list("ABCD"), correcta=ops.index(ok), truco=truco,
                    imagen=componer(rng, s[:-1], ops, ok, esfera_reloj))
    raise ValueError("no se pudo generar")

MODOS_TARTA = [(0, 1), (0, -1), (0, 2), (1, 0), (-1, 0), (2, 0), (1, 1), (1, -1), (2, 1), (-2, 1), (-1, -1)]

def tarta(rng):
    for _ in range(60):
        n = rng.choice([8, 10, 12]); r, k = rng.choice(MODOS_TARTA)
        if 5 * abs(k) > n - 2: continue
        lo = 1 + (-5 * k if k < 0 else 0); hi = n - 1 - (5 * k if k > 0 else 0)
        if lo > hi: continue
        c0, s0 = rng.randint(lo, hi), rng.randint(0, n - 1)
        s = [((s0 + i * r) % n, c0 + i * k) for i in range(6)]
        ok = s[-1]
        c = [((ok[0] + d) % n, ok[1]) for d in (1, -1, 2, -2)] + [(ok[0], ok[1] + d) for d in (1, -1, 2)] + [(ok[0] - r, ok[1] - k), ((ok[0] + r) % n, ok[1] + k), s[-2]]
        try: ops = elegir(rng, ok, c, lambda e: 1 <= e[1] <= n - 1)
        except ValueError: continue
        partes = []
        if r: partes.append(f"el bloque relleno gira {abs(r)} sector{'es' if abs(r) > 1 else ''} {'a la derecha' if r > 0 else 'a la izquierda'}")
        if k: partes.append(f"{'gana' if k > 0 else 'pierde'} {abs(k)} sector{'es' if abs(k) > 1 else ''} relleno{'s' if abs(k) > 1 else ''}")
        color = rng.choice(COLORES)
        truco = f"La tarta tiene {n} sectores. En cada paso " + " y ".join(partes) + "."
        return dict(enunciado="¿Qué gráfico circular continúa la serie?", opciones=list("ABCD"), correcta=ops.index(ok), truco=truco,
                    imagen=componer(rng, s[:-1], ops, ok, lambda ax, x, y, st: esfera_tarta(ax, x, y, st, n, color)))
    raise ValueError("no se pudo generar")

def puntos(rng):
    for _ in range(60):
        n = rng.choice([8, 10, 12]); da = rng.choice([1, 2, 3, -1, -2, -3]); db = rng.choice([1, 2, 3, -1, -2, -3])
        if da == db: continue
        a0, b0 = rng.randint(0, n - 1), rng.randint(0, n - 1)
        s = [((a0 + i * da) % n, (b0 + i * db) % n) for i in range(6)]
        if any(a == b for a, b in s): continue
        ok = s[-1]
        c = [((ok[0] + d) % n, ok[1]) for d in (1, -1, 2)] + [(ok[0], (ok[1] + d) % n) for d in (1, -1, 2)] + [(ok[1], ok[0]), s[-2], ((ok[0] - da) % n, (ok[1] - db) % n)]
        try: ops = elegir(rng, ok, c, lambda e: e[0] != e[1])
        except ValueError: continue
        d = lambda x: f"{abs(x)} {'posiciones' if abs(x) > 1 else 'posición'} {'en sentido horario' if x > 0 else 'en sentido antihorario'}"
        truco = f"Hay {n} posiciones. El punto negro se mueve {d(da)} y el punto blanco {d(db)} en cada paso."
        return dict(enunciado="¿Qué círculo continúa la serie?", opciones=list("ABCD"), correcta=ops.index(ok), truco=truco,
                    imagen=componer(rng, s[:-1], ops, ok, lambda ax, x, y, st: esfera_puntos(ax, x, y, st, n)))
    raise ValueError("no se pudo generar")

def _reg(f):
    def g(rng):
        for _ in range(20):
            try: return f(rng)
            except ValueError: continue
        raise ValueError("no se pudo generar")
    g.__name__ = f.__name__
    return ejercicio(T, peso=2, tiempo=30)(g)

serie_reloj, serie_tarta, serie_puntos = _reg(reloj), _reg(tarta), _reg(puntos)
