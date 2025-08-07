#Erstellung eines FCC Gitters mit Numpy und Pyvista
import numpy as np
import pyvista as pv
import itertools as it
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox

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

# Funktion zur Visualisierung des FCC Gitters mit PyVista
def plot_fcc_pyvista(points, a):
    r = (np.sqrt(2) * a) / 4
    plotter = pv.Plotter()
    colors = []
    for p in points:
        # Prüfe Ebenenzugehörigkeit
        val= p[0] + p[1] + p[2]
        m= int(round(val/a))
        if m % 3 == 0:
            color = 'red'
        elif (m-1) % 3 == 0:
            color = 'blue'
        elif (m-2) % 3 == 0:
            color = 'green'
        else:
            color = 'gray'
        sphere = pv.Sphere(radius=r, center=p)
        plotter.add_mesh(sphere, color=color, opacity=1)
    plotter.show()

def einheitszellenvektoren(a):
    allowed_points = [np.array(c) for c in it.product([0, a], repeat=3)]
    for axis in range(3):
        for element in [0, a]:
            v=np.array([a/2, a/2, a/2])
            v[axis] = element
            allowed_points.append(v)
    return allowed_points

# --- Eingabefenster für a und n ---
root = tk.Tk()
root.withdraw()  # Hauptfenster ausblenden

plot_unit = messagebox.askyesno(
    title="Einheitszelle?",
    message="Möchten Sie nur eine Einheitszelle plotten?")

if plot_unit:
    # Nur a abfragen
    a = simpledialog.askfloat("Gitterkonstante","Länge der Gitterkonstante",minvalue=0.01)
    
    if a is not None:
        points = einheitszellenvektoren(a)
        plot_fcc_pyvista(points, a)
    else:
        print("Abgebrochen.")
else:
    # a und n abfragen
    a = simpledialog.askfloat("Gitterkonstante", "Länge der Gitterkonstante:", minvalue=0.01)
    n = simpledialog.askinteger("Atomanzahl in jede Richtung", "Atomanzahl in jede Richtung:", minvalue=1)

    if a is not None and n is not None:
        plot_fcc_pyvista(generate_fcc(a, n), a)
    else:
        print("Abgebrochen.")

root.destroy()