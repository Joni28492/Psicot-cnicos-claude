# Psicotécnicos diarios

Genera cada día entre 10 y 20 ejercicios de psicotécnicos (resolubles en menos de 20 s con el truco adecuado) y una página HTML interactiva con cronómetro.

## Uso

```bash
pip install -r requirements.txt
python3 generar.py --fecha 2026-10-29 --salida salidas/2026-10-29
```

Opciones: `--n 15` (nº de ejercicios, por defecto aleatorio 10–20), `--sin-figuras`, `--semilla texto` (otra tanda del mismo día).

Salida en la carpeta indicada:

- `psicotecnicos_<fecha>_local.html`: documento completo, se abre con doble clic en el navegador.
- `psicotecnicos_<fecha>.html`: mismo contenido como fragmento, listo para publicar como Artifact.
- `psicotecnicos_<fecha>.json`: ejercicios con respuestas y trucos (sin imágenes).

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
