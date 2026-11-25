"""Comprension lectora: textos de 2-3 parrafos con una pregunta cuya respuesta no esta escrita, hay que deducirla.

Cuatro familias (todas con la respuesta calculada, no escrita en el texto):
  orden       ¿quien ocupo tal posicion? Las pistas son relativas (antes que, justo despues de...) y hay que encadenarlas.
  reglas      una norma con condiciones (y / o / salvo) y varios casos: ¿a quien se le concede, a quien no, cuantos?
  condicional «si p entonces q», «si q entonces r» y un dato: ¿que se puede afirmar con seguridad? (incluye falacias)
  cifras      variaciones porcentuales encadenadas contadas en prosa: ¿cual es la cifra final?
El texto va en el campo `texto` (lista de parrafos) y la pregunta en `enunciado`.
"""
import itertools
from fractions import Fraction
from .nucleo import ejercicio, num, mezclar, distractores_num

T = "Comprensión lectora"
NOMBRES = ["Ana", "Luis", "Marta", "Pedro", "Lucía", "Carlos", "Elena", "Raúl", "Sara", "Iván", "Nuria", "Hugo"]
APELLIDOS = ["García", "López", "Ruiz", "Navarro", "Moreno", "Vidal", "Castro", "Ortega", "Soler", "Prieto"]
ORDINAL = ["primera", "segunda", "tercera", "cuarta", "quinta"]

def cap(s):
    return s[0].upper() + s[1:]

def lista(xs):
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]

# ------------------------------------------------------------------ orden
ESCENARIOS_ORDEN = [
    ("En la oficina de turismo se atiende por orden de llegada. Ayer {n} personas esperaron para pedir información sobre rutas y horarios.",
     "El registro lo llevó una única persona, que anotó el orden con cuidado."),
    ("En la carrera popular del barrio participaron {n} amigos, y la organización anotó el orden en que cruzó cada uno la línea de meta.",
     "Nadie abandonó y no hubo ningún empate."),
    ("Una academia convocó a {n} aspirantes a una prueba de acceso y registró el momento en que cada uno llegó al aula.",
     "El aula se abrió a la hora prevista y ninguna persona llegó a la vez que otra."),
]

def cumple(c, perm):
    pos = {x: i for i, x in enumerate(perm)}
    k = c[0]
    if k == "antes": return pos[c[1]] < pos[c[2]]
    if k == "justo": return pos[c[1]] + 1 == pos[c[2]]
    if k == "primero": return pos[c[1]] == 0
    return pos[c[1]] == len(perm) - 1

def frase_orden(rng, c):
    k = c[0]
    if k == "antes": return rng.choice([f"{c[1]} llegó antes que {c[2]}.", f"{c[2]} llegó después de {c[1]}."])
    if k == "justo": return rng.choice([f"{c[1]} llegó justo antes de {c[2]}.", f"{c[2]} llegó justo después de {c[1]}."])
    if k == "primero": return f"{c[1]} abrió la fila."
    return f"{c[1]} cerró la fila."

@ejercicio(T, peso=2, tiempo=60)
def orden(rng):
    n = rng.choice([4, 5])
    nombres = rng.sample(NOMBRES, n)
    real = nombres[:]; rng.shuffle(real)
    pos = {x: i for i, x in enumerate(real)}
    pool = [("antes", a, b) for a in real for b in real if pos[a] < pos[b]] + [("justo", a, b) for a in real for b in real if pos[a] + 1 == pos[b]]
    pool += [("primero", real[0]), ("ultimo", real[-1])]
    rng.shuffle(pool)
    cons, pistas = list(itertools.permutations(nombres)), []
    for c in pool:
        nuevo = [p for p in cons if cumple(c, p)]
        if len(nuevo) < len(cons):
            pistas.append(c); cons = nuevo
        if len(cons) == 1: break
    # pregunta: una posicion que ninguna pista da directamente
    directas = {0 if c[0] == "primero" else n - 1 for c in pistas if c[0] in ("primero", "ultimo")}
    cand = [k for k in range(n) if k not in directas]
    if not cand: raise ValueError("todas las posiciones son directas")
    k = rng.choice(cand)
    ok = real[k]
    esc = rng.choice(ESCENARIOS_ORDEN)
    rng.shuffle(pistas)
    m = (len(pistas) + 1) // 2
    p2, p3 = " ".join(frase_orden(rng, c) for c in pistas[:m]), " ".join(frase_orden(rng, c) for c in pistas[m:])
    texto = [esc[0].format(n={4: "cuatro", 5: "cinco"}[n]) + " Se trata de " + lista(sorted(nombres)) + ".", p2, (p3 + " " if p3 else "") + esc[1]]
    ops, i = mezclar(ok, [x for x in nombres if x != ok], rng)
    return dict(enunciado=f"¿Quién ocupó la {ORDINAL[k]} posición?", texto=texto, opciones=ops, correcta=i,
                truco="Encadena las pistas hasta ordenar a todos: " + " → ".join(real) + f". La {ORDINAL[k]} posición es la de {ok}.",
                dificultad=1 if n == 4 else (2 if len(pistas) <= 4 else 3))

