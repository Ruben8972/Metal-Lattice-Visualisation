import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from fcc.plotting import plot_phys_ez, plot_fcc_pyvista
from fcc.generation import generate_fcc

def run_gui():
    # Eingabefenster
    root = tk.Tk()
    root.withdraw()  # Hauptfenster ausblenden

    # Auswahl Einheitszelle oder vollständiges Gitter
    plot_unit = messagebox.askyesno(
        title="Einheitszelle?",
        message="Möchten Sie nur eine Einheitszelle plotten?")

    if plot_unit:
        a = simpledialog.askfloat("Gitterkonstante","Länge der Gitterkonstante",minvalue=0.01)
        
        if a is not None:
            plot_phys_ez(a)
        else:
            print("Abgebrochen.")

    #Auswahl parameter für vollständiges Gitter
    else:
        # a und n abfragen
        a = simpledialog.askfloat("Gitterkonstante", "Länge der Gitterkonstante:", minvalue=0.01)
        n = simpledialog.askinteger("Atomanzahl in jede Richtung", "Atomanzahl in jede Richtung:", minvalue=1)

        if a is not None and n is not None:
            plot_fcc_pyvista(generate_fcc(a, n), a)
        else:
            print("Abgebrochen.")

    root.destroy()