import numpy as np
import itertools as it

# Funktion zur Generierung der FCC Gitterpunkte
# a: Gitterkonstante, n: Anzahl der Einheiten in jeder Richtung
def generate_fcc(a, n):
    points = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                # Basisvektoren des FCC Gitters
                points.append(np.array([i * a, j * a, k * a]))
                points.append(np.array([i * a + a/2, j * a + a/2, k * a]))
                points.append(np.array([i * a + a/2, j * a, k * a + a/2]))
                points.append(np.array([i * a, j * a + a/2, k * a + a/2]))
    return np.array(points)

# Funktion zur Erstellung der Einheitszellenvektoren
def einheitszellenvektoren(a):
    allowed_points = [np.array(c) for c in it.product([0, a], repeat=3)]
    for axis in range(3):
        for element in [0, a]:
            v=np.array([a/2, a/2, a/2])
            v[axis] = element
            allowed_points.append(v)
    return allowed_points