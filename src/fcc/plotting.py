import pyvista as pv
import numpy as np
from fcc.generation import generate_fcc, generate_bcc

# def plot_clipped_ez(a: float):

#     # Kugelradius
#     r = (np.sqrt(2) * a) / 4

#     # 1) Erzeuge und trianguliere jede Kugel, sammle in MultiBlock
#     blocks = pv.MultiBlock()
#     for p in einheitszellenvektoren_fcc(a):
#         sph = pv.Sphere(radius=r, center=p).extract_surface().triangulate()
#         blocks.append(sph)

#     # 2) Kombiniere alle Blöcke und stelle sicher, dass es ein PolyData ist
#     mesh = blocks.combine().extract_surface().triangulate()

#     # 3) Definiere die sechs Schnittebenen einer Box [0,a]^3
#     planes = [
#         ([ 1,  0,  0], [0,   0,   0]),  # x >= 0
#         ([-1,  0,  0], [a,   0,   0]),  # x <= a
#         ([ 0,  1,  0], [0,   0,   0]),  # y >= 0
#         ([ 0, -1,  0], [0,   a,   0]),  # y <= a
#         ([ 0,  0,  1], [0,   0,   0]),  # z >= 0
#         ([ 0,  0, -1], [0,   0,   a]),  # z <= a
#     ]

#     # 4) Schneide nacheinander mit clip_closed_surface (PolyData-Methode!)
#     for normal, origin in planes:
#         mesh = mesh.clip_closed_surface(normal=normal, origin=origin)

#     # 5) Färbung nach Ebenenzugehörigkeit
#     centers = mesh.cell_centers().points
#     colors = []
#     for cc in centers:
#         m = int(round((cc.sum()) / a))
#         if m % 3 == 0:
#             colors.append([1.0, 0.0, 0.0])
#         elif (m - 1) % 3 == 0:
#             colors.append([0.0, 0.0, 1.0])
#         else:
#             colors.append([0.0, 1.0, 0.0])
#     mesh.cell_data["cell_color"] = np.array(colors)

#     # 6) Plotten
#     p = pv.Plotter()
#     p.add_mesh(mesh, scalars="cell_color", rgb=True, smooth_shading=True)
#     p.show()

def radius_bcc(a):
    return (np.sqrt(3) / 4) * a

def radius_fcc(a):
    return (np.sqrt(2) / 4) * a

def radius_fcc_planes(a):
    return 

def radius_hcp(a):
    return a/2

def colors_bcc(points, a):
    layer_index = np.rint(points[:, 1] / 0.5).astype(np.int32)
    lut = np.array([
        [0, 0, 255],
        [255, 0, 0],
    ], dtype=np.uint8)
    return lut[layer_index % 2]
    
def colors_fcc(points, a):
    m = np.rint(points.sum(axis=1) / a).astype(np.int32)
    lut = np.array([[255, 0, 0], [0, 120, 255], [0, 200, 80]], dtype=np.uint8)
    return lut[m % 3]

def colors_fcc_planes(points, a):
    layer_height = np.sqrt(3)/3
    layer_index = np.rint(points[:, 1] / layer_height).astype(np.int32)
    lut = np.array([[255, 0, 0], [0, 120, 255], [0, 200, 80]], dtype=np.uint8)
    return lut[layer_index % 3]

def colors_hcp(points, a):
  
    layer_height = (2*np.sqrt(6)/3) * a / 2 
    layer_index = np.rint(points[:, 1] / layer_height).astype(np.int32)
    lut = np.array([
        [0, 0, 255],
        [255, 0, 0],
    ], dtype=np.uint8)
    return lut[layer_index % 2]

def plot_crystal_pyvista(points, r, colors):
    def auto_resolution(points, target_tris=2_000_000):
        atoms = len(points)
        tris_per_sphere = target_tris / atoms
        res = int(np.sqrt(tris_per_sphere / 2))
        return max(8, min(100, res))

    start_res = auto_resolution(points)

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