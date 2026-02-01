"""Minimal reporting assembler: runs notebooks (papermill), converts to HTML (nbconvert), and injects into Jinja templates.

Usage:
  python infra/report.py --notebook notebooks/data_quality_audit_notebook.ipynb --params '{"date":"2026-01-31"}' --out reports/data_quality_2026-01-31.html
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import tempfile

try:
    import papermill as pm
    from nbconvert import HTMLExporter
    import nbformat
    from jinja2 import Environment, FileSystemLoader
except Exception:
    pm = None
    HTMLExporter = None
    nbformat = None
    Environment = None


def run_notebook(src: Path, params: dict, executed_nb: Path):
    if pm is None:
        raise RuntimeError("papermill not installed")
    pm.execute_notebook(str(src), str(executed_nb), parameters=params)


def nb_to_html(nb_path: Path) -> str:
    if HTMLExporter is None or nbformat is None:
        raise RuntimeError("nbconvert or nbformat missing")
    nb = nbformat.read(str(nb_path), as_version=4)
    exporter = HTMLExporter()
    body, _ = exporter.from_notebook_node(nb)
    return body


def assemble_report(body_html: str, title: str, template_dir: Path, out_path: Path):
    if Environment is None:
        # fallback: write body directly
        out_path.write_text(body_html)
        return
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    tpl = env.get_template("report_base.html")
    out_html = tpl.render(title=title, body=body_html, generated_at=datetime.utcnow().isoformat())
    out_path.write_text(out_html)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--notebook", required=True)
    parser.add_argument("--params", default="{}")
    parser.add_argument("--out", required=True)
    parser.add_argument("--template-dir", default="reports/templates")
    args = parser.parse_args()

    nb = Path(args.notebook)
    out_path = Path(args.out)
    params = json.loads(args.params)

    with tempfile.TemporaryDirectory() as td:
        executed = Path(td) / (nb.stem + "_executed.ipynb")
        if pm is None:
            raise RuntimeError("papermill not installed; cannot run notebooks")
        run_notebook(nb, params, executed)
        body = nb_to_html(executed)
        assemble_report(body, title=nb.stem, template_dir=Path(args.template_dir), out_path=out_path)


if __name__ == '__main__':
    cli()
