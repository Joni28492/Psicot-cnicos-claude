"""Puzzles: rompecabezas incompletos de 2x3, 3x3 o 4x4 en los que solo cuenta la forma de los bordes (saliente o entrante).

Cada pieza es (arriba, derecha, abajo, izquierda) con 1 = saliente, -1 = entrante y 0 = borde plano. Dos piezas contiguas
encajan si sus bordes en contacto son opuestos (uno saliente y otro entrante); los bordes del marco son planos.
  puzzle_hueco    falta una pieza: hay que elegir cual encaja en el hueco.
  puzzle_sueltas  faltan varias; se dan las piezas sueltas, hay que colocarlas y elegir la que falta por colocar.
El generador comprueba por fuerza bruta que la respuesta es unica.
"""
import itertools, math
from .nucleo import ejercicio
from .dibujo import K, GRIS, Polygon, lienzo, interrogante, letras_opciones, a_uri

T = "Puzzles"
LADOS = ["arriba", "la derecha", "abajo", "la izquierda"]
NOMBRE_BORDE = {1: "saliente", -1: "entrante", 0: "plano"}
VECINO = [(-1, 0), (0, 1), (1, 0), (0, -1)]            # (fila, columna) de la celda vecina por arriba, derecha, abajo, izquierda

def rejilla(rng, R, C):
    H = {(i, j): rng.choice([1, -1]) for i in range(R) for j in range(C - 1)}       # borde derecho de (i, j)
    V = {(i, j): rng.choice([1, -1]) for i in range(R - 1) for j in range(C)}       # borde inferior de (i, j)
    piezas = {}
    for i in range(R):
        for j in range(C):
            piezas[(i, j)] = (-V[(i - 1, j)] if i else 0, H[(i, j)] if j < C - 1 else 0, V[(i, j)] if i < R - 1 else 0, -H[(i, j - 1)] if j else 0)
    return piezas

def requerida(tablero, R, C, pos):
    """pieza que necesita la celda `pos` segun sus vecinas (None si alguna vecina aun no esta colocada)."""
    out = []
    for k, (di, dj) in enumerate(VECINO):
        ni, nj = pos[0] + di, pos[1] + dj
        if not (0 <= ni < R and 0 <= nj < C): out.append(0)
        elif (ni, nj) not in tablero: return None
        else: out.append(-tablero[(ni, nj)][(k + 2) % 4])
    return tuple(out)

def valido(tablero, R, C, vacia):
    for (i, j), p in tablero.items():
        for k, (di, dj) in enumerate(VECINO):
            ni, nj = i + di, j + dj
            if not (0 <= ni < R and 0 <= nj < C): ok = p[k] == 0
            elif (ni, nj) == vacia: ok = p[k] != 0
            else: ok = p[k] == -tablero[(ni, nj)][(k + 2) % 4]
            if not ok: return False
    return True

def soluciones(R, C, piezas, huecos, sueltas):
    """todas las piezas posibles para el ultimo hueco, probando cada reparto de las sueltas en los demas huecos."""
    fijos = {p: v for p, v in piezas.items() if p not in huecos}
    res = {}
    for h in huecos:
        otros = [x for x in huecos if x != h]
        for perm in itertools.permutations(range(len(sueltas))):
            tab = dict(fijos); tab.update({o: sueltas[k] for o, k in zip(otros, perm)})
            if valido(tab, R, C, h): res.setdefault(requerida(tab, R, C, h), (h, perm))
    return res

# ------------------------------------------------------------------ dibujo
def contorno(x, y, e, r=.2):
    esq = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x, y)]
    normales = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    pts = []
    for k in range(4):
        (x0, y0), (x1, y1) = esq[k], esq[(k + 1) % 4]; n = normales[k]
        pts.append((x0, y0))
        if e[k]:
            mx, my, dx, dy = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
            for s in range(0, 17):
                t = math.pi * s / 16
                pts.append((mx - r * math.cos(t) * dx + e[k] * r * math.sin(t) * n[0], my - r * math.cos(t) * dy + e[k] * r * math.sin(t) * n[1]))
    return pts

def pieza(ax, x, y, e, etiqueta=None, fc="white"):
    ax.add_patch(Polygon(contorno(x, y, e), closed=True, fc=fc, ec=K, lw=2, joinstyle="round", zorder=2))
    if etiqueta: ax.text(x + .5, y + .5, etiqueta, ha="center", va="center", fontsize=15, color=GRIS, fontweight="bold", zorder=3)

