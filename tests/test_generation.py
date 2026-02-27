import numpy as np

from vis.generation import (
    a_vecs_fcc_planes,
    generate_crystal,
    generate_bcc,
    generate_fcc,
    generate_hcp,
    generate_hcp_hex,
    basis_fcc_frac_plane,
    basis_hcp_fracs,
    a_vecs_hcp,
)


def test_generate_bcc_n2_point_count_and_dtype():
    pts = generate_bcc(1.0, 2)
    assert pts.shape == (9, 3)
    assert pts.dtype == np.float32


def test_generate_fcc_n2_point_count_and_dtype():
    pts = generate_fcc(1.0, 2)
    assert pts.shape == (14, 3)
    assert pts.dtype == np.float32


def test_generate_hcp_n2_point_count_and_dtype():
    pts = generate_hcp(1.0, 2)
    assert pts.shape == (9, 3)
    assert pts.dtype == np.float32


def test_generate_hcp_hex_invalid_dimensions_returns_empty():
    pts = generate_hcp_hex(1.0, 2, 0, basis_hcp_fracs(), a_vecs_hcp)
    assert pts.shape == (0, 3)
    assert pts.dtype == np.float32


def test_generate_crystal_non_cubic_uses_per_axis_limits():
    a_vecs = np.array(
        [[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 3.0]],
        dtype=np.float32,
    )
    base = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]], dtype=np.float32)
    pts = generate_crystal(a_vecs, base, (1, 2, 3))
    assert np.all(pts[:, 0] <= 0.0 + 1e-5)
    assert np.all(pts[:, 1] <= 2.0 + 1e-5)
    assert np.all(pts[:, 2] <= 6.0 + 1e-5)


def test_a_vecs_fcc_planes_scales_with_lattice_constant():
    small = a_vecs_fcc_planes(1.0)
    large = a_vecs_fcc_planes(2.0)
    assert np.allclose(large, 2.0 * small, atol=1e-6)


def test_generate_hcp_hex_applies_height_filter_for_any_base():
    pts = generate_hcp_hex(1.0, 1, 1, basis_fcc_frac_plane(), a_vecs_fcc_planes)
    assert pts.shape[0] > 0
    assert np.allclose(pts[:, 1], 0.0, atol=1e-5)


def _min_pair_distance(points: np.ndarray) -> float:
    diff = points[:, None, :] - points[None, :, :]
    dist2 = np.sum(diff * diff, axis=-1)
    np.fill_diagonal(dist2, np.inf)
    return float(np.sqrt(np.min(dist2)))


def test_no_sphere_overlap_for_all_lattice_builders():
    a = 1.0
    n = 2

    lattice_cases = [
        ("bcc", generate_bcc(a, n), (np.sqrt(3) / 4) * a),
        ("fcc", generate_fcc(a, n), (np.sqrt(2) / 4) * a),
        ("hcp", generate_hcp(a, n), 0.5 * a),
        ("hcp_hex", generate_hcp_hex(a, n, n + 1, basis_hcp_fracs(), a_vecs_hcp), 0.5 * a),
        (
            "fcc_planes",
            generate_hcp_hex(a, n, n + 1, basis_fcc_frac_plane(), a_vecs_fcc_planes),
            (np.sqrt(2) / 4) * a,
        ),
    ]

    for name, pts, radius in lattice_cases:
        assert pts.shape[0] > 1, f"{name}: not enough points for distance check"
        min_dist = _min_pair_distance(pts)
        assert min_dist >= (2.0 * radius) - 1e-5, f"{name}: overlap detected (min_dist={min_dist}, 2r={2*radius})"
