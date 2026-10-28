import base64, os, tempfile
from .nucleo import ejercicio

T = "Figuras desplegables"
FIG = ["cubo", "cubo", "cubo", "tetraedro", "octaedro", "prisma", "piramide"]
TEMAS = ["formas", "dados", "lineas", "grises", "colores", "texturas", "mixto"]
TEMAS_CUBO = ["formas", "dados", "colores", "lineas", "mixto", "grises"]

@ejercicio(T, peso=3, tiempo=30)
def figura(rng):
    from . import poliedros
    f = rng.choice(FIG)
    tema = rng.choice(TEMAS_CUBO if f == "cubo" else TEMAS)
    if f in ("octaedro",) and tema in ("grises", "colores"): tema = "mixto"
    modo = rng.choice(["a", "b"])
    with tempfile.TemporaryDirectory() as d:
        ruta = os.path.join(d, "f.png")
        letra = poliedros.generate(f, tema, modo, rng.randint(1, 10 ** 6), ruta)
        datos = base64.b64encode(open(ruta, "rb").read()).decode()
    if modo == "a":
        enun = "¿Qué figura se forma al plegar este desarrollo?"
        truco = ("Elige dos caras que compartan arista en el desarrollo y comprueba si en la figura esas dos caras están juntas y con el mismo giro; "
                 "así descartas opciones rápido. Las caras opuestas nunca se ven a la vez.")
    else:
        enun = "¿Qué desarrollo forma esta figura?"
        truco = ("Localiza en la figura dos caras vecinas con un símbolo orientado (líneas, dominó…) y busca el desarrollo donde esas caras "
                 "estén pegadas con ese mismo giro. Las caras opuestas no pueden estar pegadas en el desarrollo.")
    return dict(enunciado=enun, opciones=list("ABCD"), correcta="ABCD".index(letra), truco=truco,
                imagen="data:image/png;base64," + datos, figura=f)
