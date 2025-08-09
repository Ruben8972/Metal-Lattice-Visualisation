import tkinter as tk
from tkinter import simpledialog, messagebox
from fcc.plotting import plot_fcc_pyvista, plot_phys_ez_fcc, plot_clipped_ez, plot_bcc_pyvista, plot_phys_ez_bcc
from fcc.generation import generate_fcc, generate_bcc

def run_gui():
     # 1. Auswahlfenster für Gittertyp
    auswahl = {}

    def set_gittertyp(typ):
        auswahl['typ'] = typ
        auswahlfenster.destroy()
    
    def center_window(window, width=250, height=180):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    auswahlfenster = tk.Tk()
    auswahlfenster.withdraw()  # Unsichtbar starten!

    auswahlfenster.title("Gitter auswählen")
    center_window(auswahlfenster, 250, 180)

    frage = tk.Label(auswahlfenster, text="Welches Gitter wollen Sie erstellen?")
    frage.pack(pady=10)

    for name in ["fcc", "hcp", "bcc"]:
        tk.Button(auswahlfenster, text=name.upper(), width=10,
                  command=lambda typ=name: set_gittertyp(typ)).pack(pady=5)

    auswahlfenster.deiconify()  # Jetzt erst anzeigen!
    auswahlfenster.mainloop()
    gittertyp = auswahl.get('typ', None)

    if gittertyp == "fcc":

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
                clipped = messagebox.askyesno(
                    title="Einheitszelle-Typ",
                    message="Möchten Sie die Einheitszelle geclippt anzeigen?")
                if clipped:
                    plot_clipped_ez(a)
                else: plot_phys_ez_fcc(a)
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

    elif gittertyp == "hcp":
        messagebox.showinfo("HCP", "HCP-Gitter ist noch nicht implementiert.")
    elif gittertyp == "bcc":
         # Eingabefenster
        root = tk.Tk()
        root.withdraw()  # Hauptfenster ausblenden

        # Auswahl Einheitszelle oder vollständiges Gitter
        plot_unit = messagebox.askyesno(
            title="Einheitszelle?",
            message="Möchten Sie nur eine Einheitszelle plotten?")
        if plot_unit:
            a = simpledialog.askfloat("Gitterkonstante", "Länge der Gitterkonstante:", minvalue=0.01)
            
            if a is not None:
                clipped = messagebox.askyesno(
                    title="Einheitszelle-Typ",
                    message="Möchten Sie die Einheitszelle geclippt anzeigen?")
                if clipped:
                    messagebox.showinfo("BCC", "Clipped Einheitszelle für BCC ist noch nicht implementiert.")
                else: plot_phys_ez_bcc(a)
            else:
                print("Abgebrochen.")
        else:
            # a und n abfragen
            a = simpledialog.askfloat("Gitterkonstante", "Länge der Gitterkonstante:", minvalue=0.01)
            n = simpledialog.askinteger("Atomanzahl in jede Richtung", "Atomanzahl in jede Richtung:", minvalue=1)

            if a is not None and n is not None:
                plot_bcc_pyvista(generate_bcc(a, n), a)
            else:
                print("Abgebrochen.")
    else: print ("Programmabbruch")