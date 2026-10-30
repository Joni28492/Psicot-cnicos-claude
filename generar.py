#!/usr/bin/env python3
"""Genera la sesion diaria de psicotecnicos.

uso: python3 generar.py [--fecha AAAA-MM-DD] [--n 10..20] [--salida carpeta] [--sin-figuras] [--html] [--json]
Salida: psicotecnico_<NNN>_<dificultad>.pdf (test para imprimir y, en las ultimas paginas, soluciones, autoevaluacion y trucos).
"""
import argparse, datetime, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psico import nucleo, reglas_tres, porcentajes, series, codificacion, problemas, figuras, imprimible   # noqa: F401  (registran generadores)

# peso de cada TIPO al repartir los ejercicios del dia (cada tipo sale al menos una vez)
PESO_TIPO = {"Reglas de tres": 2, "Porcentajes": 2, "Series": 3, "Codificación": 2, "Problemas": 3, "Figuras desplegables": 1.5}
MAX_FIGURAS = 3

def generar(fecha, n=None, sin_figuras=False, semilla=""):
    rng = random.Random(f"{fecha}|{semilla}")
    n = n or rng.randint(10, 20)
    tipos = [t for t in PESO_TIPO if not (sin_figuras and t == "Figuras desplegables")]
    # reparto proporcional a los pesos (maximo restos), minimo 1 por tipo
    total_p = sum(PESO_TIPO[t] for t in tipos)
    ideal = {t: n * PESO_TIPO[t] / total_p for t in tipos}
    cuota = {t: max(1, int(ideal[t])) for t in tipos}
    if "Figuras desplegables" in cuota: cuota["Figuras desplegables"] = min(cuota["Figuras desplegables"], MAX_FIGURAS)
    while sum(cuota.values()) < n:
        t = max((x for x in tipos if not (x == "Figuras desplegables" and cuota[x] >= MAX_FIGURAS)),
                key=lambda x: ideal[x] - cuota[x] + rng.random() * .6)
        cuota[t] += 1
    while sum(cuota.values()) > n:
        t = min((x for x in tipos if cuota[x] > 1), key=lambda x: ideal[x] - cuota[x] + rng.random() * .6)
        cuota[t] -= 1
    out, vistos = [], set()
    for t, k in cuota.items():
        gens = [g for g in nucleo.REGISTRO if g[0] == t]
        usados = {}
        for _ in range(k):
            for intento in range(60):
                # favorece subtipos poco usados hoy
                g = rng.choices(gens, [g[2] / (1 + 2 * usados.get(g[1], 0)) for g in gens])[0]
                try:
                    e = g[4](rng)
                    clave = e["enunciado"] + e.get("destacado", "")
                    if clave in vistos or len(set(e["opciones"])) != len(e["opciones"]): continue
                except (ValueError, RecursionError):
                    continue
                vistos.add(clave); usados[g[1]] = usados.get(g[1], 0) + 1
                e.update(tipo=t, tiempo=g[3], subtipo=g[1]); out.append(e); break
            else:
                print(f"aviso: no se pudo generar un ejercicio de {t}", file=sys.stderr)
    rng.shuffle(out)
    out.sort(key=lambda e: bool(e.get("imagen")))   # las figuras van al final del test (orden estable)
    for i, e in enumerate(out, 1): e["id"] = i
    return out

def dificultad(ejercicios):
    """facil / media / dificil segun la media de lo raro que es cada subtipo (peso bajo = mas dificil)."""
    peso = {(g[0], g[1]): g[2] for g in nucleo.REGISTRO}
    media = sum(5 - peso[(e["tipo"], e["subtipo"])] for e in ejercicios) / len(ejercicios)
    return "facil" if media <= 2.35 else "media" if media <= 2.5 else "dificil"

def siguiente_numero(carpeta):
    nums = [int(m.group(1)) for f in (os.listdir(carpeta) if os.path.isdir(carpeta) else [])
            if (m := re.match(r"psicotecnico_(\d+)_", f))]
    return max(nums, default=0) + 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fecha", default=datetime.date.today().isoformat())
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--salida", default="salidas")
    ap.add_argument("--sin-figuras", action="store_true")
    ap.add_argument("--semilla", default="")
    ap.add_argument("--numero", type=int, default=None, help="numero correlativo del test (por defecto, el siguiente libre en la carpeta de salida)")
    ap.add_argument("--html", action="store_true", help="guarda tambien el HTML de origen del PDF")
    ap.add_argument("--json", action="store_true", help="guarda tambien los ejercicios y respuestas en JSON")
    a = ap.parse_args()
    ej = generar(a.fecha, a.n, a.sin_figuras, a.semilla)
    os.makedirs(a.salida, exist_ok=True)
    numero = a.numero or siguiente_numero(a.salida)
    dif = dificultad(ej)
    base = os.path.join(a.salida, f"psicotecnico_{numero:03d}_{dif}")
    imprimible.a_pdf(imprimible.documento_html(a.fecha, ej), base + ".pdf", f"Psicotécnico {numero:03d} ({dif}) · {a.fecha}", a.html)
    if a.json:
        sin_img = [{k: v for k, v in e.items() if k != "imagen"} for e in ej]
        open(base + ".json", "w", encoding="utf-8").write(json.dumps(dict(fecha=a.fecha, ejercicios=sin_img), ensure_ascii=False, indent=1))
    por = {}
    for e in ej: por[e["tipo"]] = por.get(e["tipo"], 0) + 1
    print(f"{len(ej)} ejercicios, dificultad {dif} -> {base}.pdf  {por}")

if __name__ == "__main__":
    main()
