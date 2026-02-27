"""Plotting helpers for crystal visualizations with PyVista."""

import numpy as np
import pyvista as pv
from vis.generation import a_vecs_fcc_planes


def radius_bcc(a: float) -> float:
    return (np.sqrt(3) / 4) * a


def radius_fcc(a: float) -> float:
    return (np.sqrt(2) / 4) * a


def radius_hcp(a: float) -> float:
    return a / 2


def colors_bcc(points: np.ndarray, a: float) -> np.ndarray:
    layer_index = np.rint(points[:, 1] / (0.5 * a)).astype(np.int32)
    lut = np.array([[0, 0, 255], [255, 0, 0]], dtype=np.uint8)
    return lut[layer_index % 2]


def colors_fcc(points: np.ndarray, a: float) -> np.ndarray:
    m = np.rint(points.sum(axis=1) / a).astype(np.int32)
    lut = np.array([[255, 0, 0], [0, 120, 255], [0, 200, 80]], dtype=np.uint8)
    return lut[m % 3]


def colors_fcc_planes(points: np.ndarray, a: float) -> np.ndarray:
    # FCC(111) stacking is spaced by one third of the out-of-plane lattice vector.
    c_axis = float(a_vecs_fcc_planes(a)[2, 1])
    layer_height = abs(c_axis) / 3.0
    layer_index = np.rint(points[:, 1] / layer_height).astype(np.int32)
    lut = np.array([[255, 0, 0], [0, 120, 255], [0, 200, 80]], dtype=np.uint8)
    return lut[layer_index % 3]


def colors_hcp(points: np.ndarray, a: float) -> np.ndarray:
    layer_height = (np.sqrt(6) / 3) * a
    layer_index = np.rint(points[:, 1] / layer_height).astype(np.int32)
    lut = np.array([[0, 0, 255], [255, 0, 0]], dtype=np.uint8)
    return lut[layer_index % 2]


def auto_resolution(num_atoms: int, target_tris: int = 2_000_000) -> int:
    """Choose a sphere resolution capped to a practical range."""
    if num_atoms <= 0:
        return 8
    tris_per_sphere = target_tris / num_atoms
    res = int(np.sqrt(tris_per_sphere / 2))
    return max(8, min(100, res))


def plot_crystal_pyvista(points: np.ndarray, r: float, colors: np.ndarray) -> None:
    start_res = auto_resolution(len(points))

    sphere = pv.Sphere(radius=r, theta_resolution=start_res, phi_resolution=start_res)
    cloud = pv.PolyData(points)
    glyphs = cloud.glyph(geom=sphere, scale=False, orient=False)
    glyphs["colors"] = np.repeat(colors, sphere.n_points, axis=0)

    pl = pv.Plotter()
    actor = pl.add_mesh(glyphs, scalars="colors", rgb=True)
    pl.add_text(f"res = {start_res}", position="upper_left", font_size=14, color="black", name="res_text")

    slider = pl.add_slider_widget(
        callback=lambda _: None,
        rng=(4, 100),
        value=start_res,
        title="Sphere Resolution",
        style="modern",
        pointa=(0.0, 0.85),
        pointb=(0.2, 0.85),
    )
    slider.GetRepresentation().SetLabelFormat("%0.0f")

    def update_res(new_res: float) -> None:
        nonlocal actor
        new_res = int(round(float(new_res)))

        slider.GetRepresentation().SetValue(new_res)

        new_sphere = pv.Sphere(radius=r, theta_resolution=new_res, phi_resolution=new_res)
        new_glyphs = cloud.glyph(geom=new_sphere, scale=False, orient=False)
        new_glyphs["colors"] = np.repeat(colors, new_sphere.n_points, axis=0)

        pl.remove_actor(actor)
        actor = pl.add_mesh(new_glyphs, scalars="colors", rgb=True)

        pl.remove_actor("res_text")
        pl.add_text(f"res = {new_res}", position="upper_left", font_size=14, color="black", name="res_text")
        pl.render()

    slider.AddObserver("EndInteractionEvent", lambda *_: update_res(slider.GetRepresentation().GetValue()))
    pl.show()
