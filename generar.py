#!/usr/bin/env python3
"""Genera la sesion de psicotecnicos del dia.

uso: python3 generar.py [--fecha AAAA-MM-DD] [--modo auto|diario|especifico] [--tema TIPO] [--n N] [--salida carpeta]
                        [--sin-figuras] [--semilla texto] [--numero N] [--html] [--json]

Modos:
  diario      30-42 ejercicios de 6 de los 9 tipos (los otros 3 rotan segun la fecha y salen en los tests siguientes).
  especifico  un solo tema, con la dificultad creciente (facil -> dificil); cada ejercicio lleva su nivel en las soluciones.
  auto        (por defecto) especifico los sabados y diario el resto de dias.
El tema del test especifico sale de seguimiento/foco.json (lo que el usuario dice que mas le cuesta); si no hay, rotan todos los tipos.
Salida: psicotecnico_<NNN>_<dificultad>.pdf o psicotecnico_<NNN>_especifico_<tema>_variable.pdf, mas una entrada en indice.json.
"""
import argparse, datetime, json, os, random, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psico import nucleo, reglas_tres, porcentajes, series, codificacion, problemas, figuras, domino, relojes, combinatoria, imprimible   # noqa: F401  (registran generadores)
from psico import dificultad as dif

# peso de cada TIPO al repartir los ejercicios del dia
PESO_TIPO = {"Reglas de tres": 2, "Porcentajes": 2, "Series": 3, "Codificación": 2, "Problemas": 3, "Combinatoria": 2,
             "Figuras desplegables": 1.5, "Series de fichas": 1.5, "Series de relojes": 1.5}
# orden del ciclo de rotacion: cada dia faltan 3 tipos (posiciones i % 3 == dia % 3), asi cada tipo falta 1 de cada 3 dias
CICLO = list(PESO_TIPO)
MIN_TIPO = 3
MAX_TIPO = {"Figuras desplegables": 4, "Series de fichas": 5, "Series de relojes": 5}   # los dibujos ocupan mucho
DIA_ESPECIFICO = 5            # sabado (lunes = 0)
N_ESPECIFICO = 21             # 7 de cada nivel; 12 (4 por nivel) si el tema son dibujos
N_ESPECIFICO_DIBUJOS = 12
DIBUJOS = ("Figuras desplegables", "Series de fichas", "Series de relojes")

def tipos_del_dia(fecha, sin_figuras=False):
    g = datetime.date.fromisoformat(fecha).toordinal() % 3
    tipos = [t for i, t in enumerate(CICLO) if i % 3 != g]
    return [t for t in tipos if not (sin_figuras and t == "Figuras desplegables")]

def un_ejercicio(rng, tipo, usados, vistos, nivel=None):
    """genera un ejercicio nuevo del tipo; si se pide `nivel`, intenta que salga de ese nivel (si no puede, devuelve el mas cercano)."""
    gens = [g for g in nucleo.REGISTRO if g[0] == tipo]
    mejor = None
    for intento in range(120 if nivel else 60):
        if nivel and intento < 60:     # primero subtipos cuyo nivel base ya es el pedido
            pesos = [(4 if dif.BASE.get(g[1], 2) == nivel else .3) / (1 + 2 * usados.get(g[1], 0)) for g in gens]
        else:                          # favorece subtipos poco usados
            pesos = [g[2] / (1 + 2 * usados.get(g[1], 0)) for g in gens]
        g = rng.choices(gens, pesos)[0]
        try:
            e = g[4](rng)
            clave = e["enunciado"] + e.get("destacado", "") + str(hash(e.get("imagen", "")))     # los dibujos comparten enunciado
            if clave in vistos or len(set(e["opciones"])) != len(e["opciones"]): continue
        except (ValueError, RecursionError):
            continue
        e.update(tipo=tipo, tiempo=g[3], subtipo=g[1]); e["dificultad"] = dif.nivel(e)
        if not nivel or e["dificultad"] == nivel:
            mejor = (e, g); break
        if mejor is None or abs(e["dificultad"] - nivel) < abs(mejor[0]["dificultad"] - nivel): mejor = (e, g)
    if mejor is None: return None
    e, g = mejor
    vistos.add(e["enunciado"] + e.get("destacado", "") + str(hash(e.get("imagen", "")))); usados[g[1]] = usados.get(g[1], 0) + 1
    return e

