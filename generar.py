#!/usr/bin/env python3
"""Genera la sesion diaria de psicotecnicos.

uso: python3 generar.py [--fecha AAAA-MM-DD] [--n 10..20] [--salida carpeta] [--sin-figuras]
Salida: psicotecnicos_<fecha>.html (fragmento listo para publicar como Artifact),
        psicotecnicos_<fecha>_local.html (documento completo para abrir en el navegador),
        psicotecnicos_<fecha>.json (ejercicios con respuestas).
"""
import argparse, datetime, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psico import nucleo, reglas_tres, porcentajes, series, codificacion, problemas, figuras   # noqa: F401  (registra generadores)

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
    for i, e in enumerate(out, 1): e["id"] = i
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fecha", default=datetime.date.today().isoformat())
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--salida", default="salida")
    ap.add_argument("--sin-figuras", action="store_true")
    ap.add_argument("--semilla", default="")
    a = ap.parse_args()
    ej = generar(a.fecha, a.n, a.sin_figuras, a.semilla)
    os.makedirs(a.salida, exist_ok=True)
    datos = json.dumps(dict(fecha=a.fecha, ejercicios=ej), ensure_ascii=False).replace("</", "<\\/")
    plantilla = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plantilla.html"), encoding="utf-8").read()
    html = plantilla.replace("__DATOS__", datos)
    base = os.path.join(a.salida, f"psicotecnicos_{a.fecha}")
    open(base + ".html", "w", encoding="utf-8").write(html)
    open(base + "_local.html", "w", encoding="utf-8").write(
        '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + html + "</body></html>")
    open(base + ".json", "w", encoding="utf-8").write(json.dumps(dict(fecha=a.fecha, ejercicios=[{k: v for k, v in e.items() if k != "imagen"} for e in ej]), ensure_ascii=False, indent=1))
    por = {}
    for e in ej: por[e["tipo"]] = por.get(e["tipo"], 0) + 1
    print(f"{len(ej)} ejercicios -> {base}.html  {por}")

if __name__ == "__main__":
    main()
