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


# def generate_fcc_(a, n):
#     points_fcc = []
#     for i in range(n):
#         for j in range(n):
#             for k in range(n):
#                 # Basisvektoren des FCC Gitters
#                 points_fcc.append(np.array([i * a, j * a, k * a]))
#                 if i < n-1 and j < n-1:
#                     points_fcc.append(np.array([i * a + a/2, j * a + a/2, k * a]))
#                 if i < n-1 and k < n-1:
#                     points_fcc.append(np.array([i * a + a/2, j * a, k * a + a/2]))
#                 if j < n-1 and k < n-1:
#                     points_fcc.append(np.array([i * a, j * a + a/2, k * a + a/2]))
#     return points_fcc

# Funktion zur Erstellung der Einheitszellenvektoren
# def einheitszellenvektoren_fcc(a):
#     allowed_points = [np.array(c) for c in it.product([0, a], repeat=3)]
#     for axis in range(3):
#         for element in [0, a]:
#             v=np.array([a/2, a/2, a/2])
#             v[axis] = element
#             allowed_points.append(v)
#     return allowed_points

# def generate_bcc(a, n):
#     # Alle Gitterkoordinaten (n³ Punkte)
#     coords = np.stack(np.meshgrid(
#         np.arange(n), np.arange(n), np.arange(n),
#         indexing="ij"
#     ), axis=-1).reshape(-1, 3) * a

#     # Basisvektoren für BCC
#     basis = np.array([
#         [0, 0, 0],
#         [a/2, a/2, a/2]
#     ], dtype=np.float32)

#     # Basis auf alle Punkte anwenden (Broadcasting)
#     points = (coords[:, None, :] + basis[None, :, :]).reshape(-1, 3)

#     mask = np.all(points <= (n-1) * a + 1e-9, axis=1)
#     points = points[mask]
#     return points.astype(np.float32)
    


