"""Interactive PyVista viewer with in-window controls for lattice parameters."""

from dataclasses import dataclass
import tkinter as tk
from tkinter import simpledialog

import numpy as np
import pyvista as pv

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
from vis.plotting import auto_resolution, colors_bcc, colors_fcc, colors_fcc_planes, colors_hcp, radius_bcc, radius_fcc, radius_hcp

LATTICE_KINDS = ("bcc", "fcc", "hcp", "hcp_hex", "fcc_planes")


@dataclass
class ViewerState:
    kind: str = "fcc"
    a: float = 1.0
    n: int = 2
    sphere_res: int = 24
    unit_cell: bool = False


def _build_lattice(state: ViewerState) -> tuple[np.ndarray, float, np.ndarray]:
    if state.kind == "bcc":
        cells = 2 if state.unit_cell else state.n
        pts = generate_bcc(state.a, cells)
        radius = radius_bcc(state.a)
        colors = colors_bcc(pts, state.a)
    elif state.kind == "fcc":
        cells = 2 if state.unit_cell else state.n
        pts = generate_fcc(state.a, cells)
        radius = radius_fcc(state.a)
        colors = colors_fcc(pts, state.a)
    elif state.kind == "hcp":
        cells = 2 if state.unit_cell else state.n
        pts = generate_hcp(state.a, cells)
        radius = radius_hcp(state.a)
        colors = colors_hcp(pts, state.a)
    elif state.kind == "hcp_hex":
        r_cells = 1 if state.unit_cell else state.n
        nz = 2 if state.unit_cell else state.n + 1
        pts = generate_hcp_hex(state.a, r_cells, nz, basis_hcp_fracs(), a_vecs_hcp, clip_hex_boundary=True)
        radius = radius_hcp(state.a)
        colors = colors_hcp(pts, state.a)
    elif state.kind == "fcc_planes":
        if state.unit_cell:
            # Requested behavior: FCC planes + unit cell shows canonical FCC unit cell.
            pts = generate_fcc(state.a, 2)
            radius = radius_fcc(state.a)
            colors = colors_fcc(pts, state.a)
        else:
            r_cells = state.n
            nz = state.n + 1
            pts = generate_hcp_hex(
                state.a,
                r_cells,
                nz,
                basis_fcc_frac_plane(),
                a_vecs_fcc_planes,
                clip_hex_boundary=True,
            )
            radius = radius_fcc(state.a)
            colors = colors_fcc_planes(pts, state.a)
    else:
        raise ValueError(f"Unknown lattice kind: {state.kind}")
    return pts, radius, colors


