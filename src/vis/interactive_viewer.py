"""Interactive PyVista viewer with in-window controls for lattice parameters."""

from dataclasses import dataclass
import logging
import math
import tkinter as tk
from tkinter import simpledialog

import numpy as np
import pyvista as pv
from pyvista import _vtk

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
from vis.plotting import colors_bcc, colors_fcc, colors_fcc_planes, colors_hcp, radius_bcc, radius_fcc, radius_hcp

LATTICE_KINDS = ("bcc", "fcc", "hcp", "hcp_hex", "fcc_planes")
MANUAL_MIN_RES = 3
MANUAL_MAX_RES = 100
_TEXTURE_WARN_NEEDLE = "No scalar values found for texture input"
_VTK_FILTER_INSTALLED = False
_LOG_FILTER_INSTALLED = False


@dataclass
class ViewerState:
    kind: str = "fcc"
    a: float = 1.0
    n: int = 2
    sphere_res: int = 24
    manual_res: bool = False
    unit_cell: bool = False


def _auto_resolution_from_atom_count(num_atoms: int) -> int:
    """Compute sphere resolution from atom count using a smooth triangle-budget formula."""
    if num_atoms <= 0:
        return MANUAL_MIN_RES

    # Dynamic global triangle budget:
    # - high detail for small models
    # - smooth decay with increasing atom count (less aggressive downsizing)
    # - no hard atom-count thresholds
    total_target_tris = 400_000.0 + 20_000_000.0 / (1.0 + (num_atoms / 3_000.0) ** 0.8)
    tris_per_sphere = max(8.0, total_target_tris / float(num_atoms))

    # For pyvista Sphere, cell count scales roughly with:
    # tris ~= 2 * res * (res - 2)
    # Invert this to estimate a resolution from tris_per_sphere.
    res = 1.0 + math.sqrt(1.0 + 0.5 * tris_per_sphere)
    res = int(round(res))
    return max(MANUAL_MIN_RES, min(MANUAL_MAX_RES, res))


def _display_kind_name(kind: str) -> str:
    return kind.upper().replace("_", " ")


class _VtkTextureMessageFilter(_vtk.vtkOutputWindow):
    """Filter known non-fatal VTK texture spam while keeping other messages."""

    def _is_filtered(self, txt: object) -> bool:
        text = str(txt)
        return _TEXTURE_WARN_NEEDLE in text

    def DisplayText(self, txt: object) -> None:  # noqa: N802
        if not self._is_filtered(txt):
            super().DisplayText(txt)

    def DisplayWarningText(self, txt: object) -> None:  # noqa: N802
        if not self._is_filtered(txt):
            super().DisplayWarningText(txt)

    def DisplayErrorText(self, txt: object) -> None:  # noqa: N802
        if not self._is_filtered(txt):
            super().DisplayErrorText(txt)

    def DisplayGenericWarningText(self, txt: object) -> None:  # noqa: N802
        if not self._is_filtered(txt):
            super().DisplayGenericWarningText(txt)


class _PyLoggingTextureFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return _TEXTURE_WARN_NEEDLE not in msg


