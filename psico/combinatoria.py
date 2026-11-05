"""Combinatoria: permutaciones, variaciones y combinaciones (grupos).

Patrones:
  permutaciones -> ¿de cuántas formas se pueden ordenar/colocar ...?   (importa el orden, se usan todos los elementos)
  variaciones   -> M elementos y N espacios                           (importa el orden, se usan N de M)
  combinaciones -> ¿cuántas parejas / tríos / grupos ...?              (no importa el orden)
"""
import math
from collections import Counter
from .nucleo import ejercicio, num, mezclar, distractores_num

T = "Combinatoria"
P, C = math.perm, math.comb
F = math.factorial

def prod(n, k):
    """n·(n-1)·...· (k factores), para escribir el truco."""
    return "×".join(str(n - i) for i in range(k))

def cierre(rng, q, r, tr, extras, dif=2):
    ops, i = mezclar(num(r), [num(x) for x in distractores_num(r, rng, extras=extras)], rng)
    return dict(enunciado=q, opciones=ops, correcta=i, truco=tr, dificultad=dif)

# ------------------------------------------------------------------ permutaciones
ORDENAR = [
    ("personas", "En una fila de fotos se colocan {n} personas. ¿De cuántas formas distintas pueden colocarse?"),
    ("libros", "¿De cuántas formas se pueden ordenar {n} libros distintos en una estantería?"),
    ("corredores", "{n} corredores llegan a meta sin empates. ¿De cuántas formas distintas puede quedar la clasificación?"),
    ("banderas", "¿De cuántas formas se pueden colocar {n} banderas distintas en un mástil, una encima de otra?"),
    ("coches", "¿De cuántas formas se pueden aparcar {n} coches distintos en {n} plazas contiguas?"),
]
PALABRAS = ["CASA", "MAMA", "PAPA", "OSO", "ANA", "LUNA", "RADAR", "ROMA", "AMOR", "SOLO", "CACAO", "BOBO", "ALA", "TATA", "PEPE"]

