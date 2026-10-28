import math
from .nucleo import ejercicio, num, mezclar, distractores_num

T = "Problemas"

DOS_TIPOS = [
    ("En una granja hay gallinas y conejos. En total hay {h} cabezas y {p} patas. ¿Cuántos conejos hay?", 2, 4, "conejos"),
    ("En una granja hay patos y vacas. En total hay {h} cabezas y {p} patas. ¿Cuántos patos hay?", 4, 2, "patos"),
    ("En un aparcamiento hay motos y coches. En total hay {h} vehículos y {p} ruedas. ¿Cuántos coches hay?", 2, 4, "coches"),
    ("En un taller hay bicicletas y triciclos. En total hay {h} vehículos y {p} ruedas. ¿Cuántos triciclos hay?", 2, 3, "triciclos"),
    ("En una caja hay monedas de 1 € y de 2 €. Hay {h} monedas que suman {p} €. ¿Cuántas monedas de 2 € hay?", 1, 2, "monedas de 2 €"),
    ("Se venden {h} entradas, unas de 5 € y otras de 3 €, y se recaudan {p} €. ¿Cuántas entradas de 5 € se vendieron?", 3, 5, "entradas de 5 €"),
]

@ejercicio(T, peso=4)
def cabezas_patas(rng):
    txt, v1, v2, quien = rng.choice(DOS_TIPOS)
    h = rng.randint(8, 30); x2 = rng.randint(2, h - 2)
    p = v1 * (h - x2) + v2 * x2
    ops, i = mezclar(x2, distractores_num(x2, rng, extras=[h - x2, p // v2 if p % v2 == 0 else x2 + 4, (p - v1 * h) // 1 if (p - v1 * h) > 0 else x2 + 3]), rng)
    return dict(enunciado=txt.format(h=h, p=p), opciones=ops, correcta=i,
                truco=f"Supón que todos son del tipo menor ({v1}): {h}×{v1} = {v1 * h}. Sobran {p - v1 * h}, y cada cambio añade {v2 - v1}. "
                      f"{p - v1 * h} ÷ {v2 - v1} = {x2} {quien}.")

@ejercicio(T, peso=3)
def mas_que(rng):
    b = rng.randint(8, 40); d = rng.choice([4, 6, 8, 10, 12, 14, 16, 20])
    if (b * 2 + d) % 2: b += 1
    a = b + d; total = a + b
    quien = rng.choice([("Ana", "Luis", "euros"), ("Marta", "Pablo", "años"), ("Juan", "Sara", "libros")])
    pide_mayor = rng.random() < .5
    corr = a if pide_mayor else b
    ops, i = mezclar(corr, distractores_num(corr, rng, extras=[total - d, total // 2, a + d // 2 if pide_mayor else b - d // 2]), rng)
    return dict(enunciado=f"{quien[0]} tiene {d} {quien[2]} más que {quien[1]}, y entre los dos suman {total}. ¿Cuántos tiene {quien[0] if pide_mayor else quien[1]}?",
                opciones=ops, correcta=i,
                truco=f"Quita la diferencia al total: {total} − {d} = {total - d}, a medias = {(total - d) // 2} (el menor). "
                      f"El mayor es {(total - d) // 2} + {d} = {a}.")

@ejercicio(T, peso=2)
def veces(rng):
    k = rng.choice([2, 3, 4, 5]); b = rng.randint(3, 15); total = b * (k + 1)
    ops, i = mezclar(b * k, distractores_num(b * k, rng, extras=[total // 2, b, total - k]), rng)
    return dict(enunciado=f"Un padre tiene {k} veces los años de su hijo y entre los dos suman {total}. ¿Cuántos años tiene el padre?",
                opciones=ops, correcta=i,
                truco=f"El total son {k}+1 = {k + 1} partes iguales: {total} ÷ {k + 1} = {b} (hijo). Padre: {k}×{b} = {b * k}.")

@ejercicio(T, peso=2)
def edades(rng):
    r2 = rng.choice([2, 3]); r1 = rng.choice([x for x in range(r2 + 1, 7)]); t = rng.choice([x for x in range(2, 13) if (x * (r2 - 1)) % (r1 - r2) == 0])
    x = t * (r2 - 1) // (r1 - r2)
    ops, i = mezclar(x, distractores_num(x, rng, extras=[x * r1, t, x + t]), rng)
    return dict(enunciado=f"Ahora una madre tiene {r1} veces la edad de su hija. Dentro de {t} años tendrá {r2} veces la edad de su hija. ¿Qué edad tiene la hija hoy?",
                opciones=ops, correcta=i,
                truco=f"Con x = edad de la hija: {r1}x + {t} = {r2}(x + {t}) ⇒ {"" if r1 - r2 == 1 else r1 - r2}x = {t * (r2 - 1)} ⇒ x = {x}. Comprobación: madre {r1 * x}, dentro de {t} años {r1 * x + t} = {r2}×{x + t}.")

@ejercicio(T, peso=3)
def ecuacion(rng):
    kind = rng.choice(["lineal", "fracciones", "consecutivos", "mitad"])
    if kind == "lineal":
        x = rng.randint(2, 15); a, c = rng.choice([(5, 2), (4, 1), (7, 3), (6, 2), (3, 1), (8, 5)]); b = rng.randint(1, 12)
        d = a * x + b - c * x
        q = f"Si {a}x + {b} = {c}x + {d}, ¿cuánto vale x?"; tr = f"Pasa las x a un lado: {a - c}x = {d - b} ⇒ x = {x}."
    elif kind == "fracciones":
        k = rng.randint(2, 8); x = 6 * k
        q = f"x/2 + x/3 = {5 * k}. ¿Cuánto vale x?"; tr = f"x/2 + x/3 = 5x/6 = {5 * k} ⇒ x = {5 * k}×6/5 = {x}."
    elif kind == "consecutivos":
        n = rng.randint(5, 40); x = n + 1; s = 3 * n + 3
        q = f"La suma de tres números consecutivos es {s}. ¿Cuál es el mayor?"; x = n + 2
        tr = f"El de en medio es la media: {s} ÷ 3 = {n + 1}. El mayor es {n + 2}."
    else:
        x = 4 * rng.randint(3, 15); a = x // 2 + rng.choice([6, 8, 10]); b = (x * 3) // 4
        q = f"La mitad de un número más {b - x // 2} es igual a sus tres cuartas partes. ¿Qué número es?"
        tr = f"x/2 + {b - x // 2} = 3x/4 ⇒ {b - x // 2} = x/4 ⇒ x = {x}."
    ops, i = mezclar(x, distractores_num(x, rng), rng)
    return dict(enunciado=q, opciones=ops, correcta=i, truco=tr)

@ejercicio(T, peso=3)
def combinatoria(rng):
    kind = rng.choice(["fila", "producto", "manos", "comite", "palabras", "liga", "numeros", "mesa"])
    if kind == "fila":
        n = rng.choice([3, 4, 5]); r = math.factorial(n)
        q = f"¿De cuántas formas distintas pueden sentarse {n} personas en {n} sillas en fila?"; tr = f"{n}! = {'×'.join(map(str, range(n, 0, -1)))} = {r}."
        ex = [n * n, r * 2, r // 2]
    elif kind == "producto":
        a, b, c = rng.randint(2, 5), rng.randint(2, 5), rng.randint(2, 4); r = a * b * c
        q = f"Con {a} camisas, {b} pantalones y {c} pares de zapatos, ¿cuántos conjuntos distintos se pueden formar?"; tr = f"Se multiplican las opciones: {a}×{b}×{c} = {r}."
        ex = [a + b + c, r * 2, a * b]
    elif kind == "manos":
        n = rng.randint(5, 12); r = n * (n - 1) // 2
        q = f"En una reunión hay {n} personas y todas se saludan con un apretón de manos. ¿Cuántos apretones hay?"; tr = f"{n}×{n - 1}/2 = {r} (cada pareja una sola vez)."
        ex = [n * (n - 1), n * n // 2, n]
    elif kind == "comite":
        n, k = rng.choice([(5, 2), (6, 2), (6, 3), (7, 2), (8, 2), (5, 3), (7, 3)]); r = math.comb(n, k)
        q = f"De un grupo de {n} personas hay que elegir {k} para formar una comisión (sin cargos distintos). ¿Cuántas comisiones posibles hay?"
        tr = f"Combinaciones: {n}!/({k}!·{n - k}!) = {r}. Si importara el orden serían {math.perm(n, k)}."
        ex = [math.perm(n, k), n * k, r + n]
    elif kind == "palabras":
        w = rng.choice(["LUNA", "AMOR", "ROMA", "PATO", "SOL"]); r = math.factorial(len(w))
        q = f"¿Cuántas palabras distintas, tengan sentido o no, se pueden escribir con todas las letras de {w}?"; tr = f"Cada letra se usa una vez: {len(w)}! = {r}."
        ex = [len(w) ** 2, r * 2, r // 2]
    elif kind == "liga":
        n = rng.randint(4, 10); r = n * (n - 1)
        q = f"En una liga de {n} equipos todos juegan contra todos a ida y vuelta. ¿Cuántos partidos se juegan?"; tr = f"Cada equipo juega {n - 1} partidos de ida y {n - 1}/... más sencillo: {n}×{n - 1} = {r} (ida y vuelta cuentan por separado)."
        tr = f"Cada equipo juega contra {n - 1} rivales; {n}×{n - 1} = {r}. Si fuera solo ida: {r // 2}."
        ex = [r // 2, n * n, r + n]
    elif kind == "numeros":
        r = 60; q = "¿Cuántos números de tres cifras distintas se pueden formar con los dígitos 1, 2, 3, 4 y 5?"; tr = "5 opciones para la primera cifra, 4 para la segunda y 3 para la tercera: 5×4×3 = 60."
        ex = [125, 15, 120]
    else:
        n = rng.choice([4, 5, 6]); r = math.factorial(n - 1)
        q = f"¿De cuántas formas pueden sentarse {n} personas alrededor de una mesa redonda (los giros cuentan como la misma disposición)?"; tr = f"Se fija a una persona y las demás se ordenan: ({n}−1)! = {r}."
        ex = [math.factorial(n), n * n, r * 2]
    ops, i = mezclar(r, distractores_num(r, rng, extras=ex), rng)
    return dict(enunciado=q, opciones=ops, correcta=i, truco=tr)

@ejercicio(T, peso=1)
def encuentro(rng):
    v1, v2 = rng.choice([(60, 40), (50, 30), (70, 50), (40, 20), (80, 40), (45, 35)]); t = rng.randint(2, 6); d = (v1 + v2) * t
    ops, i = mezclar(f"{t} h", [f"{x} h" for x in distractores_num(t, rng, extras=[d // v1, d // v2])], rng)
    return dict(enunciado=f"Dos trenes salen a la vez de dos ciudades separadas {d} km y avanzan el uno hacia el otro a {v1} y {v2} km/h. ¿Cuánto tardan en cruzarse?",
                opciones=ops, correcta=i, truco=f"Se acercan a {v1}+{v2} = {v1 + v2} km/h: {d} ÷ {v1 + v2} = {t} h.")
