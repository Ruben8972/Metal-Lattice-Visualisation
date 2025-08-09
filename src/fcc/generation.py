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

def generate_bcc(a, n):
    points_bcc = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                # Basisvektoren des BCC Gitters
                points_bcc.append(np.array([i * a, j * a, k * a]))
                if i < n-1 and j < n-1 and k < n-1:
                    points_bcc.append(np.array([i*a + a/2, j*a + a/2, k*a + a/2]))
    return points_bcc
    

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