# ------------------------------------------------------------------ reglas con condiciones
def regla_beca(rng):
    d, ing = rng.choice([3, 5, 8]), rng.choice([1200, 1500, 1800])
    regla = (f"La beca de comedor se concede a las familias que vivan a más de {d} km del colegio o cuyos ingresos mensuales sean inferiores a {ing} €. "
             "En ningún caso se concede si la familia ya recibe otra ayuda para el mismo fin.")
    def caso(rng):
        km = rng.choice([x for x in range(1, 13) if x != d]); inc = rng.choice([x for x in range(900, 2600, 100) if x != ing]); otra = rng.random() < .3
        return dict(km=km, inc=inc, otra=otra)
    def frase(ap, c):
        return f"La {ap} vive a {c['km']} km del colegio y tiene unos ingresos de {num(c['inc'])} € al mes" + (", aunque ya recibe otra ayuda para el comedor." if c["otra"] else ".")
    ev = lambda c: (c["km"] > d or c["inc"] < ing) and not c["otra"]
    why = lambda c: ("ya recibe otra ayuda" if c["otra"] else "vive lejos o ingresa poco" if ev(c) else "ni vive lejos ni ingresa poco")
    return "familia", "la beca de comedor", regla, caso, frase, ev, why, 2

def regla_bono(rng):
    a, b = rng.choice([14, 16, 18]), rng.choice([26, 28, 30])
    regla = (f"El bono joven de transporte pueden obtenerlo las personas empadronadas en la ciudad que tengan entre {a} y {b} años, ambos incluidos. "
             "Las personas con carné de familia numerosa pueden obtenerlo a cualquier edad, pero también deben estar empadronadas.")
    def caso(rng):
        return dict(edad=rng.choice([a - 1, a, a + 3, b, b + 1, rng.randint(30, 45), rng.randint(12, 14)]), pad=rng.random() < .75, fam=rng.random() < .3)
    def frase(nom, c):
        return f"{nom} tiene {c['edad']} años, {'figura' if c['pad'] else 'no figura'} en el padrón de la ciudad" + (" y presenta carné de familia numerosa." if c["fam"] else ".")
    ev = lambda c: c["pad"] and (a <= c["edad"] <= b or c["fam"])
    why = lambda c: ("no figura en el padrón" if not c["pad"] else "edad dentro del rango" if a <= c["edad"] <= b else "familia numerosa" if c["fam"] else "fuera de edad y sin familia numerosa")
    return "", "el bono joven", regla, caso, frase, ev, why, 2

def regla_gimnasio(rng):
    y = rng.choice([5, 8, 10])
    regla = (f"El gimnasio municipal aplica la tarifa reducida a las personas de 65 años o más y a las que llevan más de {y} años en el centro. "
             "Quien tenga recibos pendientes no puede acogerse a la tarifa reducida, sea cual sea su situación.")
    def caso(rng):
        return dict(edad=rng.choice([rng.randint(20, 60), rng.randint(20, 60), 65, 64, rng.randint(66, 80)]), anos=rng.choice([x for x in range(1, 15) if x != y]), pend=rng.random() < .3)
    def frase(nom, c):
        return f"{nom} tiene {c['edad']} años, lleva {c['anos']} años en el gimnasio" + (" y tiene recibos pendientes." if c["pend"] else ".")
    ev = lambda c: (c["edad"] >= 65 or c["anos"] > y) and not c["pend"]
    why = lambda c: ("tiene recibos pendientes" if c["pend"] else "65 o más años o antigüedad suficiente" if ev(c) else "ni edad ni antigüedad suficientes")
    return "", "la tarifa reducida", regla, caso, frase, ev, why, 3

