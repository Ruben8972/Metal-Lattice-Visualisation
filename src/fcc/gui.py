import tkinter as tk
from tkinter import simpledialog, messagebox
from fcc.plotting import plot_crystal_pyvista, radius_bcc, colors_bcc, radius_fcc, colors_fcc, radius_hcp, colors_hcp
from fcc.generation import generate_fcc, generate_bcc, generate_hcp, generate_hcp_hex

GITTER = {
    "fcc": {"generate": generate_fcc, "radius": radius_fcc, "colors": colors_fcc},
    "bcc": {"generate": generate_bcc, "radius": radius_bcc, "colors": colors_bcc},
    "hcp": {"generate": generate_hcp, "radius": radius_hcp, "colors": colors_hcp},
    "hcp_hex": {"generate": generate_hcp_hex, "radius": radius_hcp, "colors": colors_hcp}
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

def custom_dialog(parent, title, message, button1_text, button2_text):
    dialog = tk.Toplevel()
    center_window(dialog, 300, 150)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.grab_set()
    tk.Label(dialog, text=message, padx=20, pady=10).pack()
    result = tk.StringVar()

    def set_result(value):
        result.set(value)
        dialog.destroy()
    
    frame = tk.Frame(dialog)
    frame.pack(pady=10)
    tk.Button(frame, text=button1_text, width=10, command=lambda: set_result(button1_text)).pack(side="left", padx=5)
    tk.Button(frame, text=button2_text, width=10, command=lambda: set_result(button2_text)).pack(side="left", padx=5)
    dialog.wait_window()
    return result.get()

def ask_and_plot(kind: str, fns: dict) -> None:
    root = tk.Tk()
    root.withdraw()

    if kind == "hcp":
        auswahl = custom_dialog(
            parent=root,
            title="HCP Auswahl",
            message="Bitte Wählen sie den Einheitszellentyp",
            button1_text="Primitiv",
            button2_text="Sechseckig"
        )
        if auswahl == "Sechseckig":
            kind = "hcp_hex"
            fns = GITTER.get("hcp_hex")
        elif not auswahl:
            root.destroy()
            return

    plot_unit = messagebox.askyesnocancel(
        parent=root,
        title="Einheitszelle?",
        message="Möchten Sie nur eine Einheitszelle plotten?",
    )
    if plot_unit is None:
        root.destroy()
        return

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
        
        if kind == "hcp_hex":
            R = 1
            nz = 2
            pts = fns["generate"](a, R, nz)
        else:
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
        
        if kind == "hcp_hex":
            R = n
            nz = n+1
            pts = fns["generate"](a, R, nz)
        else:
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