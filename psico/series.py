from .nucleo import ejercicio, num, mezclar, distractores_num, letra, indice, ALFABETO

T = "Series"

def cruza_enie(idx):
    """idx: indices sin envolver. Avisa si algun salto pasa por la Ñ (posicion 15)."""
    w = [i % 27 for i in idx]
    return any(a < 14 < b or a == 14 or b == 14 for a, b in zip(w, w[1:])) or w[-1] == 14

NOTA = " Ojo: en el alfabeto español la Ñ va entre la N y la O (27 letras)."

def serie_texto(items):
    return ", ".join(items) + ", ?"

def vecinos_letra(ans_idx, rng, extra=()):
    c = [letra(ans_idx + d) for d in (1, -1, 2, -2, 3)]
    rng.shuffle(c)
    return list(extra) + c

# ------------------------------------------------ letras
@ejercicio(T, peso=2)
def letras_salto(rng):
    d = rng.choice([2, 3, 4, 5, -2, -3]); s = rng.randint(0, 26)
    idx = [s + d * k for k in range(6)]
    ops, i = mezclar(letra(idx[5]), vecinos_letra(idx[5], rng, [letra(idx[5] + d)]), rng)
    return dict(enunciado="¿Qué letra continúa la serie?", destacado=serie_texto([letra(x) for x in idx[:5]]), opciones=ops, correcta=i,
                truco=f"Cada letra {'avanza' if d > 0 else 'retrocede'} {abs(d)} posiciones." + (NOTA if cruza_enie(idx) else ""))

@ejercicio(T, peso=2)
def letras_creciente(rng):
    s = rng.randint(0, 26); st = rng.choice([1, 2]); idx = [s]
    for k in range(5): idx.append(idx[-1] + st + k)
    ops, i = mezclar(letra(idx[5]), vecinos_letra(idx[5], rng), rng)
    return dict(enunciado="¿Qué letra continúa la serie?", destacado=serie_texto([letra(x) for x in idx[:5]]), opciones=ops, correcta=i,
                truco=f"Los saltos crecen: +{st}, +{st + 1}, +{st + 2}, +{st + 3}… el siguiente es +{st + 4}." + (NOTA if cruza_enie(idx) else ""))

@ejercicio(T, peso=2)
def letras_alternas(rng):
    a0, b0 = rng.randint(0, 26), rng.randint(0, 26); ka, kb = rng.choice([1, 2, 3, -1, -2]), rng.choice([1, 2, 3, -1, -2, 4])
    idx = []
    for n in range(4): idx += [a0 + ka * n, b0 + kb * n]
    ops, i = mezclar(letra(idx[7]), vecinos_letra(idx[7], rng, [letra(idx[5] + kb * 2), letra(idx[6] + ka)]), rng)
    return dict(enunciado="¿Qué letra continúa la serie?", destacado=serie_texto([letra(x) for x in idx[:7]]), opciones=ops, correcta=i,
                truco=f"Son dos series entrelazadas: posiciones impares {ka:+d} y pares {kb:+d}. Falta la de las pares." + (NOTA if cruza_enie(idx) else ""))

@ejercicio(T, peso=1)
def letras_bloques(rng):
    s = rng.randint(0, 20); st = rng.choice([2, 3, 4])
    items = [letra(s + st * k) + letra(s + st * k + 1) for k in range(5)]
    idx = [s + st * k for k in range(6)]
    ans = letra(idx[5]) + letra(idx[5] + 1)
    fals = [letra(idx[5] + 1) + letra(idx[5] + 2), letra(idx[5] - 1) + letra(idx[5]), letra(idx[5]) + letra(idx[5] + 2), letra(idx[5] + 1) + letra(idx[5])]
    ops, i = mezclar(ans, fals, rng)
    return dict(enunciado="¿Qué pareja continúa la serie?", destacado=serie_texto(items[:5]), opciones=ops, correcta=i,
                truco=f"Cada pareja son dos letras seguidas y el bloque avanza {st} posiciones." + (NOTA if cruza_enie(idx + [idx[-1] + 1]) else ""))

@ejercicio(T, peso=2)
def letra_numero(rng):
    s = rng.randint(0, 20); d = rng.choice([1, 2, 3]); regla = rng.choice(["+", "x2", "+2"])
    n0 = rng.choice([1, 2, 3])
    nums = [n0]
    for _ in range(5): nums.append(nums[-1] * 2 if regla == "x2" else nums[-1] + (1 if regla == "+" else 2))
    items = [f"{letra(s + d * k)}{nums[k]}" for k in range(5)]
    ans = f"{letra(s + d * 5)}{nums[5]}"
    fals = [f"{letra(s + d * 5)}{nums[5] + 1}", f"{letra(s + d * 5 + 1)}{nums[5]}", f"{letra(s + d * 4)}{nums[5]}", f"{letra(s + d * 5)}{nums[4] + (nums[4] - nums[3])}"]
    ops, i = mezclar(ans, fals, rng)
    rn = {"+": "+1", "x2": "×2", "+2": "+2"}[regla]
    idx = [s + d * k for k in range(6)]
    return dict(enunciado="¿Qué término continúa la serie?", destacado=serie_texto(items), opciones=ops, correcta=i,
                truco=f"Dos reglas independientes: las letras avanzan {d} y los números hacen {rn}." + (NOTA if cruza_enie(idx) else ""))

