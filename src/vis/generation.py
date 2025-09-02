"""
generation.py
==========

Hilfsfunktionen zur Erzeugung von Punktkoordinaten für ideale Kristallgitter
(BCC, FCC, HCP) in kartesischen Koordinaten. Unterstützt sowohl reguläre
rechteckige Gitterschnitte als auch eine hexagonale HCP-„Scheibe“.

Konvention
----------
- `a_vecs` sind 3*3-Matrizen, deren Zeilen die Gittervektoren a1, a2, a3
  (in kartesischen Koordinaten) enthalten.
- `base` sind Basisatome in **fraktionalen** Koordinaten relativ zu a1, a2, a3.
- Rückgaben sind immer `float32`-Arrays der Form (N, 3) in kartesischen Koordinaten.

Numerische Toleranz
-------------------
Die Konstante `TOL` ist auf 1e-5 gesetzt, was sich für Berechnungen mit
`numpy.float32` als robust erwiesen hat.

Beispiele
---------
>>> generate_bcc(1.0, 2)
array([...])  # 16 Punkte im 2x2x2-BCC-Gitter

>>> generate_fcc(1.0, 1)
array([...])  # 4 Punkte im 1x1x1-FCC-Gitter

>>> generate_hcp(1.0, 2)
array([...])  # 8 Punkte im 2x2x2-HCP-Gitter

>>> generate_hcp_hex(1.0, 2, 3, basis_hcp_fracs(), a_vecs_hcp)
array([...])  # HCP-"Scheibe" mit Radius 2 und Höhe 3
"""

import numpy as np
from typing import Callable

TOL = 1e-5  # Toleranz für float32-Vergleiche

def _is_cubic(A: np.ndarray, tol: float = TOL) -> bool:
    """
    Prüft, ob eine Gittermatrix `A` kubisch ist.

    Returns
    -------
    bool
        True, wenn die Matrix kubisch ist, sonst False.
    """
    assert A.shape == (3, 3), "A muss eine 3x3-Matrix sein."
    is_diag = np.allclose(A, np.diag(np.diag(A)), atol=tol)
    is_equal_diag = np.allclose(np.diag(A), A[0, 0], atol=tol)
    return is_diag and is_equal_diag

def generate_crystal(a_vecs: np.ndarray, base: np.ndarray, nxyz: tuple[int, int, int]) -> np.ndarray:
    """
    Erzeugt ein periodisches Gitter aus Basis und Gittervektoren.

    Returns
    -------
    np.ndarray
        Array der Form (N, 3) mit den kartesischen Koordinaten aller Gitterpunkte.
    """
    nx, ny, nz = map(int, nxyz)

    assert a_vecs.shape == (3, 3), "a_vecs muss eine 3x3-Matrix sein."
    assert base.ndim == 2 and base.shape[1] == 3, "base muss Nx3 sein."
    assert nx > 0 and ny > 0 and nz > 0, "nxyz muss positive Dimensionen haben."

    if _is_cubic(a_vecs):
        a = np.float32(a_vecs[0, 0])
        I, J, K = np.meshgrid(
            np.arange(nx, dtype=np.float32) * a,
            np.arange(ny, dtype=np.float32) * a,
            np.arange(nz, dtype=np.float32) * a,
            indexing="ij",
        )
        cells_cart = np.stack([I, J, K], axis=-1).reshape(-1, 3)
        pts = (cells_cart[:, None, :] + base[None, :, :] * a).reshape(-1, 3)
        lim = (nx - 1) * a + TOL
        m = (pts[:, 0] <= lim) & (pts[:, 1] <= lim) & (pts[:, 2] <= lim)
        return pts[m].astype(np.float32)
    else:
        I, J, K = np.meshgrid(
            np.arange(nx, dtype=np.float32),
            np.arange(ny, dtype=np.float32),
            np.arange(nz, dtype=np.float32),
            indexing="ij",
        )
        cells_frac = np.stack([I, J, K], axis=-1).reshape(-1, 3)
        pts_frac = (cells_frac[:, None, :] + base[None, :, :]).reshape(-1, 3)
        lim = (nx - 1) + TOL
        m = (pts_frac[:, 0] <= lim) & (pts_frac[:, 1] <= lim) & (pts_frac[:, 2] <= lim)
        pts_frac = pts_frac[m]
        return (pts_frac @ a_vecs).astype(np.float32)

def basis_bcc_frac() -> np.ndarray:
    """
    Basis für BCC in fraktionalen Koordinaten.

    Returns
    -------
    np.ndarray
        Array der Form (2, 3) mit den fraktionalen Basispositionen für BCC.
    """
    return np.array([[0, 0, 0], [0.5, 0.5, 0.5]], dtype=np.float32)

def basis_fcc_frac() -> np.ndarray:
    """
    Basis für FCC in fraktionalen Koordinaten.

    Returns
    -------
    np.ndarray
        Array der Form (4, 3) mit den fraktionalen Basispositionen für FCC.
    """
    return np.array([[0, 0, 0], [0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]], dtype=np.float32)

def basis_hcp_fracs() -> np.ndarray:
    """
    Basis für HCP in fraktionalen Koordinaten.

    Returns
    -------
    np.ndarray
        Array der Form (2, 3) mit den fraktionalen Basispositionen für HCP.
    """
    return np.array([[0, 0, 0], [1.0/3.0, 1.0/3.0, 0.5]], dtype=np.float32)

