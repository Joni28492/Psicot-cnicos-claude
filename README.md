# Psicotécnicos diarios

Genera cada día 30–42 ejercicios de psicotécnicos (resolubles en menos de 20 s con el truco adecuado) como documentos PDF para imprimir.

## Uso

```bash
pip install -r requirements.txt
python3 generar.py --fecha 2026-10-29 --salida salidas/2026-10-29
```

Opciones: `--n 15` (nº de ejercicios, por defecto aleatorio 10–20), `--sin-figuras`, `--semilla texto` (otra tanda del mismo día), `--html` y `--json` (ver abajo).

Requiere Python 3.11 o superior con `matplotlib` y `numpy`, y Node con `playwright` y Chromium (el PDF se crea imprimiendo el HTML con Chromium).

Salida en la carpeta indicada: `psicotecnico_<NNN>_<dificultad>.pdf` (p. ej. `psicotecnico_005_facil.pdf`; NNN es el siguiente número libre en la carpeta, o `--numero`; la dificultad `facil`/`media`/`dificil` se calcula según lo raro que es cada subtipo de ejercicio del test), un único documento A4 con:

- el test, en una columna (ejercicios de texto primero y figuras desplegables al final, a ancho completo);
- al final, las soluciones: clave de respuestas, tabla de autoevaluación por tipo y el truco de cada ejercicio (en dos columnas).

Opciones extra: `--html` guarda el HTML de origen y `--json` guarda los ejercicios con respuestas.

La misma fecha produce siempre los mismos ejercicios.

## Tests diarios y específicos

- **Diario** (de domingo a viernes): 30–42 ejercicios de 6 de los 9 tipos; los otros 3 rotan según la fecha y salen en los tests siguientes. Nombre: `psicotecnico_NNN_facil|media|dificil.pdf`.
- **Específico** (sábados): un solo tipo, 21 ejercicios (12 si son dibujos) con dificultad creciente, a partes iguales fácil/media/difícil. Nombre: `psicotecnico_NNN_especifico_<tema>_variable.pdf`. El tema sale de `seguimiento/foco.json` (los tipos en que más te atascas; rotan por semana) o, si está vacío, rotan los 9 tipos. Se puede forzar con `--modo especifico --tema "Combinatoria"`.
- Las soluciones indican la dificultad de cada ejercicio y hay una tabla de autoevaluación por tipo y por dificultad.
- `salidas/indice.json` guarda, por test, el tipo, subtipo, dificultad y respuesta correcta de cada ejercicio, para el seguimiento de resultados.

## Tipos incluidos

| Tipo | Archivo | Qué genera |
|---|---|---|
| Figuras desplegables | `psico/figuras.py`, `psico/poliedros.py` | Desarrollo → figura armada o al revés (cubo, tetraedro, octaedro, prisma, pirámide) con formas, dados, líneas, grises, colores y texturas |
| Series de fichas | `psico/domino.py` | Fichas de dominó en fila, fila vertical, dos filas, círculo o espiral; cada mitad sube/baja un paso fijo (módulo 7) |
| Series de relojes | `psico/relojes.py` | Relojes de agujas, tartas (sectores que giran y crecen) y círculos con puntos que se mueven |
| Combinatoria | `psico/combinatoria.py` | Permutaciones («¿de cuántas formas…?»), variaciones («M elementos, N espacios», con y sin repetición) y combinaciones («¿cuántas parejas/tríos/grupos…?») |
| Reglas de tres | `psico/reglas_tres.py` | Directas, inversas, compuestas y trabajo conjunto |
| Porcentajes | `psico/porcentajes.py` | Porcentajes que son fracciones sencillas, variaciones, descuentos, IVA |
| Series | `psico/series.py` | Letras (alfabeto español de 27), números y mixtas |
| Codificación | `psico/codificacion.py` | Desplazamiento, valor de palabra, espejo, vocales, cifras, renombrar |
| Problemas | `psico/problemas.py` | Cabezas y patas, uno más que otro, edades, ecuaciones, combinatoria |

## Añadir un tipo nuevo

1. Crea `psico/mi_tipo.py` con funciones decoradas con `@ejercicio("Nombre del tipo", peso=2, tiempo=20)` que reciben un `random.Random` y devuelven un dict con `enunciado`, `opciones` (4 textos distintos), `correcta` (índice), `truco` y, opcionalmente, `destacado` o `imagen`.
2. Impórtalo en `generar.py` y añade el nombre del tipo a `PESO_TIPO`.

El maquetado de impresión está en `psico/imprimible.py` (CSS y HTML) y `psico/pdf.js` (HTML → PDF).
