from .nucleo import ejercicio, num, mezclar, distractores_num, divisores

T = "Reglas de tres"

DIRECTAS = [
    ("{a} kg de naranjas cuestan {b} €. ¿Cuánto cuestan {c} kg?", " €"),
    ("Un coche recorre {b} km con {a} litros. ¿Cuántos km recorre con {c} litros?", " km"),
    ("{a} cuadernos cuestan {b} €. ¿Cuánto cuestan {c} cuadernos?", " €"),
    ("Un grifo vierte {b} litros en {a} minutos. ¿Cuántos litros vierte en {c} minutos?", " litros"),
    ("En un mapa, {a} cm equivalen a {b} km. ¿A cuántos km equivalen {c} cm?", " km"),
]

@ejercicio(T, peso=3)
def directa(rng):
    u = rng.choice([1.5, 2, 2.5, 3, 4, 5, 6, 8])
    a = rng.randint(2, 8); c = rng.choice([x for x in range(3, 17) if x != a])
    b, r = a * u, c * u
    txt, uni = rng.choice(DIRECTAS)
    corr = num(r)
    extra = [num(b + (c - a)), num(a * b / c) if (a * b) % c == 0 else num(b * 2)]
    ops, i = mezclar(corr + uni, [e + uni for e in extra + [num(r + 1), num(r - 1), num(r * 2)]], rng)
    return dict(enunciado=txt.format(a=num(a), b=num(b), c=num(c)), opciones=ops, correcta=i,
                truco=f"Busca el valor de una unidad: {num(b)} ÷ {num(a)} = {num(b / a)}; luego ×{num(c)}. "
                      f"No sumes la diferencia ({num(c - a)}) al resultado.")

INV = [
    ("{a} obreros tardan {t} días en hacer una obra. ¿Cuántos días tardarían {c} obreros?", " días"),
    ("{a} bombas vacían una piscina en {t} horas. ¿Cuántas horas tardarían {c} bombas?", " horas"),
    ("Con {a} cajeros se atiende la cola en {t} minutos. ¿Cuántos minutos con {c} cajeros?", " minutos"),
    ("Un tren a {a} km/h tarda {t} h en llegar. ¿Cuántas horas tardará a {c} km/h?", " h"),
]

@ejercicio(T, peso=3)
def inversa(rng):
    a = rng.choice([2, 3, 4, 5, 6, 8]); t = rng.choice([6, 8, 10, 12, 15, 20, 24])
    tot = a * t
    cs = [d for d in divisores(tot) if 2 <= d <= 40 and d != a]
    c = rng.choice(cs); r = tot // c
    txt, uni = rng.choice(INV)
    mal = num(t * c // a) if (t * c) % a == 0 else num(t + (c - a))
    ops, i = mezclar(num(r) + uni, [mal + uni] + [x + uni for x in map(num, distractores_num(r, rng))], rng)
    return dict(enunciado=txt.format(a=a, t=t, c=c), opciones=ops, correcta=i,
                truco=f"Es inversa (más recursos ⇒ menos tiempo): el producto se mantiene. "
                      f"{a} × {t} = {tot}; {tot} ÷ {c} = {r}.")

@ejercicio(T, peso=3)
def compuesta(rng):
    r = rng.randint(2, 9); m1, h1 = rng.randint(2, 6), rng.randint(2, 8)
    m2, h2 = rng.choice([x for x in range(2, 9) if x != m1]), rng.choice([x for x in range(2, 9) if x != h1])
    p1, p2 = m1 * h1 * r, m2 * h2 * r
    ops, i = mezclar(num(p2), [num(x) for x in distractores_num(p2, rng, extras=[p1 * m2 // m1, p1 * h2 // h1])], rng)
    return dict(enunciado=f"{m1} máquinas fabrican {num(p1)} piezas en {h1} horas. "
                          f"¿Cuántas piezas fabrican {m2} máquinas en {h2} horas?",
                opciones=ops, correcta=i,
                truco=f"Piezas por máquina y hora: {num(p1)} ÷ ({m1}×{h1}) = {r}. Luego {m2}×{h2}×{r} = {num(p2)}.")

PARES = [(6, 3), (12, 4), (10, 15), (20, 5), (6, 12), (30, 20), (15, 10), (12, 6), (8, 8), (4, 12), (9, 18), (10, 40)]

@ejercicio(T, peso=2)
def trabajo_conjunto(rng):
    a, b = rng.choice(PARES)
    if rng.random() < .5: a, b = b, a
    r = a * b // (a + b)
    if a * b % (a + b): return trabajo_conjunto(rng)
    obj = rng.choice([("Un grifo llena un depósito en {a} h y otro en {b} h", "¿Cuánto tardan abriendo los dos a la vez?"),
                      ("Ana pinta una pared en {a} h y Luis en {b} h", "¿Cuánto tardan trabajando juntos?"),
                      ("Una impresora hace un trabajo en {a} min y otra en {b} min", "¿Cuánto tardan las dos juntas?")])
    uni = " min" if "min" in obj[0] else " h"
    ops, i = mezclar(num(r) + uni, [x + uni for x in map(num, distractores_num(r, rng, extras=[(a + b) // 2, a + b, abs(a - b)]))], rng)
    return dict(enunciado=obj[0].format(a=a, b=b) + ". " + obj[1], opciones=ops, correcta=i,
                truco=f"Suma lo que hace cada uno en una hora: 1/{a} + 1/{b} = {a + b}/{a * b} ⇒ tardan {a * b}/{a + b} = {r}. "
                      f"Atajo: producto ÷ suma.")
