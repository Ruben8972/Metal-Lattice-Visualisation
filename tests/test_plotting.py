import sys
import types

import numpy as np


if "pyvista" not in sys.modules:
    pv_stub = types.SimpleNamespace(Sphere=None, PolyData=None, Plotter=None)
    sys.modules["pyvista"] = pv_stub

from vis.plotting import colors_bcc, radius_bcc, radius_fcc, radius_hcp


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
