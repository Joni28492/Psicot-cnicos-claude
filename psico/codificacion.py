from .nucleo import ejercicio, mezclar, ALFABETO, ALFABETO26

T = "Codificación"
PALABRAS = ["CASA", "MESA", "PERRO", "GATO", "LIBRO", "LUNA", "AGUA", "TREN", "FLOR", "NUBE", "PLAYA", "CARTA", "PUERTA",
            "MANO", "NIÑO", "SOL", "MAR", "PAN", "OSO", "NIDO", "ROMA", "PINO", "LAGO", "MONTE", "NORTE", "PLATO", "OJO", "MUNDO"]

def desplazar(p, k, alf=ALFABETO):
    n = len(alf)
    return "".join(alf[(alf.index(c) + k) % n] if c in alf else c for c in p)

@ejercicio(T, peso=3)
def cesar(rng):
    k = rng.choice([1, 2, 3, -1, -2]); ej = rng.choice(PALABRAS)
    cand = [p for p in PALABRAS if p != ej and desplazar(p, k) != desplazar(p, k, ALFABETO26)]
    p = rng.choice(cand or PALABRAS)
    corr = desplazar(p, k)
    falsas = [desplazar(p, k, ALFABETO26), desplazar(p, k + 1), desplazar(p, k - 1), corr[::-1], desplazar(p, -k)]
    ops, i = mezclar(corr, falsas, rng)
    return dict(enunciado=f"En un código, {ej} se escribe {desplazar(ej, k)}. Con el mismo código, ¿cómo se escribe {p}?",
                opciones=ops, correcta=i,
                truco=f"Cada letra se desplaza {k:+d} posiciones. Usa el alfabeto español de 27 letras: la Ñ cuenta (entre N y O).")

@ejercicio(T, peso=3)
def valor_palabra(rng):
    p = rng.choice([x for x in PALABRAS if len(x) <= 4])
    v = sum(ALFABETO.index(c) + 1 for c in p); v26 = sum(ALFABETO26.index(c) + 1 for c in p)
    ops, i = mezclar(v, [v26, v + 1, v - 1, v + 3, v - 2], rng)
    return dict(enunciado=f"Si A=1, B=2, C=3… (27 letras, con Ñ=15), ¿cuánto vale la palabra {p}?", opciones=ops, correcta=i,
                truco="Posiciones: " + " + ".join(str(ALFABETO.index(c) + 1) + f"({c})" for c in p) + f" = {v}. A partir de la O, cada letra vale 1 más que en un alfabeto de 26.")

@ejercicio(T, peso=2)
def espejo(rng):
    p = rng.choice([x for x in PALABRAS if len(x) <= 4])
    esp = lambda w, alf: "".join(alf[len(alf) - 1 - alf.index(c)] for c in w)
    corr = esp(p, ALFABETO)
    ops, i = mezclar(corr, [esp(p, ALFABETO26), corr[::-1], desplazar(corr, 1), desplazar(corr, -1)], rng)
    return dict(enunciado=f"Cada letra se sustituye por su simétrica en el alfabeto (A↔Z, B↔Y, C↔X…). ¿Cómo se escribe {p}?",
                opciones=ops, correcta=i,
                truco="Con 27 letras la pareja de la posición n es la 28−n: A(1)↔Z(27), M(13)↔Ñ(15), y la N(14) se queda en N.")

@ejercicio(T, peso=2)
def vocales(rng):
    p = rng.choice(["CAMINO", "VENTANA", "PUERTA", "CIUDAD", "BOTELLA", "MONTAÑA", "LIBRETA", "ESCUELA", "CAMISA"])
    cod = {"A": "1", "E": "2", "I": "3", "O": "4", "U": "5"}
    corr = "".join(cod.get(c, c) for c in p)
    otro = {"A": "5", "E": "4", "I": "3", "O": "2", "U": "1"}
    falsas = ["".join(otro.get(c, c) for c in p), "".join(cod.get(c, "") for c in p), corr[::-1],
              "".join(cod.get(c, c) if k != 1 else c for k, c in enumerate(p)), corr.replace("1", "2", 1)]
    ops, i = mezclar(corr, falsas, rng)
    return dict(enunciado=f"Se sustituyen las vocales por números (A=1, E=2, I=3, O=4, U=5) y las consonantes no cambian. ¿Cómo se escribe {p}?",
                opciones=ops, correcta=i, truco="Recorre la palabra letra a letra; no cambies el orden ni borres consonantes.")

@ejercicio(T, peso=3)
def digitos(rng):
    letras = rng.sample("ABCDEFGHILMNOPRST", 6); ds = rng.sample("123456789", 6); m = dict(zip(letras, ds))
    a, b, c, d, e, f = letras
    w1, w2 = [a, b, c, d], [c, d, e, f]
    rng.shuffle(w1); rng.shuffle(w2)
    q = [rng.choice([a, b]), rng.choice([e, f]), rng.choice([a, b, e, f]), rng.choice([c, d])]
    cod = lambda w: "".join(m[x] for x in w)
    corr = cod(q)
    falsas = [cod(q[::-1]), cod([q[1], q[0]] + q[2:]), corr[:-1] + str((int(corr[-1]) % 9) + 1), cod(q[:3] + [rng.choice([a, b, e, f])])]
    ops, i = mezclar(corr, falsas, rng)
    return dict(enunciado=f"En un código, {''.join(w1)} = {cod(w1)} y {''.join(w2)} = {cod(w2)}. Con el mismo código, ¿cómo se escribe {''.join(q)}?",
                opciones=ops, correcta=i,
                truco="Anota qué cifra corresponde a cada letra usando las dos palabras de ejemplo y sustituye en orden: " +
                      ", ".join(f"{k}={v}" for k, v in sorted(m.items())) + ".")

COSAS = [("el cielo", "azul"), ("la hierba", "verde"), ("el carbón", "negro"), ("la nieve", "blanco"), ("el sol", "amarillo"), ("la sangre", "rojo")]

@ejercicio(T, peso=2)
def renombrar(rng):
    obj, real = rng.choice(COSAS)
    otros = [c for c in ["rojo", "verde", "azul", "amarillo", "negro", "blanco"] if c != real]
    x, y = rng.sample(otros, 2)
    ciclo = [real, x, y]; rng.shuffle(ciclo)
    nuevo = {ciclo[0]: ciclo[1], ciclo[1]: ciclo[2], ciclo[2]: ciclo[0]}
    corr = nuevo[real]
    ops, i = mezclar(corr, [c for c in ["rojo", "verde", "azul", "amarillo", "negro", "blanco"] if c != corr][:6], rng)
    return dict(enunciado=f"Llamamos {nuevo[ciclo[0]]} al {ciclo[0]}, {nuevo[ciclo[1]]} al {ciclo[1]} y {nuevo[ciclo[2]]} al {ciclo[2]}. "
                          f"Con esos nombres, ¿de qué color es {obj}?", opciones=ops, correcta=i,
                truco=f"{obj.capitalize()} es {real} de verdad, y a ese color ahora lo llamamos {corr}.")
