"""Tkinter GUI for selecting and plotting crystal lattices."""

import tkinter as tk
from tkinter import messagebox, simpledialog

from vis.generation import (
    a_vecs_fcc_planes,
    a_vecs_hcp,
    basis_fcc_frac_plane,
    basis_hcp_fracs,
    generate_bcc,
    generate_fcc,
    generate_hcp,
    generate_hcp_hex,
)
from vis.plotting import (
    colors_bcc,
    colors_fcc,
    colors_fcc_planes,
    colors_hcp,
    plot_crystal_pyvista,
    radius_bcc,
    radius_fcc,
    radius_hcp,
)


def _build_standard(generate_fn, a: float, n: int, plot_unit: bool):
    cells = 2 if plot_unit else n
    return generate_fn(a, cells)


def _build_hcp_hex(a: float, n: int, plot_unit: bool):
    r_cells = 1 if plot_unit else n
    nz = 2 if plot_unit else n + 1
    return generate_hcp_hex(a, r_cells, nz, basis_hcp_fracs(), a_vecs_hcp)


def _build_fcc_planes(a: float, n: int, plot_unit: bool):
    r_cells = 1 if plot_unit else n
    nz = 2 if plot_unit else n + 1
    return generate_hcp_hex(a, r_cells, nz, basis_fcc_frac_plane(), a_vecs_fcc_planes)


GITTER = {
    "fcc": {"build": lambda a, n, u: _build_standard(generate_fcc, a, n, u), "radius": radius_fcc, "colors": colors_fcc},
    "bcc": {"build": lambda a, n, u: _build_standard(generate_bcc, a, n, u), "radius": radius_bcc, "colors": colors_bcc},
    "hcp": {"build": lambda a, n, u: _build_standard(generate_hcp, a, n, u), "radius": radius_hcp, "colors": colors_hcp},
    "hcp_hex": {"build": _build_hcp_hex, "radius": radius_hcp, "colors": colors_hcp},
    "fcc_planes": {"build": _build_fcc_planes, "radius": radius_fcc, "colors": colors_fcc_planes},
}


def center_window(window: tk.Tk, width: int = 250, height: int = 180) -> None:
    window.withdraw()
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.deiconify()


def custom_dialog(parent: tk.Tk, title: str, message: str, button1_text: str, button2_text: str) -> str:
    dialog = tk.Toplevel(parent)
    center_window(dialog, 320, 150)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.transient()
    dialog.lift()
    dialog.focus_force()

    tk.Label(dialog, text=message, padx=20, pady=10).pack()
    result = tk.StringVar(value="")

    def set_result(value: str) -> None:
        result.set(value)
        dialog.destroy()

    frame = tk.Frame(dialog)
    frame.pack(pady=10)
    tk.Button(frame, text=button1_text, width=12, command=lambda: set_result(button1_text)).pack(side="left", padx=5)
    tk.Button(frame, text=button2_text, width=12, command=lambda: set_result(button2_text)).pack(side="left", padx=5)
    dialog.wait_window()
    return result.get()


def resolve_kind(root: tk.Tk, kind: str) -> str | None:
    if kind == "hcp":
        selection = custom_dialog(
            parent=root,
            title="HCP Auswahl",
            message="Bitte waehlen Sie den Zelltyp:",
            button1_text="Primitiv",
            button2_text="Sechseckig",
        )
        if selection == "Sechseckig":
            return "hcp_hex"
        return "hcp" if selection else None

    if kind == "fcc":
        selection = custom_dialog(
            parent=root,
            title="FCC Auswahl",
            message="Bitte waehlen Sie die Darstellung:",
            button1_text="Ebenen",
            button2_text="Einheitszelle",
        )
        if selection == "Ebenen":
            return "fcc_planes"
        return "fcc" if selection else None

    return kind


def ask_and_plot(kind: str) -> None:
    root = tk.Tk()
    root.withdraw()

    resolved_kind = resolve_kind(root, kind)
    if not resolved_kind:
        root.destroy()
        return

    plot_unit = messagebox.askyesnocancel(
        parent=root,
        title="Einheitszelle",
        message="Moechten Sie nur eine Einheitszelle plotten?",
    )
    if plot_unit is None:
        root.destroy()
        return

    a = simpledialog.askfloat(
        "Gitterkonstante",
        "Laenge der Gitterkonstante:",
        parent=root,
        minvalue=0.01,
    )
    if a is None:
        root.destroy()
        return

    n = 1
    if not plot_unit:
        n = simpledialog.askinteger(
            "Atomanzahl je Richtung",
            "Atomanzahl je Richtung:",
            parent=root,
            minvalue=1,
        )
        if n is None:
            root.destroy()
            return

    fns = GITTER.get(resolved_kind)
    if fns is None:
        messagebox.showinfo(resolved_kind.upper(), f"{resolved_kind.upper()} ist nicht implementiert.")
        root.destroy()
        return

    pts = fns["build"](a, n, plot_unit)
    r = fns["radius"](a)
    cols = fns["colors"](pts, a)
    plot_crystal_pyvista(pts, r, cols)

    root.destroy()


def run_gui() -> None:
    selection = {}

    def set_choice(kind: str) -> None:
        selection["kind"] = kind
        win.destroy()

    win = tk.Tk()
    win.title("Gitter auswaehlen")
    center_window(win, 280, 220)

    tk.Label(win, text="Welches Gitter moechten Sie erstellen?").pack(pady=10)
    for name in ["fcc", "bcc", "hcp"]:
        tk.Button(win, text=name.upper(), width=14, command=lambda k=name: set_choice(k)).pack(pady=5)
    win.mainloop()

    kind = selection.get("kind")
    if kind:
        ask_and_plot(kind)
