"""Publication plotting engine for ASPECT outputs."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from .colormaps import get_preset
from .config import load_config
from .journals import get_journal
from .output_scan import scan_output
from .recipe import write_recipe


def plot_from_config(config_path: Path) -> dict[str, Any]:
    config = load_config(config_path)
    figure = config.get("figure", {}) if isinstance(config.get("figure"), dict) else {}
    field = config.get("field", {}) if isinstance(config.get("field"), dict) else {}
    layout = config.get("layout", {}) if isinstance(config.get("layout"), dict) else {}
    journal_cfg = config.get("journal", {}) if isinstance(config.get("journal"), dict) else {}
    output_cfg = config.get("output", {}) if isinstance(config.get("output"), dict) else {}
    input_file = Path(str(config.get("input") or field.get("input") or ".")).expanduser()
    variable = str(field.get("variable") or figure.get("variable") or "temperature")
    journal = get_journal(str(journal_cfg.get("preset") or "grl"))
    color_cfg = config.get("colormap", {}) if isinstance(config.get("colormap"), dict) else {}
    cmap = get_preset(str(color_cfg.get("preset") or variable), variable)
    out_prefix = Path(str(output_cfg.get("prefix") or config_path.with_suffix(""))).resolve()
    formats = tuple(output_cfg.get("formats") or journal.formats)
    recipe_path = Path(str(output_cfg.get("recipe") or f"{out_prefix}_recipe.json")).resolve()
    metadata_path = Path(str(output_cfg.get("metadata") or f"{out_prefix}_metadata.json")).resolve()
    scan = scan_output(input_file if input_file.is_dir() else input_file.parent)
    panels = config.get("panels", [])
    if not isinstance(panels, list):
        panels = []
    metadata = {
        "input": str(input_file.resolve()),
        "variable": variable,
        "figure_type": figure.get("type", "field"),
        "panels": panels,
        "journal": journal.name,
        "width_mm": int(layout.get("width_mm") or journal.width_mm),
        "dpi": int(layout.get("dpi") or journal.dpi),
        "colormap": cmap.matplotlib,
        "color_scale": color_cfg.get("scale") or cmap.scale,
        "overlay": config.get("overlay", {}),
        "domain": config.get("domain", {}),
        "time": config.get("time", {}),
        "formats": list(formats),
        "scan": scan,
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    write_recipe(metadata, recipe_path, Path(__file__).resolve().parents[1])
    rendered = []
    if not output_cfg.get("metadata_only"):
        if metadata["figure_type"] == "multipanel" and panels:
            for index, panel in enumerate(panels):
                panel_variable = str(panel.get("variable") or variable) if isinstance(panel, dict) else variable
                panel_prefix = out_prefix.parent / f"{out_prefix.name}_{chr(97 + index)}"
                rendered.extend(_render_field(input_file, panel_variable, panel_prefix, formats, metadata))
        else:
            rendered = _render_field(input_file, variable, out_prefix, formats, metadata)
    metadata["rendered_files"] = rendered
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {"metadata": str(metadata_path), "recipe": str(recipe_path), "rendered_files": rendered}


def _select_dataset(input_file: Path, scan: dict[str, Any]) -> Path:
    if input_file.is_file():
        return input_file
    if scan.get("timesteps"):
        last = scan["timesteps"][-1].get("file")
        if last:
            return Path(last)
    for key in ("vtu", "pvtu", "pvd"):
        files = scan["files"].get(key, [])
        if files:
            return Path(files[-1])
    raise RuntimeError("No PVD/VTU/PVTU dataset found for field plotting.")


def _resolve_variable(requested: str, available: list[str]) -> str:
    aliases = {
        "temperature": ["temperature", "T"],
        "pressure": ["pressure", "p"],
        "velocity": ["velocity"],
        "viscosity": ["viscosity"],
        "strain_rate": ["strain_rate", "strain rate", "strain_rate_second_invariant"],
        "composition": ["composition", "C_1", "C_2", "C_3"],
    }
    if requested in available:
        return requested
    for candidate in aliases.get(requested.lower(), []):
        if candidate in available:
            return candidate
    matches = [name for name in available if requested.lower() in name.lower()]
    if matches:
        return matches[0]
    raise RuntimeError(f"Variable '{requested}' not found. Available: {', '.join(available)}")


def _render_field(input_file: Path, variable: str, out_prefix: Path, formats: tuple[str, ...], metadata: dict[str, Any]) -> list[str]:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/aspect-yuan-matplotlib")
    try:
        import pyvista as pv  # type: ignore
    except Exception as exc:
        raise RuntimeError("PyVista is required for ASPECT field rendering. Install pyvista/vtk or set output.metadata_only: true for recipe validation.") from exc
    dataset_path = _select_dataset(input_file, metadata["scan"])
    data = pv.read(str(dataset_path))
    available = list(data.array_names)
    chosen = _resolve_variable(variable, available)
    plotter = pv.Plotter(off_screen=True, window_size=(1600, 900))
    plotter.add_mesh(data, scalars=chosen, cmap=metadata["colormap"], show_edges=False)
    plotter.add_scalar_bar(title=chosen)
    plotter.view_xy()
    png = out_prefix.with_suffix(".png")
    png.parent.mkdir(parents=True, exist_ok=True)
    plotter.screenshot(str(png))
    plotter.close()
    rendered = [str(png)]
    for fmt in formats:
        fmt = fmt.lower()
        if fmt == "png":
            continue
        target = out_prefix.with_suffix("." + fmt)
        if fmt == "svg":
            _write_svg_from_png(png, target)
        elif fmt == "pdf":
            _convert_png(png, target, "PDF")
        elif fmt in {"tif", "tiff"}:
            _convert_png(png, target, "TIFF")
        rendered.append(str(target))
    return rendered


def _convert_png(png: Path, target: Path, fmt: str) -> None:
    try:
        from PIL import Image  # type: ignore

        image = Image.open(png)
        if fmt == "PDF":
            image.convert("RGB").save(target, "PDF", resolution=300)
        else:
            image.save(target, fmt)
    except Exception:
        target.write_bytes(png.read_bytes())


def _write_svg_from_png(png: Path, target: Path) -> None:
    try:
        from PIL import Image  # type: ignore

        image = Image.open(png)
        width, height = image.size
    except Exception:
        width, height = 1600, 900
    encoded = base64.b64encode(png.read_bytes()).decode("ascii")
    target.write_text(
        "\n".join([
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'  <image href="data:image/png;base64,{encoded}" width="{width}" height="{height}"/>',
            "</svg>",
            "",
        ]),
        encoding="utf-8",
    )
