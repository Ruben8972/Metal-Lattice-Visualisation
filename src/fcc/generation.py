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
    

def basis_bcc_frac():
    return np.array([[0,0,0],[0.5,0.5,0.5]], dtype=np.float32)

def basis_fcc_frac():
    return np.array([[0,0,0],[0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5]], dtype=np.float32)

def a_vecs_cubic(a):
    a = np.float32(a)
    return np.array([[a,0,0],[0,a,0],[0,0,a]], dtype=np.float32)

def generate_bcc(a, n):
    return generate_crystal(a_vecs_cubic(a), basis_bcc_frac(), (n,n,n))

def generate_fcc(a, n):
    return generate_crystal(a_vecs_cubic(a), basis_fcc_frac(), (n,n,n))