@ejercicio(T, peso=2, tiempo=60)
def reglas(rng):
    prefijo, que, regla, caso, frase, ev, why, dif = rng.choice([regla_beca, regla_bono, regla_gimnasio])(rng)
    nombres = [f"familia {x}" for x in rng.sample(APELLIDOS, 4)] if prefijo else rng.sample(NOMBRES, 4)
    casos = [caso(rng) for _ in nombres]
    res = [ev(c) for c in casos]
    sí, no = [x for x, r in zip(nombres, res) if r], [x for x, r in zip(nombres, res) if not r]
    if len(no) == 1: q, ok, falsas = f"¿A quién se le denegará {que}?", no[0], sí
    elif len(sí) == 1: q, ok, falsas = f"¿A quién se le concederá {que}?", sí[0], no
    else: q, ok, falsas = f"¿A cuántas de las cuatro solicitudes se les concederá {que}?", len(sí), [x for x in range(5) if x != len(sí)]
    ops, i = mezclar(ok, falsas, rng)
    texto = [regla, "Se recibieron cuatro solicitudes. " + " ".join(frase(x, c) for x, c in zip(nombres, casos)),
             "Las solicitudes se resolvieron el mismo día aplicando solo las condiciones anteriores."]
    truco = "Comprueba cada caso con la norma: " + "; ".join(f"{x}: {'sí' if r else 'no'} ({why(c)})" for x, r, c in zip(nombres, res, casos)) + "."
    return dict(enunciado=q, texto=texto, opciones=[str(o) for o in ops], correcta=i, truco=truco, dificultad=dif)

# ------------------------------------------------------------------ condicional
TRIPLETAS = [
    ("Un informe del edificio municipal describe el protocolo contra incendios.", ("el sensor detecta humo", "el sensor no detecta humo"),
     ("se activan los aspersores", "no se activan los aspersores"), ("se evacúa el edificio", "no se evacúa el edificio")),
    ("Una nota de la concejalía de carreteras explica cómo actúa el servicio de nieve.", ("la nevada supera los 20 cm", "la nevada no supera los 20 cm"),
     ("se cierra el puerto de montaña", "no se cierra el puerto de montaña"), ("se suspenden las clases en el valle", "no se suspenden las clases en el valle")),
    ("Un artículo económico resume la relación entre el petróleo y los precios.", ("sube el precio del petróleo", "no sube el precio del petróleo"),
     ("aumenta el coste del transporte", "no aumenta el coste del transporte"), ("suben los precios en el supermercado", "no suben los precios en el supermercado")),
    ("El reglamento del club deportivo fija cómo se abre la venta de entradas.", ("el equipo gana el sábado", "el equipo no gana el sábado"),
     ("el equipo se clasifica para la final", "el equipo no se clasifica para la final"), ("el club abre la venta de entradas", "el club no abre la venta de entradas")),
    ("La confederación hidrográfica publica su plan de actuación ante crecidas.", ("el río supera la cota de alerta", "el río no supera la cota de alerta"),
     ("se abren las compuertas del embalse", "no se abren las compuertas del embalse"), ("se avisa a los vecinos de la ribera", "no se avisa a los vecinos de la ribera")),
    ("Una memoria anual de la biblioteca explica cómo se financia la sala de lectura.", ("la biblioteca recibe la subvención", "la biblioteca no recibe la subvención"),
     ("se amplía el horario de la sala de lectura", "no se amplía el horario de la sala de lectura"), ("aumenta el número de socios", "no aumenta el número de socios")),
]