def generar(fecha, n=None, sin_figuras=False, semilla=""):
    """test diario: n ejercicios (30-42 por defecto) repartidos entre los tipos que tocan hoy."""
    rng = random.Random(f"{fecha}|{semilla}")
    n = n or rng.randint(30, 42)
    tipos = tipos_del_dia(fecha, sin_figuras)
    # reparto proporcional a los pesos (maximo restos) con minimo MIN_TIPO por tipo y maximos para los dibujos
    total_p = sum(PESO_TIPO[t] for t in tipos)
    ideal = {t: n * PESO_TIPO[t] / total_p for t in tipos}
    tope = lambda t: MAX_TIPO.get(t, n)
    cuota = {t: min(tope(t), max(MIN_TIPO, int(ideal[t]))) for t in tipos}
    while sum(cuota.values()) < n:
        t = max((x for x in tipos if cuota[x] < tope(x)), key=lambda x: ideal[x] - cuota[x] + rng.random() * .6)
        cuota[t] += 1
    while sum(cuota.values()) > n:
        t = min((x for x in tipos if cuota[x] > MIN_TIPO), key=lambda x: ideal[x] - cuota[x] + rng.random() * .6)
        cuota[t] -= 1
    out, vistos = [], set()
    for t, k in cuota.items():
        usados = {}
        for _ in range(k):
            e = un_ejercicio(rng, t, usados, vistos)
            if e: out.append(e)
            else: print(f"aviso: no se pudo generar un ejercicio de {t}", file=sys.stderr)
    rng.shuffle(out)
    out.sort(key=lambda e: bool(e.get("imagen")))   # los dibujos van al final del test (orden estable)
    for i, e in enumerate(out, 1): e["id"] = i
    return out