def _install_texture_message_filters() -> None:
    global _VTK_FILTER_INSTALLED, _LOG_FILTER_INSTALLED

    if not _VTK_FILTER_INSTALLED:
        try:
            _vtk.vtkOutputWindow.SetInstance(_VtkTextureMessageFilter())
            _VTK_FILTER_INSTALLED = True
        except Exception:
            # Fallback: keep default output behavior if VTK filter cannot be installed.
            pass

    if not _LOG_FILTER_INSTALLED:
        logging.getLogger().addFilter(_PyLoggingTextureFilter())
        _LOG_FILTER_INSTALLED = True


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
    _install_texture_message_filters()
    state = ViewerState()
    a_slider = None
    res_slider = None
    syncing_res_slider = False
    initializing_controls = True
    initial_pts = _build_lattice(state)[0]
    state.sphere_res = _auto_resolution_from_atom_count(len(initial_pts))

    plotter = pv.Plotter()
    plotter.disable_stereo_render()
    if plotter.ren_win is not None:
        # Explicitly disable stereo-capable mode on the native VTK window.
        # Some drivers still emit CrystalEyes warnings during redraw otherwise.
        try:
            plotter.ren_win.StereoCapableWindowOff()
        except Exception:
            pass
        try:
            plotter.ren_win.StereoRenderOff()
        except Exception:
            pass
    status_name = "status_text"
    hint_name_prefix = "hint_text_"
    left_panel_name = "left_panel_text"
    layout_state = {"size": None, "updating": False}

    def text_block_size(lines: list[str], font_size: int) -> tuple[int, int]:
        char_w = max(6, int(font_size * 0.66))
        line_h = font_size + 7
        width_px = max((len(line) for line in lines), default=1) * char_w
        height_px = len(lines) * line_h
        return width_px, height_px

    def fit_font_size(lines: list[str], preferred: int, minimum: int, max_width_px: int) -> int:
        size = preferred
        while size > minimum and text_block_size(lines, size)[0] > max_width_px:
            size -= 1
        return size

    def redraw(reset_camera: bool = False) -> None:
        nonlocal res_slider, syncing_res_slider
        pts, radius, colors = _build_lattice(state)
        if not state.manual_res:
            # Auto mode follows a smooth atom-count decay curve.
            state.sphere_res = _auto_resolution_from_atom_count(len(pts))
            if res_slider is not None:
                current_value = int(round(float(res_slider.GetRepresentation().GetValue())))
                if current_value != state.sphere_res:
                    syncing_res_slider = True
                    res_slider.GetRepresentation().SetValue(state.sphere_res)
                    syncing_res_slider = False
        sphere = pv.Sphere(radius=radius, theta_resolution=state.sphere_res, phi_resolution=state.sphere_res)
        cloud = pv.PolyData(pts)
        glyphs = cloud.glyph(geom=sphere, scale=False, orient=False)
        glyphs["colors"] = np.repeat(colors, sphere.n_points, axis=0)

        plotter.add_mesh(glyphs, scalars="colors", rgb=True, name="lattice", reset_camera=reset_camera)

        win_w, win_h = plotter.ren_win.GetSize()
        left_lines = ["LATTICE TYPE"]
        for idx, kind in enumerate(LATTICE_KINDS, start=4):
            marker = ">" if state.kind == kind else " "
            left_lines.append(f"{marker} {idx} {_display_kind_name(kind)}")
        left_lines.append(f"UNIT CELL: {'ON' if state.unit_cell else 'OFF'}")
        left_font = fit_font_size(left_lines, preferred=12, minimum=9, max_width_px=int(win_w * 0.38))
        left_actor = plotter.add_text(
            "\n".join(left_lines),
            position=(0.02, 0.98),
            viewport=True,
            font_size=left_font,
            color="black",
            name=left_panel_name,
        )
        try:
            left_prop = left_actor.GetTextProperty()
            left_prop.SetJustificationToLeft()
            left_prop.SetVerticalJustificationToTop()
        except Exception:
            pass

        top_y = 0.98
        status_line = (
            f"a={state.a:.2f} | n={state.n} | "
            f"atoms={len(pts)} | res={state.sphere_res} ({'manual' if state.manual_res else 'auto'})"
        )
        status_font = fit_font_size([status_line], preferred=11, minimum=7, max_width_px=int(win_w * 0.62))
        status_actor = plotter.add_text(
            status_line,
            position=(0.98, top_y),
            viewport=True,
            font_size=status_font,
            color="black",
            name=status_name,
        )
        try:
            status_prop = status_actor.GetTextProperty()
            status_prop.SetJustificationToRight()
            status_prop.SetVerticalJustificationToTop()
        except Exception:
            pass

        hint_lines = [
            "4-8 switch lattice type",
            "N adjust atom count",
            "U toggle unit cell",
            "R enable auto-res",
            "A reset a",
        ]
        hint_font = fit_font_size(hint_lines, preferred=11, minimum=7, max_width_px=int(win_w * 0.44))
        line_px = hint_font + 7
        line_dy = line_px / max(1, win_h)
        y0 = top_y - ((status_font + 9) / max(1, win_h))
        for idx, line in enumerate(hint_lines):
            hint_actor = plotter.add_text(
                line,
                position=(0.98, max(0.02, y0 - (idx * line_dy))),
                viewport=True,
                font_size=hint_font,
                color="black",
                name=f"{hint_name_prefix}{idx}",
            )
            try:
                hint_prop = hint_actor.GetTextProperty()
                hint_prop.SetJustificationToRight()
                hint_prop.SetVerticalJustificationToTop()
            except Exception:
                pass
        if reset_camera:
            # Keep a consistent outside view after topology changes (n/kind/unit-cell).
            plotter.reset_camera()
            try:
                plotter.camera.zoom(0.9)
            except Exception:
                pass
        if plotter.ren_win is not None:
            try:
                plotter.ren_win.StereoRenderOff()
            except Exception:
                pass
        plotter.render()

    def on_a_change(value: float) -> None:
        state.a = max(0.01, float(value))
        redraw()

    def on_res_change(value: float) -> None:
        nonlocal syncing_res_slider
        if not syncing_res_slider and not initializing_controls:
            state.manual_res = True
        state.sphere_res = max(MANUAL_MIN_RES, int(round(value)))
        redraw()

    def on_kind_change(kind: str) -> None:
        state.kind = kind
        redraw(reset_camera=True)

    def toggle_unit_cell() -> None:
        state.unit_cell = not state.unit_cell
        redraw(reset_camera=True)

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
            redraw(reset_camera=True)

    def on_resize(*_) -> None:
        if layout_state["updating"]:
            return
        size = tuple(plotter.ren_win.GetSize())
        if layout_state["size"] != size:
            layout_state["size"] = size
            redraw()

    def reset_auto_res() -> None:
        state.manual_res = False
        redraw()

    def reset_a_value() -> None:
        state.a = 1.0
        if a_slider is not None:
            try:
                a_slider.GetRepresentation().SetValue(state.a)
            except Exception:
                pass
        redraw()

    a_slider = plotter.add_slider_widget(
        callback=on_a_change,
        rng=(0.2, 5.0),
        value=state.a,
        title="a (lattice constant)",
        pointa=(0.02, 0.08),
        pointb=(0.44, 0.08),
        style="modern",
        interaction_event="end",
    )
    res_slider = plotter.add_slider_widget(
        callback=on_res_change,
        rng=(MANUAL_MIN_RES, MANUAL_MAX_RES),
        value=state.sphere_res,
        title="sphere resolution",
        pointa=(0.56, 0.08),
        pointb=(0.98, 0.08),
        style="modern",
        interaction_event="end",
    )
    initializing_controls = False

    plotter.add_key_event("n", ask_n_input)
    plotter.add_key_event("N", ask_n_input)
    plotter.add_key_event("r", reset_auto_res)
    plotter.add_key_event("R", reset_auto_res)
    plotter.add_key_event("u", toggle_unit_cell)
    plotter.add_key_event("U", toggle_unit_cell)
    plotter.add_key_event("a", reset_a_value)
    plotter.add_key_event("A", reset_a_value)
    for idx, kind in enumerate(LATTICE_KINDS, start=4):
        plotter.add_key_event(str(idx), lambda k=kind: on_kind_change(k))
    resize_observer = plotter.iren.add_observer("ConfigureEvent", on_resize) if plotter.iren is not None else None

    layout_state["size"] = tuple(plotter.ren_win.GetSize())
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
