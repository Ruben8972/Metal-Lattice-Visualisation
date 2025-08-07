import pyvista as pv
import numpy as np
from fcc.generation import einheitszellenvektoren

# Funktion zur Visualisierung des FCC Gitters mit PyVista
def plot_fcc_pyvista(points, a):
    r = (np.sqrt(2) * a) / 4
    plotter = pv.Plotter()
    colors = []

    # Überprüfen der dichtesten Ebenen, zuweisen von Farben und erzeugen der Kugeln
    for p in points:
        val= p[0] + p[1] + p[2]
        m= int(round(val/a))
        if m % 3 == 0:
            color = 'red'
        elif (m-1) % 3 == 0:
            color = 'blue'
        elif (m-2) % 3 == 0:
            color = 'green'
        else:
            color = 'gray'
        sphere = pv.Sphere(radius=r, center=p)
        plotter.add_mesh(sphere, color=color, opacity=1)
    plotter.show()

def plot_phys_ez(a):
    points = einheitszellenvektoren(a)
    plot_fcc_pyvista(points, a)

def plot_clipped_ez(a: float):
    """
    1) Erzeugt alle Kugeln der konventionellen FCC-Einheitszelle.
    2) Trianguliert und kombiniert sie zu einem einzigen PolyData-Mesh.
    3) Schneidet dieses Mesh sequenziell mit sechs Ebenen (Box [0,a]^3),
       wobei clip_closed_surface an jeder Ebene eine geschlossene Kappe erzeugt.
    4) Färbt die resultierenden Teil-Kugeln rot/blau/grün nach Ebenenzugehörigkeit.
    5) Plottet im gewohnten Fenster.
    """
    # Kugelradius
    r = (np.sqrt(2) * a) / 4

    # 1) Erzeuge und trianguliere jede Kugel, sammle in MultiBlock
    blocks = pv.MultiBlock()
    for p in einheitszellenvektoren(a):
        sph = pv.Sphere(radius=r, center=p).extract_surface().triangulate()
        blocks.append(sph)

    # 2) Kombiniere alle Blöcke und stelle sicher, dass es ein PolyData ist
    mesh = blocks.combine().extract_surface().triangulate()

    # 3) Definiere die sechs Schnittebenen einer Box [0,a]^3
    planes = [
        ([ 1,  0,  0], [0,   0,   0]),  # x >= 0
        ([-1,  0,  0], [a,   0,   0]),  # x <= a
        ([ 0,  1,  0], [0,   0,   0]),  # y >= 0
        ([ 0, -1,  0], [0,   a,   0]),  # y <= a
        ([ 0,  0,  1], [0,   0,   0]),  # z >= 0
        ([ 0,  0, -1], [0,   0,   a]),  # z <= a
    ]

    # 4) Schneide nacheinander mit clip_closed_surface (PolyData-Methode!)
    for normal, origin in planes:
        mesh = mesh.clip_closed_surface(normal=normal, origin=origin)

    # 5) Färbung nach Ebenenzugehörigkeit
    centers = mesh.cell_centers().points
    colors = []
    for cc in centers:
        m = int(round((cc.sum()) / a))
        if m % 3 == 0:
            colors.append([1.0, 0.0, 0.0])
        elif (m - 1) % 3 == 0:
            colors.append([0.0, 0.0, 1.0])
        else:
            colors.append([0.0, 1.0, 0.0])
    mesh.cell_data["cell_color"] = np.array(colors)

    # 6) Plotten
    p = pv.Plotter()
    p.add_mesh(mesh, scalars="cell_color", rgb=True, smooth_shading=True)
    p.show()