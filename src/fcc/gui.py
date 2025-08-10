import tkinter as tk
from tkinter import simpledialog, messagebox
from fcc.plotting import plot_crystal_pyvista, radius_bcc, colors_bcc, radius_fcc, colors_fcc, radius_hcp, colors_hcp
from fcc.generation import generate_fcc, generate_bcc, generate_hcp

GITTER = {
    "fcc": {"generate": generate_fcc, "radius": radius_fcc, "colors": colors_fcc},
    "bcc": {"generate": generate_bcc, "radius": radius_bcc, "colors": colors_bcc},
    "hcp": {"generate": generate_hcp, "radius": radius_hcp, "colors": colors_hcp},
}

def center_window(window, width=250, height=180):
    window.withdraw()
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.deiconify()

def ask_and_plot(kind: str, fns: dict) -> None:
    root = tk.Tk()
    root.withdraw()

    plot_unit = messagebox.askyesno(
        parent=root,
        title="Einheitszelle?",
        message="Möchten Sie nur eine Einheitszelle plotten?",
    )

    a = simpledialog.askfloat(
        "Gitterkonstante",
        "Länge der Gitterkonstante:",
        parent=root,
        minvalue=0.01,
    )
    if a is None:
        root.destroy()
        print("Abgebrochen.")
        return
    
    if plot_unit:
        clipped = messagebox.askyesno(
            parent=root,
            title="Einheitszelle-Typ",
            message="Möchten Sie die Einheitszelle geclippt anzeigen?",
        )
        if clipped:
            messagebox.showinfo(kind.upper(), f"Clipped Einheitszelle für {kind.upper()} ist noch nicht implementiert.")
            root.destroy()
            return
        pts = fns["generate"](a, 2)

    else:
        n = simpledialog.askinteger(
            "Atomanzahl in jede Richtung",
            "Atomanzahl in jede Richtung:",
            parent=root,
            minvalue=1,
        )
        if n is None:
            root.destroy()
            print("Abgebrochen.")
            return
        pts = fns["generate"](a, n)
    
    r = fns["radius"](a)
    cols = fns["colors"](pts, a)
    plot_crystal_pyvista(pts, r, cols)

    root.destroy()

def run_gui() -> None:
    
    selection = {}

    def set_choice(typ: str) -> None:
        selection["typ"] = typ
        win.destroy()
    
    win = tk.Tk()
    win.title("Gitter auswählen")
    center_window(win, 260, 220)

    tk.Label(win, text="Welches Gitter wollen Sie erstellen?").pack(pady=10)
    for name in ["fcc", "bcc", "hcp"]:
        btn = tk.Button(win, 
                text=name.upper(), 
                width=12, 
                command=lambda t=name: set_choice(t)
                )
        btn.pack(pady=5)
    win.mainloop()

    kind = selection.get("typ")
    if not kind:
        print("Programmabbruch")
        return

    fns = GITTER.get(kind)
    if fns is None:
        messagebox.showinfo(kind.upper(), f"{kind.upper()} ist noch nicht implementiert.")
        return

    ask_and_plot(kind, fns)