"""Convert final print-based narrative code cells in notebooks to Markdown cells.
Heuristics:
- Scan the last 20 cells of each notebook.
- If a code cell contains markers like 'COMPLETE', 'SUMMARY', 'Overall Score', '='*10, or 'Integrated report displayed' and is primarily print statements, convert it.
- Prefer captured `outputs` (stream/text) to preserve evaluated values; fallback to extracting string literals from `print()` calls.
- Write notebooks back if modified and report which files changed.
"""
import nbformat
import glob
import os
import re
import ast

NOTEBOOK_DIR = "notebooks"
MARKERS = ["NOTEBOOK COMPLETE", "COMPLETE", "SUMMARY", "Overall Score", "Integrated report displayed", "DATA QUALITY AUDIT", "SUMMARY TABLE", "✅", "==", "="*10]


def extract_print_literals(source):
    lines = source.splitlines()
    out_lines = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("print("):
            try:
                # Extract the argument inside print(...)
                inner = s[len("print("):-1]
                # Safely evaluate string literals (handles single/double quoted strings)
                val = ast.literal_eval(inner)
                out_lines.append(str(val))
                continue
            except Exception:
                # fallback: remove leading print( and any f-prefix
                cleaned = re.sub(r"^print\(f?", "", s)
                cleaned = cleaned.rstrip(")")
                # strip surrounding quotes if present
                cleaned = cleaned.strip()
                out_lines.append(cleaned)
                continue
        # If line isn't a print, include it as-is
        out_lines.append(s)
    return out_lines


def cell_outputs_to_text(cell):
    texts = []
    for out in cell.get("outputs", []) or []:
        if out.get("output_type") == "stream":
            texts.append(out.get("text", ""))
        elif out.get("output_type") == "execute_result":
            data = out.get("data", {})
            if "text/plain" in data:
                texts.append(data["text/plain"] + "\n")
        elif out.get("output_type") == "display_data":
            # skip display_data (images/html)
            continue
    return "".join(texts).rstrip() if texts else ""


def looks_like_final_narrative(text):
    up = text.upper()
    for m in MARKERS:
        if isinstance(m, str) and m.upper() in up:
            return True
    # also check for many prints or big separators
    if "print(" in text and ("="*10 in text or "SUMMARY" in up):
        return True
    return False


def process_notebook(path):
    nb = nbformat.read(path, as_version=4)
    cells = nb.cells
    modified = False
    changed_cells = []
    for idx in range(len(cells)-1, max(-1, len(cells)-21), -1):
        cell = cells[idx]
        if cell.cell_type != "code":
            continue
        src = cell.source if isinstance(cell.source, str) else "".join(cell.source)
        if not src.strip():
            continue
        if looks_like_final_narrative(src):
            # prefer outputs
            out_text = cell_outputs_to_text(cell)
            if out_text:
                md = out_text
            else:
                md_lines = extract_print_literals(src)
                md = "\n".join(md_lines)
            # create markdown cell
            md_cell = nbformat.v4.new_markdown_cell(md)
            cells[idx] = md_cell
            modified = True
            changed_cells.append(idx)
    if modified:
        nbformat.write(nb, path)
    return modified, changed_cells


def main():
    nb_paths = glob.glob(os.path.join(NOTEBOOK_DIR, "*.ipynb"))
    modified_files = []
    for p in nb_paths:
        mod, cells = process_notebook(p)
        if mod:
            modified_files.append((p, cells))
    if modified_files:
        print("Modified notebooks:")
        for p, cells in modified_files:
            print(f" - {p}: converted cells at indices {cells}")
    else:
        print("No notebooks modified.")

if __name__ == "__main__":
    main()
