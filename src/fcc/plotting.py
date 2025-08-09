import pyvista as pv
import pyvistaqt
from pyvistaqt import BackgroundPlotter
import numpy as np
from fcc.generation import generate_fcc, einheitszellenvektoren_fcc, generate_bcc, einheitszellenvektoren_bcc

# Funktion zur Visualisierung des FCC Gitters mit PyVista
def plot_fcc_pyvista(points_fcc, a):
    r = (np.sqrt(2) * a) / 4
    plotter = pv.Plotter()
    colors = []
    # Überprüfen der dichtesten Ebenen, zuweisen von Farben und erzeugen der Kugeln
    for p in points_fcc:
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

def plot_phys_ez_fcc(a):
    points = einheitszellenvektoren_fcc(a)
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
    for p in einheitszellenvektoren_fcc(a):
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

# def plot_bcc_pyvista(points_bcc, a):
#     r = (np.sqrt(3) * a) /4
#     plotter = pv.Plotter()
#     color = []
#     for p in points_bcc:
#         val = p[0] + p[1] + p[2]
#         m = int(round(2*val/a))
#         if m % 2 == 0:
#             color = 'blue'
#         else:
#             color = 'red'
#         sphere = pv.Sphere(radius=r, center=p)
#         plotter.add_mesh(sphere, color=color, opacity=1)
#     plotter.show()

def plot_bcc_pyvista(points, a):
    def auto_resolution(points, target_tris=2_000_000):
        atoms = len(points)
        tris_per_sphere = target_tris / atoms
        res = int(np.sqrt(tris_per_sphere / 2))
        return max(8, min(100, res))

    start_res = auto_resolution(points)

    # Farben vorbereiten
    is_half = np.any(np.isclose(points % 1.0, 0.5, atol=1e-6), axis=1)
    colors = np.zeros((len(points), 3), dtype=np.uint8)
    colors[is_half] = [255, 0, 0]
    colors[~is_half] = [0, 0, 255]

    r = (np.sqrt(3) / 4) * a

    # Initial-Glyphs + Farben setzen
    sphere = pv.Sphere(radius=r, theta_resolution=start_res, phi_resolution=start_res)
    cloud = pv.PolyData(points)
    glyphs = cloud.glyph(geom=sphere, scale=False, orient=False)
    glyphs["colors"] = np.repeat(colors, sphere.n_points, axis=0)

    pl = pv.Plotter()
    actor = pl.add_mesh(glyphs, scalars="colors", rgb=True)
    pl.add_text(f"res = {start_res}", position="upper_left",
                font_size=14, color="black", name="res_text")

    # Erst Slider erstellen (ohne funktionalen Callback)
    slider = pl.add_slider_widget(
        callback=lambda v: None,  # Platzhalter
        rng=(4, 100),
        value=start_res,
        title="Sphere Resolution",
        style="modern",
        pointa=(0.0, 0.85),
        pointb=(0.2, 0.85),
    )
    slider.GetRepresentation().SetLabelFormat("%0.0f")

    # Jetzt Callback definieren (slider existiert bereits)
    def update_res(new_res):
        nonlocal actor
        new_res = int(round(float(new_res)))

        slider.GetRepresentation().SetValue(new_res)

        new_sphere = pv.Sphere(radius=r, theta_resolution=new_res, phi_resolution=new_res)
        new_glyphs = cloud.glyph(geom=new_sphere, scale=False, orient=False)
        new_glyphs["colors"] = np.repeat(colors, new_sphere.n_points, axis=0)

        pl.remove_actor(actor)
        actor = pl.add_mesh(new_glyphs, scalars="colors", rgb=True)

        pl.remove_actor("res_text")
        pl.add_text(f"res = {new_res}", position="upper_left",
                    font_size=14, color="black", name="res_text")
        pl.render()

    # Slider-Event verbinden
    slider.AddObserver("EndInteractionEvent",
        lambda *_: update_res(slider.GetRepresentation().GetValue())
    )

    pl.show()