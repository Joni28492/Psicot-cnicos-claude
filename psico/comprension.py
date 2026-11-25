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

# ====================================================================== texto largo con 5-10 preguntas
# Se construye un "mundo" (plantillas, presupuesto, actividad, encuesta, fechas...), se cuenta en 6-7 parrafos densos y se hacen
# 5-10 preguntas que hay que deducir combinando datos de distintos parrafos. Todas las respuestas se calculan del mundo.
import datetime, hashlib

TEMAS_LARGO = [
    dict(org="el Hospital Comarcal de {lugar}", fund="hospital", areas=["Urgencias", "Pediatría", "Radiología", "Cardiología", "Traumatología"],
         pers="profesionales", act="atenciones", usuarios="pacientes", sat="satisfecho con la atención recibida", sat_pl="satisfechos con la atención recibida", exc="la calificó de «excelente»", exc_pl="la calificaron de «excelente»"),
    dict(org="la Universidad Politécnica de {lugar}", fund="centro", areas=["Ingeniería Civil", "Informática", "Arquitectura", "Química", "Telecomunicaciones"],
         pers="docentes", act="matrículas", usuarios="estudiantes", sat="satisfecho con la docencia", sat_pl="satisfechos con la docencia", exc="la calificó de «excelente»", exc_pl="la calificaron de «excelente»"),
    dict(org="la Cooperativa Agraria de {lugar}", fund="cooperativa", areas=["Aceite", "Vino", "Cereal", "Fruta", "Hortalizas"],
         pers="trabajadores", act="toneladas procesadas", usuarios="socios", sat="satisfecho con el servicio de la cooperativa", sat_pl="satisfechos con el servicio de la cooperativa", exc="lo valoró como «excelente»", exc_pl="lo valoraron como «excelente»"),
]
LUGARES = ["Valverde del Sur", "Ribera Alta", "Castroviejo", "Santa Marina", "Monteluz", "Villarrosal"]
MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
FRAC_TXT = {Fraction(1, 2): "la mitad", Fraction(1, 4): "una cuarta parte", Fraction(1, 8): "un octavo", Fraction(3, 8): "tres octavos"}
REPARTOS = [(Fraction(1, 2), Fraction(1, 4), Fraction(1, 8), Fraction(1, 8)), (Fraction(3, 8), Fraction(1, 4), Fraction(1, 4), Fraction(1, 8)),
            (Fraction(1, 2), Fraction(1, 8), Fraction(1, 8), Fraction(1, 4)), (Fraction(3, 8), Fraction(3, 8), Fraction(1, 8), Fraction(1, 8))]

def de(ref):
    return "del " + ref[3:] if ref.startswith("el ") else "de " + ref

def fecha_txt(d):
    return f"{d.day} de {MESES_ES[d.month - 1]}"

class Mundo:
    pass