def basis_fcc_frac_plane() -> np.ndarray:
    """
    Basis einer FCC-Ebene entlang der <111>-Richtung.

    Returns
    -------
    np.ndarray
        Array der Form (3, 3) mit den fraktionalen Basispositionen für eine FCC-Ebene.
    """
    return np.array([[0, 0, 0], [1/3, 1/3, 1/3], [2/3, 2/3, 2/3]], dtype=np.float32)

def a_vecs_cubic(a: float) -> np.ndarray:
    """
    Kubische Gittermatrix mit Kantenlänge a.

    Returns
    -------
    np.ndarray
        3x3-Matrix der Gittervektoren für ein kubisches Gitter.
    """
    a = np.float32(a)
    return np.array([[a, 0, 0], [0, a, 0], [0, 0, a]], dtype=np.float32)

def a_vecs_hcp(a: float, c_over_a: float = (2*np.sqrt(6))/3) -> np.ndarray:
    """
    HCP-Gittermatrix mit Verhältnis c/a.

    Returns
    -------
    np.ndarray
        3x3-Matrix der Gittervektoren für ein HCP-Gitter.
    """
    a = np.float32(a)
    c = np.float32(c_over_a) * a
    return np.array([[a, 0.0, 0.0],
                     [0.5 * a, 0.0, np.float32(np.sqrt(3)/2) * a],
                     [0.0, c, 0.0]], dtype=np.float32)

def a_vecs_fcc_planes(a: float) -> np.ndarray:
    """
    Gittermatrix für FCC-Ebenen entlang <111>.

    Returns
    -------
    np.ndarray
        3x3-Matrix der Gittervektoren für eine FCC-Ebene.
    """
    c = np.sqrt(3)
    a = (np.sqrt(2) / 2) * a
    return np.array([[a, 0.0, 0.0],
                     [0.5 * a, 0.0, np.sqrt(3)/2 * a],
                     [0.0, c, 0.0]], dtype=np.float32)

def generate_bcc(a: float, n: int) -> np.ndarray:
    """
    Generiert ein BCC-Gitter.

    Returns
    -------
    np.ndarray
        Array der Form (N, 3) mit den kartesischen Koordinaten der BCC-Gitterpunkte.
    """
    return generate_crystal(a_vecs_cubic(a), basis_bcc_frac(), (n, n, n))

def generate_fcc(a: float, n: int) -> np.ndarray:
    """
    Generiert ein FCC-Gitter.

    Returns
    -------
    np.ndarray
        Array der Form (N, 3) mit den kartesischen Koordinaten der FCC-Gitterpunkte.
    """
    return generate_crystal(a_vecs_cubic(a), basis_fcc_frac(), (n, n, n))

def generate_hcp(a: float, n: int) -> np.ndarray:
    """
    Generiert ein HCP-Gitter.

    Returns
    -------
    np.ndarray
        Array der Form (N, 3) mit den kartesischen Koordinaten der HCP-Gitterpunkte.
    """
    return generate_crystal(a_vecs_hcp(a), basis_hcp_fracs(), (n, n, n))

def generate_hcp_hex(a: float, R: int, nz: int, base: np.ndarray, a_vecs: Callable[[float], np.ndarray]) -> np.ndarray:
    """
    Generiert eine hexagonale HCP-Scheibe mit Radius R und Höhe nz.

    Returns
    -------
    np.ndarray
        Array der Form (N, 3) mit den kartesischen Koordinaten der HCP-Scheibe.
    """
    a_vecs = a_vecs(np.float32(a))
    R = int(R)
    nz = int(nz)
    if R < 0 or nz <= 0:
        return np.empty((0, 3), dtype=np.float32)

    q, r = np.meshgrid(
        np.arange(-R, R + 1, dtype=np.float32),
        np.arange(-R, R + 1, dtype=np.float32),
        indexing="ij",
    )
    mask = (np.abs(q) <= R) & (np.abs(r) <= R) & (np.abs(q + r) <= R)
    qr_pairs = np.stack([q[mask], r[mask]], axis=-1)
    n_hex = qr_pairs.shape[0]

    k_vals = np.arange(nz, dtype=np.float32)
    qrk = np.stack([
        np.repeat(qr_pairs[:, 0], nz),
        np.repeat(qr_pairs[:, 1], nz),
        np.tile(k_vals, n_hex),
    ], axis=-1)

    pts_frac = (qrk[:, None, :] + base[None, :, :]).reshape(-1, 3)

    # Punkte außerhalb des hexagonalen Bereichs und der Höhe herausfiltern
    if isinstance(base, np.ndarray) and np.array_equal(base, basis_hcp_fracs()):
        eps = TOL
        qf = pts_frac[:, 0]
        rf = pts_frac[:, 1]
        kf = pts_frac[:, 2]
        keep_hex = (np.abs(qf) <= R + eps) & (np.abs(rf) <= R + eps) & (np.abs(qf + rf) <= R + eps)
        keep_k = (np.abs(kf) <= (nz - 1) + eps)
        m = keep_hex & keep_k
        pts_frac = pts_frac[m]

    pts = (pts_frac @ a_vecs).astype(np.float32)
    return pts