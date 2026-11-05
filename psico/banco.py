"""Banco de ejercicios en el repositorio: una subcarpeta por tipo con todos los ejercicios generados.

ejercicios/<tipo>/ejercicios.json   datos de cada ejercicio (para el seguimiento)
ejercicios/<tipo>/ejercicios.md     lectura comoda en GitHub (enunciado, opciones, respuesta, truco, imagen)
ejercicios/<tipo>/img/<id>.png      dibujos de los ejercicios con imagen
ejercicios/<tipo>/tests/            PDFs de los tests especificos de ese tipo
"""
import base64, hashlib, json, os, re, shutil, unicodedata
from .dificultad import ASCII, NOMBRE

def slug(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    return re.sub(r"[^a-z0-9]+", "-", "".join(c for c in t if not unicodedata.combining(c))).strip("-")

def id_ejercicio(e):
    """identificador estable: el mismo ejercicio (texto, opciones y dibujo) siempre tiene el mismo id."""
    h = hashlib.sha1((e["enunciado"] + e.get("destacado", "") + "|".join(e["opciones"]) + e.get("imagen", "")).encode()).hexdigest()
    return h[:10]

def md(tipo, datos):
    cuenta = {n: sum(1 for d in datos if d["dificultad"] == ASCII[n]) for n in (1, 2, 3)}
    out = [f"# {tipo}\n", f"{len(datos)} ejercicios · " + " · ".join(f"{NOMBRE[n]}: {c}" for n, c in cuenta.items()) + "\n"]
    for d in datos:
        niv = next(NOMBRE[n] for n in (1, 2, 3) if ASCII[n] == d["dificultad"])
        out.append(f"## {d['id']} · {niv} · {d['subtipo']}\n*Test {d['numero']:03d} ({d['fecha']}), ejercicio {d['n']}*\n")
        out.append(d["enunciado"] + "\n")
        if d.get("destacado"): out.append(f"**{d['destacado']}**\n")
        if d.get("imagen"): out.append(f"![ejercicio]({d['imagen']})\n")
        else: out.append("\n".join(f"- {'ABCD'[i]}) {o}" for i, o in enumerate(d["opciones"])) + "\n")
        out.append(f"**Respuesta: {d['correcta']}.** {d['truco']}\n")
    return "\n".join(out)

def guardar(raiz, ejercicios, numero, fecha, modo, archivo_pdf=None, ruta_pdf=None):
    """añade los ejercicios del test al banco (sin duplicar) y, si es un test especifico, copia su PDF a la carpeta de su tipo."""
    por_tipo = {}
    for e in ejercicios: por_tipo.setdefault(e["tipo"], []).append(e)
    for tipo, lista in por_tipo.items():
        carpeta = os.path.join(raiz, slug(tipo))
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, "ejercicios.json")
        try: datos = json.load(open(ruta, encoding="utf-8"))
        except (OSError, ValueError): datos = []
        ids = {d["id"] for d in datos}
        for e in lista:
            i = id_ejercicio(e)
            if i in ids: continue
            ids.add(i)
            img = None
            if e.get("imagen"):
                img = f"img/{i}.png"; os.makedirs(os.path.join(carpeta, "img"), exist_ok=True)
                open(os.path.join(carpeta, img), "wb").write(base64.b64decode(e["imagen"].split(",", 1)[1]))
            datos.append(dict(id=i, test=archivo_pdf, numero=numero, fecha=fecha, modo=modo, n=e["id"], subtipo=e["subtipo"],
                              dificultad=ASCII[e["dificultad"]], enunciado=e["enunciado"], destacado=e.get("destacado"),
                              opciones=e["opciones"], correcta="ABCD"[e["correcta"]], truco=e["truco"], imagen=img, tiempo=e["tiempo"]))
        open(ruta, "w", encoding="utf-8").write(json.dumps(datos, ensure_ascii=False, indent=1))
        open(os.path.join(carpeta, "ejercicios.md"), "w", encoding="utf-8").write(md(tipo, datos))
        if modo == "especifico" and ruta_pdf and os.path.isfile(ruta_pdf):
            os.makedirs(os.path.join(carpeta, "tests"), exist_ok=True)
            shutil.copy(ruta_pdf, os.path.join(carpeta, "tests", os.path.basename(ruta_pdf)))
