import sys
import types

import numpy as np

from vis.generation import a_vecs_fcc_planes
if "pyvista" not in sys.modules:
    pv_stub = types.SimpleNamespace(Sphere=None, PolyData=None, Plotter=None)
    sys.modules["pyvista"] = pv_stub

from vis.plotting import auto_resolution, colors_bcc, colors_fcc_planes, radius_bcc, radius_fcc, radius_hcp


def test_radius_functions_positive():
    assert radius_bcc(1.0) > 0
    assert radius_fcc(1.0) > 0
    assert radius_hcp(1.0) > 0


def test_colors_bcc_respects_lattice_constant_scale():
    points = np.array([[0.0, 1.0, 0.0]], dtype=np.float32)
    colors = colors_bcc(points, a=2.0)
    assert colors.shape == (1, 3)
    assert colors.dtype == np.uint8
    assert np.array_equal(colors[0], np.array([255, 0, 0], dtype=np.uint8))


def test_auto_resolution_handles_zero_atoms():
    assert auto_resolution(0) == 8


def test_colors_fcc_planes_follows_plane_spacing():
    a = 2.0
    layer_height = float(a_vecs_fcc_planes(a)[2, 1]) / 3.0
    points = np.array(
        [[0.0, 0.0, 0.0], [0.0, layer_height, 0.0], [0.0, 2.0 * layer_height, 0.0]],
        dtype=np.float32,
    )
    cols = colors_fcc_planes(points, a=a)
    assert len(np.unique(cols, axis=0)) == 3