def run_interactive_viewer() -> None:
    state = ViewerState()

    plotter = pv.Plotter()
    plotter.disable_stereo_render()
    status_name = "status_text"
    n_info_name = "n_info_text"
    kind_label_names = tuple(f"kind_label_{k}" for k in LATTICE_KINDS)
    panel_text_names = ("lattice_panel_title", "unit_cell_label", *kind_label_names)
    layout_state = {"size": None, "updating": False, "n_info_y": 520}

    def redraw() -> None:
        pts, radius, colors = _build_lattice(state)
        sphere = pv.Sphere(radius=radius, theta_resolution=state.sphere_res, phi_resolution=state.sphere_res)
        cloud = pv.PolyData(pts)
        glyphs = cloud.glyph(geom=sphere, scale=False, orient=False)
        glyphs["colors"] = np.repeat(colors, sphere.n_points, axis=0)

        plotter.remove_actor("lattice")
        plotter.add_mesh(glyphs, scalars="colors", rgb=True, name="lattice", reset_camera=False)

        plotter.remove_actor(status_name)
        plotter.add_text(
            (
                f"kind={state.kind} | a={state.a:.2f} | n={state.n} | "
                f"res={state.sphere_res} | unit_cell={state.unit_cell} | atoms={len(pts)}"
            ),
            position="upper_right",
            font_size=10,
            color="black",
            name=status_name,
        )

        plotter.remove_actor(n_info_name)
        plotter.add_text(
            f"Atom count n: {state.n} (N to edit)",
            position=(20, layout_state["n_info_y"]),
            font_size=10,
            color="black",
            name=n_info_name,
        )
        plotter.render()

    def on_a_change(value: float) -> None:
        state.a = max(0.01, float(value))
        redraw()

    def on_res_change(value: float) -> None:
        state.sphere_res = max(8, int(round(value)))
        redraw()

    def on_kind_change(kind: str) -> None:
        state.kind = kind
        redraw()

    def on_unit_toggle(value: bool) -> None:
        state.unit_cell = bool(value)
        redraw()

    def ask_n_input() -> None:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        new_n = simpledialog.askinteger(
            "Atom count",
            "Atom count per direction (integer >= 1):",
            parent=root,
            minvalue=1,
            initialvalue=state.n,
        )
        root.destroy()
        if new_n is not None:
            state.n = int(new_n)
            redraw()

    def build_top_left_controls() -> None:
        layout_state["updating"] = True
        try:
            plotter.clear_radio_button_widgets()
            plotter.clear_button_widgets()
            for name in panel_text_names:
                plotter.remove_actor(name)

            _, height = plotter.ren_win.GetSize()
            panel_x = 20
            panel_y_top = int(height - 68)
            row_gap = 30

            plotter.add_text(
                "LATTICE TYPE",
                position=(panel_x, panel_y_top + 24),
                font_size=12,
                color="black",
                shadow=False,
                name="lattice_panel_title",
            )

            for idx, kind in enumerate(LATTICE_KINDS):
                y = panel_y_top - (idx * row_gap)
                plotter.add_radio_button_widget(
                    callback=lambda k=kind: on_kind_change(k),
                    radio_button_group="lattice_kind",
                    value=state.kind == kind,
                    position=(panel_x, y),
                    size=18,
                )
                plotter.add_text(
                    kind.upper(),
                    position=(panel_x + 26, y + 1),
                    font_size=10,
                    color="black",
                    name=f"kind_label_{kind}",
                )

            unit_y = panel_y_top - (len(LATTICE_KINDS) * row_gap) - 6
            plotter.add_checkbox_button_widget(
                callback=on_unit_toggle,
                value=state.unit_cell,
                position=(panel_x, unit_y),
                size=18,
            )
            plotter.add_text(
                "Unit Cell",
                position=(panel_x + 26, unit_y + 1),
                font_size=10,
                color="black",
                name="unit_cell_label",
            )
            layout_state["n_info_y"] = unit_y - 34
            layout_state["size"] = tuple(plotter.ren_win.GetSize())
        finally:
            layout_state["updating"] = False

    def on_resize(*_) -> None:
        if layout_state["updating"]:
            return
        size = tuple(plotter.ren_win.GetSize())
        if layout_state["size"] != size:
            build_top_left_controls()
            redraw()

    plotter.add_slider_widget(
        callback=on_a_change,
        rng=(0.2, 5.0),
        value=state.a,
        title="a (lattice constant)",
        pointa=(0.02, 0.08),
        pointb=(0.44, 0.08),
        style="modern",
        interaction_event="end",
    )
    plotter.add_slider_widget(
        callback=on_res_change,
        rng=(8, 100),
        value=state.sphere_res,
        title="sphere resolution",
        pointa=(0.56, 0.08),
        pointb=(0.98, 0.08),
        style="modern",
        interaction_event="end",
    )

    plotter.add_key_event("n", ask_n_input)
    plotter.add_key_event("N", ask_n_input)
    resize_observer = plotter.iren.add_observer("ConfigureEvent", on_resize) if plotter.iren is not None else None

    state.sphere_res = auto_resolution(len(_build_lattice(state)[0]))
    build_top_left_controls()
    redraw()
    try:
        plotter.show()
    except KeyboardInterrupt:
        # Avoid noisy traceback when the terminal session is interrupted.
        pass
    finally:
        if resize_observer is not None and plotter.iren is not None:
            try:
                plotter.iren.remove_observer(resize_observer)
            except Exception:
                pass
