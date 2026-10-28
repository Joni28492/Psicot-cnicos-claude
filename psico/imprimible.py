"""Documentos para imprimir: el test (sin respuestas) y el solucionario, en HTML estatico -> PDF."""
import html, os, subprocess, tempfile
from collections import Counter

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
L = "ABCD"

def fecha_larga(iso):
    import datetime
    d = datetime.date.fromisoformat(iso)
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}"

e_ = html.escape

CSS = """
@page { size: A4; }
* { box-sizing: border-box; }
body { margin: 0; font: 10.2pt/1.38 "Liberation Sans", Arial, "Helvetica Neue", sans-serif; color: #000; background: #fff; }
.mono { font-family: "Liberation Mono", "DejaVu Sans Mono", monospace; }
header.cab { border-bottom: .6mm solid #000; padding-bottom: 3mm; margin-bottom: 4mm; }
h1 { font-size: 22pt; margin: 0; letter-spacing: .02em; text-transform: uppercase; }
.sub { font-size: 11pt; margin: 1mm 0 0; }
.campos { display: flex; gap: 8mm; margin: 4mm 0 2mm; font-size: 9.5pt; }
.campos span { flex: 1; border-bottom: .3mm solid #000; padding-bottom: .5mm; white-space: nowrap; }
.campos span.corto { flex: .55; }
.instr { font-size: 9pt; margin: 2mm 0 0; color: #222; }
.cols { column-count: 2; column-gap: 9mm; column-rule: .2mm solid #bbb; }
.ej { break-inside: avoid; margin: 0 0 6mm; }
.ej.fig { margin: 0 0 5mm; padding-top: 3mm; border-top: .2mm solid #bbb; }
.parte { margin: 6mm 0 3mm; break-after: avoid; }
.parte small { font-size: 9pt; font-weight: 400; text-transform: none; letter-spacing: 0; }
.cab-e { display: flex; align-items: baseline; gap: 2.5mm; margin-bottom: 1mm; }
.n { font-weight: 700; font-size: 11.5pt; min-width: 6.5mm; height: 6.5mm; border: .4mm solid #000; border-radius: 1.2mm; display: inline-grid; place-items: center; padding: 0 1mm; }
.tipo { font-size: 7.5pt; text-transform: uppercase; letter-spacing: .08em; color: #444; }
.enun { margin: 0 0 1.5mm; white-space: pre-line; }
.dest { font: 700 12.5pt "Liberation Mono", monospace; letter-spacing: .06em; border: .25mm dashed #777; padding: 1.5mm 2.5mm; margin: 0 0 2mm; overflow-wrap: anywhere; }
.ops { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(36mm, 1fr)); gap: 1.6mm 4mm; }
.ops li { display: flex; align-items: center; gap: 1.8mm; min-width: 0; }
.o { flex: none; display: inline-grid; place-items: center; width: 5.4mm; height: 5.4mm; border: .35mm solid #000; border-radius: 50%; font-size: 7.5pt; font-weight: 700; }
.fig figure { margin: 1mm auto 2mm; text-align: center; }
.fig img { max-width: 120mm; max-height: 88mm; width: auto; height: auto; }
.fig .ops { display: flex; justify-content: center; gap: 12mm; }
h2 { font-size: 13pt; margin: 0 0 3mm; text-transform: uppercase; letter-spacing: .04em; }
.soluciones { break-before: page; }
.respuestas { column-count: 3; column-gap: 8mm; }
.fila { break-inside: avoid; display: flex; align-items: center; gap: 2mm; margin-bottom: 2.2mm; }
.fila b { width: 6.5mm; text-align: right; font-size: 10pt; }
.pie-hoja { margin-top: 6mm; display: flex; gap: 10mm; font-size: 10pt; }
.pie-hoja span { border-bottom: .3mm solid #000; flex: 1; padding-bottom: .5mm; }
/* soluciones */
.clave { display: flex; flex-wrap: wrap; gap: 1.5mm 5mm; font: 700 10.5pt "Liberation Mono", monospace; margin-bottom: 5mm; }
.sol { break-inside: avoid; margin: 0 0 3.2mm; padding-bottom: 2.6mm; border-bottom: .2mm solid #ccc; display: grid; grid-template-columns: 8mm 1fr; gap: 0 2mm; }
.sol .n { min-width: 6.5mm; }
.sol p { margin: 0 0 .8mm; }
.sol .r { font-weight: 700; }
.sol img { max-width: 70mm; max-height: 55mm; margin-top: 1mm; border: .2mm solid #bbb; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin-bottom: 5mm; }
th, td { border: .25mm solid #000; padding: 1.4mm 2mm; text-align: left; }
th { background: #eee; font-size: 8pt; text-transform: uppercase; letter-spacing: .05em; }
"""

def burbujas(n_ops=4):
    return "".join(f'<span class="o">{L[i]}</span>' for i in range(n_ops))

