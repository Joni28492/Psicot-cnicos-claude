"""Series de fichas de domino: en una fila, en dos filas, en circulo o en espiral.

Cada ficha es (a, b) con a, b en 0..6. La serie sigue una regla sobre las dos mitades
(cada mitad suma o resta un paso fijo, modulo 7) y hay que elegir la ficha que falta.
"""
import math
from .nucleo import ejercicio
from .dibujo import K, Polygon, Circle, lienzo, interrogante, letras_opciones, a_uri

T = "Series de fichas"
# desplazamientos (en unidades de ficha) de los puntos dentro de cada mitad, en ejes (a lo largo, a lo ancho)
D = .25
PIPS = {0: [], 1: [(0, 0)], 2: [(-D, -D), (D, D)], 3: [(-D, -D), (0, 0), (D, D)], 4: [(-D, -D), (-D, D), (D, -D), (D, D)],
        5: [(-D, -D), (-D, D), (D, -D), (D, D), (0, 0)], 6: [(-D, -D), (-D, 0), (-D, D), (D, -D), (D, 0), (D, D)]}

def ficha(ax, x, y, ang, a, b):
    """dibuja la ficha (a, b) centrada en (x, y); su eje largo (2 x 1) forma el angulo ang."""
    u = (math.cos(ang), math.sin(ang)); v = (-u[1], u[0])
    P = lambda s, t: (x + s * u[0] + t * v[0], y + s * u[1] + t * v[1])
    ax.add_patch(Polygon([P(-1, -.5), P(1, -.5), P(1, .5), P(-1, .5)], closed=True, fc="white", ec=K, lw=1.8, joinstyle="round"))
    ax.plot(*zip(P(0, -.42), P(0, .42)), color=K, lw=1.3)
    for n, c in ((a, -.5), (b, .5)):
        for s, t in PIPS[n]:
            ax.add_patch(Circle(P(c + s, t), .085, fc=K, ec=K))

# ---------------------------------------------------------------- disposiciones: lista de (x, y, angulo)
def pos_fila(n):
    return [(i * 2.5, 0, 0) for i in range(n)]

