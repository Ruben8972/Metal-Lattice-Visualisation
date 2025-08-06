#Erstellung eines FCC Gitters mit Numpy und Matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pyvista as pv
import tkinter as tk
from tkinter import simpledialog

def generate_fcc(a, n):
    # Erzeugt ein FCC Gitter mit Gitterkonstante a und n Einheiten in jeder Richtung
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

def plot_fcc_pyvista(points, a):
    r = (np.sqrt(2) * a) / 4
    plotter = pv.Plotter()
    for p in points:
        sphere = pv.Sphere(radius=r, center=p)
        plotter.add_mesh(sphere, color='red', opacity=1)
    plotter.show()

# --- Eingabefenster für a und n ---
root = tk.Tk()
root.withdraw()  # Hauptfenster ausblenden

a = simpledialog.askfloat("Gitterkonstante", "Wert für a (z.B. 1.0):", minvalue=0.01)
n = simpledialog.askinteger("Gittergröße", "Wert für n (z.B. 5):", minvalue=1)

root.destroy()

if a is not None and n is not None:
    plot_fcc_pyvista(generate_fcc(a, n), a)
else:
    print("Abgebrochen.")