@ejercicio(T, peso=3)
def permutaciones(rng):
    kind = rng.choice(["ordenar", "ordenar", "juntos", "repetidas", "mesa"])
    if kind == "ordenar":
        n = rng.choice([4, 5, 6, 7]); _, q = rng.choice(ORDENAR); r = F(n)
        return cierre(rng, q.format(n=n), r, f"Se usan todos y el orden importa: {n}! = {'×'.join(str(i) for i in range(n, 0, -1))} = {num(r)}.",
                      [n * n, P(n, n - 1) // 2, F(n - 1), F(n + 1)], dif=1)
    if kind == "juntos":
        n = rng.choice([4, 5, 6]); r = F(n - 1) * 2
        q = f"{n} amigos se sientan en una fila de {n} sillas. ¿De cuántas formas pueden sentarse si dos de ellos, Ana y Luis, quieren estar siempre juntos?"
        return cierre(rng, q, r, f"Ana y Luis forman un bloque: {n - 1} elementos → {n - 1}! = {F(n - 1)}, y el bloque se puede dar la vuelta (×2): {num(r)}.",
                      [F(n - 1), F(n), F(n - 2) * 2, F(n - 1) * 3], dif=3)
    if kind == "repetidas":
        w = rng.choice(PALABRAS); cnt = Counter(w); r = F(len(w)) // math.prod(F(v) for v in cnt.values())
        rep = ", ".join(f"{l}×{v}" for l, v in cnt.items() if v > 1)
        q = f"¿Cuántas palabras distintas, tengan sentido o no, se pueden formar reordenando todas las letras de {w}?"
        return cierre(rng, q, r, f"{len(w)}! dividido entre las repeticiones ({rep}): {F(len(w))} ÷ {math.prod(F(v) for v in cnt.values())} = {num(r)}.",
                      [F(len(w)), r * 2, r // 2 if r > 2 else r + 1, len(w) ** 2], dif=2)
    n = rng.choice([4, 5, 6]); r = F(n - 1)
    q = f"¿De cuántas formas se pueden sentar {n} personas alrededor de una mesa redonda si solo importa quién está al lado de quién (los giros no cuentan)?"
    return cierre(rng, q, r, f"Se fija a una persona y las demás se ordenan: ({n}−1)! = {num(r)}.", [F(n), n * n, F(n - 2), r * 2], dif=3)

# ------------------------------------------------------------------ variaciones: M elementos, N espacios
VARIA = [
    "Hay {m} elementos distintos y {n} espacios en fila. Se coloca un elemento en cada espacio sin repetir ninguno. ¿De cuántas formas se pueden llenar los espacios?",
    "Un club tiene {m} socios y hay que elegir presidente, secretario y tesorero entre ellos, sin que nadie ocupe dos cargos. ¿De cuántas formas?",
    "{m} corredores compiten y se reparten medallas a los {n} primeros puestos. ¿De cuántas formas pueden quedar los puestos del podio?",
    "Con {m} libros distintos se llenan {n} huecos de una estantería, uno por hueco. ¿De cuántas formas distintas?",
    "¿Cuántos códigos de {n} cifras distintas se pueden formar con las cifras del 1 al {m}?",
]
VARIA_REP = [
    "Hay {n} espacios y cada uno se rellena con uno de {m} elementos distintos, pudiendo repetirse. ¿De cuántas formas se pueden llenar los espacios?",
    "Una cerradura tiene {n} ruedas y cada una tiene las cifras de 1 a {m}. ¿Cuántas combinaciones distintas hay?",
    "Se pintan {n} casillas en fila con uno de {m} colores, pudiendo repetir colores. ¿Cuántas formas hay?",
]

@ejercicio(T, peso=3)
def variaciones(rng):
    if rng.random() < .7:
        n = rng.choice([2, 3, 3, 4]); m = rng.randint(n + 2, 9 if n < 4 else 8); r = P(m, n)
        q = rng.choice(VARIA); q = q.replace("{n}", str(n)).replace("{m}", str(m))
        if "presidente" in q: n, m = 3, m; r = P(m, 3); q = q.replace("{n}", "3")
        return cierre(rng, q, r, f"{m} elementos en {n} espacios sin repetir, importa el orden: {prod(m, n)} = {num(r)} (empiezas con {m} opciones y cada espacio tiene una menos).",
                      [C(m, n), m ** n, F(m), m * n], dif=2)
    n = rng.choice([2, 3, 4]); m = rng.randint(3, 7 if n < 4 else 5); r = m ** n
    q = rng.choice(VARIA_REP).replace("{n}", str(n)).replace("{m}", str(m))
    return cierre(rng, q, r, f"Cada espacio tiene {m} opciones, que se repiten: {'×'.join([str(m)] * n)} = {m}^{n} = {num(r)}.",
                  [P(m, n), C(m, n), m * n, (m - 1) ** n], dif=1)

# ------------------------------------------------------------------ combinaciones: grupos sin orden
GRUPOS = {
    2: [("En una reunión hay {n} personas y todas se saludan con un apretón de manos. ¿Cuántos apretones hay?", "apretones"),
        ("¿Cuántas parejas distintas se pueden formar con {n} alumnos?", "parejas"),
        ("En un torneo juegan {n} equipos y todos juegan contra todos una sola vez. ¿Cuántos partidos hay?", "partidos"),
        ("Se quieren trazar rectas que unan {n} puntos de un círculo, tomados de dos en dos. ¿Cuántas rectas salen (sin tres puntos alineados)?", "rectas")],
    3: [("¿Cuántos tríos distintos se pueden formar con {n} amigos?", "tríos"),
        ("De un grupo de {n} agentes hay que elegir 3 para una patrulla. ¿Cuántas patrullas distintas se pueden formar?", "patrullas"),
        ("¿Cuántos triángulos distintos se pueden dibujar uniendo {n} puntos de un círculo de 3 en 3?", "triángulos")],
    4: [("De {n} candidatos se elige un comité de 4 personas. ¿Cuántos comités distintos hay?", "comités"),
        ("¿Cuántos grupos de 4 alumnos se pueden formar en una clase de {n}?", "grupos")],
}

@ejercicio(T, peso=3)
def combinaciones(rng):
    k = rng.choice([2, 2, 3, 3, 4]); n = rng.randint(k + 3, 9 if k > 2 else 12)
    q, _ = rng.choice(GRUPOS[k]); r = C(n, k)
    ext = [P(n, k), n ** k, n * k, C(n, k - 1) if k > 1 else n]
    tr = f"El orden no importa: {prod(n, k)} ÷ {k}! = {num(P(n, k))} ÷ {F(k)} = {num(r)}."
    if k == 2: tr += f" (atajo: {n}×{n - 1}/2)"
    return cierre(rng, q.format(n=n), r, tr, ext, dif={2: 1, 3: 2, 4: 3}[k])
