from fractions import Fraction as F
from .nucleo import ejercicio, num, pct, mezclar, distractores_num

T = "Porcentajes"
# porcentajes que se pueden pasar a fraccion facilmente
FRAC = [F(1, 10), F(1, 5), F(1, 4), F(1, 2), F(3, 4), F(1, 8), F(3, 8), F(5, 8), F(7, 8), F(2, 5), F(3, 5),
        F(4, 5), F(1, 20), F(3, 20), F(3, 10), F(7, 10), F(9, 10), F(1, 3), F(2, 3), F(1, 6), F(5, 6)]

def fr(f): return f"{f.numerator}/{f.denominator}"

@ejercicio(T, peso=3)
def porcentaje_de(rng):
    f = rng.choice(FRAC); n = f.denominator * rng.randint(2, 40) * (1 if f.denominator > 5 else rng.choice([1, 2, 5]))
    while n < 24 or n > 600: n = f.denominator * rng.randint(2, 40)
    r = int(n * f)
    ops, i = mezclar(num(r), [num(x) for x in distractores_num(r, rng, extras=[n - r, n // f.denominator])], rng)
    return dict(enunciado=f"¿Cuánto es el {pct(f)} de {num(n)}?", opciones=ops, correcta=i,
                truco=f"{pct(f)} = {fr(f)}. {num(n)} ÷ {f.denominator} × {f.numerator} = {num(r)}.")

@ejercicio(T, peso=3)
def porcentaje_inverso(rng):
    f = rng.choice([x for x in FRAC if x < 1]); n = f.denominator * rng.randint(2, 30)
    r = int(n * f)
    ops, i = mezclar(num(n), [num(x) for x in distractores_num(n, rng, extras=[r * 2, r * 4, n - r])], rng)
    return dict(enunciado=f"El {pct(f)} de un número es {num(r)}. ¿Cuál es el número?", opciones=ops, correcta=i,
                truco=f"{pct(f)} = {fr(f)}: {num(r)} son {f.numerator} partes de {f.denominator}. "
                      f"Una parte = {num(r // f.numerator) if r % f.numerator == 0 else num(F(r, f.numerator))}; "
                      f"el total = {num(n)}.")

@ejercicio(T, peso=2)
def que_porcentaje(rng):
    f = rng.choice([x for x in FRAC if x < 1]); b = f.denominator * rng.randint(2, 12) * rng.choice([1, 2, 5])
    a = int(b * f); c = pct(f)
    falsas = [pct(1 - f), pct(F(b - a, a)) if a else "10%", pct(F(a, 100)), pct(F(a, b) / 2)]
    ops, i = mezclar(c, falsas + [pct(F(1, 3)), pct(F(7, 10))], rng)
    return dict(enunciado=f"¿Qué porcentaje de {num(b)} es {num(a)}?", opciones=ops, correcta=i,
                truco=f"{num(a)}/{num(b)} se simplifica a {fr(f)} = {c}.")

@ejercicio(T, peso=2)
def variacion(rng):
    f = rng.choice([F(1, 10), F(1, 5), F(1, 4), F(1, 2), F(3, 4), F(1, 8), F(1, 3)])
    sube = rng.random() < .5
    a = f.denominator * rng.randint(2, 15) * 2
    b = int(a * (1 + f)) if sube else int(a * (1 - f))
    falsas = [pct(F(abs(b - a), b)), pct(F(abs(b - a), a) / 2), pct(F(abs(b - a), a) * 2), pct(F(abs(b - a), a) + F(1, 10))]
    ops, i = mezclar(pct(f), falsas, rng)
    return dict(enunciado=f"Un valor pasa de {num(a)} a {num(b)}. ¿En qué porcentaje {'aumenta' if sube else 'disminuye'}?",
                opciones=ops, correcta=i,
                truco=f"Diferencia {num(abs(b - a))} sobre el valor de partida ({num(a)}): {fr(F(abs(b - a), a))} = {pct(f)}. "
                      f"Siempre se divide entre el valor inicial.")

@ejercicio(T, peso=2)
def sube_y_baja(rng):
    p = rng.choice([F(1, 10), F(1, 5), F(1, 4), F(3, 10), F(2, 5), F(1, 2)])
    total = (1 + p) * (1 - p) - 1   # negativo
    sobre = rng.random() < .5
    if sobre: total = (1 - p) * (1 + p) - 1
    corr = f"Baja un {pct(-total)}"
    falsas = ["Se queda igual", f"Sube un {pct(-total)}", f"Baja un {pct(p)}", f"Baja un {pct(-total * 2)}"]
    ops, i = mezclar(corr, falsas, rng)
    orden = "sube un {0} y después baja un {0}" if not sobre else "baja un {0} y después sube un {0}"
    return dict(enunciado=f"Un precio {orden.format(pct(p))}. ¿Cuál es el efecto total?", opciones=ops, correcta=i,
                truco=f"Los porcentajes no se compensan: (1+{fr(p)})·(1−{fr(p)}) = 1 − {fr(p * p)} ⇒ pierde {pct(-total)}.")

@ejercicio(T, peso=2)
def descuentos(rng):
    d1, d2 = rng.sample([F(1, 10), F(1, 5), F(1, 4), F(1, 2)], 2)
    while True:
        p = rng.choice([40, 60, 80, 120, 160, 200, 240, 400])
        fin = p * (1 - d1) * (1 - d2)
        if fin.denominator == 1: break
    fin = int(fin); suma = int(p * (1 - d1 - d2))
    ops, i = mezclar(num(fin) + " €", [num(suma) + " €", num(int(p * (1 - d1))) + " €", num(fin + 4) + " €", num(fin - 4) + " €"], rng)
    return dict(enunciado=f"Una chaqueta de {num(p)} € tiene un {pct(d1)} de descuento y, sobre el nuevo precio, otro {pct(d2)}. ¿Cuánto cuesta?",
                opciones=ops, correcta=i,
                truco=f"No se suman ({pct(d1 + d2)}): se multiplican {pct(1 - d1)} × {pct(1 - d2)} = {pct((1 - d1) * (1 - d2))} del precio ⇒ {num(fin)} €.")

@ejercicio(T, peso=2)
def iva(rng):
    tasa, mult = rng.choice([(F(21, 100), 100), (F(1, 10), 10), (F(1, 5), 5), (F(1, 4), 4), (F(1, 2), 2)])
    base = mult * rng.randint(1, 12) * (1 if mult >= 10 else 10)
    con = int(base * (1 + tasa))
    ops, i = mezclar(num(base) + " €", [num(int(con * (1 - tasa))) + " €", num(con - int(con * tasa) - 2) + " €", num(base + 10) + " €", num(base - 10) + " €"], rng)
    return dict(enunciado=f"Un producto cuesta {num(con)} € con un IVA del {pct(tasa)}. ¿Cuánto costaba sin IVA?", opciones=ops, correcta=i,
                truco=f"El precio con IVA es el {pct(1 + tasa)} del original: {num(con)} ÷ {num(float(1 + tasa))} = {num(base)}. "
                      f"Restar el {pct(tasa)} al precio final es el error típico.")

@ejercicio(T, peso=1)
def porcentaje_de_porcentaje(rng):
    f1, f2 = rng.sample([F(1, 2), F(1, 4), F(1, 5), F(3, 4), F(2, 5), F(1, 10)], 2)
    n = rng.choice([40, 80, 100, 120, 160, 200, 240, 400, 800])
    r = n * f1 * f2
    if r.denominator != 1: return porcentaje_de_porcentaje(rng)
    r = int(r)
    ops, i = mezclar(num(r), [num(x) for x in distractores_num(r, rng, extras=[int(n * (f1 + f2)), int(n * f1)])], rng)
    return dict(enunciado=f"En una clase de {n} alumnos, el {pct(f1)} son chicas y de ellas el {pct(f2)} lleva gafas. ¿Cuántas chicas llevan gafas?",
                opciones=ops, correcta=i,
                truco=f"{fr(f1)} de {n} = {int(n * f1)}; {fr(f2)} de eso = {num(r)}. Se multiplican las fracciones, no se suman.")
