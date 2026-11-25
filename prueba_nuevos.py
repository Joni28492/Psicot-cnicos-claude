#!/usr/bin/env python3
"""Prueba de ejercicios nuevos sin tocar el generador diario.

uso: python3 prueba_nuevos.py [--modulos domino,relojes|comprension,puzzles] [--salida carpeta] [--semilla texto] [--por-tipo N] [--nombre archivo.pdf]
Crea un PDF (test + soluciones) con N ejercicios de cada subtipo de los modulos indicados.
"""
import argparse, importlib, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psico import nucleo, imprimible

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modulos", default="domino,relojes")
    ap.add_argument("--salida", default="pruebas")
    ap.add_argument("--semilla", default="prueba")
    ap.add_argument("--por-tipo", type=int, default=2)
    ap.add_argument("--nombre", default="pruebas_nuevos.pdf")
    ap.add_argument("--subtipos", default="", help="solo estos subtipos (separados por comas), p. ej. texto_largo")
    a = ap.parse_args()
    mods = [importlib.import_module(f"psico.{m}") for m in a.modulos.split(",")]
    tipos = {m.T for m in mods}
    rng = random.Random(a.semilla)
    ej = []
    for t, nombre, peso, tiempo, fn in nucleo.REGISTRO:
        if t not in tipos or (a.subtipos and nombre not in a.subtipos.split(",")): continue
        for _ in range(a.por_tipo):
            for _ in range(50):
                try: e = fn(rng); break
                except ValueError: continue
            else: raise SystemExit(f"no se pudo generar {nombre}")
            for x in (e if isinstance(e, list) else [e]):          # un generador puede devolver varias preguntas sobre un mismo texto
                x.update(tipo=t, tiempo=tiempo, subtipo=nombre); ej.append(x)
    for i, e in enumerate(ej, 1): e["id"] = i
    os.makedirs(a.salida, exist_ok=True)
    ruta = os.path.join(a.salida, a.nombre)
    imprimible.a_pdf(imprimible.documento_html("2026-11-25", ej, "Prueba: " + " y ".join(sorted(tipos))), ruta, "Prueba de ejercicios nuevos", False)
    print(f"{len(ej)} ejercicios -> {ruta}")

if __name__ == "__main__":
    main()
