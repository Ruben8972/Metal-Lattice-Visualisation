"""Utility functions to generate crystal lattice points."""

from typing import Callable

import numpy as np

TOL = 1e-5


def _is_cubic(a_vecs: np.ndarray, tol: float = TOL) -> bool:
    """Return True if a 3x3 lattice matrix is diagonal with equal diagonal entries."""
    assert a_vecs.shape == (3, 3), "a_vecs must be a 3x3 matrix."
    is_diag = np.allclose(a_vecs, np.diag(np.diag(a_vecs)), atol=tol)
    is_equal_diag = np.allclose(np.diag(a_vecs), a_vecs[0, 0], atol=tol)
    return is_diag and is_equal_diag


def generate_crystal(a_vecs: np.ndarray, base: np.ndarray, nxyz: tuple[int, int, int]) -> np.ndarray:
    """Generate periodic crystal points from lattice vectors and a fractional basis."""
    nx, ny, nz = map(int, nxyz)

    assert a_vecs.shape == (3, 3), "a_vecs must be a 3x3 matrix."
    assert base.ndim == 2 and base.shape[1] == 3, "base must be Nx3."
    assert nx > 0 and ny > 0 and nz > 0, "nxyz must contain positive dimensions."

    if _is_cubic(a_vecs):
        a = np.float32(a_vecs[0, 0])
        i, j, k = np.meshgrid(
            np.arange(nx, dtype=np.float32) * a,
            np.arange(ny, dtype=np.float32) * a,
            np.arange(nz, dtype=np.float32) * a,
            indexing="ij",
        )
        cells_cart = np.stack([i, j, k], axis=-1).reshape(-1, 3)
        pts = (cells_cart[:, None, :] + base[None, :, :] * a).reshape(-1, 3)
        limx = (nx - 1) * a + TOL
        limy = (ny - 1) * a + TOL
        limz = (nz - 1) * a + TOL
        mask = (pts[:, 0] <= limx) & (pts[:, 1] <= limy) & (pts[:, 2] <= limz)
        return pts[mask].astype(np.float32)

    i, j, k = np.meshgrid(
        np.arange(nx, dtype=np.float32),
        np.arange(ny, dtype=np.float32),
        np.arange(nz, dtype=np.float32),
        indexing="ij",
    )
    cells_frac = np.stack([i, j, k], axis=-1).reshape(-1, 3)
    pts_frac = (cells_frac[:, None, :] + base[None, :, :]).reshape(-1, 3)
    limx = (nx - 1) + TOL
    limy = (ny - 1) + TOL
    limz = (nz - 1) + TOL
    mask = (pts_frac[:, 0] <= limx) & (pts_frac[:, 1] <= limy) & (pts_frac[:, 2] <= limz)
    pts_frac = pts_frac[mask]
    return (pts_frac @ a_vecs).astype(np.float32)


def basis_bcc_frac() -> np.ndarray:
    return np.array([[0, 0, 0], [0.5, 0.5, 0.5]], dtype=np.float32)


def basis_fcc_frac() -> np.ndarray:
    return np.array(
        [[0, 0, 0], [0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]],
        dtype=np.float32,
    )


def basis_hcp_fracs() -> np.ndarray:
    return np.array([[0, 0, 0], [1.0 / 3.0, 1.0 / 3.0, 0.5]], dtype=np.float32)


def basis_fcc_frac_plane() -> np.ndarray:
    # Equivalent FCC(111) ABC basis; using -1/3 for the third layer reduces edge
    # truncation artifacts for finite clipped hex patches.
    return np.array([[0, 0, 0], [1 / 3, 1 / 3, 1 / 3], [-1 / 3, -1 / 3, 2 / 3]], dtype=np.float32)


def a_vecs_cubic(a: float) -> np.ndarray:
    a = np.float32(a)
    return np.array([[a, 0, 0], [0, a, 0], [0, 0, a]], dtype=np.float32)


def a_vecs_hcp(a: float, c_over_a: float = (2 * np.sqrt(6)) / 3) -> np.ndarray:
    a = np.float32(a)
    c = np.float32(c_over_a) * a
    return np.array(
        [[a, 0.0, 0.0], [0.5 * a, 0.0, np.float32(np.sqrt(3) / 2) * a], [0.0, c, 0.0]],
        dtype=np.float32,
    )


def a_vecs_fcc_planes(a: float) -> np.ndarray:
    a2d = np.float32((np.sqrt(2) / 2) * a)
    c = np.float32(np.sqrt(3) * a)
    return np.array(
        [[a2d, 0.0, 0.0], [0.5 * a2d, 0.0, np.float32(np.sqrt(3) / 2) * a2d], [0.0, c, 0.0]],
        dtype=np.float32,
    )


def generate_bcc(a: float, n: int) -> np.ndarray:
    return generate_crystal(a_vecs_cubic(a), basis_bcc_frac(), (n, n, n))


def generate_fcc(a: float, n: int) -> np.ndarray:
    return generate_crystal(a_vecs_cubic(a), basis_fcc_frac(), (n, n, n))


def generate_hcp(a: float, n: int) -> np.ndarray:
    return generate_crystal(a_vecs_hcp(a), basis_hcp_fracs(), (n, n, n))


def generate_hcp_hex(
    a: float,
    r_cells: int,
    nz: int,
    base: np.ndarray,
    a_vecs_fn: Callable[[float], np.ndarray],
    clip_hex_boundary: bool = True,
) -> np.ndarray:
    """Generate a hexagonal prism in fractional (q, r, k) space and map to Cartesian."""
    lattice_vecs = a_vecs_fn(np.float32(a))
    r_cells = int(r_cells)
    nz = int(nz)
    if r_cells < 0 or nz <= 0:
        return np.empty((0, 3), dtype=np.float32)

    q, r = np.meshgrid(
        np.arange(-r_cells, r_cells + 1, dtype=np.float32),
        np.arange(-r_cells, r_cells + 1, dtype=np.float32),
        indexing="ij",
    )
    mask = (np.abs(q) <= r_cells) & (np.abs(r) <= r_cells) & (np.abs(q + r) <= r_cells)
    qr_pairs = np.stack([q[mask], r[mask]], axis=-1)
    n_hex = qr_pairs.shape[0]

    k_vals = np.arange(nz, dtype=np.float32)
    qrk = np.stack(
        [
            np.repeat(qr_pairs[:, 0], nz),
            np.repeat(qr_pairs[:, 1], nz),
            np.tile(k_vals, n_hex),
        ],
        axis=-1,
    )

    pts_frac = (qrk[:, None, :] + base[None, :, :]).reshape(-1, 3)

    eps = TOL
    qf = pts_frac[:, 0]
    rf = pts_frac[:, 1]
    kf = pts_frac[:, 2]
    keep_k = (kf >= -eps) & (kf <= (nz - 1) + eps)
    if clip_hex_boundary:
        keep_hex = (np.abs(qf) <= r_cells + eps) & (np.abs(rf) <= r_cells + eps) & (np.abs(qf + rf) <= r_cells + eps)
        pts_frac = pts_frac[keep_hex & keep_k]
    else:
        pts_frac = pts_frac[keep_k]

    return (pts_frac @ lattice_vecs).astype(np.float32)
