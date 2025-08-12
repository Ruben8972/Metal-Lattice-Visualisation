import numpy as np
import itertools as it

def _is_cubic(A, tol=1e-5):
    A = np.asarray(A)
    return (
        abs(A[0,1]) < tol and abs(A[0,2]) < tol and
        abs(A[1,0]) < tol and abs(A[1,2]) < tol and
        abs(A[2,0]) < tol and abs(A[2,1]) < tol and
        abs(A[0,0]-A[1,1]) < tol and abs(A[1,1]-A[2,2]) < tol)

def generate_crystal(a_vecs, base, nxyz):
    a_vecs= np.asarray(a_vecs, dtype=np.float32)
    base = np.asarray(base, dtype=np.float32)
    nx, ny, nz = map(int, nxyz)

    if _is_cubic(a_vecs):
        a = np.float32(a_vecs[0,0])

        I, J, K = np.meshgrid(
            np.arange(nx, dtype=np.float32) * a,
            np.arange(ny, dtype=np.float32) * a,
            np.arange(nz, dtype=np.float32) * a,
            indexing="ij",
        )
        cells_cart = np.stack([I, J, K], axis=-1).reshape(-1, 3)
        pts = (cells_cart[:, None, :] + base[None, :, :] * a).reshape(-1, 3)
        lim = (nx - 1) * a + 1e-5
        m = (pts[:,0] <= lim) & (pts[:,1] <= lim) & (pts[:,2] <= lim)
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
        lim = (nx - 1) + 1e-5
        m = (pts_frac[:,0] <= lim) & (pts_frac[:,1] <= lim) & (pts_frac[:,2] <= lim)
        pts_frac = pts_frac[m]
        return (pts_frac @ a_vecs).astype(np.float32)

def basis_bcc_frac():
    return np.array([[0,0,0],[0.5,0.5,0.5]], dtype=np.float32)

def basis_fcc_frac():
    return np.array([[0,0,0],[0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5]], dtype=np.float32)

def basis_hcp_fracs():
     return np.array([[0, 0, 0],
                     [1.0/3.0, 1.0/3.0, 0.5]], dtype=np.float32)

def basis_fcc_frac_plane():
    return np.array([[0, 0, 0],
                     [1/3, 1/3, 1/3],
                     [2/3, 2/3, 2/3]], dtype=np.float32
                    )

def a_vecs_cubic(a):
    a = np.float32(a)
    return np.array([[a,0,0],[0,a,0],[0,0,a]], dtype=np.float32)

def a_vecs_hcp(a, c_over_a=(2*np.sqrt(6))/3):
    a = np.float32(a)
    c = np.float32(c_over_a) * a
    return np.array([[a, 0.0, 0.0],
                     [0.5 * a, 0.0, np.float32(np.sqrt(3)/2) * a],
                     [0.0, c, 0.0]], dtype=np.float32)

def generate_bcc(a, n):
    return generate_crystal(a_vecs_cubic(a), basis_bcc_frac(), (n,n,n))

def generate_fcc(a, n):
    return generate_crystal(a_vecs_cubic(a), basis_fcc_frac(), (n,n,n))

def generate_hcp(a, n):
    return generate_crystal(a_vecs_hcp(a), basis_hcp_fracs(), (n,n,n))

def generate_hcp_hex(a, R, nz, base, c_over_a=(2*np.sqrt(6))/3):
    a_vecs = a_vecs_hcp(np.float32(a), c_over_a=np.float32(c_over_a))
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
    eps = 1e-5
    qf = pts_frac[:, 0]
    rf = pts_frac[:, 1]
    kf = pts_frac[:, 2]
    keep_hex = (np.abs(qf) <= R + eps) & (np.abs(rf) <= R + eps) & (np.abs(qf + rf) <= R + eps)
    keep_k = (np.abs(kf) <= (nz-1)+ eps)
    m = keep_hex & keep_k
    pts = pts_frac[m]
    pts = (pts @ a_vecs).astype(np.float32)

    return pts