def bloque(e, n):
    fig = bool(e.get("imagen"))
    p = [f'<section class="ej{" fig" if fig else ""}"><div class="cab-e"><span class="n">{n}</span><span class="tipo">{e_(e["tipo"])}</span></div>',
         f'<p class="enun">{e_(e["enunciado"])}</p>']
    if e.get("destacado"): p.append(f'<div class="dest">{e_(e["destacado"])}</div>')
    if fig:
        p.append(f'<figure><img src="{e["imagen"]}" alt="Figura del ejercicio {n}"></figure>')
        p.append('<ul class="ops">' + "".join(f'<li><span class="o">{L[i]}</span></li>' for i in range(4)) + "</ul>")
    else:
        p.append('<ul class="ops">' + "".join(f'<li><span class="o">{L[i]}</span><span>{e_(o)}</span></li>' for i, o in enumerate(e["opciones"])) + "</ul>")
    p.append("</section>")
    return "".join(p)

def tiempo_total(ej):
    s = sum(e["tiempo"] for e in ej)
    return f"{s // 60} min {s % 60:02d} s"

def parte_test(fecha, ej):
    cab = f"""<header class="cab"><h1>Psicotécnicos</h1><p class="sub">Test del {fecha_larga(fecha)} · {len(ej)} ejercicios</p>
    <div class="campos"><span>Nombre:</span><span class="corto">Hora inicio:</span><span class="corto">Hora fin:</span></div>
    <p class="instr">Marca una sola opción por ejercicio. Todos se pueden resolver en menos de 20 segundos si ves el truco (30 segundos las figuras
    desplegables). Tiempo orientativo del test completo: <b>{tiempo_total(ej)}</b>. Pasa a otro ejercicio en cuanto te atasques. Las soluciones y sus explicaciones están en las últimas páginas.</p></header>"""
    # primero los ejercicios de texto; las figuras, al final y a ancho completo
    texto = [(i, e) for i, e in enumerate(ej, 1) if not e.get("imagen")]
    figs = [(i, e) for i, e in enumerate(ej, 1) if e.get("imagen")]
    cuerpo = "".join(bloque(e, i) for i, e in texto)
    if figs:
        cuerpo += '<h2 class="parte">Figuras desplegables <small>(30 segundos por ejercicio)</small></h2>' + "".join(bloque(e, i) for i, e in figs)
    return cab + cuerpo

def texto_respuesta(e):
    i = e["correcta"]
    return f'{L[i]}' if e.get("imagen") else f'{L[i]}) {e["opciones"][i]}'

def parte_soluciones(fecha, ej):
    clave = "".join(f"<span>{i}·{L[e['correcta']]}</span>" for i, e in enumerate(ej, 1))
    por = Counter(e["tipo"] for e in ej)
    tabla = "<table><tr><th>Tipo</th><th>Ejercicios</th><th>Aciertos</th></tr>" + "".join(
        f"<tr><td>{e_(t)}</td><td>{n}</td><td></td></tr>" for t, n in por.items()) + \
        f"<tr><td><b>Total</b></td><td><b>{len(ej)}</b></td><td></td></tr></table>"
    sol = []
    for i, e in enumerate(ej, 1):
        cuerpo = f'<p class="r">{i}. {e_(e["tipo"])} → {e_(texto_respuesta(e))}</p><p>{e_(e["truco"])}</p>'
        if e.get("imagen"): cuerpo += f'<img src="{e["imagen"]}" alt="">'
        sol.append(f'<section class="sol"><span class="n">{i}</span><div>{cuerpo}</div></section>')
    return (f'<div class="soluciones"><header class="cab"><h1>Soluciones</h1><p class="sub">Test del {fecha_larga(fecha)} · {len(ej)} ejercicios</p></header>'
            f'<h2>Clave de respuestas</h2><div class="clave">{clave}</div><h2>Autoevaluación</h2>{tabla}'
            f'<h2>Explicaciones y trucos</h2><div class="cols">{"".join(sol)}</div></div>')

def documento_html(fecha, ej):
    """test (una columna) + soluciones y explicaciones (dos columnas) en un solo documento."""
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Psicotécnicos {fecha}</title><style>{CSS}</style></head>'
            f'<body>{parte_test(fecha, ej)}{parte_soluciones(fecha, ej)}</body></html>')

def a_pdf(html_str, ruta_pdf, pie, guardar_html=False):
    aqui = os.path.dirname(os.path.abspath(__file__))
    ruta_pdf = os.path.abspath(ruta_pdf)
    ruta_html = ruta_pdf[:-4] + ".html" if guardar_html else None
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html_str); tmp = f.name
    try:
        if ruta_html: open(ruta_html, "w", encoding="utf-8").write(html_str)
        r = subprocess.run(["node", os.path.join(aqui, "pdf.js"), tmp, ruta_pdf, pie], capture_output=True, text=True, timeout=180)
        if r.returncode:
            raise RuntimeError("fallo al crear el PDF: " + r.stderr[-400:])
    finally:
        os.unlink(tmp)
