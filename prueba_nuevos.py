#!/usr/bin/env python3
"""Prueba de los ejercicios nuevos (series de fichas de domino y de relojes/tartas) sin tocar el generador diario.

uso: python3 prueba_nuevos.py [--salida carpeta] [--semilla texto]
Crea pruebas_nuevos.pdf con 2 ejercicios de cada subtipo nuevo (test + soluciones).
"""
import argparse, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psico import nucleo, domino, relojes, imprimible

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default="pruebas")
    ap.add_argument("--semilla", default="prueba")
    ap.add_argument("--por-tipo", type=int, default=2)
    a = ap.parse_args()
    rng = random.Random(a.semilla)
    ej = []
    for t, nombre, peso, tiempo, fn in nucleo.REGISTRO:
        if t not in (domino.T, relojes.T): continue
        for _ in range(a.por_tipo):
            e = fn(rng); e.update(tipo=t, tiempo=tiempo, subtipo=nombre); ej.append(e)
    for i, e in enumerate(ej, 1): e["id"] = i
    os.makedirs(a.salida, exist_ok=True)
    ruta = os.path.join(a.salida, "pruebas_nuevos.pdf")
    imprimible.a_pdf(imprimible.documento_html("2026-11-02", ej), ruta, "Prueba: fichas de dominó y relojes", False)
    print(f"{len(ej)} ejercicios -> {ruta}")

if __name__ == "__main__":
    main()
