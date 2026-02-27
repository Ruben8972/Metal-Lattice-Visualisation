"""
plotting.py
===========

Funktionen zur Visualisierung von Kristallgittern mit PyVista.
Unterstützt farbliche Hervorhebung verschiedener Gittertypen und interaktive Anpassung der Darstellungsauflösung.

Beispiele
---------
>>> r = radius_fcc(1.0)
>>> points = generate_fcc(1.0, 2)
>>> colors = colors_fcc(points, 1.0)
>>> plot_crystal_pyvista(points, r, colors)
"""

import pyvista as pv
import numpy as np

def radius_bcc(a: float) -> float:
    """
    Returns
    -------
    float
        Radius des Atoms im BCC-Gitter.
    """
    return (np.sqrt(3) / 4) * a

def radius_fcc(a: float) -> float:
    """
    Returns
    -------
    float
        Radius des Atoms im FCC-Gitter.
    """
    return (np.sqrt(2) / 4) * a

def radius_hcp(a: float) -> float:
    """
    Returns
    -------
    float
        Radius des Atoms im HCP-Gitter.
    """
    return a / 2

def colors_bcc(points: np.ndarray, a: float) -> np.ndarray:
    """
    Returns
    -------
    np.ndarray of shape (N, 3)
        RGB-Farben für jeden Punkt (BCC, abwechselnd pro Schicht).
    """
    layer_index = np.rint(points[:, 1] / (0.5 * a)).astype(np.int32)
    lut = np.array([
        [0, 0, 255],
        [255, 0, 0],
    ], dtype=np.uint8)
    return lut[layer_index % 2]
    
def colors_fcc(points: np.ndarray, a: float) -> np.ndarray:
    """
    Returns
    -------
    np.ndarray of shape (N, 3)
        RGB-Farben für jeden Punkt (FCC, 3 Farben nach Schicht).
    """
    m = np.rint(points.sum(axis=1) / a).astype(np.int32)
    lut = np.array([[255, 0, 0], [0, 120, 255], [0, 200, 80]], dtype=np.uint8)
    return lut[m % 3]

def colors_fcc_planes(points: np.ndarray, a: float) -> np.ndarray:
    """
    Returns
    -------
    np.ndarray of shape (N, 3)
        RGB-Farben für jeden Punkt (FCC-Ebene, 3 Farben nach Schicht).
    """
    layer_height = np.sqrt(3)/3
    layer_index = np.rint(points[:, 1] / layer_height).astype(np.int32)
    lut = np.array([[255, 0, 0], [0, 120, 255], [0, 200, 80]], dtype=np.uint8)
    return lut[layer_index % 3]

def colors_hcp(points: np.ndarray, a: float) -> np.ndarray:
    """
    Returns
    -------
    np.ndarray of shape (N, 3)
        RGB-Farben für jeden Punkt (HCP, abwechselnd pro Schicht).
    """
    layer_height = (2*np.sqrt(6)/3) * a / 2 
    layer_index = np.rint(points[:, 1] / layer_height).astype(np.int32)
    lut = np.array([
        [0, 0, 255],
        [255, 0, 0],
    ], dtype=np.uint8)
    return lut[layer_index % 2]

def plot_crystal_pyvista(points: np.ndarray, r: float, colors: np.ndarray) -> None:
    """
    Returns
    -------
    None
        Zeigt ein interaktives PyVista-Fenster mit den Gitterpunkten als Kugeln.
    """
    def auto_resolution(points: np.ndarray, target_tris: int = 2_000_000) -> int:
        """
        Bestimmt die Kugelauflösung so, dass die Gesamtanzahl der Dreiecke ca. target_tris nicht überschreitet.

        Returns
        -------
        int
            Empfohlene Auflösung (Anzahl der Segmente pro Kugel).
        """
        atoms = len(points)

        # Berechne, wie viele Dreiecke pro Kugel möglich sind
        tris_per_sphere = target_tris / atoms
        res = int(np.sqrt(tris_per_sphere / 2))
        return max(8, min(100, res))

    start_res = auto_resolution(points)

    # Erstellen der Kugelgeometrie mithilfe der PolyData cloud
    sphere = pv.Sphere(radius=r, theta_resolution=start_res, phi_resolution=start_res)
    cloud = pv.PolyData(points)
    glyphs = cloud.glyph(geom=sphere, scale=False, orient=False)
    glyphs["colors"] = np.repeat(colors, sphere.n_points, axis=0)

    pl = pv.Plotter()
    actor = pl.add_mesh(glyphs, scalars="colors", rgb=True)
    pl.add_text(f"res = {start_res}", position="upper_left",
                font_size=14, color="black", name="res_text")

    # Slider für die Kugelauflösung
    slider = pl.add_slider_widget(
        callback=lambda v: None,
        rng=(4, 100),
        value=start_res,
        title="Sphere Resolution",
        style="modern",
        pointa=(0.0, 0.85),
        pointb=(0.2, 0.85),
    )
    slider.GetRepresentation().SetLabelFormat("%0.0f")

    def update_res(new_res):
        """
        Aktualisiert die Kugelauflösung und das Rendering, wenn der Slider bewegt wird.

        Returns
        -------
        None
        """
        nonlocal actor
        new_res = int(round(float(new_res)))

        slider.GetRepresentation().SetValue(new_res)

        # Erzeuge neue Kugeln mit aktualisierter Auflösung und aktualisiere die Szene
        new_sphere = pv.Sphere(radius=r, theta_resolution=new_res, phi_resolution=new_res)
        new_glyphs = cloud.glyph(geom=new_sphere, scale=False, orient=False)
        new_glyphs["colors"] = np.repeat(colors, new_sphere.n_points, axis=0)

        pl.remove_actor(actor)
        actor = pl.add_mesh(new_glyphs, scalars="colors", rgb=True)

        pl.remove_actor("res_text")
        pl.add_text(f"res = {new_res}", position="upper_left",
                    font_size=14, color="black", name="res_text")
        pl.render()

    slider.AddObserver("EndInteractionEvent",
        lambda *_: update_res(slider.GetRepresentation().GetValue())
    )

    pl.show()
