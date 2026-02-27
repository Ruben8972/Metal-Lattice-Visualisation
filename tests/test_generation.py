import numpy as np

from vis.generation import (
    generate_bcc,
    generate_fcc,
    generate_hcp,
    generate_hcp_hex,
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
