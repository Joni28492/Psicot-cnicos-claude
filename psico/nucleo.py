"""Registro de generadores y utilidades comunes.

Para añadir un tipo nuevo: crea un modulo en psico/, decora funciones `f(rng) -> dict`
con @ejercicio("Nombre del tipo", peso=..., tiempo=20) y añadelo a TIPOS en psico/__init__ de generar.py.
La funcion devuelve: enunciado, opciones (lista de str), correcta (indice), truco,
y opcionalmente destacado (texto grande, p. ej. una serie) e imagen (data URI).
"""
import math
from fractions import Fraction

ALFABETO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"          # 27 letras
ALFABETO26 = ALFABETO.replace("Ñ", "")
REGISTRO = []                                       # (tipo, nombre, peso, tiempo, fn)

def ejercicio(tipo, peso=1, tiempo=20):
    def deco(fn):
        REGISTRO.append((tipo, fn.__name__, peso, tiempo, fn))
        return fn
    return deco

def num(x):
    """formato espanol: 2,5 / 12 / 1.250"""
    if isinstance(x, Fraction):
        x = float(x) if x.denominator != 1 else int(x)
    if isinstance(x, float):
        x = round(x, 2)
        if x == int(x): x = int(x)
    if isinstance(x, int):
        return f"{x:,}".replace(",", ".")
    return str(x).replace(".", ",")

def pct(f):
    """Fraction -> '12,5%' o '33⅓%'"""
    f = Fraction(f) * 100
    if f.denominator == 1: return f"{f.numerator}%"
    ent, resto = divmod(f.numerator, f.denominator)
    sufijo = {Fraction(1, 3): "⅓", Fraction(2, 3): "⅔"}.get(Fraction(resto, f.denominator))
    if sufijo: return f"{ent}{sufijo}%"
    return f"{float(f):.2f}".rstrip("0").rstrip(".").replace(".", ",") + "%"

def mezclar(correcta, falsas, rng, k=4):
    """devuelve (opciones, indice_correcto) con k opciones distintas."""
    vistas, falsas_ok = {str(correcta)}, []
    for f in falsas:
        if str(f) not in vistas:
            vistas.add(str(f)); falsas_ok.append(f)
    if len(falsas_ok) < k - 1:
        raise ValueError("faltan distractores")
    ops = [correcta] + falsas_ok[:k - 1]
    rng.shuffle(ops)
    return [str(o) for o in ops], ops.index(correcta)

def distractores_num(c, rng, extras=(), positivo=True):
    """extras primero (errores tipicos), luego vecinos."""
    cand = list(extras)
    vec = [c + 1, c - 1, c + 2, c - 2, c * 2, c + 10, c - 10, c + 5, c - 5, c + 3, c - 3]
    rng.shuffle(vec)
    cand += vec
    out = []
    for x in cand:
        if x == c or x in out: continue
        if positivo and x <= 0: continue
        out.append(x)
    return out

def letra(i):
    return ALFABETO[i % 27]

def indice(l):
    return ALFABETO.index(l)

def divisores(n):
    return [d for d in range(1, n + 1) if n % d == 0]
