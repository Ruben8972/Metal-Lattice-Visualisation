import numpy as np
import itertools as it

# Funktion zur Generierung der FCC Gitterpunkte
# a: Gitterkonstante, n: Anzahl der Einheiten in jeder Richtung
def generate_fcc(a, n):
    points_fcc = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                # Basisvektoren des FCC Gitters
                points_fcc.append(np.array([i * a, j * a, k * a]))
                if i < n-1 and j < n-1:
                    points_fcc.append(np.array([i * a + a/2, j * a + a/2, k * a]))
                if i < n-1 and k < n-1:
                    points_fcc.append(np.array([i * a + a/2, j * a, k * a + a/2]))
                if j < n-1 and k < n-1:
                    points_fcc.append(np.array([i * a, j * a + a/2, k * a + a/2]))
    return points_fcc

# def generate_bcc(a, n):
#     points_bcc = []
#     for i in range(n):
#         for j in range(n):
#             for k in range(n):
#                 # Basisvektoren des BCC Gitters
#                 points_bcc.append(np.array([i * a, j * a, k * a]))
#                 if i < n-1 and j < n-1 and k < n-1:
#                     points_bcc.append(np.array([i*a + a/2, j*a + a/2, k*a + a/2]))
#     return points_bcc

def generate_bcc(a, n):
    # Alle Gitterkoordinaten (n³ Punkte)
    coords = np.stack(np.meshgrid(
        np.arange(n), np.arange(n), np.arange(n),
        indexing="ij"
    ), axis=-1).reshape(-1, 3) * a

    # Basisvektoren für BCC
    basis = np.array([
        [0, 0, 0],
        [a/2, a/2, a/2]
    ], dtype=np.float32)

    # Basis auf alle Punkte anwenden (Broadcasting)
    points = (coords[:, None, :] + basis[None, :, :]).reshape(-1, 3)

    mask = np.all(points <= (n-1) * a + 1e-9, axis=1)
    points = points[mask]
    return points.astype(np.float32)
    

# Funktion zur Erstellung der Einheitszellenvektoren
def einheitszellenvektoren_fcc(a):
    allowed_points = [np.array(c) for c in it.product([0, a], repeat=3)]
    for axis in range(3):
        for element in [0, a]:
            v=np.array([a/2, a/2, a/2])
            v[axis] = element
            allowed_points.append(v)
    return allowed_points

def einheitszellenvektoren_bcc(a):
    allowed_points = [np.array(c) for c in it.product([0, a], repeat=3)]
    allowed_points.append(np.array([a/2, a/2, a/2]))
    return allowed_points