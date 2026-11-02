"""Utilidades de dibujo para ejercicios con imagen (fichas de domino, relojes y tartas)."""
import base64, io, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Wedge, FancyBboxPatch

K, GRIS = "#151515", "#9a9a9a"

def a_uri(fig, dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="white")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def lienzo(ancho, alto_serie, alto_ops, lim_serie, lim_ops):
    """figura con dos ejes: la serie arriba y las 4 opciones abajo (limites = (x0, x1, y0, y1))."""
    fig = plt.figure(figsize=(ancho, alto_serie + alto_ops))
    h = alto_serie + alto_ops
    ax_s = fig.add_axes([0, alto_ops / h, 1, alto_serie / h])
    ax_o = fig.add_axes([0, 0, 1, alto_ops / h])
    for ax, lim in ((ax_s, lim_serie), (ax_o, lim_ops)):
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax_s, ax_o

def interrogante(ax, x, y, w, h, ang=0.0):
    """hueco '?' como rectangulo discontinuo de w x h (largo w en la direccion ang)."""
    u = (math.cos(ang), math.sin(ang)); v = (-u[1], u[0])
    pts = [(x + sx * w / 2 * u[0] + sy * h / 2 * v[0], y + sx * w / 2 * u[1] + sy * h / 2 * v[1]) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    ax.add_patch(Polygon(pts, closed=True, fill=False, ec=GRIS, lw=1.6, ls=(0, (4, 3))))
    ax.text(x, y, "?", ha="center", va="center", fontsize=22, color=GRIS, fontweight="bold")

def letras_opciones(ax, xs, y):
    for l, x in zip("ABCD", xs):
        ax.text(x, y, l, ha="center", va="center", fontsize=15, fontweight="bold", color=K)
