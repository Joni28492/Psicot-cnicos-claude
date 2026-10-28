# Psicotécnicos diarios

Genera cada día entre 10 y 20 ejercicios de psicotécnicos (resolubles en menos de 20 s con el truco adecuado) como documentos PDF para imprimir.

## Uso

```bash
pip install -r requirements.txt
python3 generar.py --fecha 2026-10-29 --salida salidas/2026-10-29
```

Opciones: `--n 15` (nº de ejercicios, por defecto aleatorio 10–20), `--sin-figuras`, `--semilla texto` (otra tanda del mismo día), `--html` y `--json` (ver abajo).

Requiere Python 3.11 o superior con `matplotlib` y `numpy`, y Node con `playwright` y Chromium (el PDF se crea imprimiendo el HTML con Chromium).

Salida en la carpeta indicada: `psicotecnicos_<fecha>.pdf`, un único documento A4 con:

- el test, en una columna (ejercicios de texto primero y figuras desplegables al final, a ancho completo);
- al final, las soluciones: clave de respuestas, tabla de autoevaluación por tipo y el truco de cada ejercicio (en dos columnas).

Opciones extra: `--html` guarda el HTML de origen y `--json` guarda los ejercicios con respuestas.

La misma fecha produce siempre los mismos ejercicios.

## Tipos incluidos

| Tipo | Archivo | Qué genera |
|---|---|---|
| Figuras desplegables | `psico/figuras.py`, `psico/poliedros.py` | Desarrollo → figura armada o al revés (cubo, tetraedro, octaedro, prisma, pirámide) con formas, dados, líneas, grises, colores y texturas |
| Reglas de tres | `psico/reglas_tres.py` | Directas, inversas, compuestas y trabajo conjunto |
| Porcentajes | `psico/porcentajes.py` | Porcentajes que son fracciones sencillas, variaciones, descuentos, IVA |
| Series | `psico/series.py` | Letras (alfabeto español de 27), números y mixtas |
| Codificación | `psico/codificacion.py` | Desplazamiento, valor de palabra, espejo, vocales, cifras, renombrar |
| Problemas | `psico/problemas.py` | Cabezas y patas, uno más que otro, edades, ecuaciones, combinatoria |

## Añadir un tipo nuevo

1. Crea `psico/mi_tipo.py` con funciones decoradas con `@ejercicio("Nombre del tipo", peso=2, tiempo=20)` que reciben un `random.Random` y devuelven un dict con `enunciado`, `opciones` (4 textos distintos), `correcta` (índice), `truco` y, opcionalmente, `destacado` o `imagen`.
2. Impórtalo en `generar.py` y añade el nombre del tipo a `PESO_TIPO`.

El maquetado de impresión está en `psico/imprimible.py` (CSS y HTML) y `psico/pdf.js` (HTML → PDF).
