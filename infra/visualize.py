"""Utilities to render Plotly figures, save static fallbacks, and run visual diffs.

Usage examples:
  python infra/visualize.py --target dashboard.pages.spatial:build_choropleth --out-dir reports/visuals
"""
from __future__ import annotations

import argparse
import importlib
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import plotly
    import plotly.io as pio
except Exception:
    plotly = None

try:
    from PIL import Image
    import imagehash
except Exception:
    Image = None
    imagehash = None


def load_figure(target: str):
    """Load a plotting function as module:function and call it to get a Plotly Figure."""
    module_name, func_name = target.split(":")
    mod = importlib.import_module(module_name)
    fn = getattr(mod, func_name)
    fig = fn()
    return fig


def save_interactive(fig, out_html: Path):
    out_html.parent.mkdir(parents=True, exist_ok=True)
    pio.write_html(fig, file=str(out_html), include_plotlyjs="cdn")


def save_static(fig, out_png: Path):
    out_png.parent.mkdir(parents=True, exist_ok=True)
    # uses kaleido under the hood
    pio.write_image(fig, str(out_png), width=1200, height=800)


def visual_diff(img_a: Path, img_b: Path) -> Optional[int]:
    """Compute perceptual hash difference; return hamming distance or None if tools missing."""
    if Image is None or imagehash is None:
        return None
    a = Image.open(img_a).convert("RGB")
    b = Image.open(img_b).convert("RGB")
    ha = imagehash.phash(a)
    hb = imagehash.phash(b)
    return ha - hb


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="module:function that returns a plotly Figure")
    parser.add_argument("--out-dir", default="reports/visuals")
    parser.add_argument("--baseline", required=False, help="path to baseline image for visual diff")
    parser.add_argument("--name", default=None)
    parser.add_argument("--threshold", type=int, default=8, help="hamming distance threshold to fail")
    args = parser.parse_args()

    fig = load_figure(args.target)
    name = args.name or args.target.replace(":", "_")
    date = datetime.utcnow().strftime("%Y-%m-%d")
    outdir = Path(args.out_dir) / name / date
    outdir.mkdir(parents=True, exist_ok=True)

    html_path = outdir / f"{name}.html"
    png_path = outdir / f"{name}.png"
    save_interactive(fig, html_path)
    save_static(fig, png_path)

    result = {"name": name, "html": str(html_path), "png": str(png_path)}

    if args.baseline:
        diff = visual_diff(Path(args.baseline), png_path)
        result["baseline"] = args.baseline
        result["diff"] = None if diff is None else int(diff)
        result["passed"] = (diff is not None and diff <= args.threshold)

    print(result)


if __name__ == '__main__':
    cli()
