"""Dificultad de cada ejercicio: 1 = facil, 2 = media, 3 = dificil.

Un generador puede devolver `dificultad` en su dict (cuando depende de los parametros concretos);
si no, se usa el nivel base de su subtipo.
"""
NOMBRE = {1: "fácil", 2: "media", 3: "difícil"}
ASCII = {1: "facil", 2: "media", 3: "dificil"}

BASE = {
    # Reglas de tres
    "directa": 1, "inversa": 2, "compuesta": 2, "trabajo_conjunto": 3,
    # Porcentajes
    "porcentaje_de": 1, "que_porcentaje": 1, "porcentaje_inverso": 2, "variacion": 2, "sube_y_baja": 2, "descuentos": 2, "iva": 2,
    "porcentaje_de_porcentaje": 3,
    # Series
    "letras_salto": 1, "num_aritmetica": 1, "num_geometrica": 1, "num_cuadrados": 1,
    "letras_creciente": 2, "letras_alternas": 2, "letra_numero": 2, "num_creciente": 2, "num_alternas": 2, "num_fibonacci": 2,
    "letras_bloques": 3, "num_operaciones": 3, "num_dos_operaciones": 3, "num_primos_o_triangulares": 3,
    # Codificación
    "cesar": 1, "valor_palabra": 1, "espejo": 2, "vocales": 2, "digitos": 2, "renombrar": 3,
    # Problemas
    "cabezas_patas": 1, "mas_que": 1, "veces": 2, "ecuacion": 2, "combinatoria": 2, "edades": 3, "encuentro": 3,
    # Figuras, fichas y relojes (algunos suben o bajan segun el ejercicio concreto)
    "figura": 3, "domino_fila": 1, "domino_fila_vertical": 1, "domino_dos_filas": 2, "domino_circulo": 3, "domino_espiral": 3,
    "reloj": 2, "tarta": 2, "puntos": 2,
    # Combinatoria (cada ejercicio fija su nivel segun la variante)
    "permutaciones": 2, "variaciones": 2, "combinaciones": 2,
}

def nivel(e):
    return e.get("dificultad") or BASE.get(e["subtipo"], 2)

def media(ejercicios):
    return sum(nivel(e) for e in ejercicios) / len(ejercicios)