def generar_especifico(fecha, tema, n=None, semilla=""):
    """test de un solo tema, de facil a dificil, con el mismo numero de ejercicios por nivel."""
    rng = random.Random(f"{fecha}|{tema}|{semilla}")
    n = n or (N_ESPECIFICO_DIBUJOS if tema in DIBUJOS else N_ESPECIFICO)
    por_nivel = {1: n // 3, 2: n - 2 * (n // 3), 3: n // 3}
    out, vistos, usados = [], set(), {}
    for nivel in (1, 2, 3):
        for _ in range(por_nivel[nivel]):
            e = un_ejercicio(rng, tema, usados, vistos, nivel)
            if e: out.append(e)
            else: print(f"aviso: no se pudo generar un ejercicio de {tema}", file=sys.stderr)
    out.sort(key=lambda e: e["dificultad"])          # estable: dentro de cada nivel se conserva el orden de generacion
    for i, e in enumerate(out, 1): e["id"] = i
    return out

def dificultad(ejercicios):
    """facil / media / dificil segun la media de los niveles de los ejercicios (1-3)."""
    m = dif.media(ejercicios)
    return "facil" if m <= 1.88 else "media" if m <= 1.97 else "dificil"

def siguiente_numero(carpeta):
    nums = [int(m.group(1)) for f in (os.listdir(carpeta) if os.path.isdir(carpeta) else [])
            if (m := re.match(r"psicotecnico_(\d+)_", f))]
    return max(nums, default=0) + 1

def slug(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    return re.sub(r"[^a-z0-9]+", "-", "".join(c for c in t if not unicodedata.combining(c))).strip("-")

def tema_de_la_semana(fecha, ruta_foco):
    """tema del test especifico: de seguimiento/foco.json si lo hay (el primero la semana de la respuesta y luego rota semana a semana);
    si no hay, rotan todos los tipos."""
    temas, desde = [], None
    try:
        foco = json.load(open(ruta_foco, encoding="utf-8"))
        temas = [t for t in foco.get("temas", []) if t in PESO_TIPO]
        desde = foco.get("actualizado")
    except (OSError, ValueError):
        pass
    temas = temas or CICLO
    d = datetime.date.fromisoformat(fecha)
    semanas = (d - datetime.date.fromisoformat(desde)).days // 7 if desde else d.isocalendar()[1]
    return temas[semanas % len(temas)]

def registrar(ruta_indice, entrada):
    try: indice = json.load(open(ruta_indice, encoding="utf-8"))
    except (OSError, ValueError): indice = []
    indice = [e for e in indice if e["archivo"] != entrada["archivo"]] + [entrada]
    open(ruta_indice, "w", encoding="utf-8").write(json.dumps(indice, ensure_ascii=False, indent=1))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fecha", default=datetime.date.today().isoformat())
    ap.add_argument("--modo", choices=["auto", "diario", "especifico"], default="auto")
    ap.add_argument("--tema", default=None, help="tipo del test especifico (por defecto, el de seguimiento/foco.json o el que toque)")
    ap.add_argument("--foco", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "seguimiento", "foco.json"))
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--salida", default="salidas")
    ap.add_argument("--sin-figuras", action="store_true")
    ap.add_argument("--semilla", default="")
    ap.add_argument("--numero", type=int, default=None, help="numero correlativo del test (por defecto, el siguiente libre en la carpeta de salida)")
    ap.add_argument("--html", action="store_true", help="guarda tambien el HTML de origen del PDF")
    ap.add_argument("--json", action="store_true", help="guarda tambien los ejercicios y respuestas en JSON")
    a = ap.parse_args()
    modo = a.modo if a.modo != "auto" else ("especifico" if datetime.date.fromisoformat(a.fecha).weekday() == DIA_ESPECIFICO else "diario")
    os.makedirs(a.salida, exist_ok=True)
    numero = a.numero or siguiente_numero(a.salida)
    if modo == "especifico":
        tema = a.tema or tema_de_la_semana(a.fecha, a.foco)
        if tema not in PESO_TIPO: sys.exit(f"tema desconocido: {tema}. Opciones: {', '.join(PESO_TIPO)}")
        ej = generar_especifico(a.fecha, tema, a.n, a.semilla)
        nombre, titulo, etiqueta = f"psicotecnico_{numero:03d}_especifico_{slug(tema)}_variable", f"Psicotécnicos · Específico: {tema}", "variable"
    else:
        tema = None
        ej = generar(a.fecha, a.n, a.sin_figuras, a.semilla)
        etiqueta = dificultad(ej)
        nombre, titulo = f"psicotecnico_{numero:03d}_{etiqueta}", "Psicotécnicos"
    base = os.path.join(a.salida, nombre)
    imprimible.a_pdf(imprimible.documento_html(a.fecha, ej, titulo), base + ".pdf", f"Psicotécnico {numero:03d} ({etiqueta}) · {a.fecha}", a.html)
    if a.json:
        sin_img = [{k: v for k, v in e.items() if k != "imagen"} for e in ej]
        open(base + ".json", "w", encoding="utf-8").write(json.dumps(dict(fecha=a.fecha, ejercicios=sin_img), ensure_ascii=False, indent=1))
    # indice para el seguimiento: una entrada por test con el tipo, subtipo, dificultad y respuesta de cada ejercicio
    registrar(os.path.join(a.salida, "indice.json"), dict(
        numero=numero, fecha=a.fecha, archivo=nombre + ".pdf", modo=modo, tema=tema, dificultad=etiqueta,
        ejercicios=[dict(n=e["id"], tipo=e["tipo"], subtipo=e["subtipo"], dificultad=dif.ASCII[e["dificultad"]], correcta="ABCD"[e["correcta"]]) for e in ej]))
    por = {}
    for e in ej: por[e["tipo"]] = por.get(e["tipo"], 0) + 1
    niveles = {dif.ASCII[n]: sum(1 for e in ej if e["dificultad"] == n) for n in (1, 2, 3)}
    print(f"{modo}: {len(ej)} ejercicios, dificultad {etiqueta} -> {base}.pdf  {por}  niveles {niveles}")

if __name__ == "__main__":
    main()
