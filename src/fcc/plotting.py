import pyvista as pv
import numpy as np
from fcc.generation import einheitszellenvektoren

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

def plot_phys_ez(a):
    points = einheitszellenvektoren(a)
    plot_fcc_pyvista(points, a)