def crear_mundo(rng):
    w = Mundo()
    w.tema = rng.choice(TEMAS_LARGO); t = w.tema
    w.lugar = rng.choice(LUGARES); w.org = t["org"].format(lugar=w.lugar)
    w.yb = rng.randint(2019, 2025); w.ya = w.yb - 1; w.fund = rng.randint(1950, 1995)
    w.areas = rng.sample(t["areas"], 4)
    # plantilla del año anterior: la primera area tiene cifra directa y las demas se definen por relacion con otra anterior
    w.sa = {w.areas[0]: rng.choice([40, 60, 80, 100])}
    w.rel = []
    for k in range(1, 4):
        a, ref = w.areas[k], w.areas[rng.randrange(k)]
        s = w.sa[ref]
        ops = [("doble", 2 * s, "")]
        if s % 2 == 0: ops.append(("mitad", s // 2, ""))
        if s % 4 == 0: ops.append(("tres_cuartas", 3 * s // 4, ""))
        for kk in (10, 20, 30):
            ops.append(("mas", s + kk, kk))
            if s - kk >= 10: ops.append(("menos", s - kk, kk))
        tipo, val, kk = rng.choice(ops)
        w.sa[a] = val; w.rel.append((a, ref, tipo, kk))
    if len(set(w.sa.values())) < 4: raise ValueError("plantillas repetidas")
    # cambios de plantilla
    w.pct, w.sb = {}, {}
    for a in w.areas:
        opts = [p for p in (-20, -10, 0, 10, 20, 25, 50) if (w.sa[a] * (100 + p)) % 100 == 0]
        w.pct[a] = rng.choice(opts); w.sb[a] = w.sa[a] * (100 + w.pct[a]) // 100
    if len(set(w.pct.values())) < 3 or len(set(w.sb.values())) < 4: raise ValueError("cambios poco variados")
    # presupuesto (millones)
    w.B = rng.choice([16, 24, 32, 40, 48])
    rep = list(rng.choice(REPARTOS)); rng.shuffle(rep)
    w.share = dict(zip(w.areas, rep)); w.pres = {a: int(w.B * w.share[a]) for a in w.areas}
    if len(set(w.pres.values())) < 3: raise ValueError("presupuesto poco variado")
    # actividad por area: plantilla actual x ratio distinto
    ratios = rng.sample(range(4, 15), 4)
    w.ratio = dict(zip(w.areas, ratios)); w.act = {a: w.sb[a] * w.ratio[a] for a in w.areas}
    w.total_act = sum(w.act.values())
    w.g = next((g for g in rng.sample([10, 20, 25, 50], 4) if (100 * w.total_act) % (100 + g) == 0), None)
    if w.g is None: raise ValueError("total de actividad no divisible")
    w.total_act_prev = 100 * w.total_act // (100 + w.g)
    # criterio de refuerzo: umbral de ratio y de presupuesto que deje exactamente una area
    cand = []
    for T in sorted(set(r for r in ratios)):
        for U in sorted(set(w.pres.values())):
            sel = [a for a in w.areas if w.ratio[a] > T and w.pres[a] < U]
            if len(sel) == 1: cand.append((T, U, sel[0]))
    if not cand: raise ValueError("sin criterio con una sola area")
    w.T, w.U, w.refuerzo = rng.choice(cand)
    # encuesta
    w.N = rng.choice([800, 1200, 1600, 2000]); w.p1 = rng.choice([60, 70, 75, 80]); w.p2 = rng.choice([20, 25, 40, 50])
    w.n_sat = w.N * w.p1 // 100; w.n_exc = w.n_sat * w.p2 // 100
    # calendario
    base = datetime.date(w.yb, rng.randint(1, 9), rng.randint(2, 25))
    w.d_junta = base; w.k_aud = rng.choice([30, 45, 60, 90]); w.d_aud = base + datetime.timedelta(days=w.k_aud)
    w.m_entrega = rng.choice([10, 15, 20]); w.d_entrega = w.d_aud + datetime.timedelta(days=w.m_entrega)
    return w

def parrafos(w):
    t = w.tema; P_ = t["pers"]; ya, yb = w.ya, w.yb
    ar = lambda a: f"el área de {a}"
    A = w.areas
    p1 = (f"{cap(w.org)}, fundado en {w.fund}, organiza su actividad en cuatro áreas: {lista(A)}. Cada año la dirección publica una memoria en la que repasa "
          f"plantilla, presupuesto, actividad y opinión de los {t['usuarios']}, y la edición de {yb} dedica un apartado extenso a explicar qué ha cambiado respecto a {ya}. "
          f"La dirección advierte de que las cifras no son comparables con las de ejercicios anteriores a {ya}, porque entonces se contabilizaba de otro modo.")
    frases = [f"En {ya}, {ar(A[0])} contaba con {w.sa[A[0]]} {P_}."]
    forma = {"doble": lambda ref, k: f"el doble de {P_} que {ar(ref)}", "mitad": lambda ref, k: f"la mitad de {P_} que {ar(ref)}",
             "tres_cuartas": lambda ref, k: f"tres cuartas partes de los {P_} {de(ar(ref))}", "mas": lambda ref, k: f"{k} {P_} más que {ar(ref)}",
             "menos": lambda ref, k: f"{k} {P_} menos que {ar(ref)}"}
    for a, ref, tipo, kk in w.rel:
        frases.append(f"{cap(ar(a))} tenía {forma[tipo](ref, kk)}.")
    p2 = " ".join(frases) + " Estas plantillas se mantuvieron estables durante la primera mitad del año, y fue después cuando se produjeron los movimientos que se detallan a continuación."
    mov = []
    for a in A:
        p = w.pct[a]
        mov.append(f"{ar(a)} {'aumentó su plantilla un ' + str(p) + '%' if p > 0 else 'redujo su plantilla un ' + str(-p) + '%' if p < 0 else 'mantuvo su plantilla'}")
    p3 = (f"Durante {yb}, la plantilla evolucionó de forma desigual: " + "; ".join(mov) + ". "
          "La dirección atribuye estos movimientos a jubilaciones, traslados y nuevas contrataciones, y reconoce que no todas las vacantes pudieron cubrirse a tiempo.")
    orden = sorted(A, key=lambda a: -w.share[a])
    ult = A[-1]
    partes = [f"{ar(a)} recibió {FRAC_TXT[w.share[a]]}" for a in A[:3]]
    p4 = (f"El presupuesto total de {yb} fue de {w.B} millones de euros. Su reparto fue el siguiente: " + ", ".join(partes) + f", y el resto se destinó al área de {ult}. "
          "La dirección subraya que el reparto responde a necesidades estructurales y no a la evolución de la plantilla.")
    p5 = (f"En cuanto a la actividad de {yb}, medida en {t['act']}, " + ", ".join(f"{ar(a)} alcanzó {num(w.act[a])}" for a in A) +
          f". En conjunto, la actividad total de {yb} fue un {w.g}% superior a la de {ya}. Según la memoria, el aumento se debe sobre todo a la mejora de la organización interna.")
    p6 = (f"Con vistas al ejercicio siguiente, la dirección fijó un criterio para reforzar la plantilla: solo recibirán refuerzo las áreas que cumplan a la vez dos condiciones, "
          f"haber registrado en {yb} más de {w.T} {t['act']} por cada profesional y contar con un presupuesto inferior a {w.U} millones de euros. "
          "El criterio se aplicará de manera automática, sin excepciones.")
    retos = (f"La memoria incluye también una reflexión sobre los retos pendientes. La dirección admite que la formación de los {P_} de nueva incorporación se ha retrasado, "
             f"que el área de {A[1]} depende en exceso de contratos temporales y que prevé revisar el criterio de refuerzo en {yb + 2}, aunque no antes. "
             "Añade que cualquier cambio de criterio deberá comunicarse a las áreas con seis meses de antelación.")
    j, au, en = w.d_junta, w.d_aud, w.d_entrega
    p7 = (f"Por último, la memoria recoge la opinión de {num(w.N)} {t['usuarios']} encuestados: el {w.p1}% se declaró {t['sat']} y, de entre estos, el {w.p2}% {t['exc']}. "
          f"La junta que aprobó la memoria se celebró el {DIAS_ES[j.weekday()]} {fecha_txt(j)} de {yb}; la auditoría externa comenzó {w.k_aud} días después de la junta, "
          f"y el informe de la auditoría se entregó {w.m_entrega} días después de su comienzo.")
    return [p1, p2, p3, p4, p5, retos, p6, p7]

# ---- preguntas: cada una devuelve (enunciado, correcta, falsas, truco, dificultad) o lanza ValueError si no es viable
def opciones_num(rng, ok, extras):
    return [num(x) for x in distractores_num(ok, rng, extras=extras)]

def q_plantilla_anterior(w, rng):
    a, ref, tipo, kk = rng.choice(w.rel)
    return (f"Según el texto, ¿cuántos {w.tema['pers']} tenía el área de {a} en {w.ya}?", num(w.sa[a]), opciones_num(rng, w.sa[a], [w.sa[ref], w.sa[a] + 10, w.sb[a]]),
            f"{a} se define a partir de {ref} ({w.sa[ref]}): resulta {w.sa[a]}.", 1)

def q_plantilla_actual(w, rng):
    a = rng.choice([x for x in w.areas if w.pct[x] != 0])
    return (f"¿Cuántos {w.tema['pers']} tenía el área de {a} al terminar {w.yb}?", num(w.sb[a]), opciones_num(rng, w.sb[a], [w.sa[a], w.sa[a] * (100 - w.pct[a]) // 100 if (w.sa[a] * (100 - w.pct[a])) % 100 == 0 else w.sa[a] + 5]),
            f"En {w.ya} tenía {w.sa[a]} y su plantilla varió un {w.pct[a]:+d}%: {w.sb[a]}.", 2)

def q_total_plantilla(w, rng):
    ok = sum(w.sb.values())
    return (f"¿Cuántos {w.tema['pers']} sumaban las cuatro áreas al terminar {w.yb}?", num(ok), opciones_num(rng, ok, [sum(w.sa.values()), ok - 10, ok + 20]),
            "Suma de las plantillas actualizadas: " + " + ".join(str(w.sb[a]) for a in w.areas) + f" = {ok}.", 2)

def q_mayor_aumento(w, rng):
    dif = {a: w.sb[a] - w.sa[a] for a in w.areas}
    mx = max(dif.values())
    if list(dif.values()).count(mx) > 1: raise ValueError("empate")
    ok = next(a for a in w.areas if dif[a] == mx)
    porc = max(w.areas, key=lambda a: w.pct[a])
    return ("¿Qué área aumentó más su plantilla en número de personas (no en porcentaje) durante el año?", ok, [a for a in w.areas if a != ok],
            "Diferencia de plantilla: " + "; ".join(f"{a} {dif[a]:+d}" for a in w.areas) + f". El mayor aumento es el de {ok}" + (f" (el mayor porcentaje es el de {porc})." if porc != ok else "."), 3)

def q_presupuesto_resto(w, rng):
    a = w.areas[3]; ok = w.pres[a]
    return (f"¿Qué cantidad, en millones de euros, recibió el área de {a}?", num(ok), opciones_num(rng, ok, [w.B // 4, w.B // 8, w.B - ok]),
            f"Las tres primeras áreas suman {sum(w.pres[x] for x in w.areas[:3])} de {w.B}; el resto, {ok} millones.", 2)

def q_actividad_por_profesional(w, rng):
    ok = max(w.areas, key=lambda a: w.ratio[a])
    return ("¿Qué área registró más actividad por cada profesional en el año?", ok, [a for a in w.areas if a != ok],
            "Actividad ÷ plantilla actual: " + "; ".join(f"{a} {w.act[a]}÷{w.sb[a]} = {w.ratio[a]}" for a in w.areas) + ".", 3)

def q_refuerzo(w, rng):
    return ("Aplicando el criterio de la dirección, ¿qué área recibirá refuerzo de plantilla?", w.refuerzo, [a for a in w.areas if a != w.refuerzo],
            f"Hay que cumplir las dos condiciones: más de {w.T} por profesional y menos de {w.U} millones. " +
            "; ".join(f"{a}: {w.ratio[a]} y {w.pres[a]} M€" for a in w.areas) + f". Solo las cumple {w.refuerzo}.", 3)

def q_encuesta(w, rng):
    if rng.random() < .5:
        ok = w.N - w.n_sat
        return (f"¿Cuántos {w.tema['usuarios']} encuestados no se declararon {w.tema['sat_pl']}?", num(ok), opciones_num(rng, ok, [w.n_sat, w.n_exc, w.N - w.n_exc]),
                f"{w.p1}% de {w.N} = {w.n_sat} satisfechos; el resto: {w.N} − {w.n_sat} = {ok}.", 2)
    ok = w.n_exc
    return (f"¿Cuántos {w.tema['usuarios']} {w.tema['exc_pl']}?", num(ok), opciones_num(rng, ok, [w.n_sat, w.N * w.p2 // 100, w.N - w.n_sat]),
            f"El {w.p2}% se aplica solo a los satisfechos: {w.n_sat} × {w.p2}% = {ok}.", 3)

def q_actividad_previa(w, rng):
    ok = w.total_act_prev
    return (f"¿Cuántas {w.tema['act']} se registraron en total en {w.ya}?", num(ok), opciones_num(rng, ok, [w.total_act * (100 - w.g) // 100, w.total_act - w.g, w.total_act]),
            f"El total de {w.yb} ({num(w.total_act)}) es un {w.g}% mayor que el anterior: {num(w.total_act)} ÷ {1 + w.g / 100:g} = {num(ok)}.", 3)

def q_fecha(w, rng):
    if rng.random() < .5:
        ok = fecha_txt(w.d_aud); f = [fecha_txt(w.d_aud + datetime.timedelta(days=d)) for d in (-7, 7, -1, 1, 14)]
        rng.shuffle(f)
        return (f"¿En qué fecha comenzó la auditoría externa?", ok, f, f"{fecha_txt(w.d_junta)} + {w.k_aud} días = {fecha_txt(w.d_aud)}.", 2)
    ok = DIAS_ES[w.d_entrega.weekday()]
    f = [d for d in DIAS_ES if d != ok]
    return ("¿Qué día de la semana se entregó el informe de la auditoría?", ok, f, f"Junta: {DIAS_ES[w.d_junta.weekday()]} {fecha_txt(w.d_junta)}. +{w.k_aud} días = {fecha_txt(w.d_aud)}; +{w.m_entrega} días = {fecha_txt(w.d_entrega)}, que cae en {ok}.", 3)

def afirmaciones(w):
    """lista de (texto, verdadera) con comparaciones entre cifras del texto."""
    out, A, act, P_ = [], w.areas, w.tema["act"], w.tema["pers"]
    for x, y in itertools.permutations(A, 2):
        out.append((f"El área de {x} tenía más {P_} que el área de {y} en {w.ya}.", w.sa[x] > w.sa[y]))
        out.append((f"Al terminar {w.yb}, el área de {x} tenía más {P_} que el área de {y}.", w.sb[x] > w.sb[y]))
        out.append((f"El área de {x} recibió más presupuesto que el área de {y}.", w.pres[x] > w.pres[y]))
        out.append((f"El área de {x} registró más {act} en total que el área de {y}.", w.act[x] > w.act[y]))
    out.append((f"La plantilla total de las cuatro áreas fue mayor en {w.yb} que en {w.ya}.", sum(w.sb.values()) > sum(w.sa.values())))
    out += [(f"La dirección considera que las cifras de {w.yb} no se pueden comparar con las de antes de {w.ya}.", True),
            (f"La dirección considera que las cifras de {w.yb} se pueden comparar con las de cualquier año anterior.", False),
            ("No todas las vacantes de plantilla se cubrieron a tiempo.", True), ("Todas las vacantes de plantilla se cubrieron a tiempo.", False),
            ("El criterio de refuerzo se aplicará sin excepciones.", True), ("El criterio de refuerzo admite excepciones a juicio de la dirección.", False),
            ("La dirección afirma que el reparto del presupuesto no depende de la evolución de la plantilla.", True),
            ("La dirección afirma que el reparto del presupuesto depende de la evolución de la plantilla.", False),
            ("La memoria atribuye el aumento de actividad a la mejora de la organización interna.", True),
            ("La memoria atribuye el aumento de actividad a la contratación de más personal.", False),
            (f"La dirección admite retrasos en la formación de los {P_} de nueva incorporación.", True),
            (f"La dirección asegura que la formación de los {P_} nuevos se completó sin retrasos.", False),
            (f"Según la memoria, el área de {A[1]} depende en exceso de contratos temporales.", True),
            (f"Según la memoria, el área de {A[2]} depende en exceso de contratos temporales.", False),
            (f"La dirección prevé revisar el criterio de refuerzo en {w.yb + 2}, no antes.", True),
            (f"La dirección prevé revisar el criterio de refuerzo en {w.yb + 1}.", False),
            ("Un cambio de criterio de refuerzo debe comunicarse a las áreas con seis meses de antelación.", True),
            ("Un cambio de criterio de refuerzo puede aplicarse sin avisar a las áreas.", False)]
    out.append((f"Alguna de las áreas redujo su plantilla en {w.yb}.", any(p < 0 for p in w.pct.values())))
    out.append((f"Ninguna de las áreas mantuvo su plantilla igual en {w.yb}.", all(p != 0 for p in w.pct.values())))
    return out

def q_afirmacion(w, rng, cierta=True):
    af = afirmaciones(w); rng.shuffle(af)
    ver = [t for t, v in af if v]; fal = [t for t, v in af if not v]
    if len(ver) < 3 or len(fal) < 3: raise ValueError("pocas afirmaciones")
    if cierta:
        ok, falsas = ver[0], fal[:3]
        return ("¿Cuál de las siguientes afirmaciones es cierta según el texto?", ok, falsas, f"Comprobando con las cifras del texto, solo es cierta: «{ok}»", 2)
    ok, falsas = fal[0], ver[:3]
    return ("¿Cuál de las siguientes afirmaciones es FALSA según el texto?", ok, falsas, f"Las otras tres se comprueban con las cifras del texto; la falsa es: «{ok}»", 3)

CONSTRUCTORES = [q_plantilla_anterior, q_plantilla_actual, q_total_plantilla, q_mayor_aumento, q_presupuesto_resto, q_actividad_por_profesional, q_refuerzo,
                 q_encuesta, q_actividad_previa, q_fecha, lambda w, r: q_afirmacion(w, r, True), lambda w, r: q_afirmacion(w, r, False)]

@ejercicio(T, peso=1, tiempo=75)
def texto_largo(rng):
    """un texto de 7 parrafos con entre 5 y 10 preguntas: devuelve la LISTA de ejercicios (una por pregunta)."""
    w = crear_mundo(rng)
    texto = parrafos(w)
    k = rng.randint(5, 10)
    cons = CONSTRUCTORES[:]; rng.shuffle(cons)
    preguntas = []
    for c in cons:
        try: enun, ok, falsas, truco, dif = c(w, rng)
        except (ValueError, StopIteration): continue
        try: ops, i = mezclar(ok, falsas, rng)
        except ValueError: continue
        preguntas.append(dict(enunciado=enun, opciones=[str(o) for o in ops], correcta=i, truco=truco, dificultad=dif))
        if len(preguntas) == k: break
    if len(preguntas) < 5: raise ValueError("pocas preguntas")
    preguntas.sort(key=lambda q: 0)     # se conserva el orden aleatorio
    gid = hashlib.sha1("|".join(texto).encode()).hexdigest()[:8]
    for n, q in enumerate(preguntas):
        q.update(texto=texto, grupo=gid, grupo_idx=n, grupo_n=len(preguntas))
    return preguntas