# ------------------------------------------------ numeros
def numerica(rng, nombre, termino, truco, enun="¿Qué número continúa la serie?", extras=lambda s: []):
    ans = termino[5]
    ops, i = mezclar(num(ans), [num(x) for x in distractores_num(ans, rng, extras=extras(termino))], rng)
    return dict(enunciado=enun, destacado=", ".join(num(x) for x in termino[:5]) + ", ?", opciones=ops, correcta=i, truco=truco)

@ejercicio(T, peso=2)
def num_aritmetica(rng):
    a, d = rng.randint(1, 40), rng.choice([3, 4, 5, 6, 7, 8, 9, 11, -3, -4, -6])
    s = [a + d * k for k in range(6)]
    if min(s) < 0: return num_aritmetica(rng)
    return numerica(rng, "", s, f"Suma constante: {d:+d} en cada paso.", extras=lambda t: [t[4] + d + 1, t[4] + d - 1])

@ejercicio(T, peso=2)
def num_geometrica(rng):
    a, r = rng.choice([1, 2, 3, 4, 5]), rng.choice([2, 3, 4])
    s = [a * r ** k for k in range(6)]
    return numerica(rng, "", s, f"Cada término se multiplica por {r}.", extras=lambda t: [t[4] + t[3], t[4] + (t[4] - t[3])])

@ejercicio(T, peso=3)
def num_creciente(rng):
    a, d0, k = rng.randint(1, 20), rng.choice([1, 2, 3]), rng.choice([1, 2, 3])
    s, d = [a], d0
    for _ in range(5): s.append(s[-1] + d); d += k
    ds = [s[j + 1] - s[j] for j in range(5)]
    return numerica(rng, "", s, f"Las diferencias son {', '.join(map(str, ds[:4]))}… y crecen {k} cada vez: la siguiente es +{ds[4]}.",
                    extras=lambda t: [t[4] + (t[4] - t[3])])

@ejercicio(T, peso=2)
def num_alternas(rng):
    a, b = rng.randint(1, 20), rng.randint(30, 80); ka, kb = rng.choice([2, 3, 4, 5]), rng.choice([-2, -3, -4, 5, 6])
    s = []
    for n in range(4): s += [a + ka * n, b + kb * n]
    ans = s[7]
    ops, i = mezclar(num(ans), [num(x) for x in distractores_num(ans, rng, extras=[s[5] + ka * 2 if False else s[6] + ka, s[5] + kb + 1])], rng)
    return dict(enunciado="¿Qué número continúa la serie?", destacado=", ".join(map(num, s[:7])) + ", ?", opciones=ops, correcta=i,
                truco=f"Dos series entrelazadas: lugares impares {ka:+d}, lugares pares {kb:+d}. Toca un lugar par: {s[5]} {kb:+d} = {ans}.")

@ejercicio(T, peso=2)
def num_cuadrados(rng):
    n0, c = rng.randint(1, 4), rng.choice([0, 0, 1, -1, 2])
    s = [(n0 + k) ** 2 + c for k in range(6)]
    return numerica(rng, "", s, f"Son cuadrados{'' if c == 0 else f' {c:+d}'}: {', '.join(f'{n0 + k}²' for k in range(3))}… El siguiente es {n0 + 5}²{'' if c == 0 else f' {c:+d}'} = {s[5]}.",
                    extras=lambda t: [t[4] + (t[4] - t[3]) + 2])

@ejercicio(T, peso=2)
def num_fibonacci(rng):
    a, b = rng.randint(1, 5), rng.randint(2, 7); s = [a, b]
    for _ in range(4): s.append(s[-1] + s[-2])
    return numerica(rng, "", s, "Cada término es la suma de los dos anteriores.", extras=lambda t: [t[4] + t[4] - t[3], t[4] + t[3] + 1])

@ejercicio(T, peso=2)
def num_operaciones(rng):
    m, c = rng.choice([2, 3]), rng.choice([-2, -1, 1, 2, 3]); a = rng.randint(1, 6); s = [a]
    for _ in range(5): s.append(s[-1] * m + c)
    return numerica(rng, "", s, f"Cada término = anterior ×{m} {c:+d}.", extras=lambda t: [t[4] * m, t[4] + (t[4] - t[3])])

@ejercicio(T, peso=1)
def num_dos_operaciones(rng):
    p, m = rng.choice([2, 3, 4, 5, 6]), rng.choice([2, 3]); a = rng.randint(1, 5); s = [a]
    for k in range(5): s.append(s[-1] + p if k % 2 == 0 else s[-1] * m)
    return numerica(rng, "", s, f"Se alternan dos operaciones: +{p} y ×{m}.", extras=lambda t: [t[4] + p if False else t[4] * m, t[4] + (t[4] - t[3])])

@ejercicio(T, peso=1)
def num_primos_o_triangulares(rng):
    if rng.random() < .5:
        pr = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]; k = rng.randint(0, 4); s = pr[k:k + 6]
        return numerica(rng, "", s, "Son los números primos consecutivos.", extras=lambda t: [t[4] + 2, t[4] + 4])
    k = rng.randint(2, 5); s = [n * (n + 1) // 2 for n in range(k, k + 6)]
    return numerica(rng, "", s, "Números triangulares: se suma 1 más cada vez a la diferencia anterior (n·(n+1)/2).", extras=lambda t: [t[4] + (t[4] - t[3])])