def pos_dos_filas(n):
    m = n // 2
    return [((i % m) * 2.5, -(i // m) * 1.7, 0) for i in range(n)]

def pos_circulo(n):
    R = 3.4
    return [(R * math.cos(th), R * math.sin(th), th - math.pi / 2) for th in (math.pi / 2 - 2 * math.pi * i / n for i in range(n))]

ESP_A, ESP_B = 2.0, .34

def thetas_espiral(n, paso=2.6):
    th, out = 0.0, []
    for _ in range(n):
        out.append(th)
        th += paso / math.hypot(ESP_A + ESP_B * th, ESP_B)     # avanza ~`paso` de longitud de arco
    return out

def pos_espiral(n):
    """espiral de Arquimedes que se abre desde el centro (sentido horario); las fichas siguen la tangente."""
    return [((ESP_A + ESP_B * th) * math.cos(math.pi / 2 - th), (ESP_A + ESP_B * th) * math.sin(math.pi / 2 - th), -th) for th in thetas_espiral(n)]

DISPOSICIONES = {"fila": (pos_fila, 6), "dos filas": (pos_dos_filas, 8), "círculo": (pos_circulo, 8), "espiral": (pos_espiral, 8)}

# ---------------------------------------------------------------- reglas
def regla(rng):
    """devuelve (paso_a, paso_b, descripcion)."""
    opciones = []
    for k in (1, 2, 3):
        opciones += [(k, k, f"las dos mitades suben {k}"), (-k, -k, f"las dos mitades bajan {k}"),
                     (k, -k, f"la mitad izquierda sube {k} y la derecha baja {k}"),
                     (0, k, f"la mitad izquierda se queda igual y la derecha sube {k}"),
                     (k, 0, f"la mitad izquierda sube {k} y la derecha se queda igual"),
                     (0, -k, f"la mitad izquierda se queda igual y la derecha baja {k}")]
        for j in (1, 2, 3):
            if j != k:
                opciones.append((k, j, f"la mitad izquierda sube {k} y la derecha sube {j}"))
    return rng.choice(opciones)

def serie(rng, n, ka, kb):
    a0, b0 = rng.randint(0, 6), rng.randint(0, 6)
    return [((a0 + i * ka) % 7, (b0 + i * kb) % 7) for i in range(n)]

def clave(f):
    return tuple(sorted(f))          # (a, b) y (b, a) son la misma ficha fisica

def distractores(rng, ok, previa, ka, kb):
    a, b = ok
    cand = [(a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1), (a + ka, b + kb), (a - ka, b - kb), previa, (a + 1, b + 1), (a - 1, b - 1), (a + 2, b), (a, b + 2)]
    rng.shuffle(cand)
    vistos, out = {clave(ok)}, []
    for c in cand:
        c = (c[0] % 7, c[1] % 7)
        if clave(c) not in vistos:
            vistos.add(clave(c)); out.append(c)
        if len(out) == 3: break
    return out

def generar(rng, disposicion):
    posf, n = DISPOSICIONES[disposicion]
    ka, kb, desc = regla(rng)
    s = serie(rng, n, ka, kb)
    if len({clave(f) for f in s}) < n - 1:     # series demasiado repetitivas no sirven
        raise ValueError("serie degenerada")
    ok = s[-1]
    ops = [ok] + distractores(rng, ok, s[-2], ka, kb)
    if len(ops) != 4: raise ValueError("faltan distractores")
    rng.shuffle(ops)
    pos = posf(n)
    xs, ys = [p[0] for p in pos], [p[1] for p in pos]
    m = 2.1
    lim = (min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m)
    w, h = lim[1] - lim[0], lim[3] - lim[2]
    ancho = 8.4
    alto_s = min(ancho * h / w, 5.6)
    fig, ax_s, ax_o = lienzo(ancho, alto_s, 1.3, lim, (-1.6, 3 * 4.6 + 1.6, -1.4, 1.4))
    if disposicion in ("círculo", "espiral"):
        t = [i / 200 * 2 * math.pi for i in range(201)]
        if disposicion == "círculo": gx, gy = [3.4 * math.cos(q) for q in t], [3.4 * math.sin(q) for q in t]
        else:
            gx, gy = [], []
            tmax = thetas_espiral(n)[-1]
            for q in [tmax * i / 200 for i in range(201)]:
                r = ESP_A + ESP_B * q; gx.append(r * math.cos(math.pi / 2 - q)); gy.append(r * math.sin(math.pi / 2 - q))
        ax_s.plot(gx, gy, color="#d4d4d4", lw=1.2, zorder=0)
        x0, y0, _ = pos[0]; d = math.hypot(x0, y0) or 1
        k = -1.5 if disposicion == "espiral" else 1.7          # espiral: la etiqueta va en el hueco central; circulo: fuera
        ax_s.annotate("inicio", xy=(x0 - x0 / d * .5 * (k < 0) + x0 / d * .6 * (k > 0), y0 - y0 / d * .5 * (k < 0) + y0 / d * .6 * (k > 0)),
                      xytext=(x0 + x0 / d * k, y0 + y0 / d * k), ha="center", va="center", fontsize=11, color="#666",
                      arrowprops=dict(arrowstyle="->", color="#666", lw=1.2))
    for i, (x, y, ang) in enumerate(pos):
        if i == n - 1: interrogante(ax_s, x, y, 2, 1, ang)
        else: ficha(ax_s, x, y, ang, *s[i])
    for j, f in enumerate(ops):
        ficha(ax_o, j * 4.6, .35, 0, *f)
    letras_opciones(ax_o, [j * 4.6 for j in range(4)], -.95)
    truco = (f"Mira cada mitad por separado: {desc} en cada paso (los puntos vuelven a 0 después del 6). "
             f"La ficha que falta es {ok[0]}–{ok[1]}.")
    return dict(enunciado="¿Qué ficha de dominó continúa la serie? (" + {"fila": "en fila", "dos filas": "en dos filas, de izquierda a derecha y de arriba abajo",
                "círculo": "en círculo, en el sentido de las agujas del reloj desde la ficha de inicio", "espiral": "en espiral, desde la ficha de inicio hacia fuera"}[disposicion] + ")",
                opciones=list("ABCD"), correcta=ops.index(ok), truco=truco, imagen=a_uri(fig))

def _reg(nombre, disp):
    def f(rng):
        for _ in range(40):
            try: return generar(rng, disp)
            except ValueError: continue
        raise ValueError("no se pudo generar")
    f.__name__ = nombre
    return ejercicio(T, peso=2, tiempo=30)(f)

domino_fila = _reg("domino_fila", "fila")
domino_dos_filas = _reg("domino_dos_filas", "dos filas")
domino_circulo = _reg("domino_circulo", "círculo")
domino_espiral = _reg("domino_espiral", "espiral")

REGISTRO_F = {"fila": domino_fila, "dos filas": domino_dos_filas, "círculo": domino_circulo, "espiral": domino_espiral}