def dibujar(R, C, piezas, huecos, sueltas, opciones):
    nsue = len(sueltas)
    cw = C + (2.3 if nsue else 0)                        # ancho del contenido: rejilla + columna de piezas sueltas
    w = max(cw + 1.2, 6.0)                               # con minimo para que las 4 opciones no se solapen
    x0 = -(w - cw) / 2
    lim_s = (x0, x0 + w, -.6, R + .9)
    anch = 8.4
    alto_s = anch * (lim_s[3] - lim_s[2]) / w
    fig, ax_s, ax_o = lienzo(anch, alto_s, anch * 2.6 / w, lim_s, (lim_s[0], lim_s[1], -1.1, 1.5))
    for (i, j), p in piezas.items():
        y = R - 1 - i
        if (i, j) in huecos: interrogante(ax_s, j + .5, y + .5, 1, 1)
        else: pieza(ax_s, j, y, p)
    if nsue:
        ax_s.text(C + 1.15, R + .45, "Piezas sueltas", ha="center", fontsize=11, color="#555")
        cols = 1 if nsue <= 3 else 2
        for k, p in enumerate(sueltas):
            pieza(ax_s, C + .65 + (k % cols) * 1.5 - (.5 if cols == 1 else 0) + .0, R - 1.3 - (k // cols) * 1.5, p, str(k + 1))
    xs = [lim_s[0] + w * (j + .5) / 4 - .5 for j in range(4)]
    for x, p in zip(xs, opciones): pieza(ax_o, x, -.3, p)
    letras_opciones(ax_o, [x + .5 for x in xs], -.85)
    return a_uri(fig)

# ------------------------------------------------------------------ generacion
def describe(p):
    return ", ".join(f"{LADOS[k]} {NOMBRE_BORDE[p[k]]}" for k in range(4))

def generar(rng, R, C, n_sueltas):
    for _ in range(80):
        piezas = rejilla(rng, R, C)
        huecos = rng.sample(sorted(piezas), n_sueltas + 1)
        sueltas = [piezas[h] for h in huecos[:-1]]
        rng.shuffle(sueltas)
        sol = soluciones(R, C, piezas, huecos, sueltas)
        ok = piezas[huecos[-1]]
        if list(sol) != [ok]: continue                          # respuesta unica: solo cabe una pieza en el hueco que queda
        # distractores: la misma pieza con uno o dos bordes (no planos) invertidos
        libres = [k for k in range(4) if ok[k]]
        cand = []
        for m in range(1, len(libres) + 1):
            for sub in itertools.combinations(libres, m):
                cand.append(tuple(-ok[k] if k in sub else ok[k] for k in range(4)))
        rng.shuffle(cand)
        cand.sort(key=lambda c: sum(a != b for a, b in zip(c, ok)))         # primero los que difieren en un solo borde
        dist = cand[:3]
        if len(dist) < 3: continue
        ops = dist + [ok]; rng.shuffle(ops)
        # cual de las sueltas va en cada hueco (para el truco)
        h_ult, perm = sol[ok]
        otros = [x for x in huecos if x != h_ult]
        asign = ", ".join(f"la {k + 1} en la fila {o[0] + 1}, columna {o[1] + 1}" for o, k in sorted(zip(otros, perm), key=lambda t: t[1]))
        veci = ", ".join(f"{LADOS[k]} {NOMBRE_BORDE[ok[k]]}" for k in range(4))
        if n_sueltas:
            truco = (f"Coloca cada pieza suelta donde encaje ({asign}). El hueco que queda es el de la fila {h_ult[0] + 1}, columna {h_ult[1] + 1}: "
                     f"cada borde debe ser el opuesto al de su vecina (saliente con entrante) y los bordes del marco son planos. Pieza que falta: {veci}.")
        else:
            truco = (f"El hueco está en la fila {h_ult[0] + 1}, columna {h_ult[1] + 1}. Cada borde de la pieza debe ser el opuesto al de la vecina "
                     f"(saliente con entrante) y los del marco son planos: {veci}.")
        dif = 1 if (n_sueltas == 0 and R * C <= 6) else 3 if (R * C >= 16 and n_sueltas >= 2) else 2
        enun = "¿Qué pieza completa el puzzle?" if not n_sueltas else \
               f"En el puzzle faltan {n_sueltas + 1} piezas. Coloca las {n_sueltas} pieza{'s' if n_sueltas > 1 else ''} suelta{'s' if n_sueltas > 1 else ''} y elige la pieza que falta por colocar."
        return dict(enunciado=f"Puzzle de {R}×{C}. " + enun, opciones=list("ABCD"), correcta=ops.index(ok), truco=truco, dificultad=dif,
                    imagen=a_uri_safe(R, C, piezas, huecos, sueltas, ops))
    raise ValueError("no se pudo generar un puzzle de respuesta unica")

def a_uri_safe(R, C, piezas, huecos, sueltas, ops):
    return dibujar(R, C, piezas, huecos, sueltas, ops)

def _reg(nombre, peso, configuraciones):
    def f(rng):
        R, C, k = rng.choice(configuraciones)
        return generar(rng, R, C, k)
    f.__name__ = nombre
    return ejercicio(T, peso=peso, tiempo=40)(f)

puzzle_hueco = _reg("puzzle_hueco", 3, [(2, 3, 0), (3, 3, 0), (3, 3, 0), (4, 4, 0)])
puzzle_sueltas = _reg("puzzle_sueltas", 2, [(2, 3, 1), (3, 3, 1), (3, 3, 2), (4, 4, 2)])