@ejercicio(T, peso=2, tiempo=60)
def condicional(rng):
    intro, (p, pn), (q, qn), (r, rn) = rng.choice(TRIPLETAS)
    tipo = rng.choice(["cadena", "tollens", "consecuente", "antecedente"])
    if tipo == "cadena":
        hecho, ok, falsas, dif = f"{cap(p)}.", cap(r), [cap(qn), cap(rn), f"{cap(q)}, pero {rn}"], 1
        truco = f"Si {p}, {q}; y si {q}, {r}. Encadenando: si {p}, {r}. Como {p}, se cumple que {r}."
    elif tipo == "tollens":
        hecho, ok, falsas, dif = f"{cap(rn)}.", cap(pn), [cap(p), cap(q), f"{cap(p)} y {qn}"], 2
        truco = f"Si {p}, entonces {r} (por la cadena). Como {rn}, no puede haber ocurrido que {p}: {pn}."
    elif tipo == "consecuente":
        hecho, ok, falsas, dif = f"{cap(r)}.", f"No puede asegurarse si {p}.", [cap(p), cap(q), cap(pn)], 3
        truco = f"Los condicionales van en un solo sentido: {r} puede deberse a otras causas, así que no se puede asegurar nada sobre si {p}."
    else:
        hecho, ok, falsas, dif = f"{cap(pn)}.", f"No puede asegurarse si {r}.", [cap(rn), cap(qn), cap(r)], 3
        truco = f"Que {pn} no impide que {r} por otros motivos: la norma solo dice qué pasa cuando {p}."
    ops, i = mezclar(ok, falsas, rng)
    texto = [intro, f"Según el documento, si {p}, entonces {q}. Además, siempre que {q}, {r}. No se menciona ninguna otra circunstancia que lleve a esos resultados.",
             f"En la última revisión se constató lo siguiente: {hecho[0].lower() + hecho[1:]}"]
    return dict(enunciado="A partir de lo anterior, ¿qué se puede afirmar con seguridad?", texto=texto, opciones=ops, correcta=i, truco=truco, dificultad=dif)

# ------------------------------------------------------------------ cifras en prosa
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre"]
CIFRAS = [("La biblioteca del barrio", "préstamos de libros"), ("El museo de la ciudad", "visitas"), ("La tienda de la cooperativa", "unidades vendidas")]

@ejercicio(T, peso=2, tiempo=60)
def cifras(rng):
    sujeto, cosa = rng.choice(CIFRAS)
    pasos = rng.choice([2, 3])
    a = rng.choice([400, 800, 1200, 1600, 2000, 2400])
    cambios = [(rng.choice([1, -1]), rng.choice([10, 20, 25, 50])) for _ in range(pasos)]
    valores = [Fraction(a)]
    for s, pc in cambios: valores.append(valores[-1] * (100 + s * pc) / 100)
    if any(v.denominator != 1 or v <= 0 for v in valores): raise ValueError("cifras no enteras")
    ok = int(valores[-1])
    m0 = rng.randint(0, len(MESES) - pasos - 1); ms = MESES[m0:m0 + pasos + 1]
    verbo = lambda s: "subió" if s > 0 else "bajó"
    frases = [f"En {ms[i + 1]}, la cifra {verbo(s)} un {pc}% respecto a {ms[i]}." for i, (s, pc) in enumerate(cambios)]
    texto = [f"{sujeto} lleva un registro mensual de {cosa}. En {ms[0]} anotó {num(a)}.", " ".join(frases[:1]),
             " ".join(frases[1:]) + " Todas las variaciones se calculan sobre el mes inmediatamente anterior."]
    neto = sum(s * pc for s, pc in cambios)
    ext = [int(a * (100 + neto) / 100), int(valores[-2]), a]
    ops, i = mezclar(num(ok), [num(x) for x in distractores_num(ok, rng, extras=ext)], rng)
    truco = " → ".join(f"{ms[j]}: {num(int(v))}" for j, v in enumerate(valores)) + ". Cada porcentaje se aplica al mes anterior, no al de partida."
    return dict(enunciado=f"¿Cuál fue la cifra de {cosa} de {ms[-1]}?", texto=texto, opciones=ops, correcta=i, truco=truco, dificultad=1 if pasos == 2 else 2)
